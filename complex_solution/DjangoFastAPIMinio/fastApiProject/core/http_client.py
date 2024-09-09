from aiohttp import ClientSession


async def custom_http_client() -> ClientSession:
    async with ClientSession() as session:
        yield session
