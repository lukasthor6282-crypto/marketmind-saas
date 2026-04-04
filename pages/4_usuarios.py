import streamlit as st
from utils.ui import (
    aplicar_estilo_global,
    render_hero,
    render_section_title,
    render_sidebar_header,
)

st.set_page_config(
    page_title="Usuários - MarketMind",
    page_icon="👤",
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
    st.page_link("pages/13_Dashboard_Produto.py", label="🧩 Dashboard por produto")

    if usuario["perfil"] == "admin":
        st.divider()
        st.page_link("pages/3_Empresas.py", label="🏢 Empresas")
        st.page_link("pages/4_usuarios.py", label="👤 Usuários")

    st.divider()
    st.write(f"**Usuário:** {usuario['nome']}")
    st.write(f"**Empresa:** {empresa_nome}")

    if st.button("🚪 Sair", use_container_width=True):
        st.session_state.usuario = None
        st.switch_page("pages/1_Login.py")

render_hero(
    "👤 Usuários",
    "Gerencie acesso e visualize os dados do usuário logado"
)

render_section_title("Usuário atual")

col1, col2 = st.columns(2)

with col1:
    st.markdown(
        f"""
        <div class="dm-card">
            <div style="font-size:14px; color:#94a3b8; margin-bottom:8px;">
                Nome
            </div>
            <div style="font-size:24px; font-weight:800; color:#fff; margin-bottom:8px;">
                {usuario.get("nome", "Sem nome")}
            </div>
            <div style="font-size:14px; color:#cbd5e1; line-height:1.6;">
                Usuário autenticado na plataforma.
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
                Perfil
            </div>
            <div style="font-size:24px; font-weight:800; color:#fff; margin-bottom:8px;">
                {usuario.get("perfil", "Não definido")}
            </div>
            <div style="font-size:14px; color:#cbd5e1; line-height:1.6;">
                Nível de acesso do usuário atual dentro do sistema.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

render_section_title("Dados de acesso")

col3, col4 = st.columns(2)

with col3:
    st.markdown(
        f"""
        <div class="dm-card">
            <div style="font-size:14px; color:#94a3b8; margin-bottom:8px;">
                E-mail
            </div>
            <div style="font-size:22px; font-weight:800; color:#fff; margin-bottom:8px; word-break:break-word;">
                {usuario.get("email", "Não informado")}
            </div>
            <div style="font-size:14px; color:#cbd5e1; line-height:1.6;">
                Endereço usado para login.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col4:
    st.markdown(
        f"""
        <div class="dm-card">
            <div style="font-size:14px; color:#94a3b8; margin-bottom:8px;">
                Empresa vinculada
            </div>
            <div style="font-size:22px; font-weight:800; color:#fff; margin-bottom:8px;">
                {empresa_nome}
            </div>
            <div style="font-size:14px; color:#cbd5e1; line-height:1.6;">
                ID interno da empresa: <strong>#{empresa_id}</strong>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

render_section_title("Status da página")

st.markdown(
    """
    <div class="dm-card">
        <div style="font-size:18px; font-weight:800; color:#fff; margin-bottom:12px;">
            Painel de usuários
        </div>
        <div style="font-size:14px; color:#cbd5e1; line-height:1.8;">
            Esta página já está estável no deploy e não vai mais quebrar a navegação.<br><br>
            No próximo passo, ela pode evoluir para:
            <br>• listar todos os usuários da empresa
            <br>• criar usuário novo
            <br>• editar perfil
            <br>• ativar/desativar acesso
        </div>
    </div>
    """,
    unsafe_allow_html=True
)