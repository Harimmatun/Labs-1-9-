import aiohttp
import asyncio
import logging
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
logger = logging.getLogger(__name__)

class AuthProxy:
    def __init__(self, base_url, auth_config):
        self.base_url = base_url
        self.auth_config = auth_config
        self.token = None
        self.token_expiry = None

    async def get_token(self):
        if self.auth_config["type"] == "jwt":
            if self.token and self.token_expiry > datetime.now():
                return self.token
            logger.info("Fetching new JWT token")
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.auth_config["token_url"],
                    json={"client_id": self.auth_config["client_id"], "client_secret": self.auth_config["client_secret"]}
                ) as response:
                    data = await response.json()
                    self.token = data["access_token"]
                    self.token_expiry = datetime.now() + timedelta(seconds=data["expires_in"])
                    return self.token
        return self.auth_config.get("api_key")

    async def request(self, method, endpoint, **kwargs):
        url = f"{self.base_url}{endpoint}"
        headers = kwargs.get("headers", {})

        if self.auth_config["type"] == "api_key":
            headers["X-API-Key"] = await self.get_token()
        else:
            headers["Authorization"] = f"Bearer {await self.get_token()}"

        kwargs["headers"] = headers
        async with aiohttp.ClientSession() as session:
            logger.info(f"Sending {method} request to {url}")
            async with session.request(method, url, **kwargs) as response:
                if response.status == 401 and self.auth_config["type"] == "jwt":
                    logger.info("Token expired, renewing")
                    self.token = None
                    headers["Authorization"] = f"Bearer {await self.get_token()}"
                    async with session.request(method, url, headers=headers, **kwargs) as retry_response:
                        data = await retry_response.json()
                        logger.info(f"Received response: {retry_response.status} {data}")
                        return data
                data = await response.json()
                logger.info(f"Received response: {response.status} {data}")
                return data

async def mock_auth_server():
    async def handler(request):
        data = await request.json()
        if data.get("client_id") == "test_client" and data.get("client_secret") == "test_secret":
            return aiohttp.web.json_response({"access_token": "jwt_token", "expires_in": 5})
        return aiohttp.web.json_response({"error": "Invalid credentials"}, status=401)

    app = aiohttp.web.Application()
    app.router.add_post("/auth/token", handler)
    runner = aiohttp.web.AppRunner(app)
    await runner.setup()
    site = aiohttp.web.TCPSite(runner, "localhost", 8081)
    await site.start()
    return runner

async def mock_api_server():
    async def handler(request):
        auth_header = request.headers.get("Authorization")
        if auth_header != "Bearer jwt_token":
            return aiohttp.web.json_response({"error": "Invalid or expired token"}, status=401)
        return aiohttp.web.json_response({"message": "Success", "data": await request.json()})

    app = aiohttp.web.Application()
    app.router.add_post("/api/test", handler)
    runner = aiohttp.web.AppRunner(app)
    await runner.setup()
    site = aiohttp.web.TCPSite(runner, "localhost", 8080)
    await site.start()
    return runner

async def main():
    auth_server = await mock_auth_server()
    api_server = await mock_api_server()

    auth_config = {
        "type": "jwt",
        "token_url": "http://localhost:8081/auth/token",
        "client_id": "test_client",
        "client_secret": "test_secret"
    }
    proxy = AuthProxy("http://localhost:8080", auth_config)

    print("Test 2: JWT Authentication with Token Renewal")
    response1 = await proxy.request("POST", "/api/test", json={"value": 42})
    print(f"Response 1: {response1}")
    await asyncio.sleep(6)
    response2 = await proxy.request("POST", "/api/test", json={"value": 43})
    print(f"Response 2: {response2}")

    await auth_server.cleanup()
    await api_server.cleanup()

if __name__ == "__main__":
    asyncio.run(main())