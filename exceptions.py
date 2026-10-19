"""
Módulo de Excepciones del Dominio.

Buenas prácticas aplicadas:
- Principio de Responsabilidad Única (SRP): Este módulo centraliza las excepciones de negocio.
- Desacoplamiento: La capa de servicio y persistencia no conocen de códigos de estado HTTP;
  solo lanzan excepciones semánticas de dominio que luego la capa de transporte (Flask) traduce.
"""

class VoiceCallError(Exception):
    """Excepción base para cualquier error de la entidad VoiceCall."""
    pass


class CallNotFoundError(VoiceCallError):
    """Lanzada cuando un recurso VoiceCall no existe en el almacenamiento."""
    def __init__(self, call_id: str) -> None:
        super().__init__(f"Voice call with ID '{call_id}' was not found.")
        self.call_id = call_id


class InvalidCallDataError(VoiceCallError):
    """Lanzada cuando las validaciones de negocio fallan (ej. formato de teléfono o duración)."""
    pass
