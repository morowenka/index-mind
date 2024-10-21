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
|
└──── tests/
    └──── unit_tests            # Юнит-тесты для каждого модуля

frontend_mac_app/
├── IndexMindApp.xcodeproj      # Проект Xcode для Mac-приложения на Swift/Cocoa
└─ src/
      └─ AppDelegate.swift       # Главный файл приложения macOS  
      └─ MainViewController.swift        
      └─ SearchViewController.swift    
                                   

scripts/
├──────── setup.sh                    
├──────── run_backend.sh               
|

docs/
├──────── agile_plans/
├──────── README.md                    
|

.gitignore                            

requirements.txt                      

setup.cfg                             

Dockerfile                            
```
