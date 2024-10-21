from pydantic import BaseSettings


class DatabaseConfig(BaseSettings):
    CLICKHOUSE_HOST: str = "localhost"
    CLICKHOUSE_PORT: int = 9000
    CLICKHOUSE_DB: str = "indexmind"
    
    class Config:
        env_prefix = 'DB_'
