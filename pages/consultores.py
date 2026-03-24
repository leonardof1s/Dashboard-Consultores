import streamlit as st


def render(col_consultores):
    st.header("🧑‍💼 Cadastrar Consultor")

    nome = st.text_input("Nome do consultor")

    if st.button("Cadastrar", type="primary"):
        nome = nome.strip()

        if not nome:
            st.warning("Digite um nome válido.")
            return

        usuario_id = st.session_state["usuario"]["_id"]

        # 🔥 verifica duplicado SOMENTE do usuário logado
        existe = col_consultores.find_one({
            "nome": nome,
            "usuario_id": usuario_id
        })

        if existe:
            st.warning("Já existe consultor com esse nome.")
            return

        # ✅ insert correto
        col_consultores.insert_one({
            "nome": nome,
            "usuario_id": usuario_id
        })

        st.success(f"Consultor {nome} cadastrado!")
        st.balloons()