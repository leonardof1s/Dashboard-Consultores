import streamlit as st


def login(col_usuarios):
    st.title("🔐 Acesso ao Sistema")

    tab1, tab2 = st.tabs(["🔑 Login", "📝 Cadastro"])

    # ================= LOGIN =================
    with tab1:
        email = st.text_input("Email")
        senha = st.text_input("Senha", type="password")

        if st.button("Entrar"):
            user = col_usuarios.find_one({
                "email": email,
                "senha": senha
            })

            if user:
                st.session_state["usuario"] = user
                st.success("Login realizado!")
                st.rerun()
            else:
                st.error("Email ou senha inválidos")

    # ================= CADASTRO =================
    with tab2:
        novo_email = st.text_input("Novo Email")
        nova_senha = st.text_input("Nova Senha", type="password")

        if st.button("Cadastrar"):
            if not novo_email or not nova_senha:
                st.warning("Preencha todos os campos")
                return

            existe = col_usuarios.find_one({"email": novo_email})

            if existe:
                st.warning("Usuário já existe")
                return

            col_usuarios.insert_one({
                "email": novo_email,
                "senha": nova_senha
            })

            st.success("Usuário criado com sucesso! Faça login.")