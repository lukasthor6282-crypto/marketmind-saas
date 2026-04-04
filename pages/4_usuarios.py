import streamlit as st
import pandas as pd

from services.usuarios_service import (
    listar_usuarios,
    criar_usuario,
)
from services.empresas_service import listar_empresas
from utils.ui import (
    aplicar_estilo_global,
    render_hero,
    render_section_title,
    render_sidebar_header,
)

st.set_page_config(
    page_title="Usuários",
    page_icon="👤",
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
    "👤 Usuários",
    "Gerencie os usuários do sistema"
)

try:
    empresas = listar_empresas()
except Exception as e:
    st.error(f"Erro ao carregar empresas: {e}")
    empresas = []

col_form, col_lista = st.columns([1, 1.2])

with col_form:
    st.markdown(
        """
        <div class="dm-card">
            <div style="font-size:22px; font-weight:800; color:#fff; margin-bottom:8px;">
                Cadastrar novo usuário
            </div>
            <div style="font-size:14px; color:#94a3b8; margin-bottom:18px;">
                Crie usuários e vincule cada um à empresa correta.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    if not empresas:
        st.warning("Cadastre uma empresa antes de criar usuários.")
    else:
        mapa_empresas = {empresa["nome"]: empresa["id"] for empresa in empresas}

        with st.form("form_usuario"):
            nome = st.text_input("Nome", placeholder="Ex.: Lukas Andrade")
            email = st.text_input("E-mail", placeholder="Ex.: lukas@email.com")
            senha = st.text_input("Senha", type="password", placeholder="Digite uma senha")
            perfil = st.selectbox("Perfil", ["admin", "cliente"])
            empresa_nome_selecionada = st.selectbox("Empresa", list(mapa_empresas.keys()))
            enviar = st.form_submit_button("Cadastrar usuário", use_container_width=True)

        if enviar:
            if not nome.strip() or not email.strip() or not senha.strip():
                st.warning("Preencha nome, e-mail e senha.")
            else:
                try:
                    empresa_id = mapa_empresas[empresa_nome_selecionada]
                    criar_usuario(
                        nome=nome.strip(),
                        email=email.strip().lower(),
                        senha=senha.strip(),
                        perfil=perfil,
                        empresa_id=empresa_id
                    )
                    st.success("Usuário cadastrado com sucesso.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao cadastrar usuário: {e}")

with col_lista:
    render_section_title("Usuários cadastrados")

    try:
        usuarios = listar_usuarios()
    except Exception as e:
        st.error(f"Erro ao carregar usuários: {e}")
        usuarios = []

    if usuarios:
        df = pd.DataFrame(usuarios)

        colunas_renomeadas = {}
        if "id" in df.columns:
            colunas_renomeadas["id"] = "ID"
        if "nome" in df.columns:
            colunas_renomeadas["nome"] = "Nome"
        if "email" in df.columns:
            colunas_renomeadas["email"] = "E-mail"
        if "perfil" in df.columns:
            colunas_renomeadas["perfil"] = "Perfil"
        if "empresa_id" in df.columns:
            colunas_renomeadas["empresa_id"] = "Empresa ID"
        if "criado_em" in df.columns:
            colunas_renomeadas["criado_em"] = "Criado em"

        if colunas_renomeadas:
            df = df.rename(columns=colunas_renomeadas)

        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("Nenhum usuário cadastrado ainda.") 