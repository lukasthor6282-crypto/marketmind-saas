from core.db import get_connection


# =============================
# 🔧 FUNÇÃO PARA CORRIGIR NUMPY
# =============================
def to_python(value):
    if value is None:
        return None

    try:
        return float(value)
    except:
        return value


# =============================
# 💾 SALVAR SNAPSHOT
# =============================
def salvar_snapshot_analise(
    empresa_id: int,
    coleta_id: int,
    usuario_id: int,
    termo_busca: str,
    resumo: dict,
    score_info: dict,
):
    with get_connection() as conn:
        with conn.cursor() as cur:

            cur.execute("""
                INSERT INTO analise_snapshots (
                    empresa_id,
                    coleta_id,
                    usuario_id,
                    termo_busca,
                    preco_medio,
                    preco_mediano,
                    menor_preco,
                    maior_preco,
                    quantidade_produtos,
                    score,
                    nivel_oportunidade,
                    nivel_concorrencia
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (
                empresa_id,
                coleta_id,
                usuario_id,
                termo_busca,

                to_python(resumo.get("preco_medio")),
                to_python(resumo.get("preco_mediano")),
                to_python(resumo.get("menor_preco")),
                to_python(resumo.get("maior_preco")),

                int(resumo.get("quantidade_produtos") or 0),
                int(score_info.get("score") or 0),

                str(score_info.get("nivel_oportunidade")),
                str(resumo.get("nivel_concorrencia")),
            ))

            snapshot = cur.fetchone()
            conn.commit()

            return snapshot


# =============================
# 🔍 BUSCAR ÚLTIMO SNAPSHOT
# =============================
def buscar_ultimo_snapshot_da_coleta(empresa_id: int, coleta_id: int):
    with get_connection() as conn:
        with conn.cursor() as cur:

            cur.execute("""
                SELECT *
                FROM analise_snapshots
                WHERE empresa_id = %s
                  AND coleta_id = %s
                ORDER BY criado_em DESC
                LIMIT 1
            """, (empresa_id, coleta_id))

            return cur.fetchone()


# =============================
# 🚨 CRIAR ALERTA
# =============================
def criar_alerta(
    empresa_id: int,
    coleta_id: int,
    tipo: str,
    titulo: str,
    mensagem: str,
    severidade: str = "info"
):
    with get_connection() as conn:
        with conn.cursor() as cur:

            cur.execute("""
                INSERT INTO alertas_mercado (
                    empresa_id,
                    coleta_id,
                    tipo,
                    titulo,
                    mensagem,
                    severidade
                )
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (
                empresa_id,
                coleta_id,
                tipo,
                titulo,
                mensagem,
                severidade
            ))

            alerta = cur.fetchone()
            conn.commit()

            return alerta


# =============================
# 📋 LISTAR ALERTAS
# =============================
def listar_alertas_por_empresa(empresa_id: int, limite: int = 10):
    with get_connection() as conn:
        with conn.cursor() as cur:

            cur.execute("""
                SELECT id, tipo, titulo, mensagem, severidade, criado_em
                FROM alertas_mercado
                WHERE empresa_id = %s
                ORDER BY criado_em DESC
                LIMIT %s
            """, (empresa_id, limite))

            return cur.fetchall()


# =============================
# 🤖 COMPARAR E GERAR ALERTAS
# =============================
def comparar_e_gerar_alertas(
    empresa_id: int,
    coleta_id: int,
    resumo_atual: dict,
    score_atual: dict
):
    ultimo = buscar_ultimo_snapshot_da_coleta(empresa_id, coleta_id)

    if not ultimo:
        return []

    alertas = []

    # =============================
    # 📉 PREÇO MÉDIO
    # =============================
    preco_antigo = float(ultimo["preco_medio"] or 0)
    preco_novo = float(resumo_atual.get("preco_medio") or 0)

    if preco_antigo > 0:
        variacao = ((preco_novo - preco_antigo) / preco_antigo) * 100

        if variacao <= -10:
            alertas.append(criar_alerta(
                empresa_id,
                coleta_id,
                "preco",
                "Queda forte no preço médio",
                f"O preço médio caiu {abs(round(variacao, 2))}%",
                "alerta"
            ))

        elif variacao >= 10:
            alertas.append(criar_alerta(
                empresa_id,
                coleta_id,
                "preco",
                "Alta forte no preço médio",
                f"O preço médio subiu {round(variacao, 2)}%",
                "positivo"
            ))

    # =============================
    # 📊 SCORE
    # =============================
    score_antigo = int(ultimo["score"] or 0)
    score_novo = int(score_atual.get("score") or 0)

    if score_novo - score_antigo >= 2:
        alertas.append(criar_alerta(
            empresa_id,
            coleta_id,
            "score",
            "Mercado melhorou",
            "O score de oportunidade aumentou",
            "positivo"
        ))

    elif score_antigo - score_novo >= 2:
        alertas.append(criar_alerta(
            empresa_id,
            coleta_id,
            "score",
            "Mercado piorou",
            "O score de oportunidade caiu",
            "alerta"
        ))

    # =============================
    # ⚔️ CONCORRÊNCIA
    # =============================
    conc_antiga = ultimo["nivel_concorrencia"]
    conc_nova = resumo_atual.get("nivel_concorrencia")

    if conc_antiga != conc_nova:
        alertas.append(criar_alerta(
            empresa_id,
            coleta_id,
            "concorrencia",
            "Mudança na concorrência",
            f"A concorrência mudou de {conc_antiga} para {conc_nova}",
            "info"
        ))

    return alertas