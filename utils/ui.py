import streamlit as st


def aplicar_estilo_global():
    st.markdown("""
    <style>
    .stApp {
        background:
            radial-gradient(circle at 15% 20%, rgba(168,85,247,0.16), transparent 28%),
            radial-gradient(circle at 85% 75%, rgba(34,211,238,0.14), transparent 26%),
            linear-gradient(135deg, #070b17 0%, #0b1020 45%, #0f172a 100%);
        color: #f8fafc;
    }

    section[data-testid="stSidebar"] {
        background:
            linear-gradient(180deg, rgba(15,23,42,0.98) 0%, rgba(10,15,30,0.98) 100%);
        border-right: 1px solid rgba(255,255,255,0.06);
    }

    .block-container {
        padding-top: 1.6rem;
        padding-bottom: 2rem;
        max-width: 1450px;
    }

    header[data-testid="stHeader"] {
        background: rgba(10, 15, 30, 0.20) !important;
        backdrop-filter: blur(10px);
        border-bottom: 1px solid rgba(255,255,255,0.04);
    }

    button[title="Deploy"] {
        display: none !important;
    }

    div[data-testid="stMetric"] {
        background:
            linear-gradient(180deg, rgba(17,24,39,0.95) 0%, rgba(11,16,32,0.95) 100%);
        border: 1px solid rgba(255,255,255,0.07);
        padding: 16px;
        border-radius: 20px;
        box-shadow:
            0 0 0 1px rgba(255,255,255,0.02) inset,
            0 16px 34px rgba(0,0,0,0.30);
    }

    div[data-testid="stMetric"] label {
        color: #cbd5e1 !important;
        font-size: 14px !important;
        font-weight: 600 !important;
    }

    div[data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-size: 34px !important;
        font-weight: 800 !important;
        line-height: 1.1 !important;
    }

    div[data-testid="stMetric"] [data-testid="stMetricDelta"] {
        color: #22d3ee !important;
    }

    .dm-hero {
        background:
            linear-gradient(135deg, rgba(168,85,247,0.22), rgba(34,211,238,0.16)),
            linear-gradient(180deg, rgba(19,27,48,0.96), rgba(10,15,30,0.96));
        border: 1px solid rgba(255,255,255,0.07);
        border-radius: 28px;
        padding: 30px;
        margin-bottom: 24px;
        box-shadow:
            0 0 0 1px rgba(255,255,255,0.02) inset,
            0 22px 48px rgba(0,0,0,0.34);
        position: relative;
        overflow: hidden;
    }

    .dm-hero:before {
        content: "";
        position: absolute;
        width: 260px;
        height: 260px;
        top: -90px;
        right: -70px;
        background: radial-gradient(circle, rgba(168,85,247,0.32), transparent 65%);
        filter: blur(10px);
    }

    .dm-hero:after {
        content: "";
        position: absolute;
        width: 220px;
        height: 220px;
        bottom: -90px;
        left: -60px;
        background: radial-gradient(circle, rgba(34,211,238,0.25), transparent 65%);
        filter: blur(10px);
    }

    .dm-title {
        font-size: 36px;
        font-weight: 800;
        letter-spacing: -0.5px;
        margin-bottom: 8px;
        color: #ffffff;
        position: relative;
        z-index: 2;
    }

    .dm-subtitle {
        font-size: 15px;
        color: #cbd5e1;
        margin-bottom: 0;
        position: relative;
        z-index: 2;
    }

    .dm-section-title {
        font-size: 22px;
        font-weight: 700;
        color: #f8fafc;
        margin: 10px 0 14px 0;
        letter-spacing: -0.3px;
    }

    .dm-card {
        background:
            linear-gradient(180deg, rgba(16,22,40,0.96) 0%, rgba(9,14,28,0.96) 100%);
        border: 1px solid rgba(255,255,255,0.07);
        border-radius: 24px;
        padding: 22px;
        box-shadow:
            0 0 0 1px rgba(255,255,255,0.02) inset,
            0 16px 36px rgba(0,0,0,0.30);
        margin-bottom: 18px;
    }

    .dm-glow-shell {
        background:
            linear-gradient(135deg, rgba(168,85,247,0.16), rgba(34,211,238,0.12)),
            linear-gradient(180deg, rgba(16,22,40,0.97), rgba(9,14,28,0.97));
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 24px;
        padding: 24px;
        box-shadow:
            0 0 24px rgba(168,85,247,0.08),
            0 0 40px rgba(34,211,238,0.05),
            0 18px 40px rgba(0,0,0,0.30);
        margin-bottom: 18px;
    }

    .dm-card-title {
        font-size: 18px;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 12px;
    }

    .dm-badge {
        display: inline-block;
        padding: 6px 12px;
        border-radius: 999px;
        font-size: 13px;
        font-weight: 700;
        color: #fff;
        background: linear-gradient(90deg, #a855f7, #22d3ee);
        box-shadow: 0 8px 20px rgba(34,211,238,0.12);
    }

    .dm-price-big {
        font-size: 32px;
        font-weight: 800;
        color: #ffffff;
        margin: 10px 0 4px 0;
    }

    .dm-price-sub {
        font-size: 14px;
        color: #cbd5e1;
        margin-bottom: 14px;
    }

    .dm-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 10px 0;
        border-bottom: 1px solid rgba(255,255,255,0.06);
    }

    .dm-row:last-child {
        border-bottom: none;
    }

    .dm-row-label {
        color: #cbd5e1;
        font-size: 15px;
    }

    .dm-row-value {
        color: #ffffff;
        font-size: 15px;
        font-weight: 700;
    }

    .dm-sidebar-title {
        font-size: 24px;
        font-weight: 800;
        color: #ffffff;
        margin-bottom: 2px;
    }

    .dm-sidebar-sub {
        color: #94a3b8;
        font-size: 13px;
        margin-bottom: 8px;
    }

    .stDataFrame, div[data-testid="stPlotlyChart"] {
        background: rgba(255,255,255,0.02);
        border-radius: 18px;
    }

    div[data-testid="stInfo"], div[data-testid="stSuccess"], div[data-testid="stWarning"] {
        border-radius: 18px;
    }

    button[kind="primary"] {
        border-radius: 14px;
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)


def render_hero(titulo: str, subtitulo: str):
    st.markdown(
        f"""
        <div class="dm-hero">
            <div class="dm-title">{titulo}</div>
            <div class="dm-subtitle">{subtitulo}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_section_title(titulo: str):
    st.markdown(f'<div class="dm-section-title">{titulo}</div>', unsafe_allow_html=True)


def render_strategy_card(
    titulo: str,
    valor: str,
    subtitulo: str = "",
    detalhes=None,
    badge: str | None = None
):
    badge_html = f'<span class="dm-badge">{badge}</span>' if badge else ""

    st.markdown(
        f"""
        <div class="dm-glow-shell">
            <div style="display:flex; justify-content:space-between; align-items:center; gap:12px;">
                <div class="dm-card-title">{titulo}</div>
                <div>{badge_html}</div>
            </div>
            <div class="dm-price-big">{valor}</div>
            <div class="dm-price-sub">{subtitulo}</div>
        """,
        unsafe_allow_html=True
    )

    if detalhes:
        for label, value in detalhes:
            st.markdown(
                f"""
                <div class="dm-row">
                    <div class="dm-row-label">{label}</div>
                    <div class="dm-row-value">{value}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

    st.markdown("</div>", unsafe_allow_html=True)


def render_sidebar_header():
    st.markdown(
        """
        <div class="dm-sidebar-title">MarketMind</div>
        <div class="dm-sidebar-sub">Inteligência estratégica para vendas</div>
        """,
        unsafe_allow_html=True
    )