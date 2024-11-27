import pytest
from httpx import AsyncClient
from app import app
from src.utils.logger import logger
import time

base_url="http://127.0.0.1"

'''
curl -X POST "http://127.0.0.1:8000/add_indexes" -H "Content-Type: application/json" -d '{"file_paths": ["/Users/m.basov/Desktop/AITalentHub/index-mind/data/", "/Users/m.basov/Desktop/AITalentHub/index-mind/data/вкр марата.txt"]}'
curl -X POST "http://127.0.0.1:8000/update_indexes" -H "Content-Type: application/json" -d {}
'''

@pytest.mark.asyncio
async def test_add_one_file_for_index():
    async with AsyncClient(app=app) as client:
        response = await client.post(
            "/add_indexes",
            json={"file_paths": ["/Users/m.basov/Desktop/AITalentHub/index-mind/data/вкр марата.txt"]}
        )
        assert response.status_code == 200
        assert response.json() == {"message": "Индексация начата"}
        
@pytest.mark.asyncio
async def test_add_one_folder_for_index():
    async with AsyncClient(app=app) as client:
        response = await client.post(
            "/add_indexes",
            json={"file_paths": ["/Users/m.basov/Desktop/AITalentHub/index-mind/data/"]}
        )
        assert response.status_code == 200
        assert response.json() == {"message": "Индексация начата"}
        
@pytest.mark.asyncio
async def test_add_folder_and_file_for_index():
    async with AsyncClient(app=app) as client:
        response = await client.post(
            "/add_indexes",
            json={"file_paths": [
                "/Users/m.basov/Desktop/AITalentHub/index-mind/data/",
                "/Users/m.basov/Desktop/AITalentHub/index-mind/data/вкр марата.txt"
            ]}
        )
        assert response.status_code == 200
        assert response.json() == {"message": "Индексация начата"}


@pytest.mark.asyncio
async def test_update_indexes():
    async with AsyncClient(app=app) as client:
        response = await client.post("/update_indexes", json={})
        assert response.status_code == 200
        assert response.json() == {"message": "Обновление индексов начато"}
        
        # response = await client.post("/update_indexes", json={})
        # assert response.status_code == 200
        # assert response.json() == {"message": "Обновление индексов начато"}

@pytest.mark.asyncio
async def test_set_llm_model():
    async with AsyncClient(app=app) as client:
        # response = await client.post("/set_llm_model", json={"model_type": "openai"})
        # assert response.status_code == 200
        # assert response.json() == {"message": "Тип LLM модели установлен на 'openai'"}

        response = await client.post("/set_llm_model", json={"model_type": "huggingface"})
        assert response.status_code == 200
        assert response.json() == {"message": "Тип LLM модели установлен на 'huggingface'"}

        response = await client.post("/set_llm_model", json={"model_type": "unsupported"})
        assert response.status_code == 422

@pytest.mark.asyncio
async def test_search():
    async with AsyncClient(app=app) as client:
        response = await client.post(
            "/search",
            json={
                "query": "пример запроса",
                "n": 5,
                "filters": None
            }
        )
        assert response.status_code == 200
        assert "response" in response.json()
        assert "retrieved_documents" in response.json()
        
        # logger.debug(f"response: {response.json()}")

@pytest.mark.asyncio
async def test_search_with_filters_noone_document():
    async with AsyncClient(app=app) as client:
        response = await client.post(
            "/search",
            json={
                "query": "пример запроса",
                "n": 5,
                "filters": {
                    "operator": "AND",
                    "conditions": [
                        {"field": "meta.status", "operator": "==", "value": "ready"},
                        {
                            "operator": "AND",
                            "conditions": [
                                {"field": "meta.creation_time", "operator": ">", "value": time.mktime(time.strptime("2001-10-27 18:33:52", "%Y-%m-%d %H:%M:%S"))},
                                {"field": "meta.creation_time", "operator": "<", "value": time.mktime(time.strptime("2001-11-27 18:33:54", "%Y-%m-%d %H:%M:%S"))},
                            ]
                        }
                    ]
                }
            }
        )
        assert response.status_code == 200
        assert "response" in response.json()
        assert "retrieved_documents" in response.json()
        
        # logger.debug(f"response: {response.json()}")
