"""SQLAlchemy models for KIVerdienst v2 backend."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from .database import Base


class TimestampMixin:
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )


class SystemConfig(Base, TimestampMixin):
    __tablename__ = "system_config"

    id: int = Column(Integer, primary_key=True, index=True)
    key: str = Column(String(100), unique=True, nullable=False)
    value: Optional[str] = Column(Text, nullable=True)
    description: Optional[str] = Column(Text, nullable=True)


class Brand(Base, TimestampMixin):
    __tablename__ = "brands"

    id: int = Column(Integer, primary_key=True, index=True)
    name: str = Column(String(100), nullable=False)
    niche: Optional[str] = Column(String(100), nullable=True)
    target_audience: Optional[str] = Column(Text, nullable=True)
    content_strategy: Optional[str] = Column(Text, nullable=True)
    active: bool = Column(Boolean, default=True, nullable=False)

    characters = relationship("Character", back_populates="brand", cascade="all, delete-orphan")
    videos = relationship("Video", back_populates="brand", cascade="all, delete-orphan")


class Character(Base, TimestampMixin):
    __tablename__ = "characters"

    id: int = Column(Integer, primary_key=True, index=True)
    brand_id: Optional[int] = Column(Integer, ForeignKey("brands.id"), nullable=True)
    name: Optional[str] = Column(String(100), nullable=True)
    gender: Optional[str] = Column(String(20), nullable=True)
    voice_id: Optional[str] = Column(String(100), nullable=True)
    personality: Optional[str] = Column(Text, nullable=True)

    brand = relationship("Brand", back_populates="characters")
    videos = relationship("Video", back_populates="character")


class Video(Base, TimestampMixin):
    __tablename__ = "videos"

    id: int = Column(Integer, primary_key=True, index=True)
    brand_id: Optional[int] = Column(Integer, ForeignKey("brands.id"), nullable=True)
    character_id: Optional[int] = Column(Integer, ForeignKey("characters.id"), nullable=True)
    title: Optional[str] = Column(String(200), nullable=True)
    script: Optional[str] = Column(Text, nullable=True)
    status: Optional[str] = Column(String(50), nullable=True)
    posted: bool = Column(Boolean, default=False, nullable=False)

    brand = relationship("Brand", back_populates="videos")
    character = relationship("Character", back_populates="videos")
