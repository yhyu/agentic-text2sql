
from uuid import uuid4 as guid

from fastapi import APIRouter, BackgroundTasks, Header

from app.core.pipeline.graph import Graph
from app.rag.models import (
    HealthCheckResponse,
    QueryRequest, QueryResponse,
    SQLQueryResult,
)
from app.rag.utils import fetch_sqlite

router = APIRouter()


@router.get('/health', response_model=HealthCheckResponse)
async def health_check():
    return {
        'status': 'OK'
    }


@router.post('/query', response_model=QueryResponse)
async def query(
    request: QueryRequest,
    background_tasks: BackgroundTasks,
):
    g = Graph()
    ret = g(request.query, thread_id=request.session_id)
    db = ret['state']['database'][-1]
    sql = ret['state']['sql'][-1]
    response = QueryResponse(
        request_id=request.request_id,
        response_id=str(guid().hex),
        results=SQLQueryResult(
            database=db,
            sql=sql,
            value=fetch_sqlite(db, sql)
        ),
        session_id=ret['thread_id']
    )
    return response
