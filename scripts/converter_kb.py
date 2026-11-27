#!/usr/bin/env python3
"""
Utilitário de Conversão Bidirecional da Base de Conhecimento (JSON <-> CSV).

Permite aos engenheiros de conhecimento exportar e importar regras
entre formato tabular (editável em Excel/Planilhas) e JSON estruturado.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.loaders.kb_loader import (
    KnowledgeBaseError,
    load_from_csv,
    load_from_json,
    save_to_csv,
    save_to_json,
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Conversor bidirecional da Base de Conhecimento (JSON <-> CSV)."
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--json-to-csv", action="store_true", help="Converte JSON para CSV.")
    group.add_argument("--csv-to-json", action="store_true", help="Converte CSV para JSON.")

    parser.add_argument(
        "--input",
        type=Path,
        default=None,
        help="Caminho do arquivo de entrada (se omitido, usa caminho padrão da base).",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Caminho do arquivo de saída gerado.",
    )

    args = parser.parse_args()

    default_json = PROJECT_ROOT / "knowledge_base" / "regras_oficina.json"
    default_csv = PROJECT_ROOT / "knowledge_base" / "regras_oficina.csv"

    try:
        if args.json_to_csv:
            in_file = args.input or default_json
            out_file = args.output or default_csv
            print(f"🔄 Convertendo JSON ({in_file.name}) -> CSV ({out_file.name})...")
            kb = load_from_json(in_file)
            save_to_csv(kb["regras"], out_file)
            print(f"✅ Sucesso: {len(kb['regras'])} regras exportadas para '{out_file}'.")

        elif args.csv_to_json:
            in_file = args.input or default_csv
            out_file = args.output or default_json
            print(f"🔄 Convertendo CSV ({in_file.name}) -> JSON ({out_file.name})...")
            kb_csv = load_from_csv(in_file)

            # Tenta preservar catálogo de sintomas se o JSON de destino já existir
            catalogo = {}
            if out_file.exists():
                try:
                    existing = load_from_json(out_file)
                    catalogo = existing.get("sintomas_catalogo", {})
                except KnowledgeBaseError:
                    pass

            data = {
                "sintomas_catalogo": catalogo,
                "regras": kb_csv["regras"],
            }
            save_to_json(data, out_file)
            print(f"✅ Sucesso: {len(kb_csv['regras'])} regras importadas para '{out_file}'.")

    except KnowledgeBaseError as exc:
        print(f"❌ Erro durante a conversão: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
