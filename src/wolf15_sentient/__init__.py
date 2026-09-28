"""WOLF15 Sentient deterministic runtime foundation."""

__version__ = "0.1.0"


def create_app():
    """Lazily create an app without importing FastAPI at package import time."""

    from wolf15_sentient.api.app import create_app as app_factory

    return app_factory()

__all__ = ["create_app"]
