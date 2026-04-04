import os
import psycopg2
from psycopg2.extras import RealDictCursor
import streamlit as st
from dotenv import load_dotenv

load_dotenv()


def get_secret(name, default=None):
    try:
        if name in st.secrets:
            return st.secrets[name]
    except Exception:
        pass

    return os.getenv(name, default)


def get_connection():
    database_url = get_secret("DATABASE_URL")

    if database_url:
        return psycopg2.connect(
            database_url,
            cursor_factory=RealDictCursor
        )

    return psycopg2.connect(
        host=get_secret("DB_HOST"),
        port=get_secret("DB_PORT", "5432"),
        dbname=get_secret("DB_NAME"),
        user=get_secret("DB_USER"),
        password=get_secret("DB_PASSWORD"),
        cursor_factory=RealDictCursor,
        sslmode="require"
    )