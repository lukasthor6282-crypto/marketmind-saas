from core.db import get_connection
from core.security import verificar_senha


def autenticar_usuario(email: str, senha: str):
    query = """
        SELECT
            u.id,
            u.empresa_id,
            u.nome,
            u.email,
            u.senha_hash,
            u.perfil,
            u.ativo,
            e.nome AS empresa_nome
        FROM usuarios u
        JOIN empresas e ON e.id = u.empresa_id
        WHERE u.email = %s
        LIMIT 1
    """

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (email,))
            usuario = cur.fetchone()

    if not usuario:
        return None

    if not usuario["ativo"]:
        return None

    if not verificar_senha(senha, usuario["senha_hash"]):
        return None

    return {
        "id": usuario["id"],
        "empresa_id": usuario["empresa_id"],
        "nome": usuario["nome"],
        "email": usuario["email"],
        "perfil": usuario["perfil"],
        "empresa_nome": usuario["empresa_nome"]
    }