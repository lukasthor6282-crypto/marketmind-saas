import streamlit as st
from services.coletas_service import listar_coletas_por_empresa
from utils.ui import (
    aplicar_estilo_global,
    render_hero,
    render_section_title,
    render_sidebar_header
)

st.set_page_config(
    page_title="Histórico - MarketMind",
    page_icon="📚",
    layout="wide"
)

aplicar_estilo_global()

if "usuario" not in st.session_state or st.session_state.usuario is None:
    st.switch_page("pages/1_Login.py")

usuario = st.session_state.usuario
empresa_id = usuario["empresa_id"]
empresa_nome = usuario.get("empresa_nome", f"Empresa {empresa_id}")

with st.sidebar:
    render_sidebar_header()

    st.divider()
    st.page_link("pages/2_Dashboard.py", label="📊 Dashboard")
    st.page_link("pages/10_Nova_Analise.py", label="🚀 Nova análise")
    st.page_link("pages/11_Historico.py", label="📚 Histórico")

    if usuario["perfil"] == "admin":
        st.divider()
        st.page_link("pages/3_Empresas.py", label="🏢 Empresas")
        st.page_link("pages/4_Usuarios.py", label="👤 Usuários")

    st.divider()
    st.write(f"**Usuário:** {usuario['nome']}")
    st.write(f"**Empresa:** {empresa_nome}")

    if st.button("🚪 Sair", use_container_width=True):
        st.session_state.usuario = None
        st.switch_page("pages/1_Login.py")

render_hero(
    "📚 Histórico de Análises",
    "Abra análises anteriores e continue acompanhando suas oportunidades"
)

coletas = listar_coletas_por_empresa(empresa_id)

if not coletas:
    st.info("Nenhuma análise encontrada.")
    st.stop()

render_section_title("Análises salvas")

for coleta in coletas:
    col1, col2, col3 = st.columns([2, 1.2, 1])

    with col1:
        st.markdown(
            f"""
            <div class="dm-card">
                <div style="font-size:20px; font-weight:800; color:#fff; margin-bottom:6px;">
                    🔎 {coleta['termo_busca']}
                </div>
                <div style="color:#94a3b8; font-size:13px;">
                    Coleta #{coleta['id']}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            f"""
            <div class="dm-card">
                <div style="font-size:14px; color:#94a3b8; margin-bottom:8px;">
                    Criado em
                </div>
                <div style="font-size:16px; font-weight:700; color:#fff;">
                    {coleta['criado_em']}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col3:
        st.markdown(
            """
            <div class="dm-card" style="padding:18px 18px 8px 18px;">
                <div style="font-size:14px; color:#94a3b8; margin-bottom:10px;">
                    Ação
                </div>
            """,
            unsafe_allow_html=True
        )

        if st.button(
            f"Abrir análise #{coleta['id']}",
            key=f"abrir_{coleta['id']}",
            use_container_width=True
        ):
            st.session_state["ultima_coleta_id"] = coleta["id"]
            st.session_state["ultimo_termo_busca"] = coleta["termo_busca"]
            st.switch_page("pages/12_Dashboard_Analise.py")

        st.markdown("</div>", unsafe_allow_html=True)