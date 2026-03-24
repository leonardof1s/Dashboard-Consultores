import streamlit as st
import pandas as pd
import altair as alt


def render(col_vendas):
    st.title("📜 Histórico de Pagamentos")

    # 🔐 VALIDA LOGIN
    if "usuario" not in st.session_state:
        st.warning("Faça login primeiro")
        st.stop()

    usuario_id = st.session_state["usuario"]["_id"]

    # 🔥 FILTRO POR USUÁRIO
    vendas = list(col_vendas.find({"usuario_id": usuario_id}))

    if not vendas:
        st.info("Nenhuma venda encontrada.")
        return

    # ------------------ TRANSFORMAÇÃO ------------------
    dados = []

    for venda in vendas:
        for parcela in venda.get("comissoes", []):
            dados.append({
                "consultor": venda.get("consultor"),
                "cliente": venda.get("cliente"),
                "mes": parcela.get("mes"),
                "valor": float(parcela.get("valor_parcela", 0)),
                "recebido": parcela.get("consultor_recebe", False),
            })

    if not dados:
        st.warning("Nenhuma comissão encontrada.")
        return

    df = pd.DataFrame(dados)

    # ------------------ FILTRO ------------------
    consultores = ["Todos"] + sorted(df["consultor"].dropna().unique().tolist())

    consultor_sel = st.selectbox("Filtrar por consultor", consultores)

    if consultor_sel != "Todos":
        df = df[df["consultor"] == consultor_sel]

    # ------------------ KPIs ------------------
    total_recebido = df[df["recebido"] == True]["valor"].sum()
    total_pendente = df[df["recebido"] == False]["valor"].sum()

    col1, col2 = st.columns(2)
    col1.metric("💰 Recebido", f"R$ {total_recebido:,.2f}")
    col2.metric("⏳ Pendente", f"R$ {total_pendente:,.2f}")

    # ------------------ TABELA ------------------
    st.subheader("📋 Detalhamento")

    st.dataframe(
        df.sort_values("mes").style.format({"valor": "R$ {:,.2f}"}),
        use_container_width=True,
        hide_index=True
    )

    # ------------------ GRÁFICO ------------------
    st.subheader("📊 Evolução por Mês")

    grafico = (
        alt.Chart(df)
        .mark_bar()
        .encode(
            x=alt.X("mes:N", title="Mês"),
            y=alt.Y("valor:Q", title="Valor (R$)"),
            color=alt.Color("recebido:N", title="Status"),
            tooltip=["cliente", "valor", "recebido"]
        )
    )

    st.altair_chart(grafico, use_container_width=True)
