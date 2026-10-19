"""
Módulo de Repositorios (Capa de Acceso a Datos / Persistencia).

Principios SOLID y OOP aplicados:
- Single Responsibility Principle (SRP): Encapsula exclusivamente las consultas SQL
  y operaciones de persistencia mediante SQLAlchemy. Ni la capa de servicio ni la de rutas
  ejecutan sentencias SQL o manipulan directamente la sesión.
- Dependency Injection (DI): Recibe la sesión de SQLAlchemy en el constructor (`__init__`),
  lo que facilita inyectar sesiones mock o sesiones de prueba en memoria.
"""

from typing import Optional, Sequence
from sqlalchemy import select
from sqlalchemy.orm import Session

from models import VoiceCall


class VoiceCallRepository:
    """
    Repositorio concreto para la entidad VoiceCall.
    Aísla las operaciones CRUD de base de datos del resto de la aplicación.
    """

    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_id(self, call_id: str) -> Optional[VoiceCall]:
        """Obtiene una llamada por su clave primaria UUID."""
        return self._session.get(VoiceCall, call_id)

    def list_all(self, limit: int = 50, offset: int = 0) -> Sequence[VoiceCall]:
        """Obtiene un listado paginado de llamadas ordenadas cronológicamente."""
        stmt = (
            select(VoiceCall)
            .order_by(VoiceCall.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        return self._session.scalars(stmt).all()

    def create(self, call: VoiceCall) -> VoiceCall:
        """Persiste una nueva llamada en la base de datos."""
        self._session.add(call)
        self._session.commit()
        self._session.refresh(call)
        return call

    def update(self, call: VoiceCall) -> VoiceCall:
        """Confirma los cambios realizados en una entidad VoiceCall ya existente."""
        self._session.commit()
        self._session.refresh(call)
        return call

    def delete(self, call: VoiceCall) -> None:
        """Elimina la llamada de la base de datos."""
        self._session.delete(call)
        self._session.commit()
