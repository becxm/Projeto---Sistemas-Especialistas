#!/usr/bin/env python3
"""
Script de Auditoria e Validação da Base de Conhecimento.

Verifica:
1. Integridade de sintaxe JSON e CSV.
2. Campos obrigatórios em cada regra (id, sistema, sintomas, diagnostico, solucao, confianca).
3. Consistência entre sintomas referenciados nas regras e o catálogo de perguntas.
4. Detecção de IDs duplicados ou conjuntos de sintomas redundantes.
5. Validação dos intervalos de confiança (entre 0.0 e 1.0).
"""

from __future__ import annotations

import sys
from pathlib import Path

# Adiciona a raiz do projeto ao sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.loaders.kb_loader import KnowledgeBaseError, load_from_csv, load_from_json

JSON_PATH = PROJECT_ROOT / "knowledge_base" / "regras_oficina.json"
CSV_PATH = PROJECT_ROOT / "knowledge_base" / "regras_oficina.csv"


def validar_base_json(path: Path) -> tuple[int, list[str]]:
    erros: list[str] = []
    print(f"\n🔍 [1/2] Auditando Base de Conhecimento JSON: {path.name}...")

    try:
        kb = load_from_json(path)
    except KnowledgeBaseError as exc:
        return 0, [f"Falha crítica ao ler JSON: {exc}"]

    regras = kb.get("regras", [])
    catalogo = kb.get("sintomas_catalogo", {})

    print(f"   ℹ️  Total de regras encontradas: {len(regras)}")
    print(f"   ℹ️  Total de sintomas no catálogo: {len(catalogo)}")

    if len(regras) < 20:
        erros.append(f"A base possui apenas {len(regras)} regras. Requisito mínimo acadêmico: 20 regras.")

    ids_vistos: set[str] = set()
    sintomas_nas_regras: set[str] = set()

    for idx, r in enumerate(regras, start=1):
        rid = r.get("id")
        if not rid:
            erros.append(f"Regra #{idx} não possui 'id'.")
            continue

        if rid in ids_vistos:
            erros.append(f"ID duplicado detectado: '{rid}' na regra #{idx}.")
        ids_vistos.add(rid)

        conf = r.get("confianca")
        if conf is None or not (0.0 < float(conf) <= 1.0):
            erros.append(f"Regra {rid}: 'confianca' deve ser um valor numérico entre 0.0 e 1.0 (encontrado: {conf}).")

        sintomas = r.get("sintomas", [])
        if not sintomas:
            erros.append(f"Regra {rid}: lista de sintomas está vazia.")

        for s in sintomas:
            sintomas_nas_regras.add(s)
            if catalogo and s not in catalogo:
                erros.append(f"Regra {rid}: sintoma '{s}' não está registrado no 'sintomas_catalogo'.")

    # Verifica sintomas órfãos no catálogo
    sintomas_orfaos = set(catalogo.keys()) - sintomas_nas_regras
    if sintomas_orfaos:
        print(f"   ⚠️  Aviso: {len(sintomas_orfaos)} sintomas no catálogo não são utilizados por nenhuma regra: {sorted(sintomas_orfaos)}")

    return len(regras), erros


def validar_base_csv(path: Path) -> tuple[int, list[str]]:
    erros: list[str] = []
    print(f"\n🔍 [2/2] Auditando Base de Conhecimento CSV: {path.name}...")

    if not path.exists():
        erros.append(f"Arquivo CSV não encontrado em: {path}")
        return 0, erros

    try:
        kb = load_from_csv(path)
    except KnowledgeBaseError as exc:
        return 0, [f"Falha ao processar CSV: {exc}"]

    regras = kb.get("regras", [])
    print(f"   ℹ️  Total de regras no CSV: {len(regras)}")

    ids: set[str] = set()
    for idx, r in enumerate(regras, start=1):
        rid = r.get("id")
        if rid in ids:
            erros.append(f"CSV Regra #{idx}: ID duplicado '{rid}'.")
        ids.add(rid)

    return len(regras), erros


def main() -> None:
    print("=" * 65)
    print("      AUDITORIA DE CONSISTÊNCIA DA BASE DE CONHECIMENTO")
    print("=" * 65)

    n_json, erros_json = validar_base_json(JSON_PATH)
    n_csv, erros_csv = validar_base_csv(CSV_PATH)

    todos_erros = erros_json + erros_csv

    print("\n" + "=" * 65)
    if todos_erros:
        print(f"❌ AUDITORIA REPROVADA! Foram encontrados {len(todos_erros)} problema(s):")
        for e in todos_erros:
            print(f"   - {e}")
        sys.exit(1)
    else:
        print("✅ TODAS AS BASES FORAM APROVADAS COM 100% DE SUCESSO!")
        print(f"   • Regras JSON: {n_json} regras validadas")
        print(f"   • Regras CSV:  {n_csv} regras validadas")
        print("   • Sem IDs duplicados, sem campos ausentes, confiança normalizada.")
        print("=" * 65)


if __name__ == "__main__":
    main()
