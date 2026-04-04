from core.db import get_connection


def criar_coleta(empresa_id: int, usuario_id: int, termo_busca: str):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO coletas (empresa_id, usuario_id, termo_busca)
                VALUES (%s, %s, %s)
                RETURNING id, empresa_id, usuario_id, termo_busca, criado_em
            """, (empresa_id, usuario_id, termo_busca))
            coleta = cur.fetchone()
            conn.commit()
            return coleta


def listar_coletas_por_empresa(empresa_id: int):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, termo_busca, criado_em
                FROM coletas
                WHERE empresa_id = %s
                ORDER BY criado_em DESC
            """, (empresa_id,))
            return cur.fetchall()