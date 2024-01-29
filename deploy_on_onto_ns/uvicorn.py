"""Customize running application with uvicorn."""

from __future__ import annotations

from typing import Any, ClassVar

from uvicorn.workers import UvicornWorker as OriginalUvicornWorker


class UvicornWorker(OriginalUvicornWorker):
    """Uvicorn worker class to be used in production with gunicorn."""

    CONFIG_KWARGS: ClassVar[dict[str, Any]] = {
        "server_header": False,
        "headers": [("Server", "Deploy on onto-ns.com")],
        "proxy_headers": True,
        "root_path": "/deploy",
    }
