# =========================
#  database.py  (ZAS-TRAC)
# =========================
import os
from urllib.parse import urlparse, urlunparse, parse_qsl, urlencode

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# --- БЛОК 1: ЧТЕНИЕ ПЕРЕМЕННЫХ ОКРУЖЕНИЯ ---
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./zastrac.db")
DB_SSLMODE = os.getenv("DB_SSLMODE", "require")
DB_POOL_SIZE = int(os.getenv("DB_POOL_SIZE", "5"))
DB_MAX_OVERFLOW = int(os.getenv("DB_MAX_OVERFLOW", "10"))
DB_POOL_RECYCLE = int(os.getenv("DB_POOL_RECYCLE", "1800"))  # 30 минут


def _ensure_psycopg_scheme(url: str) -> str:
    """Гарантируем драйвер psycopg v3 (совместимо с Windows и Supabase)."""
    if url.startswith("postgresql+psycopg://"):
        return url
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+psycopg://", 1)
    return url


def _with_sslmode(url: str, sslmode: str) -> str:
    """Добавляем sslmode к строке подключения Postgres."""
    if not (url.startswith("postgresql://") or url.startswith("postgresql+psycopg://")):
        return url
    p = urlparse(url)
    q = dict(parse_qsl(p.query))
    q.setdefault("sslmode", sslmode)
    return urlunparse(p._replace(query=urlencode(q)))


# --- БЛОК 2: ПРИВЕДЕНИЕ URL И СОЗДАНИЕ ENGINE ---
DATABASE_URL = _ensure_psycopg_scheme(DATABASE_URL)
DATABASE_URL = _with_sslmode(DATABASE_URL, DB_SSLMODE)

is_pg = DATABASE_URL.startswith("postgresql")

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    # Параметры пула только для Postgres (для SQLite не задаём)
    **({
        "pool_size": DB_POOL_SIZE,
        "max_overflow": DB_MAX_OVERFLOW,
        "pool_recycle": DB_POOL_RECYCLE,
    } if is_pg else {}),
    future=True,
)

# --- БЛОК 3: СЕССИЯ И БАЗА ---
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False, future=True)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
