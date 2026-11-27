"""
Ponto de entrada raiz da aplicação Flask.
Compatível com execuções a partir da raiz (python app.py) ou python -m backend.app.
"""

from __future__ import annotations

from backend.app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True, port=5000)
