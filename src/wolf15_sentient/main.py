"""ASGI entry point for ``uvicorn wolf15_sentient.main:app``."""

from wolf15_sentient.api.app import app, create_app

__all__ = ["app", "create_app"]
