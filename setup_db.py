from core.db import get_connection

with open("sql/001_schema.sql", "r", encoding="utf-8") as f:
    sql = f.read()

with get_connection() as conn:
    with conn.cursor() as cur:
        cur.execute(sql)
        conn.commit()

print("Banco criado com sucesso!")