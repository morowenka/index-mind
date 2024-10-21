from clickhouse_driver import Client as CHClient


class ClickhouseClient:
    def __init__(self, host: str, port: int):
        self.client = CHClient(host=host, port=port)

    def create_database(self, db_name):
        query = f"CREATE DATABASE IF NOT EXISTS {db_name}"
        self.client.execute(query)

    def create_table(self):
        query = """
            CREATE TABLE IF NOT EXISTS documents (
                id UUID,
                content String,
                embedding Array(Float32),
                metadata JSON,
                PRIMARY KEY id) ENGINE MergeTree()
            """
        self.client.execute(query)

    def insert_document(self, doc_id: str, content: str, embedding: list[float], metadata: dict):
        query = "INSERT INTO documents VALUES"
        data_tuple = (doc_id, content.strip(), embedding.tolist(), metadata)

        self.client.execute(f"{query}(?, ?, ?, ?)", [data_tuple])


if __name__ == "__main__":
    from config import CLICKHOUSE_HOST, CLICKHOUSE_PORT, CLICKHOUSE_DB
    
    client_db = ClickhouseClient(host=CLICKHOUSE_HOST, port=CLICKHOUSE_PORT)
    
    client_db.create_database(CLICKHOUSE_DB)
    client_db.create_table()