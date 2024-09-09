from functools import wraps
import mimetypes

from aiohttp import web
from cloudpathlib import CloudPath
from google.api_core.exceptions import Forbidden


def bucket_proxy(gs_path):
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
