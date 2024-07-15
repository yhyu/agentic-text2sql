import os
import sqlite3


def fetch_sqlite(db: str, sql: str) -> list:
    db_cache = os.environ.get('SPIDER_CACHE', 'spider')
    try:
        con = sqlite3.connect(f'{db_cache}/spider/database/{db}/{db}.sqlite')
        cursor = con.cursor()
        cursor.execute(sql)
        return cursor.fetchall()
    except Exception as e:
        print('fetch_sqlite exception:', e)
        return []
