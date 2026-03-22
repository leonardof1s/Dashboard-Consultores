import streamlit as st
from datetime import date
from db import col_consultores, col_vendas
from utils import carregar_vendas

st.set_page_config(page_title="Dashboard Consultores", layout="wide", page_icon="📊")

# ====================== SIDEBAR – FILTROS GLOBAIS ======================
st.sidebar.header("Filtros Globais")
data_inicio = st.sidebar.date_input("Data inicial", value=date(2024, 1, 1))
data_fim = st.sidebar.date_input("Data final", value=date.today())
filtro_ativa = st.sidebar.checkbox("Aplicar filtro de período", value=True)

if not filtro_ativa:
    data_inicio = data_fim = None

df_vendas = carregar_vendas(col_vendas, data_inicio, data_fim)

# ====================== MENU PRINCIPAL ======================
pagina = st.sidebar.selectbox(
    "Página",
    [
        "Dashboard Inicial",
        "Cadastrar Consultor",
        "Gerenciar Vendas",
        "Buscar Cliente",
        "Buscar Consultor",
        "Comissão por Mês",
        "Rankings e Relatórios"
    ]
)

# Importa páginas
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

st.sidebar.caption("v4.0 – Estrutura modular e segura")
