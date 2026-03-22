import streamlit as st


def render(df_vendas):
    st.title("📊 Dashboard Geral")
    if df_vendas.empty:
        st.info("Nenhuma venda no período.")
    else:
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Vendas", f"R$ {df_vendas['valor'].sum():,.2f}")
        col2.metric("Total Comissão (13x)", f"R$ {df_vendas['total_comissao'].sum():,.2f}")
        col3.metric("Quantidade de Vendas", len(df_vendas))
        col4.metric("Líder em Vendas", df_vendas.groupby("consultor")["valor"].sum().idxmax())
