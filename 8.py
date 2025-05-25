import aiohttp
import asyncio
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
logger = logging.getLogger(__name__)

class AuthProxy:
    def __init__(self, base_url, api_key):
        self.base_url = base_url
        self.api_key = api_key

    async def request(self, method, endpoint, **kwargs):
        url = f"{self.base_url}{endpoint}"
        headers = kwargs.get("headers", {})
        headers["X-API-Key"] = self.api_key
        kwargs["headers"] = headers

        async with aiohttp.ClientSession() as session:
            logger.info(f"Sending {method} request to {url}")
            async with session.request(method, url, **kwargs) as response:
                data = await response.json()
                logger.info(f"Received response: {response.status} {data}")
                return data

async def mock_api_server():
    async def handler(request):
        if request.headers.get("X-API-Key") != "test-api-key":
            return aiohttp.web.json_response({"error": "Invalid API Key"}, status=401)
        return aiohttp.web.json_response({"message": "Success", "data": await request.json()})

    app = aiohttp.web.Application()
    app.router.add_post("/api/test", handler)
    runner = aiohttp.web.AppRunner(app)
    await runner.setup()
    site = aiohttp.web.TCPSite(runner, "localhost", 8080)
    await site.start()
    return runner

async def main():
    server = await mock_api_server()
    proxy = AuthProxy("http://localhost:8080", "test-api-key")

    print("Test 1: Basic API Key Authentication")
    response = await proxy.request("POST", "/api/test", json={"value": 42})
    print(f"Response: {response}")

    await server.cleanup()

if __name__ == "__main__":
    asyncio.run(main())