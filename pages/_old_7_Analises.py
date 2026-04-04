import streamlit as st
from services.coleta_service import coletar_e_salvar

st.set_page_config(page_title="Coleta", page_icon="🔍", layout="wide")

if "usuario" not in st.session_state or st.session_state.usuario is None:
    st.switch_page("pages/1_Login.py")

usuario = st.session_state.usuario
empresa_id = usuario["empresa_id"]
usuario_id = usuario["id"]

st.title("🔍 Coleta de Produtos")
st.write("Busque produtos diretamente do Mercado Livre.")

with st.form("form_coleta"):
    produto = st.text_input("Digite o produto para buscar")
    buscar = st.form_submit_button("Coletar")

if buscar:
    if not produto.strip():
        st.warning("Digite um produto.")
    else:
        with st.spinner("Coletando dados..."):
            try:
                resultado = coletar_e_salvar(produto, empresa_id, usuario_id)
                st.success(f"Coleta criada: #{resultado['coleta_id']} - {resultado['termo_busca']}")
                st.success(f"{resultado['total_encontrados']} encontrados")
                st.success(f"{resultado['novos_salvos']} novos produtos salvos")
            except Exception as e:
                st.error("Erro ao coletar ou salvar os dados.")
                st.code(str(e))