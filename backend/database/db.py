"""
Persistência em SQLite para Histórico Operacional e Dashboard Estatístico.

Responsabilidade (Membro 1 & Membro 5):
- Registrar cada diagnóstico realizado pela oficina.
- Fornecer métricas agregadas (ex: % de chamados por sistema do veículo).
"""

from __future__ import annotations

from contextlib import contextmanager
import json
import sqlite3
from pathlib import Path
from typing import Any, Iterator


class DiagnosticDatabase:
    """Gerencia o banco SQLite de histórico de diagnósticos."""

    def __init__(self, db_path: str | Path = "data/oficina.db") -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    @contextmanager
    def _connect(self) -> Iterator[sqlite3.Connection]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS diagnosticos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sistema TEXT NOT NULL,
                    diagnostico TEXT NOT NULL,
                    regra_id TEXT,
                    probabilidade INTEGER NOT NULL,
                    sintomas_json TEXT NOT NULL,
                    status TEXT NOT NULL,
                    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            conn.commit()

    def log_diagnostic(
        self,
        sistema: str,
        diagnostico: str,
        regra_id: str | None,
        probabilidade: int,
        sintomas: list[str],
        status: str,
    ) -> int:
        with self._connect() as conn:
            cursor = conn.execute(
                """
                INSERT INTO diagnosticos (sistema, diagnostico, regra_id, probabilidade, sintomas_json, status)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    sistema,
                    diagnostico,
                    regra_id,
                    probabilidade,
                    json.dumps(sintomas, ensure_ascii=False),
                    status,
                ),
            )
            conn.commit()
            return int(cursor.lastrowid)

    def get_stats(self, limit_recent: int = 10) -> dict[str, Any]:
        with self._connect() as conn:
            total = conn.execute("SELECT COUNT(*) FROM diagnosticos").fetchone()[0]

            rows_by_system = conn.execute(
                """
                SELECT sistema, COUNT(*) as qtd
                FROM diagnosticos
                GROUP BY sistema
                ORDER BY qtd DESC
                """
            ).fetchall()

            por_sistema = [
                {
                    "sistema": row["sistema"],
                    "quantidade": row["qtd"],
                    "percentual": round((row["qtd"] / total) * 100, 1) if total else 0,
                }
                for row in rows_by_system
            ]

            recent_rows = conn.execute(
                """
                SELECT id, sistema, diagnostico, regra_id, probabilidade, status, criado_em
                FROM diagnosticos
                ORDER BY id DESC
                LIMIT ?
                """,
                (limit_recent,),
            ).fetchall()

            recentes = [dict(row) for row in recent_rows]

        return {
            "total_diagnosticos": total,
            "por_sistema": por_sistema,
            "recentes": recentes,
        }
