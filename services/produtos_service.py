from core.db import get_connection


def definir_empresa_sessao(cur, empresa_id: int):
    cur.execute(
        "SELECT set_config('app.empresa_id', %s, false)",
        (str(empresa_id),)
    )


def listar_produtos_por_empresa(empresa_id: int):
    with get_connection() as conn:
        with conn.cursor() as cur:
            definir_empresa_sessao(cur, empresa_id)

            cur.execute("""
                SELECT id, coleta_id, marketplace, item_id, titulo, preco, status, permalink, criado_em
                FROM produtos
                ORDER BY criado_em DESC
            """)
            return cur.fetchall()


def listar_produtos_df_por_empresa(empresa_id: int):
    with get_connection() as conn:
        with conn.cursor() as cur:
            definir_empresa_sessao(cur, empresa_id)

            cur.execute("""
                SELECT id, coleta_id, marketplace, item_id, titulo, preco, status, permalink, criado_em
                FROM produtos
                ORDER BY criado_em DESC
            """)
            return cur.fetchall()


def listar_produtos_por_coleta(empresa_id: int, coleta_id: int):
    with get_connection() as conn:
        with conn.cursor() as cur:
            definir_empresa_sessao(cur, empresa_id)

            cur.execute("""
                SELECT id, coleta_id, marketplace, item_id, titulo, preco, status, permalink, criado_em
                FROM produtos
                WHERE coleta_id = %s
                ORDER BY criado_em DESC
            """, (coleta_id,))
            return cur.fetchall()


def salvar_produto(
    empresa_id: int,
    coleta_id: int,
    marketplace: str,
    item_id: str,
    titulo: str,
    preco: float,
    status: str,
    permalink: str
):
    with get_connection() as conn:
        with conn.cursor() as cur:
            definir_empresa_sessao(cur, empresa_id)

            cur.execute("""
                INSERT INTO produtos (
                    empresa_id, coleta_id, marketplace, item_id, titulo, preco, status, permalink
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (
                empresa_id,
                coleta_id,
                marketplace,
                item_id,
                titulo,
                preco,
                status,
                permalink
            ))

            produto = cur.fetchone()
            conn.commit()
            return produto


def produto_existe(empresa_id: int, coleta_id: int, item_id: str):
    with get_connection() as conn:
        with conn.cursor() as cur:
            definir_empresa_sessao(cur, empresa_id)

            cur.execute("""
                SELECT id
                FROM produtos
                WHERE coleta_id = %s AND item_id = %s
                LIMIT 1
            """, (coleta_id, item_id))
            return cur.fetchone() is not None


def resumo_produtos_empresa(empresa_id: int):
    with get_connection() as conn:
        with conn.cursor() as cur:
            definir_empresa_sessao(cur, empresa_id)

            cur.execute("""
                SELECT
                    COUNT(*) AS total_produtos,
                    COUNT(*) FILTER (WHERE status = 'active') AS ativos,
                    AVG(preco) AS preco_medio,
                    SUM(preco) AS valor_total
                FROM produtos
            """)
            return cur.fetchone()


def top_produtos_mais_caros(empresa_id: int, limite: int = 5):
    with get_connection() as conn:
        with conn.cursor() as cur:
            definir_empresa_sessao(cur, empresa_id)

            cur.execute("""
                SELECT titulo, preco, status
                FROM produtos
                ORDER BY preco DESC NULLS LAST
                LIMIT %s
            """, (limite,))
            return cur.fetchall()


def classificar_produto(preco: float, status: str):
    if preco is None:
        return "sem dados"

    if status != "active":
        return "inativo"

    if preco < 50:
        return "baixo valor"

    if 50 <= preco <= 200:
        return "bom"

    if preco > 200:
        return "alto valor"

    return "indefinido"