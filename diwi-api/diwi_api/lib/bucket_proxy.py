import asyncio
from pathlib import PurePosixPath
from functools import wraps
import urllib.parse
import mimetypes

from aiohttp import web
from google.api_core.exceptions import Forbidden
from google.cloud import storage

from cloudpathlib import CloudPath  # to remove


def bucket_proxy(gs_path, chunk_size=1024):
    client = storage.Client()  # Initialize the GCS client

    path_parse = urllib.parse.urlparse(gs_path, scheme="gs")
    bucket_name = path_parse.netloc
    base_path = PurePosixPath(path_parse.path.rstrip("/"))

    async def stream_file(bucket, blob_name, response):
        """Stream file in chunks to the client"""
        blob = bucket.blob(blob_name)
        # Stream the file in chunks
        with blob.open("rb") as file:
            while chunk := file.read(chunk_size):
                await response.write(chunk)
        await response.write_eof()

    def _(fxn):
        @wraps(fxn)
        async def handler(request: web.Request):
            relative_path = request.match_info.get("path") or "index.html"
            target_path = (base_path / relative_path).resolve()
            if not target_path.is_relative_to(base_path):
                return web.json_response({"error": "Unauthorized Path"}, status=403)

            blob_name = str(target_path)
            try:
                bucket = client.bucket(bucket_name)
                blob = bucket.blob(blob_name)

                # Check if file exists
                if not blob.exists():
                    raise web.HTTPNotFound(text="File not found.")
            except Forbidden:
                raise web.HTTPForbidden(text="No access to storage")

            mime_type, _ = mimetypes.guess_type(blob_name)
            if mime_type is None:
                mime_type = "application/octet-stream"  # Default binary content type

            # Prepare for streaming response
            response = web.StreamResponse(
                status=200,
                reason="OK",
                headers={
                    "Content-Type": mime_type,
                    "Cache-Control": "public, max-age=3600",  # Cache for 1 hour
                },
            )
            await response.prepare(request)

            # Stream the file to the client
            await stream_file(bucket, blob_name, response)
            return response

        return handler

    return _


def bucket_proxy_old(gs_path):
    base_path: CloudPath = CloudPath(gs_path)

    def _(fxn):
        @wraps(fxn)
        async def handler(request: web.Request):
            relative_path = request.match_info.get("path") or "index.html"
            target: CloudPath = base_path / relative_path
            print(f"target: {target}")
            if not target.is_relative_to(base_path):
                return web.json_response({"error": "Unauthorized Path"}, status=403)
            try:
                if not target.exists():
                    raise web.HTTPNotFound(text="File not found.")
            except Forbidden:
                raise web.HTTPForbidden(text="No access to storage")

            mime_type, _ = mimetypes.guess_type(target)
            if mime_type is None:
                mime_type = "application/octet-stream"  # Default binary content type
            body = target.read_bytes()
            return web.Response(body=body, content_type=mime_type)

        return handler

    return _


def register_bucket_proxy(app: web.Application, root: str, handler: web.RequestHandler):
    app.router.add_get(f"{root.rstrip('/')}/{{path:.*}}", handler)
    app.router.add_get(f"{root}", handler)
