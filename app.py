"""
Ponto de entrada raiz da aplicação Flask.
Compatível com execuções a partir da raiz (python app.py) ou python -m backend.app.
"""

from __future__ import annotations

from backend.app import create_app

import os

app = create_app()

if __name__ == "__main__":
    debug_mode = os.environ.get("FLASK_DEBUG", "0").lower() in ("1", "true")
    app.run(debug=debug_mode, port=5000)
