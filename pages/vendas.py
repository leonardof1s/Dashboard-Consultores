import streamlit as st
import pandas as pd
from datetime import datetime, date
from utils import calcular_comissao


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
            valor = col_a.number_input("Valor da Venda", min_value=0.0, step=1000.0)
            data_v = col_b.date_input("Data da Venda", value=date.today())

            if st.form_submit_button("Salvar Nova Venda", type="primary"):
                if cliente and valor > 0:
                    valor_parcela = calcular_comissao(valor)
                    meses = (
                        pd.date_range(
                            start=datetime.combine(data_v, datetime.min.time()).replace(
                                day=1
                            ),
                            periods=13,
                            freq="MS",
                        )
                        .strftime("%Y-%m")
                        .tolist()
                    )

                    # Apenas a primeira comissão marcada
                    comissoes = []
                    for i, m in enumerate(meses):
                        comissoes.append(
                            {
                                "mes": m,
                                "valor_parcela": valor_parcela,
                                "cliente_pagou": True,
                                "consultor_recebe": True if i == 0 else False,
                            }
                        )

                    doc = {
                        "consultor": consultor,
                        "cliente": cliente.strip(),
                        "grupo": grupo.strip(),
                        "cota": cota.strip(),
                        "valor": float(valor),
                        "data": datetime.combine(data_v, datetime.min.time()),
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
                    df_vendas[df_vendas["consultor"] == consultor_sel][
                        "cliente"
                    ].unique()
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
                            valor_e = st.number_input(
                                "Valor", value=float(venda["valor"])
                            )
                            data_e = st.date_input("Data", venda["data"].date())

                            st.subheader("Parcelas de Comissão")
                            com_df = pd.DataFrame(venda.get("comissoes", []))

                            com_edited = st.data_editor(
                                com_df,
                                column_config={
                                    "mes": st.column_config.TextColumn(
                                        "Mês", disabled=True
                                    ),
                                    "valor_parcela": st.column_config.NumberColumn(
                                        "Valor Parcela", disabled=True, format="R$ %.2f"
                                    ),
                                    "cliente_pagou": st.column_config.CheckboxColumn(
                                        "Cliente Pagou"
                                    ),
                                    "consultor_recebe": st.column_config.CheckboxColumn(
                                        "Consultor Recebe"
                                    ),
                                },
                                use_container_width=True,
                                hide_index=True,
                            )

                            col_btn1, col_btn2 = st.columns(2)
                            if col_btn1.form_submit_button(
                                "✅ Salvar Alterações", type="primary"
                            ):
                                col_vendas.update_one(
                                    {"_id": venda["_id"]},
                                    {
                                        "$set": {
                                            "cliente": cliente_e.strip(),
                                            "grupo": grupo_e.strip(),
                                            "cota": cota_e.strip(),
                                            "valor": float(valor_e),
                                            "data": datetime.combine(
                                                data_e, datetime.min.time()
                                            ),
                                            "comissoes": com_edited.to_dict("records"),
                                        }
                                    },
                                )
                                st.success("Alterações salvas!")
                                st.rerun()

                            if col_btn2.form_submit_button(
                                "🗑️ Excluir Venda", type="primary"
                            ):
                                if st.session_state.get("confirma_excluir", False):
                                    col_vendas.delete_one({"_id": venda["_id"]})
                                    st.success("Venda excluída!")
                                    if "confirma_excluir" in st.session_state:
                                        del st.session_state["confirma_excluir"]
                                    st.rerun()
                                else:
                                    st.session_state["confirma_excluir"] = True
                                    st.warning(
                                        "Clique novamente para confirmar exclusão."
                                    )
