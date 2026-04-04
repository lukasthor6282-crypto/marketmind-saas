import json
from core.db import get_connection


def salvar_analise_mercado(
    empresa_id,
    usuario_id,
    resumo,
    palavras_chave,
    score,
    insights,
    preco_sugerido,
    faixa_ideal
):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO analises_mercado
        (empresa_id, usuario_id, resumo, palavras_chave, score, insights, preco_sugerido, faixa_ideal)
        VALUES (%s, %s, %s::jsonb, %s::jsonb, %s::jsonb, %s::jsonb, %s::jsonb, %s::jsonb)
    """, (
        empresa_id,
        usuario_id,
        json.dumps(resumo, ensure_ascii=False),
        json.dumps(palavras_chave, ensure_ascii=False),
        json.dumps(score, ensure_ascii=False),
        json.dumps(insights, ensure_ascii=False),
        json.dumps(preco_sugerido, ensure_ascii=False),
        json.dumps(faixa_ideal, ensure_ascii=False)
    ))

    conn.commit()
    cur.close()
    conn.close()


def listar_analises_mercado(empresa_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT *
        FROM analises_mercado
        WHERE empresa_id = %s
        ORDER BY criado_em DESC
    """, (empresa_id,))

    dados = cur.fetchall()

    cur.close()
    conn.close()

    return dados