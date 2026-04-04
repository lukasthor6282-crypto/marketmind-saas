import streamlit as st
import pandas as pd
import plotly.express as px

from services.analise_engine import rodar_analise_completa
from services.coletas_service import listar_coletas_por_empresa
from utils.ui import (
    aplicar_estilo_global,
    render_hero,
    render_section_title,
    render_sidebar_header,
)
from utils.formatters import formatar_moeda
from components.states import empty_state, warning
from components.charts import donut_chart, ranking_cards


st.set_page_config(
    page_title="Dashboard por Produto",
    page_icon="🧩",
    layout="wide"
)

aplicar_estilo_global()

if "usuario" not in st.session_state or st.session_state.usuario is None:
    st.switch_page("pages/1_Login.py")

usuario = st.session_state.usuario
empresa_id = usuario["empresa_id"]
empresa_nome = usuario.get("empresa_nome", f"Empresa {empresa_id}")


def normalizar_valor_monetario(valor):
    try:
        if valor is None or valor == "":
            return 0.0
        return float(valor)
    except Exception:
        return 0.0


def extrair_lista_produtos(resultado: dict) -> list:
    chaves_possiveis = [
        "produtos",
        "produtos_analise",
        "produtos_analisados",
        "dados_produtos",
        "itens",
        "resultados_produtos",
    ]

    for chave in chaves_possiveis:
        valor = resultado.get(chave)
        if isinstance(valor, list) and len(valor) > 0 and isinstance(valor[0], dict):
            return valor

    return []


def enriquecer_produto(produto: dict) -> dict:
    titulo = (
        produto.get("titulo")
        or produto.get("nome")
        or produto.get("produto")
        or produto.get("title")
        or "Produto sem nome"
    )

    preco = normalizar_valor_monetario(
        produto.get("preco")
        or produto.get("preco_atual")
        or produto.get("valor")
        or produto.get("price")
    )

    score = normalizar_valor_monetario(
        produto.get("score")
        or produto.get("score_oportunidade")
        or produto.get("oportunidade_score")
    )

    concorrencia = (
        produto.get("concorrencia")
        or produto.get("nivel_concorrencia")
        or produto.get("tipo_concorrencia")
        or "Não informado"
    )

    preco_sugerido = normalizar_valor_monetario(
        produto.get("preco_sugerido")
        or produto.get("suggested_price")
    )

    faixa_min = normalizar_valor_monetario(
        produto.get("faixa_ideal_min")
        or produto.get("faixa_min")
        or produto.get("ideal_min")
    )

    faixa_max = normalizar_valor_monetario(
        produto.get("faixa_ideal_max")
        or produto.get("faixa_max")
        or produto.get("ideal_max")
    )

    oportunidade = (
        produto.get("oportunidade")
        or produto.get("status_oportunidade")
        or produto.get("classificacao")
        or "Não classificado"
    )

    palavras = produto.get("palavras_chave") or produto.get("keywords") or []
    if isinstance(palavras, str):
        palavras = [palavras]

    historico = produto.get("historico_precos") or produto.get("historico") or []

    decisao = produto.get("decisao") or {
        "status": "cautela",
        "mensagem": "Decisão ainda não disponível para este produto.",
        "cor": "neutro"
    }

    return {
        **produto,
        "titulo_resolvido": titulo,
        "preco_resolvido": preco,
        "score_resolvido": score,
        "concorrencia_resolvida": concorrencia,
        "preco_sugerido_resolvido": preco_sugerido,
        "faixa_min_resolvida": faixa_min,
        "faixa_max_resolvida": faixa_max,
        "oportunidade_resolvida": oportunidade,
        "palavras_resolvidas": palavras,
        "historico_resolvido": historico,
        "decisao_resolvida": decisao,
    }


def cor_oportunidade(texto: str) -> str:
    texto = str(texto).lower()
    if "alta" in texto or "boa" in texto or "oportun" in texto:
        return "rgba(34,211,238,0.18)"
    if "media" in texto or "moderad" in texto:
        return "rgba(168,85,247,0.18)"
    if "baixa" in texto or "ruim" in texto or "evitar" in texto:
        return "rgba(244,63,94,0.18)"
    return "rgba(255,255,255,0.06)"


