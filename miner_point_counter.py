import asyncpg
import asyncio
from datetime import datetime


DATABASE_URL = "postgresql://coin_farmer:1234@localhost:5432/coin_farmer"


class Database:
    def __init__(self):
        self._pool = None

    async def connect(self):
        self._pool = await asyncpg.create_pool(DATABASE_URL)

    async def disconnect(self):
        await self._pool.close()

    async def fetch(self, query: str, *args):
        async with self._pool.acquire() as connection:
            return await connection.fetch(query, *args)

    async def fetchrow(self, query: str, *args):
        async with self._pool.acquire() as connection:
            return await connection.fetchrow(query, *args)

    async def execute(self, query: str, *args):
        async with self._pool.acquire() as connection:
            return await connection.execute(query, *args)

database = Database()


async def get_user_data():
    await database.connect()

    user_for_upgrade = await database.fetch(
        """
        SELECT *
        FROM public.points
        WHERE rise_count < 3 AND next_rise < $1;
        """, datetime.now()
    )

    for record in user_for_upgrade:
        print(record)

    await database.disconnect()


if __name__ == "__main__":
    asyncio.run(get_user_data())