import streamlit as st
import plotly.express as px
import pandas as pd

from services.analise_engine import rodar_analise_completa
from services.analise_mercado_service import salvar_analise_mercado
from services.relatorio_service import gerar_relatorio_pdf
from services.monitoramento_service import (
    salvar_snapshot_analise,
    comparar_e_gerar_alertas,
    listar_alertas_por_empresa,
)
from utils.ui import (
    aplicar_estilo_global,
    render_hero,
    render_section_title,
    render_strategy_card,
    render_sidebar_header
)
from utils.formatters import formatar_moeda
from services.analise_base import (
    calcular_lucro_estimado,
    calcular_preco_minimo_lucrativo,
    avaliar_viabilidade,
)
from components.charts import donut_chart, ranking_cards

st.set_page_config(
    page_title="Dashboard da Análise",
    page_icon="📈",
    layout="wide"
)

aplicar_estilo_global()

if "usuario" not in st.session_state or st.session_state.usuario is None:
    st.switch_page("pages/1_Login.py")

usuario = st.session_state.usuario
empresa_id = usuario["empresa_id"]
empresa_nome = usuario.get("empresa_nome", f"Empresa {empresa_id}")

if "ultima_coleta_id" not in st.session_state:
    st.warning("Nenhuma análise selecionada.")
    st.switch_page("pages/11_Historico.py")

coleta_id = st.session_state["ultima_coleta_id"]
termo_busca = st.session_state.get("ultimo_termo_busca", f"Coleta #{coleta_id}")

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
    "📈 Dashboard da Análise",
    f"Mercado analisado: {termo_busca}"
)

resultado = rodar_analise_completa(empresa_id, coleta_id)

if not resultado:
    st.warning("Sem dados suficientes para esta análise.")
    st.stop()

salvar_analise_mercado(
    empresa_id,
    usuario["id"],
    resultado["resumo"],
    resultado["palavras_chave"],
    resultado["score"],
    resultado["insights_premium"],
    resultado["preco_sugerido"],
    resultado["faixa_ideal"]
)

salvar_snapshot_analise(
    empresa_id,
    coleta_id,
    usuario["id"],
    termo_busca,
    resultado["resumo"],
    resultado["score"]
)

comparar_e_gerar_alertas(
    empresa_id,
    coleta_id,
    resultado["resumo"],
    resultado["score"]
)

resumo = resultado["resumo"]
score = resultado["score"]
preco_sugerido = resultado["preco_sugerido"]
faixa_ideal = resultado["faixa_ideal"]
decisao_final = resultado["decisao_final"]
concorrencia = resultado.get("concorrencia", {}) or {}

col1, col2, col3, col4 = st.columns(4)
col1.metric("Produtos", resumo["quantidade_produtos"])
col2.metric("Preço médio", formatar_moeda(resumo["preco_medio"]))
col3.metric("Preço mediano", formatar_moeda(resumo["preco_mediano"]))
col4.metric("Score", score["score"])

render_section_title("Ações rápidas")

col_ac1, col_ac2 = st.columns([1, 1])

with col_ac1:
    st.markdown(
        f"""
        <div style="
            background: linear-gradient(135deg, rgba(15,23,42,0.78), rgba(8,12,24,0.98));
            border: 1px solid rgba(255,255,255,0.07);
            border-radius: 22px;
            padding: 18px;
            min-height: 135px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.18);
        ">
            <div style="font-size:18px; font-weight:800; color:#f8fafc; margin-bottom:8px;">
                🧩 Ir para o Dashboard por Produto
            </div>
            <div style="font-size:14px; color:#cbd5e1; line-height:1.7;">
                Abra a visão individual dos produtos desta mesma coleta para ver score, decisão IA,
                oportunidade e ranking estratégico por item.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    if st.button("🧩 Abrir Dashboard por Produto", use_container_width=True):
        st.session_state["coleta_dashboard_produto"] = coleta_id
        st.session_state["termo_dashboard_produto"] = termo_busca
        st.switch_page("pages/13_Dashboard_Produto.py")

with col_ac2:
    st.markdown(
        f"""
        <div style="
            background: linear-gradient(135deg, rgba(34,211,238,0.12), rgba(59,130,246,0.10));
            border: 1px solid rgba(34,211,238,0.18);
            border-radius: 22px;
            padding: 18px;
            min-height: 135px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.18);
        ">
            <div style="font-size:18px; font-weight:800; color:#f8fafc; margin-bottom:8px;">
                📌 Coleta atual
            </div>
            <div style="font-size:14px; color:#cbd5e1; line-height:1.7;">
                <strong>Termo:</strong> {termo_busca}<br>
                <strong>ID da coleta:</strong> {coleta_id}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