def config_decisao(decisao: dict) -> dict:
    status = str(decisao.get("status", "cautela")).lower()

    if status == "comprar":
        return {
            "icone": "🔥",
            "titulo": "Comprar / Testar agora",
            "badge": "Comprar",
            "fundo": "rgba(34,211,238,0.14)",
            "borda": "rgba(34,211,238,0.35)"
        }

    if status == "evitar":
        return {
            "icone": "❌",
            "titulo": "Evitar no cenário atual",
            "badge": "Evitar",
            "fundo": "rgba(244,63,94,0.14)",
            "borda": "rgba(244,63,94,0.35)"
        }

    return {
        "icone": "⚠️",
        "titulo": "Entrar com cautela",
        "badge": "Cautela",
        "fundo": "rgba(168,85,247,0.14)",
        "borda": "rgba(168,85,247,0.35)"
    }


def render_badge_decisao(decisao: dict) -> str:
    visual = config_decisao(decisao)

    return f"""
    <span style="
        background:{visual['fundo']};
        border:1px solid {visual['borda']};
        color:#f8fafc;
        padding:6px 10px;
        border-radius:999px;
        font-size:12px;
        font-weight:700;
        white-space:nowrap;
        display:inline-block;
    ">
        {visual['icone']} {visual['badge']}
    </span>
    """


def mensagem_estrategica(produto: dict) -> tuple[str, str]:
    score = produto["score_resolvido"]
    concorrencia = str(produto["concorrencia_resolvida"]).lower()
    preco = produto["preco_resolvido"]
    preco_sugerido = produto["preco_sugerido_resolvido"]

    if score >= 80:
        return (
            "🔥 Produto com alto potencial",
            "Este produto mostra sinais fortes de oportunidade. Vale priorizar monitoramento e teste comercial."
        )

    if "alta" in concorrencia or "agress" in concorrencia:
        return (
            "⚠️ Mercado pressionado",
            "A concorrência parece intensa. A decisão depende mais de diferenciação e margem do que só preço."
        )

    if preco_sugerido > 0 and preco > 0 and preco_sugerido > preco:
        return (
            "💎 Espaço para reposicionamento",
            "O preço sugerido está acima do preço atual, indicando possibilidade de trabalhar valor percebido."
        )

    return (
        "📊 Produto em observação",
        "O produto merece acompanhamento. Reúna mais histórico e compare com concorrentes antes de escalar."
    )


def gerar_insight_portfolio(df_portfolio: pd.DataFrame) -> tuple[str, str, str, str]:
    total = len(df_portfolio)
    qtd_comprar = (df_portfolio["decisao_badge"] == "Comprar").sum()
    qtd_evitar = (df_portfolio["decisao_badge"] == "Evitar").sum()

    pct_comprar = (qtd_comprar / total * 100) if total else 0
    pct_evitar = (qtd_evitar / total * 100) if total else 0

    if pct_comprar >= 40:
        return (
            "🔥 Portfólio com boa tração",
            "Uma parte relevante dos produtos caiu na categoria de compra/teste.",
            "Estratégia sugerida: priorizar validação rápida dos produtos melhor ranqueados.",
            "rgba(34,211,238,0.16)"
        )

    if pct_evitar >= 40:
        return (
            "⚠️ Portfólio com risco elevado",
            "Muitos produtos foram classificados para evitar no cenário atual.",
            "Estratégia sugerida: reduzir foco em itens fracos e concentrar energia nos mais promissores.",
            "rgba(244,63,94,0.16)"
        )

    return (
        "📊 Portfólio equilibrado",
        "A maior parte dos produtos ficou em zona intermediária de decisão.",
        "Estratégia sugerida: usar testes controlados e aprofundar análise nos produtos com melhor score.",
        "rgba(168,85,247,0.16)"
    )


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
    "🧩 Dashboard por Produto",
    f"Detalhamento individual dos produtos monitorados da {empresa_nome}"
)

coletas = listar_coletas_por_empresa(empresa_id)

