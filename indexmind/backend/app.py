# indexmind/backend/app.py

from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from src.index_manager import IndexManager
from src.search_engine import SearchEngine

app = FastAPI()
index_manager = IndexManager()
search_engine = SearchEngine()

class IndexRequest(BaseModel):
    file_paths: List[str]

class SearchRequest(BaseModel):
    query: str
    n: int = 5
    filters: Optional[Dict[str, Any]] = None

@app.post("/index")
def index_documents(request: IndexRequest):
    index_manager.index(request.file_paths)
    return {"message": "Indexing completed"}

@app.post("/search")
def search(request: SearchRequest):
    return search_engine.search(request.query, request.n, request.filters)
