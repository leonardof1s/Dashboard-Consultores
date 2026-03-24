import pandas as pd
from datetime import datetime
from io import BytesIO


def calcular_comissao_padrao(valor: float) -> float:
    return round((valor * 0.015), 2)


def calcular_parcela(comissao_total: float) -> float:
    return round(comissao_total / 13, 2)


def carregar_vendas(col_vendas, data_inicio=None, data_fim=None, usuario_id=None):
    query = {}

    if data_inicio:
        query["data"] = {
            "$gte": datetime.combine(data_inicio, datetime.min.time())
        }

    if data_fim:
        if "data" not in query:
            query["data"] = {}
        query["data"]["$lte"] = datetime.combine(data_fim, datetime.max.time())

    # 🔐 filtro por usuário (multi-tenant)
    if usuario_id:
        query["usuario_id"] = usuario_id

    vendas = list(col_vendas.find(query).sort("data", -1))

    # 🛑 evita erro se não houver dados
    if not vendas:
        return pd.DataFrame()

    df = pd.DataFrame(vendas)
    df["data"] = pd.to_datetime(df["data"])

    # 🔥 cálculo profissional de comissão
    def calcular_total_comissao(row):
        # caso tenha parcelas
        if isinstance(row.get("comissoes"), list) and row["comissoes"]:
            return sum(
                float(p.get("valor_parcela", 0))
                for p in row["comissoes"]
                if p.get("consultor_recebe", False)
            )

        # fallback: comissão definida manualmente
        if row.get("comissao_definida"):
            return float(row["comissao_definida"])

        # fallback final: padrão 1.5%
        valor = float(row.get("valor", 0))
        return calcular_comissao_padrao(valor)

    df["total_comissao"] = df.apply(calcular_total_comissao, axis=1)

    df["mes_ano"] = df["data"].dt.strftime("%Y-%m")
    df["semana"] = df["data"].dt.strftime("%Y-%W")

    return df


def to_excel(df: pd.DataFrame) -> BytesIO:
    output = BytesIO()

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False)

    output.seek(0)
    return output