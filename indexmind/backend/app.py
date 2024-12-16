# indexmind/backend/app.py

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional, Dict, Any, Literal
from src.managers.index_manager import IndexManager
from src.managers.search_engine import SearchEngine
from src.managers.websocket_manager import WebSocketManager
from src.utils.logger import logger
from src.managers.llm_manager import llm_manager

app = FastAPI()
index_manager = IndexManager()
search_engine = SearchEngine()
manager = WebSocketManager()

class AddDocumentsRequest(BaseModel):
    file_paths: List[str]

class UpdateIndexesRequest(BaseModel):
    pass

class SearchRequest(BaseModel):
    query: str
    n: int = 5
    filters: Optional[Dict[str, Any]] = None

class SetLLMModelRequest(BaseModel):
    model_type: Literal['openai', 'huggingface', 'gigachat']


@app.websocket("/ws/progress")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.post("/add_indexes")
async def add_indexes(request: AddDocumentsRequest, background_tasks: BackgroundTasks):
    background_tasks.add_task(index_manager.add_indexes_async, request.file_paths, manager)
    return {"message": "Индексация начата"}

@app.post("/update_indexes")
async def update_indexes(request: UpdateIndexesRequest, background_tasks: BackgroundTasks):
    background_tasks.add_task(index_manager.update_indexes_async, manager)
    return {"message": "Обновление индексов начато"}

@app.post("/set_llm_model")
def set_llm_model(request: SetLLMModelRequest):
    try:
        llm_manager.set_model_type(request.model_type)
        return {"message": f"Тип LLM модели установлен на '{request.model_type}'"}
    except Exception as e:
        logger.error(f"Ошибка при установке типа LLM модели: {e}")
        raise HTTPException(status_code=400, detail=str(e)) from e

@app.post("/search")
def search(request: SearchRequest):
    response, retrieved_documents = search_engine.search(request.query, request.n, request.filters)
    return {
        "response": response,
        "retrieved_documents": retrieved_documents
    }

@app.delete("/delete_all_documents")
def delete_all_documents():
    try:
        return index_manager.indexers['document'].delete_all_documents()
    except Exception as e:
        logger.error(f"Ошибка при удалении всех документов: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e

@app.get("/health")
def health_check():
    return {"status": "healthy"}
