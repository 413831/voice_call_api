"""
Módulo de Servicios (Capa de Lógica de Negocio).

Principios SOLID y OOP aplicados:
- Single Responsibility Principle (SRP): Concentra las reglas de negocio, validaciones de dominio
  y orquestación de operaciones. No depende de Flask ni de peticiones HTTP.
- Dependency Inversion Principle (DIP) / Dependency Injection (DI):
  VoiceCallService depende de una instancia del repositorio inyectada en su constructor (`__init__`).
  Esto permite testear el servicio de forma aislada inyectando un repositorio simulado (Mock).
"""

import re
from typing import Any, Mapping, Sequence

from exceptions import CallNotFoundError, InvalidCallDataError
from models import VoiceCall
from repositories import VoiceCallRepository

VALID_STATUSES = {"completed", "failed", "in-progress"}
# Expresión regular estándar para validación básica de formato E.164 / internacional
PHONE_REGEX = re.compile(r"^\+?[1-9]\d{6,14}$")


class VoiceCallService:
    """
    Servicio de dominio para gestionar el ciclo de vida y la integridad de las llamadas de voz.
    """

    def __init__(self, repository: VoiceCallRepository) -> None:
        # Inyección de dependencias a través del constructor
        self._repository = repository

    def _validate_call_data(self, data: Mapping[str, Any], is_update: bool = False) -> None:
        """
        Valida que los datos cumplan las reglas de negocio del dominio.
        Lanza InvalidCallDataError si alguna regla no se cumple.
        """
        if not is_update or "phone_number" in data:
            phone = data.get("phone_number")
            if not phone or not isinstance(phone, str) or not PHONE_REGEX.match(phone.strip()):
                raise InvalidCallDataError(
                    "El número telefónico es obligatorio y debe tener un formato válido (ej. +14155552671)."
                )

        if not is_update or "duration_seconds" in data:
            duration = data.get("duration_seconds", 0)
            if not isinstance(duration, int) or duration < 0:
                raise InvalidCallDataError("La duración de la llamada no puede ser un número negativo.")

        if not is_update or "status" in data:
            status = data.get("status", "in-progress")
            if status not in VALID_STATUSES:
                raise InvalidCallDataError(
                    f"Estado '{status}' inválido. Los estados permitidos son: {', '.join(sorted(VALID_STATUSES))}."
                )

    def create_call(self, data: Mapping[str, Any]) -> VoiceCall:
        """Valida y crea una nueva llamada."""
        self._validate_call_data(data, is_update=False)

        new_call = VoiceCall(
            phone_number=data["phone_number"].strip(),
            duration_seconds=data.get("duration_seconds", 0),
            status=data.get("status", "in-progress"),
            transcript_summary=data.get("transcript_summary"),
        )
        return self._repository.create(new_call)

    def get_call(self, call_id: str) -> VoiceCall:
        """Obtiene una llamada por ID o lanza CallNotFoundError si no existe."""
        call = self._repository.get_by_id(call_id)
        if not call:
            raise CallNotFoundError(call_id)
        return call

    def list_calls(self, limit: int = 50, offset: int = 0) -> Sequence[VoiceCall]:
        """Obtiene la lista de llamadas con paginación defensiva."""
        safe_limit = max(1, min(limit, 100))  # Evita sobrecargas forzando un límite máximo
        safe_offset = max(0, offset)
        return self._repository.list_all(limit=safe_limit, offset=safe_offset)

    def update_call(self, call_id: str, data: Mapping[str, Any]) -> VoiceCall:
        """Actualiza parcialmente los atributos de una llamada existente."""
        call = self.get_call(call_id)
        self._validate_call_data(data, is_update=True)

        if "phone_number" in data:
            call.phone_number = data["phone_number"].strip()
        if "duration_seconds" in data:
            call.duration_seconds = data["duration_seconds"]
        if "status" in data:
            call.status = data["status"]
        if "transcript_summary" in data:
            call.transcript_summary = data["transcript_summary"]

        return self._repository.update(call)

    def delete_call(self, call_id: str) -> None:
        """Elimina una llamada existente."""
        call = self.get_call(call_id)
        self._repository.delete(call)
