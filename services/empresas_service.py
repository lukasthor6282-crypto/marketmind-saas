from core.db import get_connection


def listar_empresas():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, nome, slug, ativo, criado_em
                FROM empresas
                ORDER BY nome
            """)
            return cur.fetchall()


def criar_empresa(nome: str, slug: str):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO empresas (nome, slug)
                VALUES (%s, %s)
                RETURNING id, nome, slug, ativo, criado_em
            """, (nome, slug))
            empresa = cur.fetchone()
            conn.commit()
            return empresa