render_section_title("Decisão final")

cor_decisao = {
    "positivo": "rgba(34,211,238,0.35)",
    "neutro": "rgba(168,85,247,0.35)",
    "alerta": "rgba(244,63,94,0.35)"
}.get(decisao_final["cor"], "rgba(255,255,255,0.15)")

st.markdown(
    f"""
    <div class="dm-card" style="border:1px solid {cor_decisao};">
        <div style="font-size:24px; font-weight:800; color:#fff; margin-bottom:10px;">
            {decisao_final["titulo"]}
        </div>
        <div style="font-size:15px; color:#cbd5e1; line-height:1.65;">
            {decisao_final["mensagem"]}
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

render_section_title("Alertas automáticos")

alertas = listar_alertas_por_empresa(empresa_id, limite=5)

if alertas:
    for alerta in alertas:
        cor = {
            "positivo": "rgba(34,211,238,0.35)",
            "alerta": "rgba(244,63,94,0.35)",
            "info": "rgba(168,85,247,0.35)"
        }.get(alerta["severidade"], "rgba(255,255,255,0.15)")

        st.markdown(
            f"""
            <div class="dm-card" style="border:1px solid {cor};">
                <div style="font-size:18px; font-weight:700; color:#fff; margin-bottom:6px;">
                    {alerta["titulo"]}
                </div>
                <div style="font-size:14px; color:#cbd5e1; line-height:1.55;">
                    {alerta["mensagem"]}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
else:
    st.info("Nenhum alerta disponível ainda.")

render_section_title("Resumo executivo")
st.markdown(
    f"""
    <div class="dm-card">
        <div style="font-size:15px; color:#cbd5e1; line-height:1.7;">
            {resultado["resumo_executivo"]}
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

col_a, col_b = st.columns([1.1, 1])

with col_a:
    render_section_title("Palavras-chave estratégicas")
    df_palavras = pd.DataFrame(resultado["palavras_chave"], columns=["palavra", "frequencia"])
    st.dataframe(df_palavras, use_container_width=True, hide_index=True)

    if not df_palavras.empty:
        df_palavras = df_palavras.sort_values("frequencia", ascending=True)

        fig_palavras = px.bar(
            df_palavras,
            x="frequencia",
            y="palavra",
            orientation="h",
            title="Ranking das palavras mais relevantes"
        )
        fig_palavras.update_traces(
            marker=dict(
                color=df_palavras["frequencia"],
                colorscale=[
                    [0.0, "#22d3ee"],
                    [0.5, "#3b82f6"],
                    [1.0, "#a855f7"]
                ],
                line=dict(color="rgba(255,255,255,0.15)", width=1)
            )
        )
        fig_palavras.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(255,255,255,0.02)",
            font=dict(color="#E5E7EB"),
            xaxis_title="Frequência",
            yaxis_title="",
            coloraxis_showscale=False,
            margin=dict(l=10, r=10, t=50, b=10)
        )
        st.plotly_chart(fig_palavras, use_container_width=True)

with col_b:
    render_section_title("Insights estratégicos")
    for insight in resultado["insights_premium"]:
        cor_borda = {
            "positivo": "rgba(34,211,238,0.35)",
            "alerta": "rgba(244,63,94,0.35)",
            "neutro": "rgba(168,85,247,0.35)"
        }.get(insight["tipo"], "rgba(255,255,255,0.15)")

        st.markdown(
            f"""
            <div class="dm-card" style="border:1px solid {cor_borda};">
                <div style="font-size:12px; color:#94a3b8; margin-bottom:6px;">
                    {insight["categoria"]}
                </div>
                <div style="font-size:18px; font-weight:700; color:#fff; margin-bottom:8px;">
                    {insight["titulo"]}
                </div>
                <div style="font-size:14px; color:#cbd5e1; line-height:1.55;">
                    {insight["mensagem"]}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

render_section_title("Distribuição de concorrência")

if concorrencia:
    df_conc = pd.DataFrame(
        [{"categoria": k, "quantidade": v} for k, v in concorrencia.items()]
    ).sort_values("quantidade", ascending=False)

    categorias = df_conc["categoria"].tolist()
    valores = df_conc["quantidade"].tolist()
    total = sum(valores)

    lider_categoria = categorias[0]
    lider_valor = valores[0]
    lider_percentual = (lider_valor / total * 100) if total else 0

    categoria_lower = lider_categoria.lower()

    if "agressiv" in categoria_lower:
        insight_titulo = "🔥 Mercado com forte pressão competitiva"
        insight_texto = (
            f"{lider_categoria} lidera com {lider_percentual:.1f}% da distribuição. "
            "Isso indica uma disputa mais intensa por preço e posicionamento."
        )
        insight_acao = "Estratégia sugerida: entrar com preço competitivo e diferenciação clara."
        insight_cor = "rgba(244,63,94,0.16)"
        insight_borda = "rgba(244,63,94,0.35)"
    elif "premium" in categoria_lower:
        insight_titulo = "💎 Mercado com espaço para posicionamento de valor"
        insight_texto = (
            f"{lider_categoria} lidera com {lider_percentual:.1f}% da distribuição. "
            "O nicho aparenta aceitar mais percepção de valor e diferenciação."
        )
        insight_acao = "Estratégia sugerida: reforçar qualidade, oferta e apresentação do produto."
        insight_cor = "rgba(168,85,247,0.16)"
        insight_borda = "rgba(168,85,247,0.35)"
    else:
        insight_titulo = "⚖️ Mercado relativamente equilibrado"
        insight_texto = (
            f"{lider_categoria} aparece na frente com {lider_percentual:.1f}% da distribuição, "
            "mas sem domínio extremo do cenário."
        )
        insight_acao = "Estratégia sugerida: buscar equilíbrio entre preço, margem e valor percebido."
        insight_cor = "rgba(34,211,238,0.16)"
        insight_borda = "rgba(34,211,238,0.35)"

    col_pizza, col_tabela = st.columns([1.05, 0.95])

    with col_pizza:
        st.markdown(
            """
            <div style="
                background: linear-gradient(135deg, rgba(15,23,42,0.82), rgba(8,12,24,0.98));
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
                font-size: 22px;
                font-weight: 800;
                color: #f8fafc;
                margin-bottom: 8px;
            ">
                Participação dos tipos de concorrente
            </div>
            <div style="
                color:#94a3b8;
                font-size:14px;
                margin-bottom: 18px;
            ">
                Entenda rapidamente quem domina a distribuição competitiva do nicho
            </div>
            """,
            unsafe_allow_html=True
        )

        if len(categorias) == 1:
            categoria = categorias[0]
            valor = valores[0]

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
                            CATEGORIA DOMINANTE
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
                            concorrentes identificados
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            fig_pizza = donut_chart(
                labels=categorias,
                values=valores,
                center_title="TOTAL MAPEADO",
                center_value=total,
                colors=["#22d3ee", "#3b82f6", "#a855f7", "#ec4899", "#14b8a6"],
                height=380
            )
            st.plotly_chart(fig_pizza, use_container_width=True)

        st.markdown("</div>", unsafe_allow_html=True)

    with col_tabela:
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
                    LÍDER DE CONCORRÊNCIA
                </div>
                <div style="font-size:24px; font-weight:800; color:#f8fafc; margin-bottom:6px;">
                    🔥 {lider_categoria}
                </div>
                <div style="font-size:15px; color:#cbd5e1; line-height:1.6;">
                    Essa categoria concentra <strong>{lider_percentual:.1f}%</strong> da distribuição observada,
                    com <strong>{lider_valor}</strong> registros na análise atual.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        ranking_cards(
            labels=categorias,
            values=valores,
            colors=["#22d3ee", "#3b82f6", "#a855f7", "#ec4899", "#14b8a6"],
            highlight_first=True
        )

        st.markdown(
            f"""
            <div style="
                background:{insight_cor};
                border:1px solid {insight_borda};
                border-radius:20px;
                padding:16px 18px;
                margin-top:14px;
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

render_section_title("Estratégia de precificação")

col_c, col_d = st.columns(2)

with col_c:
    render_strategy_card(
        titulo="Preço sugerido",
        valor=formatar_moeda(preco_sugerido["preco_sugerido"]),
        subtitulo="Melhor posição no mercado",
        badge=preco_sugerido["estrategia_preco"],
        detalhes=[
            ("Preço agressivo", formatar_moeda(preco_sugerido["preco_agressivo"])),
            ("Preço competitivo", formatar_moeda(preco_sugerido["preco_competitivo"])),
            ("Preço premium", formatar_moeda(preco_sugerido["preco_premium"]))
        ]
    )

with col_d:
    media_faixa = (faixa_ideal["faixa_ideal_min"] + faixa_ideal["faixa_ideal_max"]) / 2

    render_strategy_card(
        titulo="Faixa ideal",
        valor=formatar_moeda(media_faixa),
        subtitulo="Zona ideal de mercado",
        badge="Mercado",
        detalhes=[
            ("Faixa mínima", formatar_moeda(faixa_ideal["faixa_ideal_min"])),
            ("Faixa máxima", formatar_moeda(faixa_ideal["faixa_ideal_max"])),
            ("Amplitude", formatar_moeda(faixa_ideal["faixa_ideal_max"] - faixa_ideal["faixa_ideal_min"]))
        ]
    )

render_section_title("Simulador de lucro")

col_l1, col_l2, col_l3 = st.columns(3)

with col_l1:
    custo_produto = st.number_input("Custo do produto", min_value=0.0, value=50.0, step=1.0)

with col_l2:
    taxa_percentual = st.number_input("Taxa da plataforma (%)", min_value=0.0, value=16.0, step=0.5)

with col_l3:
    lucro_desejado = st.number_input("Lucro desejado", min_value=0.0, value=20.0, step=1.0)

lucro_info = calcular_lucro_estimado(
    custo_produto,
    preco_sugerido["preco_sugerido"],
    taxa_percentual
)

preco_minimo = calcular_preco_minimo_lucrativo(
    custo_produto,
    taxa_percentual,
    lucro_desejado
)

viabilidade = avaliar_viabilidade(
    preco_sugerido["preco_sugerido"],
    preco_minimo
)

col_s1, col_s2, col_s3 = st.columns(3)
col_s1.metric("Lucro estimado", formatar_moeda(lucro_info["lucro_estimado"]))
col_s2.metric("Margem estimada", f'{lucro_info["margem_estimada"]}%')
col_s3.metric("Preço mínimo lucrativo", formatar_moeda(preco_minimo or 0))

st.markdown(
    f"""
    <div class="dm-card">
        <div style="font-size:22px; font-weight:800; color:#fff; margin-bottom:10px;">
            {viabilidade["mensagem"]}
        </div>
        <div style="font-size:14px; color:#cbd5e1;">
            Diferença entre preço competitivo e mínimo lucrativo:
            <strong>{formatar_moeda(viabilidade["diferenca"] or 0)}</strong>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

st.divider()

if st.button("📄 Gerar relatório PDF"):
    caminho = gerar_relatorio_pdf(resultado)

    with open(caminho, "rb") as f:
        st.download_button(
            "📥 Baixar relatório",
            f,
            file_name="relatorio_mercado.pdf"
        )