import streamlit as st
from services.auth_service import autenticar_usuario

st.set_page_config(
    page_title="Login - MarketMind",
    page_icon="🔐",
    layout="centered"
)

if "usuario" in st.session_state and st.session_state.usuario:
    st.switch_page("pages/2_Dashboard.py")

st.markdown(
    """
    <div style="
        background: linear-gradient(135deg, rgba(15,23,42,0.92), rgba(8,12,24,0.98));
        border: 1px solid rgba(255,255,255,0.07);
        border-radius: 24px;
        padding: 28px;
        margin-top: 40px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.18);
    ">
        <div style="font-size:32px; font-weight:900; color:#f8fafc; margin-bottom:8px;">
            🔐 MarketMind
        </div>
        <div style="font-size:15px; color:#94a3b8; line-height:1.6;">
            Faça login para acessar sua inteligência de mercado.
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown("### Entrar")

email = st.text_input("Email", placeholder="seuemail@empresa.com")
senha = st.text_input("Senha", type="password", placeholder="Digite sua senha")

if st.button("Entrar", use_container_width=True):
    if not email or not senha:
        st.warning("Preencha email e senha.")
    else:
        usuario = autenticar_usuario(email, senha)

        if usuario:
            st.session_state.usuario = usuario
            st.success("Login realizado com sucesso.")
            st.switch_page("pages/2_Dashboard.py")
        else:
            st.error("Email ou senha inválidos.")