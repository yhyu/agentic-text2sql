import os
from typing import Any, List

import chromadb
from crewai_tools import BaseTool

from embedding import EmbeddingModel


class SemanticSearchTool(BaseTool):
    name: str ="Search database and table schemas tool"
    description: str = ("Useful to search database and table schemas from vector DB, "
                        "about a given question and return relevant database andtable schemas")
    client: Any = None
    collection: Any = None
    tokenizer: Any = None
    embedding_model: Any = None
    source: List[str] = []
    n_results: int = 10
    
    def __init__(self, n_results=10, **kwargs):
        super().__init__(**kwargs)
        db_path = kwargs.get('chroma_db_path', os.environ.get('CHROMA_STORAGE', 'chroma_db'))
        collection_name = kwargs.get('chroma_collection', os.environ.get('CHROMA_COLLECTION', 'spider-schemas'))
        self.client = chromadb.PersistentClient(path=db_path)
        self.collection = self.client.get_collection(
            collection_name,
            embedding_function=EmbeddingModel()
        )
        self.n_results = n_results

        data_path = os.environ.get('SCHEMA_PATH', 'table_schemas.jsonl')
        with open(data_path) as f:
            self.source = f.readlines()

    def _run(self, question: str) -> str:
        results = self.collection.query(
            query_texts=question,
            n_results=self.n_results,
        )
        return '\n'.join([self.source[int(id)] for id in results['ids'][0]])