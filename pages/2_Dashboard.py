import streamlit as st
import pandas as pd
import plotly.express as px

from components.cards import metric_card
from components.sections import section
from components.states import loading

from services.analises_service import contar_analises_empresa, media_score_empresa
from services.produtos_service import resumo_produtos_empresa
from services.coletas_service import listar_coletas_por_empresa

from utils.ui import (
    aplicar_estilo_global,
    render_hero,
    render_section_title,
    render_sidebar_header
)
from utils.formatters import formatar_moeda


st.set_page_config(
    page_title="Dashboard - MarketMind",
    page_icon="📊",
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
    "📊 Dashboard Premium",
    f"Visão estratégica da operação da {empresa_nome}"
)

with st.spinner("Carregando indicadores do dashboard..."):
    total_analises = contar_analises_empresa(empresa_id)
    media_score = media_score_empresa(empresa_id)
    resumo_produtos = resumo_produtos_empresa(empresa_id)
    coletas = listar_coletas_por_empresa(empresa_id)

total_produtos = resumo_produtos.get("total_produtos", 0) or 0
produtos_ativos = resumo_produtos.get("ativos", 0) or 0
preco_medio = resumo_produtos.get("preco_medio", 0) or 0
total_coletas = len(coletas)

section("Indicadores principais", "Resumo rápido da operação atual")

col1, col2, col3, col4 = st.columns(4)

with col1:
    metric_card(
        "Análises registradas",
        total_analises,
        "Quantidade total de análises da empresa",
        "📈"
    )

with col2:
    metric_card(
        "Score médio",
        f"{round(media_score or 0, 2)}",
        "Desempenho médio das análises",
        "🎯"
    )

with col3:
    metric_card(
        "Produtos monitorados",
        total_produtos,
        "Produtos disponíveis na base",
        "📦"
    )

with col4:
    metric_card(
        "Coletas realizadas",
        total_coletas,
        "Histórico total de coletas",
        "🛰️"
    )

render_section_title("Painel executivo")

col_a, col_b, col_c = st.columns(3)

