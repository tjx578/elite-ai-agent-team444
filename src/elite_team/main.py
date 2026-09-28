"""ASGI entry point for ``uvicorn elite_team.main:app``."""

from elite_team.api.app import app, create_app

__all__ = ["app", "create_app"]
