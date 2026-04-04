import streamlit as st
import pandas as pd
from services.coleta_service import coletar_e_salvar
from services.coletas_service import listar_coletas_por_empresa
from utils.ui import (
    aplicar_estilo_global,
    render_hero,
    render_section_title,
    render_sidebar_header
)

st.set_page_config(
    page_title="Nova Análise - MarketMind",
    page_icon="🚀",
    layout="wide"
)

aplicar_estilo_global()

# 🔐 Proteção de login
if "usuario" not in st.session_state or st.session_state.usuario is None:
    st.switch_page("pages/1_login.py")  # corrigido

usuario = st.session_state.usuario
empresa_id = usuario["empresa_id"]
usuario_id = usuario["id"]
empresa_nome = usuario.get("empresa_nome", f"Empresa {empresa_id}")

# 🔥 Sidebar
with st.sidebar:
    render_sidebar_header()

    st.divider()
    st.page_link("pages/2_dashboard.py", label="📊 Dashboard")
    st.page_link("pages/10_nova_analise.py", label="🚀 Nova análise")
    st.page_link("pages/11_historico.py", label="📚 Histórico")

    if usuario["perfil"] == "admin":
        st.divider()
        st.page_link("pages/3_empresas.py", label="🏢 Empresas")
        st.page_link("pages/4_usuarios.py", label="👤 Usuários")  # corrigido

    st.divider()
    st.write(f"**Usuário:** {usuario['nome']}")
    st.write(f"**Empresa:** {empresa_nome}")

    if st.button("🚪 Sair", use_container_width=True):
        st.session_state.usuario = None
        st.switch_page("pages/1_login.py")  # corrigido

# 🚀 Hero
render_hero(
    "🚀 Nova Análise",
    "Digite um produto e deixe o MarketMind coletar e preparar um dashboard exclusivo"
)

col_a, col_b = st.columns([1.5, 1])

# 📊 Área principal
with col_a:
    st.markdown(
        """
        <div class="dm-card">
            <div style="font-size:22px; font-weight:800; color:#fff; margin-bottom:8px;">
                Criar nova análise
            </div>
            <div style="font-size:14px; color:#94a3b8; margin-bottom:18px;">
                Fluxo simples: buscar produto → coletar anúncios → abrir dashboard da análise
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    with st.form("form_nova_analise"):
        produto = st.text_input(
            "Produto para analisar",
            placeholder="Ex.: iphone 11, notebook gamer, mouse sem fio"
        )
        analisar = st.form_submit_button("Analisar produto", use_container_width=True)

    if analisar:
        if not produto.strip():
            st.warning("Digite um produto.")
        else:
            with st.spinner("Coletando dados do mercado..."):
                try:
                    resultado = coletar_e_salvar(produto.strip(), empresa_id, usuario_id)

                    st.session_state["ultima_coleta_id"] = resultado["coleta_id"]
                    st.session_state["ultimo_termo_busca"] = resultado["termo_busca"]

                    st.success(f"Coleta criada: #{resultado['coleta_id']}")
                    st.success(f"Busca: {resultado['termo_busca']}")
                    st.success(f"Produtos novos salvos: {resultado['novos_salvos']}")

                    # 🔥 corrigido
                    st.switch_page("pages/12_dashboard_analise.py")

                except Exception as e:
                    st.error("Erro ao criar análise.")
                    st.code(str(e))

# 📘 Como funciona
with col_b:
    st.markdown(
        """
        <div class="dm-card">
            <div style="font-size:22px; font-weight:800; color:#fff; margin-bottom:12px;">
                Como funciona
            </div>
            <div style="display:flex; flex-direction:column; gap:12px; color:#cbd5e1; line-height:1.6;">
                <div>1. Você digita um produto</div>
                <div>2. O sistema faz a coleta</div>
                <div>3. A análise fica separada por busca</div>
                <div>4. Um dashboard exclusivo é criado</div>
                <div>5. O resultado fica salvo no histórico</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

# 📜 Histórico rápido
render_section_title("Últimas análises criadas")

coletas = listar_coletas_por_empresa(empresa_id)

if coletas:
    df = pd.DataFrame(coletas[:8])
    df_exibicao = df.rename(columns={
        "id": "ID",
        "termo_busca": "Busca",
        "criado_em": "Criado em"
    })
    st.dataframe(df_exibicao, use_container_width=True, hide_index=True)
else:
    st.info("Nenhuma análise criada ainda.")