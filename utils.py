import pandas as pd
from datetime import datetime
from io import BytesIO

def calcular_comissao(valor: float) -> float:
    return round((valor * 0.015) / 13, 2)

def carregar_vendas(col_vendas, data_inicio=None, data_fim=None):
    query = {}
    if data_inicio:
        query["data"] = {"$gte": datetime.combine(data_inicio, datetime.min.time())}
    if data_fim:
        if "data" not in query:
            query["data"] = {}
        query["data"]["$lte"] = datetime.combine(data_fim, datetime.max.time())

    vendas = list(col_vendas.find(query).sort("data", -1))
    if not vendas:
        return pd.DataFrame()

    df = pd.DataFrame(vendas)
    df["data"] = pd.to_datetime(df["data"])
    df["total_comissao"] = df.apply(
        lambda row: sum(p.get("valor_parcela", 0) for p in row.get("comissoes", [])
                        if p.get("consultor_recebe", False))
        if isinstance(row.get("comissoes"), list) else 0.0, axis=1
    )
    df["mes_ano"] = df["data"].dt.strftime("%Y-%m")
    df["semana"] = df["data"].dt.strftime("%Y-%W")
    return df

def to_excel(df: pd.DataFrame) -> BytesIO:
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False)
    output.seek(0)
    return output
