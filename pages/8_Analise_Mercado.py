import time
import streamlit as st
import pandas as pd

from services.analise_engine import rodar_analise_completa
from services.coletas_service import listar_coletas_por_empresa
from services.analise_mercado_service import salvar_analise_mercado
from services.relatorio_service import gerar_relatorio_pdf

from components.states import (
    loading_card,
    progress_step,
    success,
    warning,
    empty_state,
)


st.set_page_config(
    page_title="Análise Inteligente",
    page_icon="📈",
    layout="wide"
)

if "usuario" not in st.session_state or st.session_state.usuario is None:
    st.switch_page("pages/1_Login.py")

usuario = st.session_state.usuario
empresa_id = usuario["empresa_id"]
empresa_nome = usuario.get("empresa_nome", f"Empresa {empresa_id}")


st.markdown(
    f"""
    <div style="
        background: linear-gradient(135deg, rgba(15,23,42,0.92), rgba(10,15,30,0.98));
        border: 1px solid rgba(255,255,255,0.07);
        border-radius: 24px;
        padding: 24px;
        margin-bottom: 22px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.18);
    ">
        <div style="font-size: 30px; font-weight: 900; color: #f8fafc; margin-bottom: 8px;">
            📈 Análise Inteligente de Mercado
        </div>
        <div style="font-size: 15px; color: #94a3b8; line-height: 1.6;">
            Escolha uma coleta específica da <strong>{empresa_nome}</strong> para gerar uma análise executiva,
            com resumo, score, insights, precificação e relatório.
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

coletas = listar_coletas_por_empresa(empresa_id)

if not coletas:
    empty_state(
        titulo="Nenhuma coleta encontrada",
        descricao="Faça uma coleta primeiro para habilitar a análise inteligente de mercado.",
        icone="📭"
    )
    st.stop()

opcoes = {
    f'#{coleta["id"]} - {coleta["termo_busca"]} ({coleta["criado_em"]})': coleta["id"]
    for coleta in coletas
}

col_f1, col_f2 = st.columns([1.4, 0.6])

with col_f1:
    coleta_label = st.selectbox("Selecione a coleta", list(opcoes.keys()))

with col_f2:
    st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
    rodar = st.button("🚀 Rodar análise completa", use_container_width=True)

coleta_id = opcoes[coleta_label]

if rodar:
    loading_area = st.empty()
    progress_area = st.empty()

    with loading_area.container():
        loading_card(
            titulo="Preparando análise",
            descricao="Estamos validando a coleta escolhida e organizando os dados do mercado."
        )

    etapas = [
        ("Validando coleta", "Verificando consistência dos dados selecionados."),
        ("Lendo dados do mercado", "Carregando os produtos encontrados e preparando a base."),
        ("Calculando métricas", "Gerando médias, score, preço sugerido e faixa ideal."),
        ("Gerando insights", "Interpretando concorrência, palavras-chave e oportunidade."),
        ("Montando resultado final", "Consolidando resumo executivo e preparando o relatório."),
    ]

    for i, (titulo_etapa, descricao_etapa) in enumerate(etapas, start=1):
        with progress_area.container():
            progress_step(
                i,
                len(etapas),
                titulo=titulo_etapa,
                descricao=descricao_etapa
            )
        time.sleep(0.22)

    resultado = rodar_analise_completa(empresa_id, coleta_id)

    loading_area.empty()
    progress_area.empty()

    if not resultado:
        warning("Sem dados suficientes para gerar a análise.")
        st.stop()

    salvar_analise_mercado(
        empresa_id,
        usuario["id"],
        resultado["resumo"],
        resultado["palavras_chave"],
        resultado["score"],
        resultado["insights"],
        resultado["preco_sugerido"],
        resultado["faixa_ideal"]
    )

    success("Análise concluída com sucesso.")

    resumo = resultado["resumo"]
    score = resultado["score"]
    resumo_executivo = resultado.get("resumo_executivo", "Sem resumo executivo.")
    palavras_chave = resultado.get("palavras_chave", [])
    insights = resultado.get("insights", [])
    preco_sugerido = resultado.get("preco_sugerido", {})
    faixa_ideal = resultado.get("faixa_ideal", {})

    st.markdown("## Visão geral da análise")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            f"""
            <div style="
                background: linear-gradient(145deg, #1e1e2f, #2a2a40);
                padding: 20px;
                border-radius: 18px;
                box-shadow: 0 4px 15px rgba(0,0,0,0.25);
                margin-bottom: 10px;
            ">
                <div style="font-size: 14px; color: #94a3b8;">📦 Produtos analisados</div>
                <div style="font-size: 30px; font-weight: 800; color: #ffffff;">{resumo.get("quantidade_produtos", 0)}</div>
                <div style="font-size: 12px; color: #cbd5e1;">Volume identificado na coleta</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            f"""
            <div style="
                background: linear-gradient(145deg, #1e1e2f, #2a2a40);
                padding: 20px;
                border-radius: 18px;
                box-shadow: 0 4px 15px rgba(0,0,0,0.25);
                margin-bottom: 10px;
            ">
                <div style="font-size: 14px; color: #94a3b8;">💰 Preço médio</div>
                <div style="font-size: 30px; font-weight: 800; color: #ffffff;">R$ {resumo.get("preco_medio", 0)}</div>
                <div style="font-size: 12px; color: #cbd5e1;">Média geral encontrada</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col3:
        st.markdown(
            f"""
            <div style="
                background: linear-gradient(145deg, #1e1e2f, #2a2a40);
                padding: 20px;
                border-radius: 18px;
                box-shadow: 0 4px 15px rgba(0,0,0,0.25);
                margin-bottom: 10px;
            ">
                <div style="font-size: 14px; color: #94a3b8;">🎯 Score estratégico</div>
                <div style="font-size: 30px; font-weight: 800; color: #ffffff;">{score.get("score", 0)}</div>
                <div style="font-size: 12px; color: #cbd5e1;">Pontuação da oportunidade</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("## Resumo executivo")
    st.markdown(
        f"""
        <div style="
            background: rgba(255,255,255,0.03);
            border: 1px solid rgba(255,255,255,0.06);
            border-radius: 18px;
            padding: 18px;
            color: #e2e8f0;
            line-height: 1.7;
            margin-bottom: 18px;
        ">
            {resumo_executivo}
        </div>
        """,
        unsafe_allow_html=True
    )

    col_a, col_b = st.columns([1, 1])

    with col_a:
        st.markdown("## Palavras-chave")

        if palavras_chave:
            if isinstance(palavras_chave, list) and len(palavras_chave) > 0 and isinstance(palavras_chave[0], (list, tuple)):
                df_palavras = pd.DataFrame(palavras_chave, columns=["palavra", "frequencia"])
            else:
                df_palavras = pd.DataFrame({"palavra": palavras_chave})

            st.dataframe(df_palavras, use_container_width=True, hide_index=True)
        else:
            warning("Nenhuma palavra-chave disponível.")

    with col_b:
        st.markdown("## Insights estratégicos")

        if insights:
            for insight in insights:
                st.markdown(
                    f"""
                    <div style="
                        background: rgba(34,211,238,0.08);
                        border: 1px solid rgba(34,211,238,0.22);
                        border-radius: 16px;
                        padding: 14px 16px;
                        margin-bottom: 12px;
                        color: #e2e8f0;
                        line-height: 1.6;
                    ">
                        {insight}
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        else:
            warning("Nenhum insight disponível.")

    st.markdown("## Estratégia de preço")

    col_p1, col_p2 = st.columns(2)

    with col_p1:
        st.markdown(
            f"""
            <div style="
                background: linear-gradient(145deg, rgba(34,211,238,0.12), rgba(59,130,246,0.10));
                border: 1px solid rgba(34,211,238,0.20);
                border-radius: 18px;
                padding: 18px;
                min-height: 180px;
            ">
                <div style="font-size: 14px; color: #94a3b8;">Preço sugerido</div>
                <div style="font-size: 30px; font-weight: 900; color: #f8fafc; margin: 10px 0;">
                    {preco_sugerido.get("preco_sugerido", "N/A")}
                </div>
                <div style="font-size: 14px; color: #cbd5e1; line-height: 1.7;">
                    <strong>Agressivo:</strong> {preco_sugerido.get("preco_agressivo", "N/A")}<br>
                    <strong>Competitivo:</strong> {preco_sugerido.get("preco_competitivo", "N/A")}<br>
                    <strong>Premium:</strong> {preco_sugerido.get("preco_premium", "N/A")}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col_p2:
        st.markdown(
            f"""
            <div style="
                background: linear-gradient(145deg, rgba(168,85,247,0.12), rgba(236,72,153,0.10));
                border: 1px solid rgba(168,85,247,0.20);
                border-radius: 18px;
                padding: 18px;
                min-height: 180px;
            ">
                <div style="font-size: 14px; color: #94a3b8;">Faixa ideal</div>
                <div style="font-size: 30px; font-weight: 900; color: #f8fafc; margin: 10px 0;">
                    {faixa_ideal.get("faixa_ideal_min", "N/A")} - {faixa_ideal.get("faixa_ideal_max", "N/A")}
                </div>
                <div style="font-size: 14px; color: #cbd5e1; line-height: 1.7;">
                    Intervalo recomendado para posicionamento estratégico no mercado atual.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("## Relatório final")

    col_r1, col_r2 = st.columns([0.5, 0.5])

    with col_r1:
        if st.button("📄 Gerar relatório PDF", use_container_width=True):
            caminho = gerar_relatorio_pdf(resultado)

            with open(caminho, "rb") as f:
                st.download_button(
                    "📥 Baixar relatório",
                    f,
                    file_name="relatorio_mercado.pdf",
                    use_container_width=True
                )

    with col_r2:
        st.markdown(
            """
            <div style="
                background: rgba(255,255,255,0.03);
                border: 1px solid rgba(255,255,255,0.06);
                border-radius: 16px;
                padding: 14px;
                color: #94a3b8;
                line-height: 1.6;
            ">
                Gere o PDF para compartilhar a análise com cliente, sócio ou equipe.
            </div>
            """,
            unsafe_allow_html=True
        )