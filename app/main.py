from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.rag.router import router as rag_router
from app.core.models import preload_models


@asynccontextmanager
async def lifespan(app: FastAPI):
    # start up
    preload_models()

    yield

    # shutdown


app = FastAPI(lifespan=lifespan)

app.include_router(rag_router, prefix='/v1/rag', tags=['RAG'])
