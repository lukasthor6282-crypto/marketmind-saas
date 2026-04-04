from core.db import get_connection
import bcrypt


def verificar_senha(senha_digitada: str, senha_hash: str) -> bool:
    try:
        return bcrypt.checkpw(senha_digitada.encode(), senha_hash.encode())
    except Exception:
        return False


def autenticar_usuario(email: str, senha: str):
    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute(
            """
            SELECT id, nome, email, senha_hash, perfil, empresa_id
            FROM usuarios
            WHERE email = %s
            LIMIT 1
            """,
            (email,)
        )

        usuario = cur.fetchone()

        if not usuario:
            return None

        if not verificar_senha(senha, usuario["senha_hash"]):
            return None

        return {
            "id": usuario["id"],
            "nome": usuario["nome"],
            "email": usuario["email"],
            "perfil": usuario["perfil"],
            "empresa_id": usuario["empresa_id"],
        }

    finally:
        cur.close()
        conn.close()