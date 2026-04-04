import requests
from core.config import ML_BASE_URL, ML_SITE_ID


def buscar_itens_por_vendedor(access_token: str, seller_id: str):
    url = f"{ML_BASE_URL}/sites/{ML_SITE_ID}/search"

    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    params = {
        "seller_id": seller_id
    }

    response = requests.get(url, headers=headers, params=params, timeout=30)
    response.raise_for_status()
    return response.json()