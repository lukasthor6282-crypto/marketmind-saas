import time
import random
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote
import os
import streamlit as st

from services.coletas_service import criar_coleta
from services.produtos_service import salvar_produto, produto_existe


ML_SEARCH_URL = "https://api.mercadolibre.com/sites/MLB/search"

HEADERS_HTML = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Connection": "keep-alive",
}

HEADERS_API = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json",
    "Content-Type": "application/json",
}

SESSION = requests.Session()
SESSION.headers.update(HEADERS_HTML)


def get_secret(name: str, default=None):
    try:
        if name in st.secrets:
            return st.secrets[name]
    except Exception:
        pass
    return os.getenv(name, default)


def formatar_busca(produto: str) -> str:
    return produto.strip()


def extrair_item_id(item_id: str = "", link: str = "") -> str:
    if item_id:
        return item_id

    if link:
        match = re.search(r"(MLB\d+)", link)
        if match:
            return match.group(1)

    return ""


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


def buscar_produtos_api(produto: str) -> list[dict]:
    params = {
        "q": formatar_busca(produto),
        "limit": 30,
    }

    headers = HEADERS_API.copy()
    access_token = get_secret("ML_ACCESS_TOKEN")

    if access_token:
        headers["Authorization"] = f"Bearer {access_token}"

    response = requests.get(
        ML_SEARCH_URL,
        headers=headers,
        params=params,
        timeout=30,
    )

    if response.status_code == 403:
        raise PermissionError("API do Mercado Livre respondeu 403 Forbidden")

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
        raise ValueError("Nenhum produto encontrado na API")

    return produtos


def baixar_pagina_html(produto: str) -> str:
    busca = quote(produto.strip())
    url = f"https://lista.mercadolivre.com.br/{busca}"

    time.sleep(random.uniform(1.0, 2.0))

    response = SESSION.get(url, timeout=30, allow_redirects=True)
    response.raise_for_status()

    html = response.text
    if "captcha" in html.lower():
        raise Exception("Mercado Livre bloqueou a página com captcha")

    return html


def coletar_produtos_html(html: str) -> list[dict]:
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
                "item_id": extrair_item_id("", link)
            })

    produtos_unicos = []
    vistos = set()

    for produto in produtos:
        chave = (produto["titulo"], produto["preco"])
        if chave not in vistos:
            vistos.add(chave)
            produtos_unicos.append(produto)

    return produtos_unicos


def buscar_produtos(produto_busca: str) -> list[dict]:
    try:
        return buscar_produtos_api(produto_busca)
    except PermissionError:
        html = baixar_pagina_html(produto_busca)
        return coletar_produtos_html(html)


def coletar_e_salvar(produto_busca: str, empresa_id: int, usuario_id: int):
    produtos = buscar_produtos(produto_busca)

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