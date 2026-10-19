"""
Módulo de Rutas y Controladores HTTP (Capa de Presentación / API).

Principios SOLID y OOP aplicados:
- Single Responsibility Principle (SRP): Se encarga exclusivamente del protocolo HTTP:
  deserializar requests, invocar al servicio de negocio y formatear respuestas con códigos HTTP.
- Dependency Injection (DI) vía Factory Function: `create_calls_blueprint` recibe la instancia
  de `VoiceCallService` por parámetro, evitando variables globales o acoplamiento estricto.
"""

from typing import Any
from flask import Blueprint, Response, jsonify, request

from exceptions import CallNotFoundError, InvalidCallDataError
from services import VoiceCallService


def create_calls_blueprint(service: VoiceCallService) -> Blueprint:
    """
    Crea y configura el Blueprint de Flask para los endpoints de llamadas.
    Inyecta la instancia del servicio requerida para operar.
    """
    bp = Blueprint("voice_calls", __name__, url_prefix="/api/calls")

    # --- Manejadores de Excepciones del Blueprint ---
    @bp.errorhandler(CallNotFoundError)
    def handle_not_found(error: CallNotFoundError) -> tuple[Response, int]:
        return jsonify({"error": str(error)}), 404

    @bp.errorhandler(InvalidCallDataError)
    def handle_invalid_data(error: InvalidCallDataError) -> tuple[Response, int]:
        return jsonify({"error": str(error)}), 400

    # --- Rutas CRUD ---

    @bp.post("")
    def create_call() -> tuple[Response, int]:
        """Crea un nuevo registro de llamada de voz."""
        payload: Any = request.get_json(silent=True)
        if not isinstance(payload, dict):
            return jsonify({"error": "El cuerpo de la solicitud debe ser un objeto JSON válido."}), 400

        created = service.create_call(payload)
        return jsonify(created.to_dict()), 201

    @bp.get("")
    def list_calls() -> tuple[Response, int]:
        """Lista llamadas con soporte para paginación opcional (?limit=N&offset=M)."""
        try:
            limit = int(request.args.get("limit", 50))
            offset = int(request.args.get("offset", 0))
        except ValueError:
            return jsonify({"error": "Los parámetros 'limit' y 'offset' deben ser enteros."}), 400

        calls = service.list_calls(limit=limit, offset=offset)
        return jsonify([call.to_dict() for call in calls]), 200

    @bp.get("/<string:call_id>")
    def get_call(call_id: str) -> tuple[Response, int]:
        """Obtiene el detalle de una llamada específica por su UUID."""
        call = service.get_call(call_id)
        return jsonify(call.to_dict()), 200

    @bp.patch("/<string:call_id>")
    @bp.put("/<string:call_id>")
    def update_call(call_id: str) -> tuple[Response, int]:
        """Actualiza campos de una llamada existente."""
        payload: Any = request.get_json(silent=True)
        if not isinstance(payload, dict):
            return jsonify({"error": "El cuerpo de la solicitud debe ser un objeto JSON válido."}), 400

        updated = service.update_call(call_id, payload)
        return jsonify(updated.to_dict()), 200

    @bp.delete("/<string:call_id>")
    def delete_call(call_id: str) -> tuple[Response, int]:
        """Elimina el registro de una llamada."""
        service.delete_call(call_id)
        return jsonify({"message": f"Llamada '{call_id}' eliminada correctamente."}), 200

    return bp
