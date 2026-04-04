import streamlit as st
import pandas as pd
from services.analise_mercado_service import listar_analises_mercado

if "usuario" not in st.session_state:
    st.switch_page("pages/1_Login.py")

usuario = st.session_state.usuario
empresa_id = usuario["empresa_id"]

st.title("📚 Histórico de Análises")

dados = listar_analises_mercado(empresa_id)

if not dados:
    st.info("Nenhuma análise ainda")
else:
    df = pd.DataFrame(dados)
    st.dataframe(df, use_container_width=True)