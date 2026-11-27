"""
Ponto de entrada da aplicação Flask.

Para executar a partir da raiz do projeto:
    python -m backend.app
"""

from __future__ import annotations

from pathlib import Path

from flask import Flask, send_from_directory
from flask_cors import CORS

from backend.api.routes import api_bp
from backend.database.db import DiagnosticDatabase
from backend.engine.inference import InferenceEngine
from backend.loaders.kb_loader import load_from_json

BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"
KB_PATH = BASE_DIR / "knowledge_base" / "regras_oficina.json"
DB_PATH = BASE_DIR / "data" / "oficina.db"


def create_app(kb_path: Path = KB_PATH, db_path: Path = DB_PATH) -> Flask:
    app = Flask(__name__, static_folder=str(FRONTEND_DIR), static_url_path="")
    CORS(app)

    kb = load_from_json(kb_path)
    engine = InferenceEngine(kb)
    db = DiagnosticDatabase(db_path)
    app.config["ENGINE"] = engine
    app.config["DB"] = db
    app.extensions["oficina"] = db

    app.register_blueprint(api_bp)

    @app.get("/")
    def index():
        return send_from_directory(FRONTEND_DIR, "index.html")

    return app


if __name__ == "__main__":
    application = create_app()
    application.run(debug=True, port=5000)
