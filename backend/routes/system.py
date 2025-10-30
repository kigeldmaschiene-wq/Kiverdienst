"""System routes providing health and statistics endpoints."""

from __future__ import annotations

from typing import Any, Dict

from flask import current_app, jsonify

from ..database import SessionLocal
from ..models import Brand, Character, Video
from . import api_bp


@api_bp.route("/health", methods=["GET"])
def health() -> Any:
    """Return API health status."""
    try:
        return jsonify({"success": True, "data": {"status": "healthy"}})
    except Exception as exc:  # pragma: no cover - defensive
        current_app.logger.error("Health check failed: %s", exc)
        return jsonify({"success": False, "error": str(exc)}), 500


@api_bp.route("/system/stats", methods=["GET"])
def system_stats() -> Any:
    """Return aggregate statistics for the system."""
    session = SessionLocal()
    try:
        brands_count = session.query(Brand).count()
        videos_count = session.query(Video).count()
        characters_count = session.query(Character).count()

        data: Dict[str, Any] = {
            "brands": {"count": brands_count},
            "videos": {"count": videos_count},
            "characters": {"count": characters_count},
        }
        return jsonify({"success": True, "data": data})
    except Exception as exc:
        session.rollback()
        current_app.logger.error("Failed to fetch system stats: %s", exc)
        return jsonify({"success": False, "error": str(exc)}), 500
    finally:
        session.close()
