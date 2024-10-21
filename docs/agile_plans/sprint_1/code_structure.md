# Структура репозитория IndexMind

```(bash)
indexmind/
├── backend/                    # Папка с кодом бэкенда (Python)
│   ├── __init__.py             # Инициализация пакета
│   ├── app.py                  # Основной файл запуска бэкенда
│   ├── config.py               # Конфигурации приложения (например, параметры БД)
│   ├── indexers/               # Модуль индексации данных
│   │   ├── __init__.py         # Инициализация пакета индексов
│   │   ├── document_indexer.py  # Индексация текстовых документов 
│   │   └── image_indexer.py    # Индексация изображений (будет добавлено позже)
│   ├── search/                 # Модуль поиска по данным
│       └── search_engine.py    # Логика поиска с использованием FAISS + ClickHouse 
├───── utils/                   # Утилиты общего назначения (логирование, обработка ошибок)
|        |-- logger.py          # Логирование событий системы.
|        |-- helpers.py         # Вспомогательные функции.
|
├───── db/                      # Работа с базой данных ClickHouse 
|        |-- clickhouse_client.py  # Клиент для работы с ClickHouse.
|
├───── embeddings/              # Работа с эмбеддингами через Hugging Face модели  
|        |-- embedding_model_loader.py        
|├── frontend/                   # Фронтенд приложения (Mac App)
│   ├── mac_app/                # Проект Xcode для Mac-приложения на Swift/Cocoa
│   │   └─ IndexMindApp.xcodeproj  
│   │   └─ src/
│       └─ AppDelegate.swift    
│       └─ MainViewController.swift 
│       └─ SearchViewController.swift  
|
└──── tests/
    ├──── unit_tests            # Юнит-тесты для каждого модуля

scripts/
├──────── setup.sh                    
├──────── run_backend.sh               
|

docs/
├──────── agile_plans/           # Планы разработки (Agile)
|        |-- sprint_1/
|               |-- code_structure.md 
|               |-- sprint_1.md       
|               |-- core_plan.md      
|
├──────── usage_docs/            # Документация по использованию системы
|        |-- installation.md     # Инструкция по установке приложения.
|        |-- usage_examples.md      # Примеры использования.
|
.gitignore                            

requirements.txt                      

setup.cfg                             

Dockerfile                            
```
