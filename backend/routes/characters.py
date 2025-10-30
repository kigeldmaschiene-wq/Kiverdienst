"""Character management API endpoints."""

from __future__ import annotations

from typing import Any, Dict, List

from flask import current_app, jsonify, request

from ..database import SessionLocal
from ..models import Brand, Character
from . import api_bp


def _serialize_character(character: Character) -> Dict[str, Any]:
    return {
        "id": character.id,
        "brand_id": character.brand_id,
        "name": character.name,
        "gender": character.gender,
        "voice_id": character.voice_id,
        "personality": character.personality,
        "created_at": character.created_at.isoformat() if character.created_at else None,
        "updated_at": character.updated_at.isoformat() if character.updated_at else None,
    }


@api_bp.route("/characters", methods=["GET"])
def list_characters() -> Any:
    session = SessionLocal()
    try:
        characters: List[Character] = session.query(Character).order_by(Character.created_at.desc()).all()
        return jsonify({"success": True, "data": [_serialize_character(character) for character in characters]})
    except Exception as exc:
        current_app.logger.error("Failed to list characters: %s", exc)
        return jsonify({"success": False, "error": str(exc)}), 500
    finally:
        session.close()


@api_bp.route("/characters", methods=["POST"])
def create_character() -> Any:
    session = SessionLocal()
    try:
        payload = request.get_json(force=True, silent=True) or {}
        brand_id = payload.get("brand_id")
        if brand_id and not session.get(Brand, brand_id):
            return jsonify({"success": False, "error": "Brand not found"}), 404

        character = Character(
            brand_id=brand_id,
            name=payload.get("name"),
            gender=payload.get("gender"),
            voice_id=payload.get("voice_id"),
            personality=payload.get("personality"),
        )
        session.add(character)
        session.commit()
        session.refresh(character)

        return jsonify({"success": True, "data": _serialize_character(character)}), 201
    except Exception as exc:
        session.rollback()
        current_app.logger.error("Failed to create character: %s", exc)
        return jsonify({"success": False, "error": str(exc)}), 500
    finally:
        session.close()
