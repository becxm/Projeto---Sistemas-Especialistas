"""Popula o banco local com atendimentos fictícios de demonstração."""
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if RAIZ not in sys.path:
    sys.path.insert(0, RAIZ)

from app import create_app  # noqa: E402
from backend.demo import popular_dados_demo  # noqa: E402


if __name__ == "__main__":
    app = create_app()
    total = popular_dados_demo(app.extensions["oficina"])
    print(f"{total} atendimentos de demonstração gravados com sucesso.")