with col_a:
    st.markdown(
        f"""
        <div class="dm-card">
            <div style="font-size:18px; font-weight:800; color:#fff; margin-bottom:18px;">
                📌 Situação atual
            </div>
            <div style="display:flex; flex-direction:column; gap:14px;">
                <div><span style="color:#cbd5e1;">Empresa ativa:</span> <strong>{empresa_nome}</strong></div>
                <div><span style="color:#cbd5e1;">Análises registradas:</span> <strong>{total_analises}</strong></div>
                <div><span style="color:#cbd5e1;">Coletas realizadas:</span> <strong>{total_coletas}</strong></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col_b:
    st.markdown(
        f"""
        <div class="dm-card">
            <div style="font-size:18px; font-weight:800; color:#fff; margin-bottom:18px;">
                💰 Mercado consolidado
            </div>
            <div style="display:flex; flex-direction:column; gap:14px;">
                <div><span style="color:#cbd5e1;">Produtos totais:</span> <strong>{total_produtos}</strong></div>
                <div><span style="color:#cbd5e1;">Produtos ativos:</span> <strong>{produtos_ativos}</strong></div>
                <div><span style="color:#cbd5e1;">Preço médio geral:</span> <strong>{formatar_moeda(preco_medio)}</strong></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col_c:
    if total_coletas == 0:
        mensagem_acao = "Crie sua primeira análise para começar a gerar inteligência de mercado."
        cor_acao = "rgba(168,85,247,0.18)"
    elif total_produtos == 0:
        mensagem_acao = "Cadastre produtos para enriquecer suas análises e visualizar mais oportunidades."
        cor_acao = "rgba(244,63,94,0.14)"
    else:
        mensagem_acao = "Continue monitorando os produtos com melhor potencial e acompanhe a evolução do mercado."
        cor_acao = "rgba(34,211,238,0.14)"

    st.markdown(
        f"""
        <div class="dm-card">
            <div style="font-size:18px; font-weight:800; color:#fff; margin-bottom:18px;">
                ⚡ Ação recomendada
            </div>
            <div style="
                background:{cor_acao};
                border:1px solid rgba(255,255,255,0.06);
                border-radius:18px;
                padding:16px;
                color:#e2e8f0;
                line-height:1.6;
            ">
                {mensagem_acao}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

render_section_title("Distribuição geral das análises")

if coletas:
    df_coletas = pd.DataFrame(coletas).copy()
    df_coletas["criado_em"] = pd.to_datetime(df_coletas["criado_em"], errors="coerce")
    df_coletas["mês"] = df_coletas["criado_em"].dt.strftime("%m/%Y")

    resumo_mes = (
        df_coletas["mês"]
        .value_counts()
        .reset_index()
    )
    resumo_mes.columns = ["período", "quantidade"]

    categorias = resumo_mes["período"].tolist()
    quantidades = resumo_mes["quantidade"].tolist()
    total_geral = sum(quantidades)

    periodo_lider = categorias[0]
    valor_lider = quantidades[0]
    percentual_lider = (valor_lider / total_geral * 100) if total_geral else 0

    if len(categorias) == 1:
        insight_titulo = "📍 Base concentrada em um único período"
        insight_texto = (
            f"Todas as coletas registradas estão concentradas em {periodo_lider}. "
            "Isso indica baixa diversidade temporal no histórico atual."
        )
        insight_acao = "Estratégia sugerida: ampliar novas coletas para criar visão comparativa ao longo do tempo."
        insight_cor = "rgba(168,85,247,0.16)"
        insight_borda = "rgba(168,85,247,0.35)"
    elif percentual_lider >= 60:
        insight_titulo = "🔥 Forte concentração temporal"
        insight_texto = (
            f"O período {periodo_lider} concentra {percentual_lider:.1f}% das coletas. "
            "A leitura atual do histórico está muito apoiada nesse intervalo."
        )
        insight_acao = "Estratégia sugerida: comparar com períodos anteriores para validar tendência real."
        insight_cor = "rgba(244,63,94,0.16)"
        insight_borda = "rgba(244,63,94,0.35)"
    else:
        insight_titulo = "📊 Histórico mais distribuído"
        insight_texto = (
            f"O período líder é {periodo_lider}, com {percentual_lider:.1f}% das coletas. "
            "O histórico mostra distribuição mais equilibrada entre os períodos."
        )
        insight_acao = "Estratégia sugerida: usar esse equilíbrio para detectar evolução do mercado com mais segurança."
        insight_cor = "rgba(34,211,238,0.16)"
        insight_borda = "rgba(34,211,238,0.35)"

    col_p1, col_p2 = st.columns([1.15, 0.85])

    with col_p1:
        cores_premium = [
            "#22d3ee",
            "#3b82f6",
            "#8b5cf6",
            "#ec4899",
            "#14b8a6",
            "#f59e0b",
            "#ef4444"
        ]

        st.markdown(
            """
            <div style="
                background: linear-gradient(135deg, rgba(15,23,42,0.78), rgba(10,15,30,0.96));
                border: 1px solid rgba(255,255,255,0.07);
                border-radius: 24px;
                padding: 20px 20px 10px 20px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.18);
            ">
            """,
            unsafe_allow_html=True
        )

        st.markdown(
            """
            <div style="
                font-size: 24px;
                font-weight: 800;
                color: #f8fafc;
                margin-bottom: 8px;
            ">
                Participação por período
            </div>
            <div style="
                color:#94a3b8;
                font-size:14px;
                margin-bottom: 18px;
            ">
                Evolução das coletas registradas ao longo do tempo
            </div>
            """,
            unsafe_allow_html=True
        )

        if len(categorias) == 1:
            categoria = categorias[0]
            valor = quantidades[0]

            st.markdown(
                f"""
                <div style="
                    display:flex;
                    align-items:center;
                    justify-content:center;
                    height:350px;
                    border-radius:24px;
                    background:
                        radial-gradient(circle at center, rgba(34,211,238,0.22), rgba(34,211,238,0.08) 28%, rgba(0,0,0,0) 62%);
                    border: 1px solid rgba(255,255,255,0.05);
                    margin-bottom: 14px;
                ">
                    <div style="text-align:center;">
                        <div style="
                            font-size:13px;
                            color:#94a3b8;
                            letter-spacing:0.3px;
                            margin-bottom:8px;
                        ">
                            PERÍODO DOMINANTE
                        </div>
                        <div style="
                            font-size:26px;
                            font-weight:800;
                            color:#22d3ee;
                            margin-bottom:10px;
                        ">
                            {categoria}
                        </div>
                        <div style="
                            font-size:42px;
                            font-weight:900;
                            color:#f8fafc;
                            line-height:1;
                        ">
                            {valor}
                        </div>
                        <div style="
                            color:#94a3b8;
                            font-size:13px;
                            margin-top:6px;
                        ">
                            coletas registradas
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        else:
            fig_pizza = px.pie(
                names=categorias,
                values=quantidades,
                hole=0.76
            )

            fig_pizza.update_traces(
                textinfo="none",
                hovertemplate=(
                    "<b>%{label}</b><br>"
                    "Quantidade: %{value}<br>"
                    "Participação: %{percent}<extra></extra>"
                ),
                pull=[0.06 if i == 0 else 0.015 for i in range(len(categorias))],
                marker=dict(
                    colors=cores_premium[:len(categorias)],
                    line=dict(color="#081225", width=7)
                ),
                sort=False,
                direction="clockwise",
                rotation=90
            )

            fig_pizza.update_layout(
                showlegend=False,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=10, r=10, t=10, b=10),
                annotations=[
                    dict(
                        text="TOTAL DE COLETAS",
                        x=0.5,
                        y=0.58,
                        xanchor="center",
                        yanchor="middle",
                        showarrow=False,
                        font=dict(
                            family="Trebuchet MS",
                            size=11,
                            color="#94a3b8"
                        )
                    ),
                    dict(
                        text=f"{total_geral}",
                        x=0.5,
                        y=0.45,
                        xanchor="center",
                        yanchor="middle",
                        showarrow=False,
                        font=dict(
                            family="Arial Black",
                            size=28,
                            color="#f8fafc"
                        )
                    )
                ]
            )

            st.plotly_chart(fig_pizza, use_container_width=True)

        st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

        cards_html = ""
        for i, (categoria, qtd) in enumerate(zip(categorias, quantidades)):
            percentual = (qtd / total_geral * 100) if total_geral else 0
            cor = cores_premium[i]
            destaque = "🔥 " if i == 0 and len(categorias) > 1 else ""

            cards_html += f"""
            <div style="
                display:flex;
                align-items:center;
                justify-content:space-between;
                gap:12px;
                background: rgba(255,255,255,0.03);
                border: 1px solid rgba(255,255,255,0.06);
                border-radius: 16px;
                padding: 12px 14px;
                margin-bottom: 10px;
            ">
                <div style="display:flex; align-items:center; gap:10px;">
                    <div style="
                        width:12px;
                        height:12px;
                        border-radius:999px;
                        background:{cor};
                        box-shadow: 0 0 12px {cor};
                    "></div>
                    <div style="color:#e2e8f0; font-size:14px; font-weight:600;">
                        {destaque}{categoria}
                    </div>
                </div>
                <div style="text-align:right;">
                    <div style="color:#f8fafc; font-size:15px; font-weight:700;">{qtd}</div>
                    <div style="color:#94a3b8; font-size:12px;">{percentual:.1f}%</div>
                </div>
            </div>
            """

        st.markdown(cards_html, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col_p2:
        st.markdown(
            f"""
            <div style="
                background: linear-gradient(135deg, rgba(15,23,42,0.78), rgba(8,12,24,0.98));
                border: 1px solid rgba(255,255,255,0.07);
                border-radius: 24px;
                padding: 20px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.18);
                margin-bottom: 14px;
            ">
                <div style="font-size:13px; color:#94a3b8; margin-bottom:8px;">
                    PERÍODO LÍDER
                </div>
                <div style="font-size:24px; font-weight:800; color:#f8fafc; margin-bottom:6px;">
                    🔥 {periodo_lider}
                </div>
                <div style="font-size:15px; color:#cbd5e1; line-height:1.6;">
                    Esse período concentra <strong>{percentual_lider:.1f}%</strong> das coletas,
                    com <strong>{valor_lider}</strong> registros no histórico atual.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown(
            f"""
            <div style="
                background:{insight_cor};
                border:1px solid {insight_borda};
                border-radius:20px;
                padding:16px 18px;
                margin-bottom:14px;
            ">
                <div style="font-size:18px; font-weight:800; color:#f8fafc; margin-bottom:8px;">
                    {insight_titulo}
                </div>
                <div style="font-size:14px; color:#dbe4f0; line-height:1.6; margin-bottom:8px;">
                    {insight_texto}
                </div>
                <div style="font-size:14px; color:#f8fafc; font-weight:600; line-height:1.6;">
                    {insight_acao}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown(
            """
            <div style="
                background: linear-gradient(135deg, rgba(15,23,42,0.72), rgba(10,15,30,0.96));
                border: 1px solid rgba(255,255,255,0.07);
                border-radius: 24px;
                padding: 20px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.18);
            ">
            <h4 style="margin-top: 0; color: #f8fafc;">Últimas coletas</h4>
            """,
            unsafe_allow_html=True
        )

        df_exibicao = df_coletas.copy()

        colunas_desejadas = ["id", "termo_busca", "criado_em"]
        colunas_existentes = [col for col in colunas_desejadas if col in df_exibicao.columns]
        df_exibicao = df_exibicao[colunas_existentes].head(6)

        rename_map = {
            "id": "ID",
            "termo_busca": "Busca",
            "criado_em": "Criado em"
        }
        df_exibicao = df_exibicao.rename(columns=rename_map)

        if "Criado em" in df_exibicao.columns:
            df_exibicao["Criado em"] = pd.to_datetime(
                df_exibicao["Criado em"], errors="coerce"
            ).dt.strftime("%d/%m/%Y %H:%M")

        st.dataframe(df_exibicao, use_container_width=True, hide_index=True)

        st.markdown("</div>", unsafe_allow_html=True)

else:
    loading("Preparando ambiente do dashboard...")
    st.info("Nenhuma análise ainda. Vá em Nova análise para começar.")