import aiohttp
import asyncio
import logging
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from concurrent.futures import ThreadPoolExecutor
import socketserver

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class MockAPIHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.headers.get("X-API-Key") != "test-api-key":
            self.send_response(401)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Invalid API key"}).encode())
            logger.warning("Invalid API key received")
            return
        content_length = int(self.headers["Content-Length"])
        data = json.loads(self.rfile.read(content_length))
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        response = {"message": "Success", "data": data}
        self.wfile.write(json.dumps(response).encode())
        logger.info(f"Mock server responded: {response}")

class ThreadedHTTPServer(socketserver.ThreadingMixIn, HTTPServer):
    pass

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
            try:
                async with session.request(method, url, **kwargs) as response:
                    data = await response.json()
                    logger.info(f"Received response: {response.status} {data}")
                    return data
            except aiohttp.ClientError as e:
                logger.error(f"Error in request: {e}")
                raise

async def start_mock_server():
    server = ThreadedHTTPServer(("localhost", 8080), MockAPIHandler)
    executor = ThreadPoolExecutor(max_workers=1)
    loop = asyncio.get_running_loop()

    def run_server():
        try:
            server.serve_forever()
        except Exception as e:
            logger.error(f"Server error: {e}")

    server_task = loop.run_in_executor(executor, run_server)
    logger.info("Mock API server started on http://localhost:8080")
    return server, server_task, executor

async def stop_mock_server(server, server_task, executor):
    try:
        server.shutdown()
        server.server_close()
        executor.shutdown(wait=True)
        await server_task
        logger.info("Mock API server stopped")
    except Exception as e:
        logger.error(f"Error stopping server: {e}")

async def main():
    try:
        server, server_task, executor = await start_mock_server()
        proxy = AuthProxy("http://localhost:8080", "test-api-key")

        print("Test 1: Basic API Key Authentication")
        response = await proxy.request("POST", "/api/test", json={"value": 42})
        print(f"Response: {response}")

        await stop_mock_server(server, server_task, executor)
    except Exception as e:
        print(f"Test failed: {e}")
        logger.error(f"Test error: {e}")

if __name__ == "__main__":
    asyncio.run(main())