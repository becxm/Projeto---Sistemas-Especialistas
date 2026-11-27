"""
Persistência em SQLite para Histórico Operacional e Dashboard Estatístico.

Responsabilidade (Membro 1 & Membro 5):
- Registrar cada diagnóstico realizado pela oficina.
- Fornecer métricas agregadas (ex: % de chamados por sistema do veículo, taxa de assertividade).
- Suportar consultas paginadas e filtradas por sistema, data ou status.
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
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_diagnosticos_sistema ON diagnosticos(sistema)"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_diagnosticos_status ON diagnosticos(status)"
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
        """Registra um diagnóstico concluído ou inconclusivo no histórico."""
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

    def get_history(
        self,
        limit: int = 50,
        offset: int = 0,
        sistema: str | None = None,
        status: str | None = None,
    ) -> dict[str, Any]:
        """Retorna histórico com filtros dinâmicos e paginação."""
        query = "SELECT * FROM diagnosticos WHERE 1=1"
        count_query = "SELECT COUNT(*) FROM diagnosticos WHERE 1=1"
        params: list[Any] = []

        if sistema:
            query += " AND LOWER(sistema) = LOWER(?)"
            count_query += " AND LOWER(sistema) = LOWER(?)"
            params.append(sistema)

        if status:
            query += " AND LOWER(status) = LOWER(?)"
            count_query += " AND LOWER(status) = LOWER(?)"
            params.append(status)

        query += " ORDER BY id DESC LIMIT ? OFFSET ?"
        exec_params = params + [limit, offset]

        with self._connect() as conn:
            total = conn.execute(count_query, params).fetchone()[0]
            rows = conn.execute(query, exec_params).fetchall()

            registros = []
            for r in rows:
                item = dict(r)
                try:
                    item["sintomas"] = json.loads(item.get("sintomas_json", "[]"))
                except (json.JSONDecodeError, TypeError):
                    item["sintomas"] = []
                registros.append(item)

        return {
            "total": total,
            "limit": limit,
            "offset": offset,
            "registros": registros,
        }

    def get_stats(self, limit_recent: int = 10) -> dict[str, Any]:
        """Calcula métricas analíticas e sumarizações para o painel do dashboard."""
        with self._connect() as conn:
            total = conn.execute("SELECT COUNT(*) FROM diagnosticos").fetchone()[0]

            rows_by_system = conn.execute(
                """
                SELECT sistema, COUNT(*) as qtd, AVG(probabilidade) as media_prob
                FROM diagnosticos
                GROUP BY sistema
                ORDER BY qtd DESC
                """
            ).fetchall()

            por_sistema = [
                {
                    "sistema": row["sistema"],
                    "quantidade": row["qtd"],
                    "media_probabilidade": round(row["media_prob"] or 0, 1),
                    "percentual": round((row["qtd"] / total) * 100, 1) if total else 0,
                }
                for row in rows_by_system
            ]

            status_rows = conn.execute(
                """
                SELECT status, COUNT(*) as qtd
                FROM diagnosticos
                GROUP BY status
                """
            ).fetchall()
            status_dist = {r["status"]: r["qtd"] for r in status_rows}

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

        concluidos = status_dist.get("concluido", 0)
        taxa_resolucao = round((concluidos / total) * 100, 1) if total else 0.0

        return {
            "total_diagnosticos": total,
            "taxa_resolucao_percentual": taxa_resolucao,
            "status_distribuicao": status_dist,
            "por_sistema": por_sistema,
            "recentes": recentes,
        }

    def clear(self) -> None:
        """Limpa todos os registros do histórico (utilitário para testes/reset)."""
        with self._connect() as conn:
            conn.execute("DELETE FROM diagnosticos")
            conn.commit()
