import pandas as pd

from services.produtos_service import listar_produtos_por_coleta

from services.analise_base import (
    limpar_dados,
    analisar_precos,
    classificar_concorrencia,
    analisar_titulos,
    calcular_faixa_preco,
    detectar_oportunidade,
    calcular_score_oportunidade,
    gerar_resumo_executivo,
    calcular_preco_sugerido,
    calcular_faixa_ideal_mercado,
    classificar_concorrentes,
    resumo_concorrentes,
    gerar_insights
)


def gerar_insights_premium(resumo, score_info, faixa_ideal, preco_info, resumo_conc):
    insights = []

    if resumo["nivel_concorrencia"] == "Alta":
        insights.append({
            "categoria": "Concorrência",
            "titulo": "Mercado disputado",
            "mensagem": "Alta concorrência detectada.",
            "tipo": "alerta"
        })
    elif resumo["nivel_concorrencia"] == "Média":
        insights.append({
            "categoria": "Concorrência",
            "titulo": "Mercado intermediário",
            "mensagem": "Concorrência moderada.",
            "tipo": "neutro"
        })
    else:
        insights.append({
            "categoria": "Concorrência",
            "titulo": "Mercado com baixa pressão",
            "mensagem": "Pouca concorrência.",
            "tipo": "positivo"
        })

    return insights


def gerar_decisao_final(resumo, score_info, preco_info, faixa_ideal):
    score = score_info["score"]
    preco_sugerido = preco_info["preco_sugerido"]

    if score >= 7:
        return {
            "status": "vale_a_pena",
            "titulo": "Mercado atrativo",
            "mensagem": "Boa oportunidade.",
            "cor": "positivo"
        }

    if score >= 4:
        return {
            "status": "cautela",
            "titulo": "Cuidado",
            "mensagem": "Mercado moderado.",
            "cor": "neutro"
        }

    return {
        "status": "evitar",
        "titulo": "Evitar",
        "mensagem": "Mercado fraco.",
        "cor": "alerta"
    }


def rodar_analise_completa(empresa_id: int, coleta_id: int):
    produtos = listar_produtos_por_coleta(empresa_id, coleta_id)

    if not produtos:
        return None

    df = pd.DataFrame(produtos)

    if df.empty:
        return None

    df["preco"] = pd.to_numeric(df.get("preco", 0), errors="coerce").fillna(0)
    df["titulo"] = df.get("titulo", "").astype(str)

    df = limpar_dados(df)

    if df.empty:
        return None

    resumo = analisar_precos(df)
    resumo["nivel_concorrencia"] = classificar_concorrencia(
        resumo["quantidade_produtos"]
    )

    palavras = analisar_titulos(df["titulo"].tolist())
    faixa_preco = calcular_faixa_preco(df, resumo["preco_medio"])
    oportunidade = detectar_oportunidade(resumo)
    score_info = calcular_score_oportunidade(resumo)
    resumo_exec = gerar_resumo_executivo(resumo, score_info)
    preco_info = calcular_preco_sugerido(df)
    faixa_ideal = calcular_faixa_ideal_mercado(df)

    df = classificar_concorrentes(df, resumo["preco_medio"])
    resumo_conc = resumo_concorrentes(df)

    insights_simples = gerar_insights(resumo_conc)
    insights_premium = gerar_insights_premium(
        resumo,
        score_info,
        faixa_ideal,
        preco_info,
        resumo_conc
    )

    decisao_final = gerar_decisao_final(
        resumo,
        score_info,
        preco_info,
        faixa_ideal
    )

    # =========================
    # 🔥 PRODUTOS DETALHADOS
    # =========================

    produtos_detalhados = []

    for _, row in df.iterrows():

        preco = float(row.get("preco", 0))
        titulo = row.get("titulo", "Produto")

        # SCORE SIMPLES
        if resumo["preco_medio"] > 0:
            diferenca = abs(preco - resumo["preco_medio"])
            score_produto = max(0, 100 - (diferenca * 2))
        else:
            score_produto = 0

        # OPORTUNIDADE
        if score_produto >= 70:
            oportunidade_produto = "Alta"
        elif score_produto >= 40:
            oportunidade_produto = "Média"
        else:
            oportunidade_produto = "Baixa"

        # 🔥 DECISÃO IA
        if score_produto >= 75:
            decisao_produto = {
                "status": "comprar",
                "mensagem": "Produto com alto potencial.",
                "cor": "positivo"
            }

        elif score_produto >= 45:
            decisao_produto = {
                "status": "cautela",
                "mensagem": "Produto com potencial moderado.",
                "cor": "neutro"
            }

        else:
            decisao_produto = {
                "status": "evitar",
                "mensagem": "Produto com baixa atratividade.",
                "cor": "alerta"
            }

        produtos_detalhados.append({
            "titulo": titulo,
            "preco": preco,
            "score": round(score_produto, 2),
            "concorrencia": row.get("tipo_concorrente", "Equilibrado"),
            "preco_sugerido": preco_info["preco_sugerido"],
            "faixa_ideal_min": faixa_ideal["faixa_ideal_min"],
            "faixa_ideal_max": faixa_ideal["faixa_ideal_max"],
            "oportunidade": oportunidade_produto,
            "palavras_chave": palavras[:5],
            "decisao": decisao_produto
        })

    return {
        "resumo": resumo,
        "palavras_chave": palavras,
        "faixa_preco": faixa_preco,
        "oportunidade": oportunidade,
        "score": score_info,
        "resumo_executivo": resumo_exec,
        "preco_sugerido": preco_info,
        "faixa_ideal": faixa_ideal,
        "concorrencia": resumo_conc,
        "insights": insights_simples,
        "insights_premium": insights_premium,
        "decisao_final": decisao_final,
        "produtos": produtos_detalhados
    }