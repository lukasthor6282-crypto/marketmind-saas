import streamlit as st

def metric_card(titulo, valor, subtitulo="", icone="📊"):
    st.markdown(f"""
        <div style="
            background: linear-gradient(145deg, #1e1e2f, #2a2a40);
            padding: 20px;
            border-radius: 15px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.3);
            margin-bottom: 10px;
        ">
            <div style="font-size: 14px; color: #aaa;">{icone} {titulo}</div>
            <div style="font-size: 28px; font-weight: bold; color: #fff;">{valor}</div>
            <div style="font-size: 12px; color: #bbb;">{subtitulo}</div>
        </div>
    """, unsafe_allow_html=True)