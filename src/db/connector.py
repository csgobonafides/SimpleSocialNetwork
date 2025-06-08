
import asyncpg

class DataBaseConnector:
    def __init__(self, db_url: str, max_connections: int = 10):
        self.db_url = db_url
        self.pool = None
        self.max_connections = max_connections

    async def connect(self):
        self.pool = await asyncpg.create_pool(
            self.db_url,
            max_size=self.max_connections
        )

    async def disconnect(self):
        await self.pool.close()

    async def fetch(self, query: str, *args):
        async with self.pool.acquire() as connection:
            return await connection.fetch(query, *args)

    async def execute(self, query: str, *args):
        async with self.pool.acquire() as connection:
            return await connection.execute(query, *args)

    async def create_account_table(self):
        await self.execute("""
        CREATE TABLE IF NOT EXISTS accounts (
        id SERIAL PRIMARY KEY,
        login VARCHAR(50) NOT NULL UNIQUE,
        password VARCHAR(50) NOT NULL
        );
        """)

    async def create_social_table(self):
        await self.execute("""
        CREATE TABLE IF NOT EXISTS social (
        id INT PRIMARY KEY,
        first_name VARCHAR(50) NOT NULL,
        last_name VARCHAR(50) NOT NULL,
        data_of_birth DATE NOT NULL,
        gender VARCHAR(20) NOT NULL,
        interests VARCHAR(100) NOT NULL,
        city VARCHAR(50) NOT NULL,
        FOREIGN KEY(id) REFERENCES accounts(id) ON DELETE CASCADE
        );""")
