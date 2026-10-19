"""
Módulo Principal y Application Factory.

Principios SOLID y OOP aplicados:
- Application Factory Pattern (`create_app`): Permite instanciar la aplicación con distintas
  configuraciones (ej. SQLite en memoria para tests vs. PostgreSQL para producción).
- Composition Root: `create_app` actúa como el punto central donde se ensambla el grafo de
  dependencias (Database Engine -> Session -> Repository -> Service -> Blueprint).
- Global Exception Handler: Captura excepciones imprevistas (HTTP 500) manteniendo
  contratos JSON consistentes.
"""

from typing import Optional
from flask import Flask, Response, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.pool import StaticPool

from models import Base
from repositories import VoiceCallRepository
from routes import create_calls_blueprint
from services import VoiceCallService


def create_app(db_uri: Optional[str] = None) -> Flask:
    """
    Fábrica de aplicaciones de Flask.
    Configura la base de datos, ensambla dependencias y registra rutas.
    """
    app = Flask(__name__)
    
    # Configuración por defecto: SQLite en memoria usando StaticPool para persistir entre requests
    database_uri = db_uri or "sqlite:///:memory:"
    app.config["SQLALCHEMY_DATABASE_URI"] = database_uri

    # Configuración del Engine de SQLAlchemy
    if database_uri.startswith("sqlite"):
        engine = create_engine(
            database_uri,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool if ":memory:" in database_uri else None,
        )
    else:
        engine = create_engine(database_uri)

    # Creación de tablas de base de datos
    Base.metadata.create_all(engine)

    # Scoped session para asegurar aislamiento de transacciones por hilo/petición
    session_factory = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    db_session = scoped_session(session_factory)

    # --- Composición de Dependencias (Dependency Injection) ---
    repository = VoiceCallRepository(session=db_session)
    service = VoiceCallService(repository=repository)

    # Registro del Blueprint HTTP
    calls_bp = create_calls_blueprint(service=service)
    app.register_blueprint(calls_bp)

    # Manejo de cierre de sesión al terminar cada request
    @app.teardown_appcontext
    def shutdown_session(exception: Optional[BaseException] = None) -> None:
        db_session.remove()

    # Manejador global de excepciones imprevistas
    @app.errorhandler(500)
    def handle_internal_server_error(error: Exception) -> tuple[Response, int]:
        return jsonify({"error": "Ocurrió un error interno del servidor."}), 500

    @app.get("/health")
    def health_check() -> tuple[Response, int]:
        return jsonify({"status": "healthy", "service": "voice-call-telemetry"}), 200

    return app


if __name__ == "__main__":
    # Permite ejecutar directamente el archivo con: python app.py
    application = create_app()
    print("Iniciando Voice Call API en http://127.0.0.1:5000 ...")
    application.run(host="127.0.0.1", port=5000, debug=True)
