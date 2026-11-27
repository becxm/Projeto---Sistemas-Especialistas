"""
Módulo de carregamento e exportação da Base de Conhecimento (JSON e CSV).

Responsabilidade (Membro 5):
- Ler regras e fatos de arquivos externos (.json ou .csv) sem alterar código-fonte.
- Validar a estrutura mínima de cada regra antes de entregar ao motor de inferência.
- Suportar persistência e exportação bidirecional de regras.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


class KnowledgeBaseError(Exception):
    """Exceção lançada quando a base de conhecimento está ausente ou inválida."""


def _validate_rule(rule: dict[str, Any], index: int) -> None:
    required_fields = ("id", "sistema", "sintomas", "diagnostico")
    for field in required_fields:
        if field not in rule or not rule[field]:
            raise KnowledgeBaseError(
                f"Regra na posição {index} está sem o campo obrigatório '{field}'."
            )
    if not isinstance(rule["sintomas"], list):
        raise KnowledgeBaseError(
            f"Regra '{rule['id']}' deve possuir 'sintomas' como lista."
        )


def load_from_json(file_path: str | Path) -> dict[str, Any]:
    """Carrega catálogo de sintomas e regras a partir de um arquivo JSON."""
    path = Path(file_path)
    if not path.exists():
        raise KnowledgeBaseError(f"Arquivo de base não encontrado: {path}")

    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as exc:
        raise KnowledgeBaseError(f"JSON inválido em {path}: {exc}") from exc

    regras = data.get("regras", [])
    if not regras:
        raise KnowledgeBaseError("A base JSON não contém nenhuma regra em 'regras'.")

    for idx, rule in enumerate(regras):
        _validate_rule(rule, idx)

    return {
        "sintomas_catalogo": data.get("sintomas_catalogo", {}),
        "regras": regras,
    }


def load_from_csv(file_path: str | Path) -> dict[str, Any]:
    """Carrega regras a partir de um arquivo CSV (sintomas separados por ';')."""
    path = Path(file_path)
    if not path.exists():
        raise KnowledgeBaseError(f"Arquivo CSV não encontrado: {path}")

    regras: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for idx, row in enumerate(reader):
            sintomas = [s.strip() for s in row.get("sintomas", "").split(";") if s.strip()]
            rule = {
                "id": row.get("id", f"CSV_{idx + 1}").strip(),
                "sistema": row.get("sistema", "Geral").strip(),
                "sintomas": sintomas,
                "diagnostico": row.get("diagnostico", "").strip(),
                "solucao": row.get("solucao", "").strip(),
                "especialista": row.get("especialista", "Mecânico Geral").strip(),
                "confianca": float(row.get("confianca", 0.8) or 0.8),
            }
            _validate_rule(rule, idx)
            regras.append(rule)

    if not regras:
        raise KnowledgeBaseError("O arquivo CSV não contém regras válidas.")

    return {"sintomas_catalogo": {}, "regras": regras}


def save_to_json(data: dict[str, Any], file_path: str | Path) -> None:
    """Salva catálogo de sintomas e regras em formato JSON estruturado."""
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def save_to_csv(rules: list[dict[str, Any]], file_path: str | Path) -> None:
    """Exporta lista de regras para arquivo CSV padronizado."""
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["id", "sistema", "sintomas", "diagnostico", "solucao", "especialista", "confianca"]
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for rule in rules:
            sintomas_str = ";".join(rule.get("sintomas", []))
            writer.writerow({
                "id": rule.get("id", ""),
                "sistema": rule.get("sistema", ""),
                "sintomas": sintomas_str,
                "diagnostico": rule.get("diagnostico", ""),
                "solucao": rule.get("solucao", ""),
                "especialista": rule.get("especialista", ""),
                "confianca": rule.get("confianca", 0.85),
            })
