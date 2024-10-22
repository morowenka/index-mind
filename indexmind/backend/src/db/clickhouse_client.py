from clickhouse_driver import Client as CHClient
import uuid

from config import settings
from utils.logger import logger



class ClickhouseClient:
    def __init__(
        self,
        host: str,
        port: int
    ):
        self.client = CHClient(host=host, port=port)

    def create_database(
        self,
        db_name: str
    ):
        """Создает базу данных IndexMind"""
        self.db_name = db_name
        query = f"CREATE DATABASE IF NOT EXISTS {db_name}"
        self.client.execute(query)

    def create_document_table(
        self,
        table_name: str
    ):
        """Создает таблицу в базе данных"""
        query = f"""
            CREATE TABLE IF NOT EXISTS {self.db_name}.{table_name} (
                id UUID,
                file_hash String,
                file_path String,
                start_idx UInt32,
                end_idx UInt32,
                PRIMARY KEY id
            ) ENGINE = MergeTree()
            """
        self.client.execute(query)

    def insert_document_block_metadata(
        self, 
        file_hash: str,
        file_path: str,
        start_idx: int,
        end_idx: int,
        table_name: str = settings.CLICKHOUSE_DOCUMENTS_TABLE,
    ) -> str:
        
        block_id = str(uuid.uuid4())
        query = f"INSERT INTO {self.db_name}.{table_name} VALUES"
        data_tuple = (block_id, file_hash.strip(), file_path.strip(), start_idx, end_idx)
        
        try:
            self.client.execute(f"{query} (?, ?, ?, ?, ?)", [data_tuple])
            return block_id
        except Exception as e:
            logger.error(f"Error inserting metadata into database {e}")
            return None


if __name__ == "__main__":
    setup_client = ClickhouseClient(settings.CLICKHOUSE_HOST, settings.CLICKHOUSE_PORT)
    setup_client.create_database(settings.CLICKHOUSE_DB)
    setup_client.create_document_table(settings.CLICKHOUSE_DOCUMENTS_TABLE)
