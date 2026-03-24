import streamlit as st
import pandas as pd
import altair as alt
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime, date


def render(df_vendas, col_consultores, col_vendas):
    st.header("📝 Gerenciar Vendas")
    tab1, tab2 = st.tabs(["➕ Nova Venda", "✏️ Editar / Excluir"])

    # ----------- NOVA VENDA -----------
    with tab1:
        consultores = [doc["nome"] for doc in col_consultores.find().sort("nome")]

        with st.form("nova_venda"):
            col_a, col_b = st.columns(2)

            consultor = col_a.selectbox("Consultor", consultores)
            cliente = col_a.text_input("Cliente")
            grupo = col_b.text_input("Grupo")
            cota = col_b.text_input("Cota")

            valor_str = col_a.text_input("Valor da Venda", "100000")
            valor_str = valor_str.replace(".", "").replace(",", ".")
            valor = Decimal(valor_str)

            # 🔥 NOVO: tipo de comissão
            tipo_comissao = col_a.selectbox(
                "Tipo de Comissão",
                ["Percentual", "Valor Fixo"]
            )

            if tipo_comissao == "Percentual":
                comissao_input = col_a.text_input("Comissão (%)", "1.5")
                percentual = Decimal(comissao_input.replace(",", ".")) / Decimal(100)
                comissao_total = (valor * percentual).quantize(
                    Decimal("0.01"), rounding=ROUND_HALF_UP
                )
            else:
                comissao_input = col_a.text_input("Comissão (R$)", "1500")
                comissao_total = Decimal(
                    comissao_input.replace(".", "").replace(",", ".")
                ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

            data_v = col_b.date_input("Data da Venda", value=date.today())

            if st.form_submit_button("Salvar Nova Venda", type="primary"):
                if cliente and valor > 0:

                    valor_parcela = (comissao_total / Decimal("13")).quantize(
                        Decimal("0.01"), rounding=ROUND_HALF_UP
                    )

                    meses = (
                        pd.date_range(
                            start=datetime.combine(data_v, datetime.min.time()).replace(day=1),
                            periods=13,
                            freq="MS",
                        )
                        .strftime("%Y-%m")
                        .tolist()
                    )

                    comissoes = []
                    for i, m in enumerate(meses):
                        comissoes.append(
                            {
                                "mes": m,
                                "valor_parcela": float(valor_parcela),
                                "cliente_pagou": True,
                                "consultor_recebe": True if i == 0 else False,
                            }
                        )

                    doc = {
                        "usuario_id": st.session_state["usuario"]["_id"],
                        "consultor": consultor,
                        "cliente": cliente.strip(),
                        "grupo": grupo.strip(),
                        "cota": cota.strip(),
                        "valor": float(valor),
                        "data": datetime.combine(data_v, datetime.min.time()),
                        "tipo_comissao": tipo_comissao,
                        "comissao_definida": float(comissao_total),
                        "comissoes": comissoes,
                    }

                    col_vendas.insert_one(doc)
                    st.success(
                        "Venda criada com 13 parcelas (apenas a primeira marcada)!"
                    )
                    st.rerun()

    # ----------- EDITAR / EXCLUIR -----------
    with tab2:
        if df_vendas.empty:
            st.info("Nenhuma venda no período.")
        else:
            consultores = sorted(df_vendas["consultor"].unique())
            consultor_sel = st.selectbox("Selecione o consultor", consultores)

            if consultor_sel:
                clientes = sorted(
                    df_vendas[df_vendas["consultor"] == consultor_sel]["cliente"].unique()
                )
                cliente_sel = st.selectbox("Selecione o cliente", clientes)

                if cliente_sel:
                    vendas_cliente = df_vendas[
                        (df_vendas["consultor"] == consultor_sel)
                        & (df_vendas["cliente"] == cliente_sel)
                    ]

                    venda_sel_str = st.selectbox(
                        "Selecione a venda",
                        options=vendas_cliente["_id"].astype(str).tolist(),
                        format_func=lambda x: (
                            f"Valor: R$ {vendas_cliente[vendas_cliente['_id'].astype(str) == x]['valor'].iloc[0]:,.2f}"
                        ),
                    )

                    if venda_sel_str:
                        venda = vendas_cliente[
                            vendas_cliente["_id"].astype(str) == venda_sel_str
                        ].iloc[0]

                        with st.form("editar_venda"):
                            cliente_e = st.text_input("Cliente", venda["cliente"])
                            grupo_e = st.text_input("Grupo", venda.get("grupo", ""))
                            cota_e = st.text_input("Cota", venda.get("cota", ""))

                            valor_str_e = st.text_input("Valor", str(venda["valor"]))
                            valor_str_e = valor_str_e.replace(".", "").replace(",", ".")
                            valor_e = Decimal(valor_str_e)

                            data_e = st.date_input("Data", venda["data"].date())

                            # 🔥 NOVO: tipo comissão edição
                            tipo_comissao_e = st.selectbox(
                                "Tipo de Comissão",
                                ["Percentual", "Valor Fixo"],
                                index=0 if venda.get("tipo_comissao") == "Percentual" else 1
                            )

                            if tipo_comissao_e == "Percentual":
                                comissao_input_e = st.text_input("Comissão (%)", "1.5")
                                percentual_e = Decimal(comissao_input_e.replace(",", ".")) / Decimal(100)
                                comissao_total = (valor_e * percentual_e).quantize(
                                    Decimal("0.01"), rounding=ROUND_HALF_UP
                                )
                            else:
                                comissao_input_e = st.text_input("Comissão (R$)", "1500")
                                comissao_total = Decimal(
                                    comissao_input_e.replace(".", "").replace(",", ".")
                                ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

                            valor_parcela = (comissao_total / Decimal(13)).quantize(
                                Decimal("0.01"), rounding=ROUND_HALF_UP
                            )

                            meses = (
                                pd.date_range(
                                    start=datetime.combine(data_e, datetime.min.time()).replace(day=1),
                                    periods=13,
                                    freq="MS",
                                )
                                .strftime("%Y-%m")
                                .tolist()
                            )

                            comissoes = []
                            for i, m in enumerate(meses):
                                comissoes.append(
                                    {
                                        "mes": m,
                                        "valor_parcela": float(valor_parcela),
                                        "cliente_pagou": True,
                                        "consultor_recebe": True if i == 0 else False,
                                    }
                                )

                            st.subheader("Parcelas de Comissão")
                            com_df = pd.DataFrame(comissoes)

                            com_edited = st.data_editor(
                                com_df,
                                column_config={
                                    "mes": st.column_config.TextColumn("Mês", disabled=True),
                                    "valor_parcela": st.column_config.NumberColumn(
                                        "Valor Parcela", disabled=True, format="R$ %.2f"
                                    ),
                                    "cliente_pagou": st.column_config.CheckboxColumn("Cliente Pagou"),
                                    "consultor_recebe": st.column_config.CheckboxColumn("Consultor Recebe"),
                                },
                                use_container_width=True,
                                hide_index=True,
                            )

                            col_btn1, col_btn2 = st.columns(2)

                            if col_btn1.form_submit_button("✅ Salvar Alterações", type="primary"):
                                col_vendas.update_one(
                                    {"_id": venda["_id"]},
                                    {
                                        "$set": {
                                            "cliente": cliente_e.strip(),
                                            "grupo": grupo_e.strip(),
                                            "cota": cota_e.strip(),
                                            "valor": float(valor_e),
                                            "data": datetime.combine(data_e, datetime.min.time()),
                                            "tipo_comissao": tipo_comissao_e,
                                            "comissao_definida": float(comissao_total),
                                            "comissoes": com_edited.to_dict("records"),
                                        }
                                    },
                                )
                                st.success("Alterações salvas!")
                                st.balloons()
                                st.rerun()

                            if col_btn2.form_submit_button("🗑️ Excluir Venda", type="primary"):
                                if st.session_state.get("confirma_excluir", False):
                                    col_vendas.delete_one({"_id": venda["_id"]})
                                    st.success("Venda excluída!")
                                    st.balloons()
                                    if "confirma_excluir" in st.session_state:
                                        del st.session_state["confirma_excluir"]
                                    st.rerun()
                                else:
                                    st.session_state["confirma_excluir"] = True
                                    st.warning(
                                        "Clique novamente para confirmar exclusão."
                                    )


def comissao_por_mes(col_consultores, col_vendas):
    import streamlit as st
    import pandas as pd
    from decimal import Decimal, ROUND_HALF_UP

    st.title("📅 Comissão por Mês")

    vendas = list(col_vendas.find())

    if not vendas:
        st.info("Nenhuma venda registrada.")
        return

    comissoes = []

    for venda in vendas:
        # 🔥 usa comissão já salva (novo padrão)
        if "comissoes" in venda and venda["comissoes"]:
            for parcela in venda["comissoes"]:
                comissoes.append({
                    "consultor": venda["consultor"],
                    "cliente": venda["cliente"],
                    "mes": parcela.get("mes"),
                    "valor_parcela": float(parcela.get("valor_parcela", 0)),
                    "consultor_recebe": parcela.get("consultor_recebe", False),
                })

        # 🔴 fallback (caso antigo)
        else:
            valor = Decimal(str(venda.get("valor", 0)))
            comissao_total = (valor * Decimal("0.015")).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
            valor_parcela = (comissao_total / Decimal("13")).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )

            for i in range(1, 14):
                comissoes.append({
                    "consultor": venda["consultor"],
                    "cliente": venda["cliente"],
                    "mes": f"Parcela {i}",
                    "valor_parcela": float(valor_parcela),
                    "consultor_recebe": True,
                })

    df = pd.DataFrame(comissoes)

    # 🔥 só parcelas que o consultor recebe
    df = df[df["consultor_recebe"] == True]

    if df.empty:
        st.warning("Nenhuma comissão encontrada.")
        return

    consultores = sorted(df["consultor"].unique())

    consultor_sel = st.selectbox(
        "Selecione o consultor", ["Todos"] + consultores
    )

    if consultor_sel != "Todos":
        df = df[df["consultor"] == consultor_sel]

    resumo = df.groupby("mes")["valor_parcela"].sum().reset_index()
    resumo = resumo.sort_values("mes")

    st.dataframe(
        resumo.style.format({"valor_parcela": "R$ {:,.2f}"}),
        hide_index=True
    )

    st.bar_chart(resumo.set_index("mes")["valor_parcela"])