if not coletas:
    empty_state(
        titulo="Nenhuma coleta encontrada",
        descricao="Faça uma coleta primeiro para habilitar o dashboard por produto.",
        icone="📭"
    )
    st.stop()

opcoes_labels = [
    f'#{coleta["id"]} - {coleta["termo_busca"]} ({coleta["criado_em"]})'
    for coleta in coletas
]
opcoes_map = {
    f'#{coleta["id"]} - {coleta["termo_busca"]} ({coleta["criado_em"]})': coleta["id"]
    for coleta in coletas
}

coleta_preselecionada = st.session_state.get("coleta_dashboard_produto")
indice_padrao = 0

if coleta_preselecionada is not None:
    for idx, label in enumerate(opcoes_labels):
        if opcoes_map[label] == coleta_preselecionada:
            indice_padrao = idx
            break

col_top_1, col_top_2 = st.columns([1.4, 0.8])

with col_top_1:
    coleta_label = st.selectbox(
        "Selecione a coleta",
        opcoes_labels,
        index=indice_padrao
    )

with col_top_2:
    st.markdown("<div style='height:28px;'></div>", unsafe_allow_html=True)
    carregar = st.button("🔎 Carregar produtos", use_container_width=True)

coleta_id = opcoes_map[coleta_label]

if not carregar and coleta_preselecionada is None:
    empty_state(
        titulo="Selecione uma coleta para começar",
        descricao="Escolha uma coleta acima e clique em “Carregar produtos” para abrir o painel detalhado.",
        icone="🧩"
    )
    st.stop()

if not carregar and coleta_preselecionada is not None:
    carregar = True

with st.spinner("Carregando análise por produto..."):
    resultado = rodar_analise_completa(empresa_id, coleta_id)

if not resultado:
    warning("Não foi possível gerar a análise dessa coleta.")
    st.stop()

produtos_brutos = extrair_lista_produtos(resultado)

if not produtos_brutos:
    warning(
        "Sua engine ainda não está retornando a lista detalhada de produtos. "
        "A página foi criada, mas o próximo passo será adaptar o retorno do serviço para preencher este painel."
    )
    st.stop()

produtos = [enriquecer_produto(p) for p in produtos_brutos]
df_produtos = pd.DataFrame(produtos)

if df_produtos.empty:
    warning("Nenhum produto detalhado foi encontrado para esta coleta.")
    st.stop()

df_produtos["decisao_badge"] = df_produtos["decisao_resolvida"].apply(
    lambda x: config_decisao(x)["badge"]
)

render_section_title("Visão geral dos produtos")

total_produtos = len(df_produtos)
preco_medio = df_produtos["preco_resolvido"].mean() if "preco_resolvido" in df_produtos else 0
score_medio = df_produtos["score_resolvido"].mean() if "score_resolvido" in df_produtos else 0
preco_sugerido_medio = (
    df_produtos["preco_sugerido_resolvido"].mean()
    if "preco_sugerido_resolvido" in df_produtos else 0
)

m1, m2, m3, m4 = st.columns(4)

with m1:
    st.metric("Produtos detalhados", total_produtos)

with m2:
    st.metric("Preço médio", formatar_moeda(preco_medio or 0))

with m3:
    st.metric("Score médio", round(score_medio or 0, 2))

with m4:
    st.metric("Preço sugerido médio", formatar_moeda(preco_sugerido_medio or 0))

render_section_title("Visão executiva do portfólio")

dist_decisao = df_produtos["decisao_badge"].value_counts().reset_index()
dist_decisao.columns = ["categoria", "quantidade"]

dist_oportunidade = df_produtos["oportunidade_resolvida"].value_counts().reset_index()
dist_oportunidade.columns = ["categoria", "quantidade"]

titulo_portfolio, texto_portfolio, acao_portfolio, cor_portfolio = gerar_insight_portfolio(df_produtos)

vp1, vp2, vp3 = st.columns([1, 1, 1])

