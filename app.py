import streamlit as st

st.set_page_config(
    page_title="MarketMind",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
        padding-left: 2rem;
        padding-right: 2rem;
        max-width: 100%;
    }

    .stApp {
        background: linear-gradient(180deg, #0f1117 0%, #151924 100%);
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #111827 0%, #0f172a 100%);
        border-right: 1px solid rgba(255,255,255,0.06);
    }

    div[data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255,255,255,0.06);
        padding: 12px;
        border-radius: 16px;
    }
    </style>
""", unsafe_allow_html=True)

if "usuario" not in st.session_state:
    st.session_state.usuario = None

if st.session_state.usuario is None:
    st.switch_page("pages/1_Login.py")
else:
    st.switch_page("pages/2_Dashboard.py")