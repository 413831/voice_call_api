"""
Módulo de Modelos de Base de Datos.

Principios SOLID y OOP aplicados:
- Single Responsibility Principle (SRP): El modelo VoiceCall representa únicamente
  la estructura de datos y el mapeo relacional de la entidad.
- Declarative Mapping moderno (SQLAlchemy 2.0): Tipado estático con Mapped y mapped_column
  para compatibilidad total con analizadores estáticos como mypy/pyright.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Clase base declarativa de SQLAlchemy 2.0."""
    pass


class VoiceCall(Base):
    """
    Entidad VoiceCall: Representa los metadatos de una llamada procesada por el sistema.
    """
    __tablename__ = "voice_calls"

    # Identificador único (UUID v4) como cadena para máxima interoperabilidad
    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )
    
    # Número de teléfono en formato internacional (E.164)
    phone_number: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    
    # Duración de la llamada en segundos
    duration_seconds: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    
    # Estado de la llamada: 'completed', 'failed', 'in-progress'
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="in-progress")
    
    # Resumen de transcripción (opcional / nullable)
    transcript_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Marca de tiempo de creación en UTC
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )

    def to_dict(self) -> dict[str, Any]:
        """
        Serializa el modelo a un diccionario serializable en JSON.
        Mantiene el modelo libre de dependencias de frameworks web (como Flask jsonify).
        """
        return {
            "id": self.id,
            "phone_number": self.phone_number,
            "duration_seconds": self.duration_seconds,
            "status": self.status,
            "transcript_summary": self.transcript_summary,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
