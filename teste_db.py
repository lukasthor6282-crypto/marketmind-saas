from core.db import get_connection

try:
    conn = get_connection()
    print("Conectado com sucesso!")
    conn.close()
except Exception as e:
    print("Erro ao conectar:")
    print(e)