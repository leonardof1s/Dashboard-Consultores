import streamlit as st
from datetime import date

from db import col_usuarios, col_consultores, col_vendas
from auth import login
from utils import carregar_vendas

st.set_page_config(
    page_title="Dashboard Consultores",
    layout="wide",
    page_icon="📊"
)

# ================= 🔐 LOGIN PRIMEIRO =================
if "usuario" not in st.session_state:
    login(col_usuarios)
    st.stop()

# ================= 👤 USUÁRIO LOGADO =================
usuario = st.session_state["usuario"]
usuario_id = usuario["_id"]

# ====================== SIDEBAR – FILTROS ======================
st.sidebar.header(f"👤 {usuario.get('email', 'Usuário')}")

data_inicio = st.sidebar.date_input("Data inicial", value=date(2024, 1, 1))
data_fim = st.sidebar.date_input("Data final", value=date.today())

filtro_ativa = st.sidebar.checkbox("Aplicar filtro de período", value=True)

if not filtro_ativa:
    data_inicio = None
    data_fim = None

# ================= 📊 CARREGAR DADOS =================
df_vendas = carregar_vendas(
    col_vendas,
    data_inicio,
    data_fim,
    usuario_id
)

# ====================== MENU ======================
pagina = st.sidebar.selectbox(
    "Página",
    [
        "Dashboard Inicial",
        "Cadastrar Consultor",
        "Gerenciar Vendas",
        "Buscar Cliente",
        "Buscar Consultor",
        "Comissão por Mês",
        "Rankings e Relatórios",
        "Histórico de Pagamentos",
    ]
)

# ====================== ROTAS ======================
if pagina == "Dashboard Inicial":
    from pages import dashboard
    dashboard.render(df_vendas)

elif pagina == "Cadastrar Consultor":
    from pages import consultores
    consultores.render(col_consultores)

elif pagina == "Gerenciar Vendas":
    from pages import vendas
    vendas.render(df_vendas, col_consultores, col_vendas)

elif pagina == "Buscar Cliente":
    from pages import clientes
    clientes.render(df_vendas)

elif pagina == "Buscar Consultor":
    from pages import consultores
    consultores.buscar(df_vendas)

elif pagina == "Comissão por Mês":
    from pages import vendas
    vendas.comissao_por_mes(col_consultores, col_vendas)

elif pagina == "Rankings e Relatórios":
    from pages import rankings
    rankings.render(df_vendas)

elif pagina == "Histórico de Pagamentos":
    from pages import historico
    historico.render(col_vendas)

st.sidebar.caption("v4.0 – Estrutura modular e segura")