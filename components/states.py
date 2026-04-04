import time
import streamlit as st


def loading(texto="Carregando..."):
    with st.spinner(texto):
        time.sleep(1)


def loading_card(
    titulo="Carregando dados",
    descricao="Estamos preparando as informações para você."
):
    st.markdown(
        f"""
        <div style="
            background: linear-gradient(135deg, rgba(15,23,42,0.88), rgba(8,12,24,0.98));
            border: 1px solid rgba(255,255,255,0.07);
            border-radius: 22px;
            padding: 22px;
            margin: 10px 0 18px 0;
            box-shadow: 0 10px 28px rgba(0,0,0,0.18);
            overflow: hidden;
            position: relative;
        ">
            <div style="
                position:absolute;
                top:0;
                left:-35%;
                width:35%;
                height:100%;
                background: linear-gradient(
                    90deg,
                    rgba(255,255,255,0.00),
                    rgba(255,255,255,0.08),
                    rgba(255,255,255,0.00)
                );
                animation: shimmer 1.8s infinite;
            "></div>

            <div style="font-size:18px; font-weight:800; color:#f8fafc; margin-bottom:8px;">
                ⏳ {titulo}
            </div>

            <div style="font-size:14px; color:#94a3b8; line-height:1.6; margin-bottom:16px;">
                {descricao}
            </div>

            <div style="
                width:100%;
                height:10px;
                background: rgba(255,255,255,0.06);
                border-radius:999px;
                overflow:hidden;
            ">
                <div style="
                    width:42%;
                    height:100%;
                    border-radius:999px;
                    background: linear-gradient(90deg, #22d3ee, #3b82f6, #8b5cf6);
                    animation: pulsebar 1.6s ease-in-out infinite;
                "></div>
            </div>
        </div>

        <style>
        @keyframes shimmer {{
            0% {{ left: -35%; }}
            100% {{ left: 120%; }}
        }}

        @keyframes pulsebar {{
            0% {{ width: 22%; opacity: 0.85; }}
            50% {{ width: 68%; opacity: 1; }}
            100% {{ width: 22%; opacity: 0.85; }}
        }}
        </style>
        """,
        unsafe_allow_html=True
    )


def progress_step(
    etapa_atual: int,
    total_etapas: int,
    titulo="Processando",
    descricao="Aguarde enquanto finalizamos esta etapa."
):
    percentual = 0
    if total_etapas > 0:
        percentual = int((etapa_atual / total_etapas) * 100)

    st.markdown(
        f"""
        <div style="
            background: linear-gradient(135deg, rgba(15,23,42,0.88), rgba(8,12,24,0.98));
            border: 1px solid rgba(255,255,255,0.07);
            border-radius: 22px;
            padding: 20px;
            margin: 10px 0 18px 0;
            box-shadow: 0 10px 28px rgba(0,0,0,0.18);
        ">
            <div style="
                display:flex;
                justify-content:space-between;
                align-items:center;
                gap:12px;
                margin-bottom:10px;
            ">
                <div style="font-size:18px; font-weight:800; color:#f8fafc;">
                    ⚙️ {titulo}
                </div>
                <div style="
                    font-size:13px;
                    font-weight:700;
                    color:#22d3ee;
                    background: rgba(34,211,238,0.10);
                    border: 1px solid rgba(34,211,238,0.20);
                    padding: 6px 10px;
                    border-radius: 999px;
                ">
                    {percentual}%
                </div>
            </div>

            <div style="
                font-size:14px;
                color:#94a3b8;
                line-height:1.6;
                margin-bottom:14px;
            ">
                {descricao}
            </div>

            <div style="
                width:100%;
                height:10px;
                background: rgba(255,255,255,0.06);
                border-radius:999px;
                overflow:hidden;
            ">
                <div style="
                    width:{percentual}%;
                    height:100%;
                    border-radius:999px;
                    background: linear-gradient(90deg, #22d3ee, #3b82f6, #8b5cf6);
                    transition: width 0.4s ease;
                "></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


def success(texto="Sucesso!"):
    st.markdown(
        f"""
        <div style="
            background: rgba(34,211,238,0.10);
            border: 1px solid rgba(34,211,238,0.22);
            color: #e6fffb;
            border-radius: 18px;
            padding: 14px 16px;
            margin: 10px 0 14px 0;
            font-weight: 600;
            line-height: 1.6;
        ">
            ✅ {texto}
        </div>
        """,
        unsafe_allow_html=True
    )


def error(texto="Erro ao processar"):
    st.markdown(
        f"""
        <div style="
            background: rgba(244,63,94,0.10);
            border: 1px solid rgba(244,63,94,0.22);
            color: #ffe4ea;
            border-radius: 18px;
            padding: 14px 16px;
            margin: 10px 0 14px 0;
            font-weight: 600;
            line-height: 1.6;
        ">
            ❌ {texto}
        </div>
        """,
        unsafe_allow_html=True
    )


def warning(texto="Atenção"):
    st.markdown(
        f"""
        <div style="
            background: rgba(245,158,11,0.10);
            border: 1px solid rgba(245,158,11,0.22);
            color: #fff5dd;
            border-radius: 18px;
            padding: 14px 16px;
            margin: 10px 0 14px 0;
            font-weight: 600;
            line-height: 1.6;
        ">
            ⚠️ {texto}
        </div>
        """,
        unsafe_allow_html=True
    )


def info_state(
    titulo="Informação",
    descricao="Aqui você encontra um aviso importante."
):
    st.markdown(
        f"""
        <div style="
            background: rgba(59,130,246,0.10);
            border: 1px solid rgba(59,130,246,0.22);
            border-radius: 20px;
            padding: 18px;
            margin: 10px 0 16px 0;
        ">
            <div style="font-size:18px; font-weight:800; color:#f8fafc; margin-bottom:8px;">
                ℹ️ {titulo}
            </div>
            <div style="font-size:14px; color:#dbe4f0; line-height:1.6;">
                {descricao}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


def empty_state(
    titulo="Nenhum dado encontrado",
    descricao="Ainda não há informações disponíveis para exibir nesta seção.",
    icone="📭"
):
    st.markdown(
        f"""
        <div style="
            background: linear-gradient(135deg, rgba(15,23,42,0.86), rgba(8,12,24,0.98));
            border: 1px dashed rgba(255,255,255,0.10);
            border-radius: 24px;
            padding: 34px 24px;
            text-align:center;
            margin: 12px 0 18px 0;
        ">
            <div style="font-size:40px; margin-bottom:12px;">
                {icone}
            </div>
            <div style="font-size:22px; font-weight:800; color:#f8fafc; margin-bottom:8px;">
                {titulo}
            </div>
            <div style="
                font-size:14px;
                color:#94a3b8;
                max-width:620px;
                margin:0 auto;
                line-height:1.7;
            ">
                {descricao}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )