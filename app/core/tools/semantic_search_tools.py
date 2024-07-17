import os
from typing import Any, List

import chromadb
from pydantic import BaseModel

from app.core.configs.config import settings
from app.core.models.embedding import EmbeddingModel


class SemanticSearchTool(BaseModel):
    client: Any = None
    collection: Any = None
    tokenizer: Any = None
    embedding_model: Any = None
    source: List[str] = []
    n_results: int = 10
    
    def __init__(self, n_results=10, **kwargs):
        super().__init__(**kwargs)
        db_path = kwargs.get('chroma_db_path', settings.CHROMA_STORAGE)
        collection_name = kwargs.get('chroma_collection', settings.CHROMA_COLLECTION)
        self.client = chromadb.PersistentClient(path=db_path)
        self.collection = self.client.get_collection(
            collection_name,
            embedding_function=EmbeddingModel()
        )
        self.n_results = n_results

        data_path = kwargs.get('schema_path', settings.SCHEMA_PATH)
        with open(data_path) as f:
            self.source = f.readlines()

    def __call__(self, question: str) -> str:
        results = self.collection.query(
            query_texts=question,
            n_results=self.n_results,
        )
        return '\n'.join([self.source[int(id)] for id in results['ids'][0]])
