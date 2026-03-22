import streamlit as st


def render(df_vendas):
    st.title("🔍 Buscar por Cliente")
    termo = st.text_input("Nome do cliente (ou parte)").strip()
    if termo:
        res = df_vendas[df_vendas["cliente"].str.contains(termo, case=False, na=False)].copy()
        if res.empty:
            st.warning("Nenhum resultado.")
        else:
            st.dataframe(
                res[["data", "consultor", "cliente", "valor", "total_comissao"]].style.format({
                    "data": "{:%d/%m/%Y}",
                    "valor": "R$ {:,.2f}",
                    "total_comissao": "R$ {:,.2f}"
                }),
                use_container_width=True,
                hide_index=True
            )
