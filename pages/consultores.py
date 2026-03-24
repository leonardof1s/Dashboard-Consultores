import streamlit as st


def render(col_consultores):
    st.header("🧑‍💼 Cadastrar Consultor")

    if "usuario" not in st.session_state:
        st.warning("Faça login primeiro")
        st.stop()

    nome = st.text_input("Nome do consultor")

    if st.button("Cadastrar", type="primary"):
        nome = nome.strip()

        if nome and not col_consultores.find_one({"nome": nome}):
            col_consultores.insert_one({
                "nome": nome,
                "usuario_id": st.session_state["usuario"]["_id"]
            })

            st.success(f"Consultor {nome} cadastrado!")
            st.balloons()

        elif nome:
            st.warning("Já existe consultor com esse nome.")


def buscar(df_vendas):
    st.title("🔍 Buscar por Consultor")

    if df_vendas.empty:
        st.warning("Nenhuma venda encontrada.")
        return

    termo = st.text_input("Nome do consultor (ou parte)").strip()

    if termo:
        res = df_vendas[
            df_vendas["consultor"].str.contains(termo, case=False, na=False)
        ].copy()

        if res.empty:
            st.warning("Nenhum resultado.")
        else:
            st.dataframe(
                res[["data", "cliente", "valor", "total_comissao"]].style.format({
                    "data": "{:%d/%m/%Y}",
                    "valor": "R$ {:,.2f}",
                    "total_comissao": "R$ {:,.2f}"
                }),
                use_container_width=True,
                hide_index=True
            )