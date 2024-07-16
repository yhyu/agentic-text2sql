import json
import os
import sqlite3
import urllib
import zipfile
from pathlib import Path

import chromadb

from app.core.models.embedding import EmbeddingModel

def download_spider(download_path: str = 'spider') -> None:
    Path(download_path).mkdir(parents=True, exist_ok=True)
    down_url = 'https://drive.usercontent.google.com/download?id=1iRDVHLr4mX2wQKSgA9J8Pire73Jahh0m&export=download&authuser=0&confirm=t&uuid=c3bf75f4-055a-4d70-ba8f-c8cd3992f243&at=APZUnTVUgg2SMNCakypzoELhWIIc%3A1719561987956'
    download_file = os.path.join(download_path, 'spider.zip')
    urllib.request.urlretrieve(down_url, download_file)
    with zipfile.ZipFile(download_file) as zipf:
        zipf.extractall(download_path)


def collect_schemas(data_path: str = 'spider/spider') -> None:
    tables = []
    database_path = os.path.join(data_path, 'database')
    for db_name in os.listdir(database_path):
        con = sqlite3.connect(f'{database_path}/{db_name}/{db_name}.sqlite')
        cursor = con.cursor()
        cursor.execute("SELECT tbl_name, sql FROM sqlite_master WHERE type='table';")
        tbls = cursor.fetchall()
        cursor.close()
        con.close()
        for t in tbls:
            tables.append(
                {
                    'database': db_name,
                    'table': t[0],
                    'schema': t[1].replace('    ', '')
                }
            )

    with open('table_schemas.jsonl', 'w') as f:
        for tbl in tables:
            f.write(json.dumps(tbl))
            f.write('\n')


def create_chromadb(
        data_file: str = 'table_schemas.jsonl',
        db_path: str = 'chroma_db',
        collection_name: str = 'spider-schemas',
    ) -> None:
    tables = []
    with open(data_file) as f:
        tables = f.readlines()

    # import embeddings to chromadb
    client = chromadb.PersistentClient(path=db_path)
    collection = client.create_collection(
        collection_name,
        metadata={'hnsw:space': 'ip'},
        embedding_function=EmbeddingModel()
    )
    collection.add(
        ids=[str(i) for i in range(len(tables))], documents=tables)


if __name__ == "__main__":
    # download spider dataset
    print('download spider dataset...(it may take a few minutes.)')
    download_spider()

    # collect spider table schemas
    print('prepare spider data schemas for embedding...')
    collect_schemas()

    # create persistent chroma db
    print('import embeddings to chroma db...(it takes a few minutes.)')
    create_chromadb()

    print('prepare experiment environment done!')
