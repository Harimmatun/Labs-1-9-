import aiohttp
import asyncio
import logging
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from concurrent.futures import ThreadPoolExecutor
import socketserver
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class ThreadedHTTPServer(socketserver.ThreadingMixIn, HTTPServer):
    pass

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
            try:
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
            except aiohttp.ClientError as e:
                logger.error(f"Error in request: {e}")
                raise

class MockAPIHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        auth_header = self.headers.get("Authorization")
        if auth_header != "Bearer jwt_token":
            self.send_response(401)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Invalid or expired token"}).encode())
            logger.warning("Invalid token received")
            return
        content_length = int(self.headers["Content-Length"])
        data = json.loads(self.rfile.read(content_length))
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        response = {"message": "Success", "data": data}
        self.wfile.write(json.dumps(response).encode())
        logger.info(f"Mock API responded: {response}")

class MockAuthHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers["Content-Length"])
        data = json.loads(self.rfile.read(content_length))
        if data.get("client_id") == "test_client" and data.get("client_secret") == "test_secret":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            response = {"access_token": "jwt_token", "expires_in": 5}
            self.wfile.write(json.dumps(response).encode())
            logger.info("Mock auth server issued token")
        else:
            self.send_response(401)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Invalid credentials"}).encode())
            logger.warning("Invalid auth credentials")

async def start_mock_server(port, handler_class):
    server = ThreadedHTTPServer(("localhost", port), handler_class)
    executor = ThreadPoolExecutor(max_workers=1)
    loop = asyncio.get_running_loop()

    def run_server():
        try:
            server.serve_forever()
        except Exception as e:
            logger.error(f"Server error: {e}")

    server_task = loop.run_in_executor(executor, run_server)
    logger.info(f"Mock server started on http://localhost:{port}")
    return server, server_task, executor

async def stop_mock_server(server, server_task, executor):
    try:
        server.shutdown()
        server.server_close()
        executor.shutdown(wait=True)
        await server_task
        logger.info("Mock server stopped")
    except Exception as e:
        logger.error(f"Error stopping server: {e}")

async def main():
    try:
        api_server, api_task, api_executor = await start_mock_server(8080, MockAPIHandler)
        auth_server, auth_task, auth_executor = await start_mock_server(8081, MockAuthHandler)

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

        await stop_mock_server(api_server, api_task, api_executor)
        await stop_mock_server(auth_server, auth_task, auth_executor)
    except Exception as e:
        print(f"Test failed: {e}")
        logger.error(f"Test error: {e}")

if __name__ == "__main__":
    asyncio.run(main())