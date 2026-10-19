# Voice Call Telemetry REST API

Ejemplo de arquitectura limpia, modular y orientada a objetos (SOLID) para un API REST en Flask y SQLAlchemy 2.0, diseñado como material de estudio para roles de **Forward Deployed Engineer (FDE)**.

---

## 🏛️ Arquitectura y Principios de Diseño

```
voice_call_api/
├── exceptions.py       # Excepciones de Dominio (SRP, Desacoplamiento de HTTP)
├── models.py           # Modelos Declarativos SQLAlchemy 2.0 (SRP)
├── repositories.py     # Patrón Repository / Acceso a Datos (SRP, Abstracción de BD)
├── services.py         # Lógica de Negocio y Validaciones (SRP, Dependency Injection)
├── routes.py           # Controladores y Endpoints HTTP Flask (SRP, Blueprint Factory)
├── app.py              # Application Factory y Composition Root (DIP)
├── test_api.py         # Pruebas integrales automatizadas con pytest
└── requirements.txt    # Dependencias del proyecto
```

### Principios SOLID Aplicados

1. **Single Responsibility Principle (SRP):**
   - `models.py`: Solo define la estructura de datos y el mapeo ORM.
   - `repositories.py`: Solo ejecuta sentencias de consulta y persistencia en la base de datos.
   - `services.py`: Solo contiene reglas de validación de negocio y orquestación.
   - `routes.py`: Solo maneja el protocolo HTTP (códigos 200/201/400/404/500, parsing JSON).

2. **Dependency Inversion / Injection (DIP):**
   - `VoiceCallService` recibe su repositorio a través del constructor `__init__`.
   - `create_calls_blueprint` recibe la instancia del servicio a través de un factory method.
   - El punto de ensamblaje (Composition Root) reside en `create_app()` en [app.py](file:///d:/workspace/voice_call_api/app.py).

3. **Manejo de Errores y Robustez:**
   - La capa de servicio lanza excepciones semánticas (`CallNotFoundError`, `InvalidCallDataError`).
   - La capa de presentación las traduce limpiamente a respuestas JSON con sus respectivos códigos HTTP.

---

## 🚀 Puesta en Marcha

### 1. Activar entorno virtual e instalar dependencias
```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Ejecutar pruebas unitarias / de integración
```powershell
pytest -v
```

### 3. Iniciar el servidor
```powershell
python app.py
```
El servidor quedará disponible en: `http://127.0.0.1:5000`

---

## 📡 Endpoints del API

| Método | Endpoint | Descripción | Códigos HTTP |
|---|---|---|---|
| `GET` | `/health` | Chequeo de estado | `200` |
| `POST` | `/api/calls` | Crear registro de llamada | `201`, `400` |
| `GET` | `/api/calls` | Listar llamadas (`?limit=50&offset=0`) | `200`, `400` |
| `GET` | `/api/calls/<id>` | Detalle de llamada | `200`, `404` |
| `PATCH` | `/api/calls/<id>` | Actualizar llamada | `200`, `400`, `404` |
| `DELETE` | `/api/calls/<id>` | Eliminar llamada | `200`, `404` |