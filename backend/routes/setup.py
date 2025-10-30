"""Setup wizard API endpoints."""

from __future__ import annotations

from typing import Any

from flask import current_app, jsonify, request

from ..database import SessionLocal
from ..models import SystemConfig
from . import api_bp

SETUP_KEY = "setup_completed"


def _get_config(session: SessionLocal, key: str) -> SystemConfig | None:
    return session.query(SystemConfig).filter(SystemConfig.key == key).one_or_none()


@api_bp.route("/setup/status", methods=["GET"])
def setup_status() -> Any:
    session = SessionLocal()
    try:
        config = _get_config(session, SETUP_KEY)
        completed = config.value == "true" if config else False
        return jsonify({"success": True, "data": {"completed": completed}})
    except Exception as exc:
        current_app.logger.error("Failed to fetch setup status: %s", exc)
        return jsonify({"success": False, "error": str(exc)}), 500
    finally:
        session.close()


@api_bp.route("/setup/init", methods=["POST"])
def setup_init() -> Any:
    session = SessionLocal()
    try:
        payload = request.get_json(force=True, silent=True) or {}
        description = payload.get("description", "Initial setup started")

        config = _get_config(session, SETUP_KEY)
        if not config:
            config = SystemConfig(key=SETUP_KEY)
            session.add(config)

        config.value = "false"
        config.description = description
        session.commit()

        return jsonify({"success": True, "data": {"message": "Setup initialized"}}), 201
    except Exception as exc:
        session.rollback()
        current_app.logger.error("Failed to initialize setup: %s", exc)
        return jsonify({"success": False, "error": str(exc)}), 500
    finally:
        session.close()


@api_bp.route("/setup/complete", methods=["POST"])
def setup_complete() -> Any:
    session = SessionLocal()
    try:
        config = _get_config(session, SETUP_KEY)
        if not config:
            config = SystemConfig(key=SETUP_KEY)
            session.add(config)

        config.value = "true"
        config.description = "Setup completed"
        session.commit()

        return jsonify({"success": True, "data": {"message": "Setup completed"}})
    except Exception as exc:
        session.rollback()
        current_app.logger.error("Failed to complete setup: %s", exc)
        return jsonify({"success": False, "error": str(exc)}), 500
    finally:
        session.close()
