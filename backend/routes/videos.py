"""Video management API endpoints."""

from __future__ import annotations

from typing import Any, Dict, List

from flask import current_app, jsonify, request

from ..database import SessionLocal
from ..models import Brand, Character, Video
from . import api_bp


def _serialize_video(video: Video) -> Dict[str, Any]:
    return {
        "id": video.id,
        "brand_id": video.brand_id,
        "character_id": video.character_id,
        "title": video.title,
        "script": video.script,
        "status": video.status,
        "posted": video.posted,
        "created_at": video.created_at.isoformat() if video.created_at else None,
        "updated_at": video.updated_at.isoformat() if video.updated_at else None,
    }


@api_bp.route("/videos", methods=["GET"])
def list_videos() -> Any:
    session = SessionLocal()
    try:
        brand_id = request.args.get("brand_id", type=int)
        query = session.query(Video)
        if brand_id is not None:
            query = query.filter(Video.brand_id == brand_id)
        videos: List[Video] = query.order_by(Video.created_at.desc()).all()
        return jsonify({"success": True, "data": [_serialize_video(video) for video in videos]})
    except Exception as exc:
        current_app.logger.error("Failed to list videos: %s", exc)
        return jsonify({"success": False, "error": str(exc)}), 500
    finally:
        session.close()


@api_bp.route("/videos", methods=["POST"])
def create_video() -> Any:
    session = SessionLocal()
    try:
        payload = request.get_json(force=True, silent=True) or {}
        brand_id = payload.get("brand_id")
        if not brand_id:
            return jsonify({"success": False, "error": "Field 'brand_id' is required"}), 400

        if not session.get(Brand, brand_id):
            return jsonify({"success": False, "error": "Brand not found"}), 404

        character_id = payload.get("character_id")
        if character_id and not session.get(Character, character_id):
            return jsonify({"success": False, "error": "Character not found"}), 404

        video = Video(
            brand_id=brand_id,
            character_id=character_id,
            title=payload.get("title"),
            script=payload.get("script"),
            status=payload.get("status"),
            posted=payload.get("posted", False),
        )
        session.add(video)
        session.commit()
        session.refresh(video)

        return jsonify({"success": True, "data": _serialize_video(video)}), 201
    except Exception as exc:
        session.rollback()
        current_app.logger.error("Failed to create video: %s", exc)
        return jsonify({"success": False, "error": str(exc)}), 500
    finally:
        session.close()


@api_bp.route("/videos/<int:video_id>", methods=["GET"])
def get_video(video_id: int) -> Any:
    session = SessionLocal()
    try:
        video = session.get(Video, video_id)
        if not video:
            return jsonify({"success": False, "error": "Video not found"}), 404
        return jsonify({"success": True, "data": _serialize_video(video)})
    except Exception as exc:
        current_app.logger.error("Failed to fetch video %s: %s", video_id, exc)
        return jsonify({"success": False, "error": str(exc)}), 500
    finally:
        session.close()
