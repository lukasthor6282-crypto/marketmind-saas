import time
import random
import re
import requests
from bs4 import BeautifulSoup

from services.coletas_service import criar_coleta
from services.produtos_service import salvar_produto, produto_existe


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept": (
        "text/html,application/xhtml+xml,application/xml;q=0.9,"
        "image/avif,image/webp,*/*;q=0.8"
    ),
}

SESSION = requests.Session()
SESSION.headers.update(HEADERS)


def formatar_busca(produto: str):
    return produto.lower().strip().replace(" ", "-")


def baixar_pagina(produto: str) -> str:
    busca = formatar_busca(produto)
    url = f"https://lista.mercadolivre.com.br/{busca}"

    time.sleep(random.uniform(0.8, 1.6))

    resposta = SESSION.get(url, timeout=20, allow_redirects=True)
    resposta.raise_for_status()
    return resposta.text


def extrair_texto(elemento):
    return elemento.get_text(strip=True) if elemento else ""


def converter_preco(texto_preco):
    if not texto_preco:
        return None

    texto_preco = texto_preco.replace(".", "").replace(",", "").strip()

    try:
        return float(texto_preco)
    except ValueError:
        return None


def extrair_item_id(link: str) -> str:
    if not link:
        return ""

    padroes = [
        r"(MLB\d+)",
        r"(MLA\d+)",
        r"(MLM\d+)",
        r"(MLU\d+)",
        r"(MCO\d+)",
        r"(MPE\d+)",
        r"(MEC\d+)",
        r"(MGT\d+)",
    ]

    for padrao in padroes:
        match = re.search(padrao, link)
        if match:
            return match.group(1)

    return link[:50]


def coletar_produtos(html):
    soup = BeautifulSoup(html, "html.parser")
    produtos = []

    seletores_cards = [
        ".ui-search-layout__item",
        ".ui-search-result",
        "li.ui-search-layout__item",
        ".poly-card",
    ]

    cards = []
    for seletor in seletores_cards:
        cards = soup.select(seletor)
        if cards:
            break

    if not cards:
        titulo = soup.title.get_text(strip=True) if soup.title else "Sem título"
        raise ValueError(f"Nenhum produto encontrado. Página: {titulo}")

    for card in cards:
        titulo = (
            extrair_texto(card.select_one(".poly-component__title")) or
            extrair_texto(card.select_one(".ui-search-item__title")) or
            extrair_texto(card.select_one("h2")) or
            extrair_texto(card.select_one("h3"))
        )

        preco_texto = (
            extrair_texto(card.select_one(".andes-money-amount__fraction")) or
            extrair_texto(card.select_one(".price-tag-fraction"))
        )

        preco = converter_preco(preco_texto)

        link_elemento = (
            card.select_one("a.poly-component__title") or
            card.select_one("a.ui-search-link") or
            card.select_one("a")
        )
        link = link_elemento.get("href") if link_elemento else ""

        if titulo and preco is not None:
            produtos.append({
                "titulo": titulo,
                "preco": preco,
                "link": link,
                "item_id": extrair_item_id(link)
            })

    produtos_unicos = []
    vistos = set()

    for produto in produtos:
        chave = (produto["titulo"], produto["preco"])
        if chave not in vistos:
            vistos.add(chave)
            produtos_unicos.append(produto)

    return produtos_unicos


def coletar_e_salvar(produto_busca: str, empresa_id: int, usuario_id: int):
    html = baixar_pagina(produto_busca)
    produtos = coletar_produtos(html)

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
                permalink=item["link"]
            )
            salvos += 1

    return {
        "coleta_id": coleta_id,
        "termo_busca": produto_busca,
        "total_encontrados": len(produtos),
        "novos_salvos": salvos
    }