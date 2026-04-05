import re
import requests
from urllib.parse import quote

from services.coletas_service import criar_coleta
from services.produtos_service import salvar_produto, produto_existe


ML_SEARCH_URL = "https://api.mercadolibre.com/sites/MLB/search"

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json",
    "Content-Type": "application/json",
}


def formatar_busca(produto: str) -> str:
    return produto.strip()


def extrair_item_id(item_id: str, link: str = "") -> str:
    if item_id:
        return item_id

    if link:
        match = re.search(r"(MLB\d+)", link)
        if match:
            return match.group(1)

    return ""


def buscar_produtos_api(produto: str) -> list[dict]:
    termo = formatar_busca(produto)

    params = {
        "q": termo,
        "limit": 30,
    }

    response = requests.get(
        ML_SEARCH_URL,
        headers=HEADERS,
        params=params,
        timeout=30,
    )
    response.raise_for_status()

    data = response.json()
    resultados = data.get("results", [])

    produtos = []

    for item in resultados:
        titulo = item.get("title", "").strip()
        preco = item.get("price")
        link = item.get("permalink", "")
        item_id = extrair_item_id(item.get("id", ""), link)

        if titulo and preco is not None:
            produtos.append(
                {
                    "titulo": titulo,
                    "preco": float(preco),
                    "link": link,
                    "item_id": item_id,
                }
            )

    if not produtos:
        raise ValueError("Nenhum produto encontrado")

    return produtos


def coletar_e_salvar(produto_busca: str, empresa_id: int, usuario_id: int):
    produtos = buscar_produtos_api(produto_busca)

    coleta = criar_coleta(empresa_id, usuario_id, produto_busca)
    coleta_id = coleta["id"]

    salvos = 0

    for item in produtos:
        item_id = item["item_id"]

        if item_id and not produto_existe(empresa_id, coleta_id, item_id):
            salvar_produto(
                empresa_id=empresa_id,
                coleta_id=coleta_id,
                marketplace="Mercado Livre",
                item_id=item_id,
                titulo=item["titulo"],
                preco=item["preco"],
                status="active",
                permalink=item["link"],
            )
            salvos += 1

    return {
        "coleta_id": coleta_id,
        "termo_busca": produto_busca,
        "total_encontrados": len(produtos),
        "novos_salvos": salvos,
    }