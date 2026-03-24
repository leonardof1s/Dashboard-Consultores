import streamlit as st
import pandas as pd
import altair as alt


def render(df_vendas):
    st.title("🏆 Performance de Consultores")

    if df_vendas.empty:
        st.info("Nenhuma venda no período.")
        return

    tab1, tab2, tab3 = st.tabs(
        ["💰 Comissão Total", "📅 Comissão por Mês", "📊 Performance Geral"]
    )

    medalhas = ["🥇", "🥈", "🥉"]

    # ===================== 💰 TOTAL COMISSÃO =====================
    with tab1:
        ranking = (
            df_vendas.groupby("consultor")["total_comissao"]
            .sum()
            .reset_index(name="Total Comissão")
            .sort_values("Total Comissão", ascending=False)
        )

        st.subheader("💰 Ranking por Comissão")

        st.dataframe(
            ranking.style.format({"Total Comissão": "R$ {:,.2f}"}),
            hide_index=True
        )

        # TOP 3
        top3 = ranking.head(3)
        cols = st.columns(len(top3))

        for i, row in enumerate(top3.itertuples()):
            cols[i].metric(
                f"{medalhas[i]} {row.consultor}",
                f"R$ {row._2:,.2f}"
            )

        # Gráfico
        chart = (
            alt.Chart(ranking)
            .mark_bar()
            .encode(
                x=alt.X("consultor:N", title="Consultor", sort="-y"),
                y=alt.Y("Total Comissão:Q", title="Comissão (R$)"),
                tooltip=["consultor", "Total Comissão"]
            )
        )

        st.altair_chart(chart, use_container_width=True)

    # ===================== 📅 POR MÊS =====================
    with tab2:
        meses_disp = sorted(df_vendas["mes_ano"].unique())
        mes_sel = st.selectbox("Selecione o mês", meses_disp)

        mensal = (
            df_vendas[df_vendas["mes_ano"] == mes_sel]
            .groupby("consultor")["total_comissao"]
            .sum()
            .reset_index(name="Comissão Mensal")
            .sort_values("Comissão Mensal", ascending=False)
        )

        st.dataframe(
            mensal.style.format({"Comissão Mensal": "R$ {:,.2f}"}),
            hide_index=True
        )

        # TOP 3
        top3_m = mensal.head(3)
        cols_m = st.columns(len(top3_m))

        for i, row in enumerate(top3_m.itertuples()):
            cols_m[i].metric(
                f"{medalhas[i]} {row.consultor}",
                f"R$ {row._2:,.2f}"
            )

        chart_m = (
            alt.Chart(mensal)
            .mark_bar()
            .encode(
                x=alt.X("consultor:N", sort="-y"),
                y="Comissão Mensal:Q",
                tooltip=["consultor", "Comissão Mensal"]
            )
        )

        st.altair_chart(chart_m, use_container_width=True)

    # ===================== 📊 PERFORMANCE GERAL =====================
    with tab3:
        st.subheader("📊 Indicadores de Performance")

        resumo = (
            df_vendas.groupby("consultor")
            .agg(
                total_vendas=("valor", "sum"),
                total_comissao=("total_comissao", "sum"),
                qtd_vendas=("valor", "count"),
            )
            .reset_index()
        )

        resumo["ticket_medio"] = resumo["total_vendas"] / resumo["qtd_vendas"]

        st.dataframe(
            resumo.style.format({
                "total_vendas": "R$ {:,.2f}",
                "total_comissao": "R$ {:,.2f}",
                "ticket_medio": "R$ {:,.2f}",
            }),
            hide_index=True
        )

        # gráfico combinado (comissão)
        chart_perf = (
            alt.Chart(resumo)
            .mark_bar()
            .encode(
                x=alt.X("consultor:N", sort="-y"),
                y="total_comissao:Q",
                tooltip=["consultor", "total_comissao", "qtd_vendas"]
            )
            .properties(title="Performance por Comissão")
        )

        st.altair_chart(chart_perf, use_container_width=True)