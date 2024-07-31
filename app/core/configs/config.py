import logging

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # LLM
    OPENAI_MODEL_NAME: str = 'gpt-4o-mini'

    # chromadb
    CHROMA_STORAGE: str = 'chroma_db'
    CHROMA_COLLECTION: str = 'spider-schemas'

    # spider
    SPIDER_CACHE: str = 'spider'
    SCHEMA_PATH: str = 'table_schemas.jsonl'

    # embedding model
    EMBEDDING_MODEL: str = 'Alibaba-NLP/gte-large-en-v1.5'

    # log level
    log_level: str = 'INFO'


# load settings
settings = Settings()

# logging
logger = logging.getLogger("gunicorn.error")
logger.setLevel(settings.log_level)
