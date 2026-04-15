
import asyncio
import datetime
import mimetypes
import os

from aiohttp import web
from dotenv import load_dotenv
from google import genai

load_dotenv()

HTTP_PORT = 8080
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    print("❌ Error: GEMINI_API_KEY not found in environment. Please set it in .env file.")
    exit(1)

client = genai.Client(api_key=GEMINI_API_KEY, http_options={"api_version": "v1alpha"})


async def get_ephemeral_token(request):
    try:
        now = datetime.datetime.now(tz=datetime.timezone.utc)
        expire_time = now + datetime.timedelta(minutes=30)

        token = client.auth_tokens.create(
            config={
                "uses": 1,
                "expire_time": expire_time.isoformat(),
                "new_session_expire_time": (now + datetime.timedelta(minutes=1)).isoformat(),
                "http_options": {"api_version": "v1alpha"},
            }
        )

        return web.json_response({
            "token": token.name,
            "expires_at": expire_time.isoformat()
        })
    except Exception as e:
        print(f"Error generating ephemeral token: {e}")
        return web.json_response({"error": str(e)}, status=500)


async def tts_proxy(request):
    """Proxy synthesis requests to the local F5-TTS/XTTS server."""
    try:
        reader = await request.multipart()
        
        # Prepare data for the local TTS server
        data = web.FormData()
        async for part in reader:
            if part.name == 'text':
                data.add_field('text', await part.text())
            elif part.name == 'speaker_wav':
                filename = part.filename
                content = await part.read()
                data.add_field('speaker_wav', content, filename=filename, content_type='audio/wav')

        async with web.ClientSession() as session:
            # Hit the local TTS server's upload endpoint
            print(f"Proxying request to local TTS: {len(content)} bytes of audio")
            async with session.post("http://localhost:8000/tts/upload", data=data) as resp:
                print(f"Local TTS responded with status: {resp.status}")
                if resp.status != 200:
                    text = await resp.text()
                    print(f"Local TTS error: {text}")
                    return web.Response(text=text, status=resp.status)
                
                content = await resp.read()
                print(f"Received {len(content)} bytes of synthesised audio")
                return web.Response(
                    body=content,
                    content_type="audio/wav"
                )
    except Exception as e:
        print(f"Proxy error: {e}")
        return web.json_response({"error": str(e)}, status=500)


async def serve_static_file(request):
    path = request.match_info.get("path", "index.html")
    path = path.lstrip("/")
    if ".." in path:
        return web.Response(text="Invalid path", status=400)

    if not path or path == "/":
        path = "index.html"

    frontend_dir = os.path.join(os.path.dirname(__file__), "frontend")
    file_path = os.path.join(frontend_dir, path)

    if not os.path.exists(file_path) or not os.path.isfile(file_path):
        return web.Response(text="File not found", status=404)

    content_type, _ = mimetypes.guess_type(file_path)
    if content_type is None:
        content_type = "application/octet-stream"

    try:
        with open(file_path, "rb") as f:
            content = f.read()
        return web.Response(body=content, content_type=content_type)
    except Exception as e:
        print(f"Error serving file {path}: {e}")
        return web.Response(text="Internal server error", status=500)


async def main():
    app = web.Application()
    app.router.add_post("/api/token", get_ephemeral_token)
    app.router.add_post("/api/tts-proxy", tts_proxy)
    app.router.add_get("/", serve_static_file)
    app.router.add_get("/{path:.*}", serve_static_file)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", HTTP_PORT)
    await site.start()

    print(f"Gemini Live API Server started at http://localhost:{HTTP_PORT}")
    print("Ready to connect!")

    while True:
        await asyncio.sleep(3600)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Server stopped")