with vp1:
    st.markdown("#### Distribuição por decisão")
    fig_decisao = donut_chart(
        labels=dist_decisao["categoria"].tolist(),
        values=dist_decisao["quantidade"].tolist(),
        center_title="DECISÕES",
        center_value=int(dist_decisao["quantidade"].sum()),
        colors=["#22d3ee", "#8b5cf6", "#ef4444"],
        height=330
    )
    st.plotly_chart(fig_decisao, use_container_width=True)

with vp2:
    st.markdown("#### Distribuição por oportunidade")
    fig_oportunidade = donut_chart(
        labels=dist_oportunidade["categoria"].tolist(),
        values=dist_oportunidade["quantidade"].tolist(),
        center_title="PORTFÓLIO",
        center_value=int(dist_oportunidade["quantidade"].sum()),
        colors=["#22d3ee", "#8b5cf6", "#ef4444"],
        height=330
    )
    st.plotly_chart(fig_oportunidade, use_container_width=True)

with vp3:
    st.markdown(
        f"""
        <div style="
            background:{cor_portfolio};
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 24px;
            padding: 18px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.18);
            min-height: 260px;
        ">
            <div style="font-size:13px; color:#cbd5e1; margin-bottom:8px;">
                LEITURA EXECUTIVA
            </div>
            <div style="font-size:24px; font-weight:900; color:#f8fafc; margin-bottom:10px; line-height:1.4;">
                {titulo_portfolio}
            </div>
            <div style="font-size:14px; color:#e2e8f0; line-height:1.7; margin-bottom:12px;">
                {texto_portfolio}
            </div>
            <div style="font-size:14px; color:#f8fafc; font-weight:700; line-height:1.7;">
                {acao_portfolio}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("#### Ranking de decisões")
    ranking_cards(
        labels=dist_decisao["categoria"].tolist(),
        values=dist_decisao["quantidade"].tolist(),
        colors=["#22d3ee", "#8b5cf6", "#ef4444"],
        highlight_first=False
    )

render_section_title("Ranking estratégico dos produtos")

f0, f1, f2, f3 = st.columns([1.2, 1, 1, 1])

with f0:
    busca_produto = st.text_input("Buscar produto", placeholder="Digite parte do nome...")

with f1:
    filtro_decisao = st.selectbox(
        "Filtrar por decisão",
        ["Todos", "Comprar", "Cautela", "Evitar"]
    )

with f2:
    filtro_oportunidade = st.selectbox(
        "Filtrar por oportunidade",
        ["Todas", "Alta", "Média", "Baixa"]
    )

with f3:
    qtd_top = st.slider("Quantidade no ranking", min_value=3, max_value=20, value=8)

df_ranking = df_produtos.copy()

if busca_produto:
    termo_busca = busca_produto.strip().lower()
    df_ranking = df_ranking[
        df_ranking["titulo_resolvido"].str.lower().str.contains(termo_busca, na=False)
    ]

if filtro_decisao != "Todos":
    df_ranking = df_ranking[df_ranking["decisao_badge"] == filtro_decisao]

if filtro_oportunidade != "Todas":
    df_ranking = df_ranking[df_ranking["oportunidade_resolvida"] == filtro_oportunidade]

df_ranking = df_ranking.sort_values(
    by=["score_resolvido", "preco_sugerido_resolvido"],
    ascending=[False, False]
).head(qtd_top)

if df_ranking.empty:
    empty_state(
        titulo="Nenhum produto encontrado com esses filtros",
        descricao="Tente ajustar a busca ou os filtros para visualizar o ranking estratégico.",
        icone="🔎"
    )
    st.stop()

for _, row in df_ranking.iterrows():
    badge_html = render_badge_decisao(row["decisao_resolvida"])

    st.markdown(
        f"""
        <div style="
            background: linear-gradient(135deg, rgba(15,23,42,0.82), rgba(8,12,24,0.98));
            border: 1px solid rgba(255,255,255,0.06);
            border-radius: 20px;
            padding: 16px 18px;
            margin-bottom: 12px;
            box-shadow: 0 8px 24px rgba(0,0,0,0.14);
        ">
            <div style="
                display:flex;
                justify-content:space-between;
                align-items:flex-start;
                gap:16px;
                margin-bottom:10px;
            ">
                <div style="flex:1;">
                    <div style="font-size:17px; font-weight:800; color:#f8fafc; line-height:1.5;">
                        {row["titulo_resolvido"]}
                    </div>
                </div>
                <div>{badge_html}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.metric("Score", round(row["score_resolvido"], 2))
    with k2:
        st.metric("Preço atual", formatar_moeda(row["preco_resolvido"]))
    with k3:
        st.metric("Preço sugerido", formatar_moeda(row["preco_sugerido_resolvido"]))
    with k4:
        st.metric("Oportunidade", row["oportunidade_resolvida"])

render_section_title("Seleção de produto")

nomes_produtos = df_ranking["titulo_resolvido"].tolist()
produto_escolhido_nome = st.selectbox("Escolha o produto para detalhar", nomes_produtos)

produto = df_produtos[df_produtos["titulo_resolvido"] == produto_escolhido_nome].iloc[0].to_dict()

titulo_estrategia, texto_estrategia = mensagem_estrategica(produto)
decisao = produto["decisao_resolvida"]
visual_decisao = config_decisao(decisao)

st.markdown(
    f"""
    <div style="
        background: linear-gradient(135deg, rgba(15,23,42,0.86), rgba(8,12,24,0.98));
        border: 1px solid rgba(255,255,255,0.07);
        border-radius: 24px;
        padding: 20px;
        margin-bottom: 16px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.18);
    ">
        <div style="font-size:13px; color:#94a3b8; margin-bottom:8px;">
            PRODUTO SELECIONADO
        </div>
        <div style="font-size:26px; font-weight:900; color:#f8fafc; line-height:1.4;">
            {produto["titulo_resolvido"]}
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    f"""
    <div style="
        background:{visual_decisao['fundo']};
        border:1px solid {visual_decisao['borda']};
        border-radius:22px;
        padding:18px 20px;
        margin-bottom:18px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.12);
    ">
        <div style="font-size:13px; color:#cbd5e1; margin-bottom:8px;">
            DECISÃO IA POR PRODUTO
        </div>
        <div style="font-size:24px; font-weight:900; color:#f8fafc; margin-bottom:8px;">
            {visual_decisao['icone']} {visual_decisao['titulo']}
        </div>
        <div style="font-size:14px; color:#e2e8f0; line-height:1.7;">
            {decisao.get("mensagem", "Sem mensagem de decisão.")}
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.metric("Preço atual", formatar_moeda(produto["preco_resolvido"]))
with c2:
    st.metric("Score", round(produto["score_resolvido"], 2))
with c3:
    st.metric("Preço sugerido", formatar_moeda(produto["preco_sugerido_resolvido"]))
with c4:
    st.metric("Oportunidade", produto["oportunidade_resolvida"])

render_section_title("Leitura estratégica")

st.markdown(
    f"""
    <div style="
        background: rgba(34,211,238,0.10);
        border: 1px solid rgba(34,211,238,0.22);
        border-radius: 20px;
        padding: 18px;
        margin-bottom: 18px;
    ">
        <div style="font-size:20px; font-weight:800; color:#f8fafc; margin-bottom:8px;">
            {titulo_estrategia}
        </div>
        <div style="font-size:14px; color:#dbe4f0; line-height:1.7;">
            {texto_estrategia}
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

col_left, col_right = st.columns([1.05, 0.95])

with col_left:
    render_section_title("Faixa ideal de preço")

    faixa_min = produto["faixa_min_resolvida"]
    faixa_max = produto["faixa_max_resolvida"]
    preco_atual = produto["preco_resolvido"]
    preco_sugerido = produto["preco_sugerido_resolvido"]

    df_faixa = pd.DataFrame({
        "tipo": ["Faixa mínima", "Preço atual", "Preço sugerido", "Faixa máxima"],
        "valor": [faixa_min, preco_atual, preco_sugerido, faixa_max]
    })

    fig_faixa = px.bar(
        df_faixa,
        x="tipo",
        y="valor",
        title="Comparativo de precificação"
    )
    fig_faixa.update_traces(
        marker=dict(
            color=["#22d3ee", "#3b82f6", "#8b5cf6", "#ec4899"],
            line=dict(color="rgba(255,255,255,0.12)", width=1)
        )
    )
    fig_faixa.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(255,255,255,0.02)",
        font=dict(color="#E5E7EB"),
        xaxis_title="",
        yaxis_title="Preço",
        margin=dict(l=10, r=10, t=50, b=10)
    )
    st.plotly_chart(fig_faixa, use_container_width=True)

with col_right:
    render_section_title("Concorrência e oportunidade")

    labels = ["Oportunidade", "Pressão competitiva"]
    valor_oportunidade = max(produto["score_resolvido"], 0)
    valor_concorrencia = 100 - min(max(produto["score_resolvido"], 0), 100)

    fig_donut = donut_chart(
        labels=labels,
        values=[valor_oportunidade, valor_concorrencia],
        center_title="SCORE",
        center_value=round(produto["score_resolvido"], 1),
        colors=["#22d3ee", "#334155"],
        height=360
    )
    st.plotly_chart(fig_donut, use_container_width=True)

    ranking_cards(
        labels=["Concorrência", "Oportunidade"],
        values=[
            1 if str(produto["concorrencia_resolvida"]).strip() else 0.5,
            produto["score_resolvido"] if produto["score_resolvido"] > 0 else 0.5
        ],
        colors=["#8b5cf6", "#22d3ee"],
        highlight_first=False
    )

render_section_title("Palavras-chave do produto")

palavras = produto["palavras_resolvidas"]

if palavras:
    if isinstance(palavras, list) and len(palavras) > 0 and isinstance(palavras[0], (list, tuple)):
        df_palavras = pd.DataFrame(palavras, columns=["palavra", "frequencia"])
    else:
        df_palavras = pd.DataFrame({"palavra": palavras})
        df_palavras["frequencia"] = 1

    col_kw1, col_kw2 = st.columns([0.9, 1.1])

    with col_kw1:
        st.dataframe(df_palavras, use_container_width=True, hide_index=True)

    with col_kw2:
        fig_kw = px.bar(
            df_palavras.sort_values("frequencia", ascending=True),
            x="frequencia",
            y="palavra",
            orientation="h",
            title="Palavras com maior presença"
        )
        fig_kw.update_traces(
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
        fig_kw.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(255,255,255,0.02)",
            font=dict(color="#E5E7EB"),
            xaxis_title="Frequência",
            yaxis_title="",
            coloraxis_showscale=False,
            margin=dict(l=10, r=10, t=50, b=10)
        )
        st.plotly_chart(fig_kw, use_container_width=True)
else:
    empty_state(
        titulo="Sem palavras-chave para este produto",
        descricao="Sua engine ainda não retornou palavras-chave detalhadas para o item selecionado.",
        icone="🔤"
    )

render_section_title("Resumo técnico")

st.markdown(
    f"""
    <div style="
        background: linear-gradient(135deg, rgba(15,23,42,0.82), rgba(8,12,24,0.98));
        border: 1px solid rgba(255,255,255,0.07);
        border-radius: 22px;
        padding: 18px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.18);
    ">
        <div style="font-size:14px; color:#94a3b8; line-height:1.9;">
            <strong style="color:#f8fafc;">Concorrência:</strong> {produto["concorrencia_resolvida"]}<br>
            <strong style="color:#f8fafc;">Preço atual:</strong> {formatar_moeda(produto["preco_resolvido"])}<br>
            <strong style="color:#f8fafc;">Preço sugerido:</strong> {formatar_moeda(produto["preco_sugerido_resolvido"])}<br>
            <strong style="color:#f8fafc;">Faixa ideal:</strong> {formatar_moeda(produto["faixa_min_resolvida"])} até {formatar_moeda(produto["faixa_max_resolvida"])}<br>
            <strong style="color:#f8fafc;">Score:</strong> {round(produto["score_resolvido"], 2)}<br>
            <strong style="color:#f8fafc;">Classificação:</strong> {produto["oportunidade_resolvida"]}<br>
            <strong style="color:#f8fafc;">Decisão IA:</strong> {visual_decisao["titulo"]}
        </div>
    </div>
    """,
    unsafe_allow_html=True
)