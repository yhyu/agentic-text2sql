from typing import Any, Optional
from pydantic import BaseModel


class SQLQueryResult(BaseModel):
    database: str
    sql: str


class HealthCheckResponse(BaseModel):
    status: str


class QueryRequest(BaseModel):
    request_id: str
    query: str
    session_id: Optional[str] = ''


class QueryResponse(BaseModel):
    request_id: str
    response_id: str
    results: SQLQueryResult
    session_id: str