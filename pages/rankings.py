import streamlit as st


def render(df_vendas):
    st.title("🏆 Rankings e Relatórios")

    if df_vendas.empty:
        st.info("Nenhuma venda no período.")
    else:
        tab1, tab2, tab3 = st.tabs(["Total Acumulado", "Por Mês", "Por Semana"])
        medalhas = ["🥇", "🥈", "🥉"]

        # ---------------- TOTAL ACUMULADO ----------------
        with tab1:
            ranking = (
                df_vendas.groupby("consultor")["valor"]
                .sum()
                .reset_index(name="Total Vendas")
            )
            ranking = ranking.sort_values("Total Vendas", ascending=False)
            st.dataframe(
                ranking.style.format({"Total Vendas": "R$ {:,.2f}"}), hide_index=True
            )

            # Top 3 consultores
            top3 = ranking.head(3)
            cols = st.columns(len(top3))
            for i, row in enumerate(top3.itertuples()):
                cols[i].metric(f"{medalhas[i]} {row.consultor}", f"R$ {row._2:,.2f}")

            st.bar_chart(ranking.set_index("consultor")["Total Vendas"])

        # ---------------- POR MÊS ----------------
        with tab2:
            meses_disp = sorted(df_vendas["mes_ano"].unique())
            mes_sel = st.selectbox("Selecione o mês", meses_disp)
            mensal = (
                df_vendas[df_vendas["mes_ano"] == mes_sel]
                .groupby("consultor")["valor"]
                .sum()
                .reset_index(name="Total Vendas")
            )
            mensal = mensal.sort_values("Total Vendas", ascending=False)
            st.dataframe(
                mensal.style.format({"Total Vendas": "R$ {:,.2f}"}), hide_index=True
            )

            # Top 3 consultores do mês
            top3_mensal = mensal.head(3)
            cols_m = st.columns(len(top3_mensal))
            for i, row in enumerate(top3_mensal.itertuples()):
                cols_m[i].metric(f"{medalhas[i]} {row.consultor}", f"R$ {row._2:,.2f}")

            st.bar_chart(mensal.set_index("consultor")["Total Vendas"])

        # ---------------- POR SEMANA ----------------
        with tab3:
            semanas_disp = sorted(df_vendas["semana"].unique())
            semana_sel = st.selectbox("Selecione a semana", semanas_disp)
            semanal = (
                df_vendas[df_vendas["semana"] == semana_sel]
                .groupby("consultor")["valor"]
                .sum()
                .reset_index(name="Total Vendas")
            )
            semanal = semanal.sort_values("Total Vendas", ascending=False)
            st.dataframe(
                semanal.style.format({"Total Vendas": "R$ {:,.2f}"}), hide_index=True
            )

            # Top 3 consultores da semana
            top3_sem = semanal.head(3)
            cols_s = st.columns(len(top3_sem))
            for i, row in enumerate(top3_sem.itertuples()):
                cols_s[i].metric(f"{medalhas[i]} {row.consultor}", f"R$ {row._2:,.2f}")

            st.bar_chart(semanal.set_index("consultor")["Total Vendas"])
