import streamlit as st
import pandas as pd
import plotly.express as px
from services.analises_service import (
    listar_analises_por_empresa,
    criar_analise,
    top_analises_empresa
)

st.set_page_config(
    page_title="Análises - Marketplace SaaS",
    page_icon="🧠",
    layout="wide"
)

if "usuario" not in st.session_state or st.session_state.usuario is None:
    st.switch_page("pages/1_Login.py")

usuario = st.session_state.usuario
empresa_id = usuario["empresa_id"]
usuario_id = usuario["id"]

st.title("🧠 Análises")
st.write("Gerencie e acompanhe as análises da empresa logada.")

with st.sidebar:
    st.subheader("Sessão")
    st.write(f"**Usuário:** {usuario['nome']}")
    st.write(f"**Perfil:** {usuario['perfil']}")
    st.write(f"**Empresa ID:** {usuario['empresa_id']}")

    st.divider()
    st.page_link("pages/2_Dashboard.py", label="Dashboard", icon="📊")
    st.page_link("pages/5_Produtos.py", label="Produtos", icon="📦")
    st.page_link("pages/6_Analises.py", label="Análises", icon="🧠")

    if usuario["perfil"] == "admin":
        st.page_link("pages/3_Empresas.py", label="Empresas", icon="🏢")
        st.page_link("pages/4_Usuarios.py", label="Usuários", icon="👤")

    st.divider()

    if st.button("Sair"):
        st.session_state.usuario = None
        st.switch_page("pages/1_Login.py")

st.subheader("Nova análise")

with st.form("form_analise_nova"):
    titulo = st.text_input("Título")
    resumo = st.text_area("Resumo")
    score = st.number_input("Score", min_value=0.0, max_value=10.0, value=5.0, step=0.1)
    salvar = st.form_submit_button("Salvar análise")

if salvar:
    if not titulo.strip():
        st.warning("Digite um título.")
    else:
        try:
            criar_analise(
                empresa_id=empresa_id,
                usuario_id=usuario_id,
                titulo=titulo.strip(),
                resumo=resumo.strip(),
                score=float(score)
            )
            st.success("Análise salva com sucesso.")
            st.rerun()
        except Exception as e:
            st.error(f"Erro ao salvar análise: {e}")

st.divider()

st.subheader("Análises cadastradas")

analises = listar_analises_por_empresa(empresa_id)

if analises:
    df_analises = pd.DataFrame(analises)
    st.dataframe(df_analises, use_container_width=True)

    if "score" in df_analises.columns and not df_analises["score"].isna().all():
        fig_scores = px.histogram(
            df_analises,
            x="score",
            nbins=10,
            title="Distribuição dos scores"
        )
        st.plotly_chart(fig_scores, use_container_width=True)

    st.subheader("Top análises")

    top_analises = top_analises_empresa(empresa_id)

    if top_analises:
        df_top = pd.DataFrame(top_analises)
        st.dataframe(df_top, use_container_width=True)
else:
    st.info("Nenhuma análise cadastrada ainda.")