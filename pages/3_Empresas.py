import streamlit as st
import pandas as pd

from services.empresas_service import (
    listar_empresas,
    criar_empresa,
)
from utils.ui import (
    aplicar_estilo_global,
    render_hero,
    render_section_title,
    render_sidebar_header,
)

st.set_page_config(
    page_title="Empresas",
    page_icon="🏢",
    layout="wide"
)

aplicar_estilo_global()

if "usuario" not in st.session_state or st.session_state.usuario is None:
    st.switch_page("pages/1_Login.py")

usuario = st.session_state.usuario

if usuario.get("perfil") != "admin":
    st.error("Acesso restrito ao administrador.")
    st.stop()

empresa_nome = usuario.get("empresa_nome", f"Empresa {usuario['empresa_id']}")

with st.sidebar:
    render_sidebar_header()

    st.divider()
    st.page_link("pages/2_Dashboard.py", label="📊 Dashboard")
    st.page_link("pages/10_Nova_Analise.py", label="🚀 Nova análise")
    st.page_link("pages/11_Historico.py", label="📚 Histórico")
    st.page_link("pages/3_Empresas.py", label="🏢 Empresas")
    st.page_link("pages/4_Usuarios.py", label="👤 Usuários")

    st.divider()
    st.write(f"**Usuário:** {usuario['nome']}")
    st.write(f"**Perfil:** {usuario['perfil']}")
    st.write(f"**Empresa:** {empresa_nome}")

    if st.button("🚪 Sair", use_container_width=True):
        st.session_state.usuario = None
        st.switch_page("pages/1_Login.py")

render_hero(
    "🏢 Empresas",
    "Gerencie as empresas cadastradas no sistema"
)

col_form, col_lista = st.columns([1, 1.2])

with col_form:
    st.markdown(
        """
        <div class="dm-card">
            <div style="font-size:22px; font-weight:800; color:#fff; margin-bottom:8px;">
                Cadastrar nova empresa
            </div>
            <div style="font-size:14px; color:#94a3b8; margin-bottom:18px;">
                Crie uma nova empresa para usar a plataforma com dados isolados.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    with st.form("form_empresa"):
        nome = st.text_input("Nome da empresa", placeholder="Ex.: DataMind")
        slug = st.text_input("Slug da empresa", placeholder="Ex.: datamind")
        enviar = st.form_submit_button("Cadastrar empresa", use_container_width=True)

    if enviar:
        if not nome.strip() or not slug.strip():
            st.warning("Preencha nome e slug.")
        else:
            try:
                criar_empresa(nome.strip(), slug.strip().lower())
                st.success("Empresa cadastrada com sucesso.")
                st.rerun()
            except Exception as e:
                st.error(f"Erro ao cadastrar empresa: {e}")

with col_lista:
    render_section_title("Empresas cadastradas")

    try:
        empresas = listar_empresas()
    except Exception as e:
        st.error(f"Erro ao carregar empresas: {e}")
        empresas = []

    if empresas:
        df = pd.DataFrame(empresas)

        colunas_renomeadas = {}
        if "id" in df.columns:
            colunas_renomeadas["id"] = "ID"
        if "nome" in df.columns:
            colunas_renomeadas["nome"] = "Nome"
        if "slug" in df.columns:
            colunas_renomeadas["slug"] = "Slug"
        if "criado_em" in df.columns:
            colunas_renomeadas["criado_em"] = "Criado em"

        if colunas_renomeadas:
            df = df.rename(columns=colunas_renomeadas)

        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("Nenhuma empresa cadastrada ainda.")