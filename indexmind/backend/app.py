# indexmind/backend/app.py

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from src.index_manager import IndexManager
from src.search_engine import SearchEngine
import traceback

app = FastAPI()
index_manager = IndexManager()
search_engine = SearchEngine()

class AddDocumentsRequest(BaseModel):
    file_paths: List[str] # not Paths !

class UpdateIndexesRequest(BaseModel):
    # You can add parameters if needed, e.g., specific files to update
    pass

class SearchRequest(BaseModel):
    query: str
    n: int = 5
    filters: Optional[Dict[List, Any]] = None

@app.post("/add_indexes")
def add_indexes(request: AddDocumentsRequest):
    try:
        index_manager.add_indexes(request.file_paths)
        return {"message": "Documents added to indexing queue"}
    except Exception as e:
        error_trace = traceback.format_exc()
        raise HTTPException(status_code=500, detail=error_trace) from e

@app.post("/update_indexes")
def update_indexes(request: UpdateIndexesRequest):
    try:
        index_manager.update_indexes()
        return {"message": "Indexing process completed"}
    except Exception as e:
        error_trace = traceback.format_exc()
        raise HTTPException(status_code=500, detail=error_trace) from e

@app.post("/search")
def search(request: SearchRequest):
    return search_engine.search(request.query, request.n, request.filters)
