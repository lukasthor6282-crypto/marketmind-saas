import time
import random
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote

from services.coletas_service import criar_coleta
from services.produtos_service import salvar_produto, produto_existe


HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/122.0.0.0 Safari/537.36",
    "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Connection": "keep-alive"
}

SESSION = requests.Session()
SESSION.headers.update(HEADERS)


def formatar_busca(produto: str):
    return quote(produto.strip())


def baixar_pagina(produto: str) -> str:
    busca = formatar_busca(produto)
    url = f"https://lista.mercadolivre.com.br/{busca}"

    print("🔎 URL:", url)

    time.sleep(random.uniform(1.0, 2.0))

    response = SESSION.get(url, timeout=30)

    print("📡 STATUS:", response.status_code)

    if response.status_code != 200:
        raise Exception("Erro ao acessar Mercado Livre")

    html = response.text

    if "captcha" in html.lower():
        raise Exception("🚫 Mercado Livre bloqueou (captcha)")

    return html


def extrair_texto(el):
    return el.get_text(strip=True) if el else ""


def converter_preco(texto):
    if not texto:
        return None
    texto = texto.replace(".", "").replace(",", "")
    try:
        return float(texto)
    except:
        return None


def extrair_item_id(link):
    if not link:
        return ""

    match = re.search(r"(MLB\d+)", link)
    return match.group(1) if match else link[:50]


def coletar_produtos(html):
    soup = BeautifulSoup(html, "html.parser")

    seletores = [
        ".ui-search-layout__item",
        ".ui-search-result",
        ".poly-card",
        "li.ui-search-layout__item"
    ]

    cards = []

    for s in seletores:
        cards = soup.select(s)
        if cards:
            print(f"✅ Seletor funcionando: {s}")
            break

    print("📦 Total de cards:", len(cards))

    if not cards:
        print(html[:1000])  # DEBUG
        raise Exception("Nenhum produto encontrado")

    produtos = []

    for card in cards:
        titulo = (
            extrair_texto(card.select_one(".poly-component__title")) or
            extrair_texto(card.select_one(".ui-search-item__title")) or
            extrair_texto(card.select_one("h2"))
        )

        preco_texto = (
            extrair_texto(card.select_one(".andes-money-amount__fraction")) or
            extrair_texto(card.select_one(".price-tag-fraction"))
        )

        preco = converter_preco(preco_texto)

        link_el = card.select_one("a")
        link = link_el.get("href") if link_el else ""

        if titulo and preco:
            produtos.append({
                "titulo": titulo,
                "preco": preco,
                "link": link,
                "item_id": extrair_item_id(link)
            })

    return produtos


def coletar_e_salvar(produto_busca, empresa_id, usuario_id):
    html = baixar_pagina(produto_busca)
    produtos = coletar_produtos(html)

    coleta = criar_coleta(empresa_id, usuario_id, produto_busca)
    coleta_id = coleta["id"]

    salvos = 0

    for item in produtos:
        if not produto_existe(empresa_id, coleta_id, item["item_id"]):
            salvar_produto(
                empresa_id,
                coleta_id,
                "Mercado Livre",
                item["item_id"],
                item["titulo"],
                item["preco"],
                "active",
                item["link"]
            )
            salvos += 1

    return {
        "total": len(produtos),
        "salvos": salvos
    }