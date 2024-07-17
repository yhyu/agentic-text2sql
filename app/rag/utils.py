import os
import sqlite3

from app.core.configs.config import settings


def fetch_sqlite(db: str, sql: str) -> list:
    db_cache = settings.SPIDER_CACHE
    try:
        con = sqlite3.connect(f'{db_cache}/spider/database/{db}/{db}.sqlite')
        cursor = con.cursor()
        cursor.execute(sql)
        return cursor.fetchall()
    except Exception as e:
        print('fetch_sqlite exception:', e)
        return []
