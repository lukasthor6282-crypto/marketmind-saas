import streamlit as st
import pandas as pd
from services.mercadolivre_service import buscar_itens_por_vendedor
from services.produtos_service import (
    listar_produtos_por_empresa,
    salvar_produto,
    produto_existe
)

st.set_page_config(
    page_title="Produtos - Marketplace SaaS",
    page_icon="📦",
    layout="wide"
)

if "usuario" not in st.session_state or st.session_state.usuario is None:
    st.switch_page("pages/1_Login.py")

usuario = st.session_state.usuario
empresa_id = usuario["empresa_id"]

st.title("📦 Produtos")
st.write("Busque produtos do Mercado Livre e salve no sistema.")

with st.sidebar:
    st.subheader("Sessão")
    st.write(f"**Usuário:** {usuario['nome']}")
    st.write(f"**Perfil:** {usuario['perfil']}")
    st.write(f"**Empresa ID:** {usuario['empresa_id']}")

    st.divider()
    st.page_link("pages/2_Dashboard.py", label="Dashboard", icon="📊")
    st.page_link("pages/5_Produtos.py", label="Produtos", icon="📦")

    if usuario["perfil"] == "admin":
        st.page_link("pages/3_Empresas.py", label="Empresas", icon="🏢")
        st.page_link("pages/4_Usuarios.py", label="Usuários", icon="👤")

    st.divider()

    if st.button("Sair"):
        st.session_state.usuario = None
        st.switch_page("pages/1_Login.py")

st.subheader("Buscar produtos no Mercado Livre")

with st.form("form_busca_ml"):
    access_token = st.text_input("Access Token do Mercado Livre", type="password")
    seller_id = st.text_input("Seller ID")
    buscar = st.form_submit_button("Buscar produtos")

resultados_formatados = []

if buscar:
    if not access_token.strip() or not seller_id.strip():
        st.warning("Preencha o access token e o seller ID.")
    else:
        try:
            dados = buscar_itens_por_vendedor(access_token.strip(), seller_id.strip())
            resultados = dados.get("results", [])

            for item in resultados:
                resultados_formatados.append({
                    "item_id": item.get("id"),
                    "titulo": item.get("title"),
                    "preco": item.get("price"),
                    "status": item.get("status"),
                    "permalink": item.get("permalink"),
                })

            st.session_state["resultados_ml"] = resultados_formatados

            if resultados_formatados:
                st.success(f"{len(resultados_formatados)} produtos encontrados.")
            else:
                st.info("Nenhum produto encontrado.")
        except Exception as e:
            st.error(f"Erro ao buscar produtos: {e}")

if "resultados_ml" in st.session_state and st.session_state["resultados_ml"]:
    st.subheader("Resultados da busca")

    df_resultados = pd.DataFrame(st.session_state["resultados_ml"])
    st.dataframe(df_resultados, use_container_width=True)

    if st.button("Salvar produtos encontrados no banco"):
        salvos = 0

        for item in st.session_state["resultados_ml"]:
            if not produto_existe(empresa_id, item["item_id"]):
                salvar_produto(
                    empresa_id=empresa_id,
                    marketplace="Mercado Livre",
                    item_id=item["item_id"],
                    titulo=item["titulo"],
                    preco=float(item["preco"]) if item["preco"] is not None else 0.0,
                    status=item["status"],
                    permalink=item["permalink"]
                )
                salvos += 1

        st.success(f"{salvos} produtos salvos com sucesso.")
        st.rerun()

st.divider()

st.subheader("Produtos já salvos")

try:
    produtos = listar_produtos_por_empresa(empresa_id)

    if produtos:
        df_produtos = pd.DataFrame(produtos)
        st.dataframe(df_produtos, use_container_width=True)
    else:
        st.info("Nenhum produto salvo ainda.")
except Exception as e:
    st.error(f"Erro ao listar produtos: {e}")