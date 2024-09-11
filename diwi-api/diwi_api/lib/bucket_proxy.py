import os
from functools import wraps
import urllib.parse
import mimetypes

from aiohttp import web
from aiohttp.typedefs import Handler
from google.api_core.exceptions import Forbidden
from google.cloud import storage


async def stream_file(bucket, blob_name, response, chunk_size=1024):
    """Stream file in chunks to the client"""
    blob = bucket.blob(blob_name)
    # Stream the file in chunks
    with blob.open("rb") as file:
        while chunk := file.read(chunk_size):
            await response.write(chunk)
    await response.write_eof()


def bucket_proxy(gs_path, chunk_size=1024):
    client = storage.Client()  # Initialize the GCS client

    path_parse = urllib.parse.urlparse(gs_path, scheme="gs")
    bucket_name = path_parse.netloc
    base_path = path_parse.path.strip("/")

    def _(fxn):
        @wraps(fxn)
        async def handler(request: web.Request):
            relative_path = request.match_info.get("path") or "index.html"
            blob_name = os.path.normpath(f"{base_path or '.'}/{relative_path}")
            # Ensure the target path is within the base path
            if not blob_name.startswith(base_path):
                return web.json_response({"error": "Unauthorized Path"}, status=403)

            try:
                bucket = client.bucket(bucket_name)
                blob = bucket.blob(blob_name)

                # Check if file exists
                if not blob.exists():
                    raise web.HTTPNotFound(text="File not found.")

                etag = blob.etag
                client_etag = request.headers.get("If-None-Match")
                if client_etag == etag:
                    return web.Response(status=304)
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
                    "ETag": etag,
                },
            )
            await response.prepare(request)

            # Stream the file to the client
            await stream_file(bucket, blob_name, response, chunk_size)
            return response

        return handler

    return _


def register_bucket_proxy(app: web.Application, root: str, handler: Handler):
    app.router.add_get(f"{root.rstrip('/')}/{{path:.*}}", handler)
    app.router.add_get(f"{root}", handler)
