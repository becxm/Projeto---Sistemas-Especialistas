"""
Módulo de compatibilidade para carga de dados demonstrativos.
"""

from __future__ import annotations

from typing import Any
from scripts.popular_historico import popular_banco


def popular_dados_demo(db: Any = None, total: int = 35) -> int:
    """Popula atendimentos fictícios de demonstração no banco de dados."""
    popular_banco(total_registros=total, reset=False)
    return total
