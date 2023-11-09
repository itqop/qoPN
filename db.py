import asyncpg
import asyncio

class Database:
    def __init__(self, dsn):
        self.dsn = dsn

    async def execute_query(self, query, *args):
        try:
            conn = await asyncpg.connect(self.dsn)
            result = await conn.execute(query, *args)
            await conn.close()
            return result
        except Exception as e:
            print(f"Error executing query: {e}")

    async def fetch_data(self, query, *args):
        try:
            conn = await asyncpg.connect(self.dsn)
            result = await conn.fetch(query, *args)
            await conn.close()
            return result
        except Exception as e:
            print(f"Error fetching data: {e}")

    async def insert_data(self, query, *args):
        await self.execute_query(query, *args)

    async def update_data(self, query, *args):
        await self.execute_query(query, *args)

    async def delete_data(self, query, *args):
        await self.execute_query(query, *args)