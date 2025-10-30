"""API route blueprints for KIVerdienst v2 backend."""

from __future__ import annotations

from flask import Blueprint


api_bp = Blueprint("api", __name__, url_prefix="/api")


def register_routes() -> None:
    """Import modules to register their routes with the blueprint."""
    # Importing within function avoids circular dependencies with application factory
    from . import brands, characters, content, setup, system, videos  # noqa: F401


__all__ = ["api_bp", "register_routes"]
