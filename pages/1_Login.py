import streamlit as st
from core.auth import autenticar_usuario
from utils.ui import aplicar_estilo_global, render_hero

st.set_page_config(
    page_title="Login - MarketMind",
    page_icon="🔐",
    layout="wide"
)

aplicar_estilo_global()

if "usuario" not in st.session_state:
    st.session_state.usuario = None

col_esq, col_centro, col_dir = st.columns([1, 1.3, 1])

with col_centro:
    render_hero(
        "🔐 Entrar no MarketMind",
        "Plataforma de inteligência estratégica para análises de mercado"
    )

    st.markdown(
        """
        <div class="dm-card">
            <div style="font-size:22px; font-weight:800; color:#fff; margin-bottom:8px;">
                Acesse sua conta
            </div>
            <div style="font-size:14px; color:#94a3b8;">
                Entre para visualizar dashboards, análises e oportunidades.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    with st.form("form_login"):
        email = st.text_input("E-mail", placeholder="seuemail@empresa.com")
        senha = st.text_input("Senha", type="password", placeholder="Digite sua senha")
        entrar = st.form_submit_button("Entrar", use_container_width=True)

    if entrar:
        if not email.strip() or not senha.strip():
            st.warning("Preencha e-mail e senha.")
        else:
            usuario = autenticar_usuario(email.strip(), senha.strip())

            if usuario:
                st.session_state.usuario = usuario
                st.success("Login realizado com sucesso.")
                st.switch_page("pages/2_Dashboard.py")
            else:
                st.error("E-mail ou senha inválidos.")