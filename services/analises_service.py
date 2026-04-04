from core.db import get_connection


def definir_empresa_sessao(cur, empresa_id: int):
    cur.execute(
        "SELECT set_config('app.empresa_id', %s, false)",
        (str(empresa_id),)
    )


def listar_analises_por_empresa(empresa_id: int):
    with get_connection() as conn:
        with conn.cursor() as cur:
            definir_empresa_sessao(cur, empresa_id)

            cur.execute("""
                SELECT id, titulo, resumo, score, criado_em
                FROM analises
                ORDER BY criado_em DESC
            """)
            return cur.fetchall()


def criar_analise(empresa_id: int, usuario_id: int, titulo: str, resumo: str, score: float):
    with get_connection() as conn:
        with conn.cursor() as cur:
            definir_empresa_sessao(cur, empresa_id)

            cur.execute("""
                INSERT INTO analises (empresa_id, usuario_id, titulo, resumo, score)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id
            """, (empresa_id, usuario_id, titulo, resumo, score))

            nova_analise = cur.fetchone()
            conn.commit()
            return nova_analise


def contar_analises_empresa(empresa_id: int):
    with get_connection() as conn:
        with conn.cursor() as cur:
            definir_empresa_sessao(cur, empresa_id)

            cur.execute("""
                SELECT COUNT(*) AS total
                FROM analises
            """)
            resultado = cur.fetchone()
            return resultado["total"]


def media_score_empresa(empresa_id: int):
    with get_connection() as conn:
        with conn.cursor() as cur:
            definir_empresa_sessao(cur, empresa_id)

            cur.execute("""
                SELECT COALESCE(AVG(score), 0) AS media_score
                FROM analises
            """)
            resultado = cur.fetchone()
            return float(resultado["media_score"] or 0)


def top_analises_empresa(empresa_id: int, limite: int = 5):
    with get_connection() as conn:
        with conn.cursor() as cur:
            definir_empresa_sessao(cur, empresa_id)

            cur.execute("""
                SELECT id, titulo, resumo, score, criado_em
                FROM analises
                ORDER BY score DESC NULLS LAST, criado_em DESC
                LIMIT %s
            """, (limite,))
            return cur.fetchall()