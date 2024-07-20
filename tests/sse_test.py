import aiohttp
import asyncio

async def sse_client(session, url):
    async with session.get(url) as response:
        async for line in response.content:
            print(f"Received: {line.decode('utf-8').strip()}")

async def main():
    url = 'http://localhost:8000/points/sse'
    async with aiohttp.ClientSession() as session:
        tasks = [sse_client(session, url) for _ in range(10)]  # Simulate 10 clients
        await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
