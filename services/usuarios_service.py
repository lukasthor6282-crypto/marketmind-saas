from core.db import get_connection
from core.security import gerar_hash_senha


def listar_usuarios():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    u.id,
                    u.nome,
                    u.email,
                    u.perfil,
                    u.ativo,
                    u.criado_em,
                    e.nome AS empresa_nome,
                    e.id AS empresa_id
                FROM usuarios u
                JOIN empresas e ON e.id = u.empresa_id
                ORDER BY u.nome
            """)
            return cur.fetchall()


def criar_usuario(empresa_id: int, nome: str, email: str, senha: str, perfil: str = "operador"):
    senha_hash = gerar_hash_senha(senha)

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO usuarios (empresa_id, nome, email, senha_hash, perfil)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id, empresa_id, nome, email, perfil, ativo, criado_em
            """, (empresa_id, nome, email, senha_hash, perfil))
            usuario = cur.fetchone()
            conn.commit()
            return usuario