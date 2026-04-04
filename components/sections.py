import streamlit as st

def page_header(titulo, subtitulo=""):
    st.markdown(f"""
        <div style="margin-bottom: 25px;">
            <h1 style="margin-bottom: 5px;">{titulo}</h1>
            <p style="color: gray;">{subtitulo}</p>
        </div>
    """, unsafe_allow_html=True)

def section(titulo, descricao=""):
    st.markdown(f"""
        <div style="margin-top: 30px; margin-bottom: 15px;">
            <h3 style="margin-bottom: 5px;">{titulo}</h3>
            <p style="color: gray; margin-top: 0;">{descricao}</p>
        </div>
    """, unsafe_allow_html=True)

def divider():
    st.markdown("<hr style='margin: 20px 0;'>", unsafe_allow_html=True)