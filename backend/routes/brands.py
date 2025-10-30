"""Brand management API endpoints."""

from __future__ import annotations

from typing import Any, Dict, List

from flask import current_app, jsonify, request

from ..database import SessionLocal
from ..models import Brand
from . import api_bp


def _serialize_brand(brand: Brand) -> Dict[str, Any]:
    return {
        "id": brand.id,
        "name": brand.name,
        "niche": brand.niche,
        "target_audience": brand.target_audience,
        "content_strategy": brand.content_strategy,
        "active": brand.active,
        "created_at": brand.created_at.isoformat() if brand.created_at else None,
        "updated_at": brand.updated_at.isoformat() if brand.updated_at else None,
    }


@api_bp.route("/brands", methods=["GET"])
def list_brands() -> Any:
    session = SessionLocal()
    try:
        brands: List[Brand] = session.query(Brand).order_by(Brand.created_at.desc()).all()
        data = [_serialize_brand(brand) for brand in brands]
        return jsonify({"success": True, "data": data})
    except Exception as exc:
        current_app.logger.error("Failed to list brands: %s", exc)
        return jsonify({"success": False, "error": str(exc)}), 500
    finally:
        session.close()


@api_bp.route("/brands", methods=["POST"])
def create_brand() -> Any:
    session = SessionLocal()
    try:
        payload = request.get_json(force=True, silent=True) or {}
        name = payload.get("name")
        if not name:
            return (
                jsonify({"success": False, "error": "Field 'name' is required"}),
                400,
            )

        brand = Brand(
            name=name,
            niche=payload.get("niche"),
            target_audience=payload.get("target_audience"),
            content_strategy=payload.get("content_strategy"),
            active=payload.get("active", True),
        )
        session.add(brand)
        session.commit()
        session.refresh(brand)

        return jsonify({"success": True, "data": _serialize_brand(brand)}), 201
    except Exception as exc:
        session.rollback()
        current_app.logger.error("Failed to create brand: %s", exc)
        return jsonify({"success": False, "error": str(exc)}), 500
    finally:
        session.close()


@api_bp.route("/brands/<int:brand_id>", methods=["GET"])
def get_brand(brand_id: int) -> Any:
    session = SessionLocal()
    try:
        brand = session.get(Brand, brand_id)
        if not brand:
            return jsonify({"success": False, "error": "Brand not found"}), 404
        return jsonify({"success": True, "data": _serialize_brand(brand)})
    except Exception as exc:
        current_app.logger.error("Failed to fetch brand %s: %s", brand_id, exc)
        return jsonify({"success": False, "error": str(exc)}), 500
    finally:
        session.close()


@api_bp.route("/brands/<int:brand_id>", methods=["PUT"])
def update_brand(brand_id: int) -> Any:
    session = SessionLocal()
    try:
        brand = session.get(Brand, brand_id)
        if not brand:
            return jsonify({"success": False, "error": "Brand not found"}), 404

        payload = request.get_json(force=True, silent=True) or {}
        for key in ["name", "niche", "target_audience", "content_strategy", "active"]:
            if key in payload:
                setattr(brand, key, payload[key])

        session.commit()
        session.refresh(brand)
        return jsonify({"success": True, "data": _serialize_brand(brand)})
    except Exception as exc:
        session.rollback()
        current_app.logger.error("Failed to update brand %s: %s", brand_id, exc)
        return jsonify({"success": False, "error": str(exc)}), 500
    finally:
        session.close()


@api_bp.route("/brands/<int:brand_id>", methods=["DELETE"])
def delete_brand(brand_id: int) -> Any:
    session = SessionLocal()
    try:
        brand = session.get(Brand, brand_id)
        if not brand:
            return jsonify({"success": False, "error": "Brand not found"}), 404

        session.delete(brand)
        session.commit()
        return jsonify({"success": True, "data": {"message": "Brand deleted"}})
    except Exception as exc:
        session.rollback()
        current_app.logger.error("Failed to delete brand %s: %s", brand_id, exc)
        return jsonify({"success": False, "error": str(exc)}), 500
    finally:
        session.close()
