import os
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "5432"))
DB_NAME = os.getenv("DB_NAME", "marketplace_saas")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")

APP_SECRET = os.getenv("APP_SECRET", "chave_padrao")
ML_BASE_URL = os.getenv("ML_BASE_URL", "https://api.mercadolibre.com")
ML_SITE_ID = os.getenv("ML_SITE_ID", "MLB")