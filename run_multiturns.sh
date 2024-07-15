pwd=`pwd`
export CHROMA_STORAGE=$(pwd)/chroma_db
export SCHEMA_PATH=$(pwd)/table_schemas.jsonl
export SPIDER_CACHE=$(pwd)/spider
gunicorn app.main:app -w 1 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
