#!/usr/bin/env python3
"""
Terminal CLI - Triagem e Diagnóstico Interativo do Sistema Especialista.

Permite simular o atendimento ao cliente diretamente via terminal,
executando o motor de inferência, encadeamento para frente/trás e
exibindo o painel explicativo ('Por que / Como').
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.database.db import DiagnosticDatabase
from backend.engine.inference import InferenceEngine
from backend.explanation.explainer import build_explanation
from backend.loaders.kb_loader import load_from_csv, load_from_json

DEFAULT_KB = PROJECT_ROOT / "knowledge_base" / "regras_oficina.json"
DEFAULT_DB = PROJECT_ROOT / "data" / "oficina.db"


def run_interactive_triage(engine: InferenceEngine, db: DiagnosticDatabase, sistema: str | None = None) -> None:
    print("\n" + "=" * 68)
    print("      OFICINA MECÂNICA — TRIAGEM E DIAGNÓSTICO INTELIGENTE")
    print("=" * 68)
    if sistema:
        print(f"🔧 Subsistema Selecionado: {sistema}")
    print("Responda: [S] Sim  |  [N] Não  |  [P] Pular/Não Sei  |  [C] Concluir agora\n")

    confirmed: list[str] = []
    denied: list[str] = []
    step = 1

    while True:
        next_q = engine.next_question(confirmed, denied, system_filter=sistema)
        if not next_q:
            print("\n🏁 Não há mais perguntas pendentes para as regras candidatas.")
            break

        sintoma = next_q["sintoma"]
        pergunta = next_q["pergunta"]

        print(f"[{step:02d}] {pergunta}")
        try:
            resp = input("     Sua resposta (S/N/P/C): ").strip().upper()
        except (KeyboardInterrupt, EOFError):
            print("\n\nOperação cancelada pelo usuário.")
            return

        if resp == "S":
            confirmed.append(sintoma)
            step += 1
        elif resp == "N":
            denied.append(sintoma)
            step += 1
        elif resp == "P":
            step += 1
        elif resp == "C":
            break
        else:
            print("     ⚠️ Opção inválida! Digite 'S', 'N', 'P' ou 'C'.")

    print("\n⏳ Executando Motor de Inferência e Gerando Diagnóstico...")
    matches = engine.evaluate(confirmed, denied, system_filter=sistema)
    result = build_explanation(matches, confirmed, engine.symptoms_catalog)

    print("\n" + "=" * 68)
    print(f"📊 RESULTADO: {result['status'].upper()}")
    print("=" * 68)
    print(f"• Diagnóstico Principal : {result['diagnostico']}")
    print(f"• Subsistema Afetado    : {result.get('sistema', 'N/D')}")
    print(f"• Probabilidade Calculada: {result['probabilidade_percentual']}%")
    print(f"• Especialista Indicado : {result.get('especialista', 'N/D')}")
    print(f"• Solução Recomendada   : {result.get('solucao', 'N/D')}")

    print("\n📝 PAINEL EXPLICATIVO ('Por que / Como'):")
    explicacao = result.get("explicacao", {})
    print(f"  Justificativa: {explicacao.get('por_que', '')}")

    fatos = explicacao.get("fatos_confirmados", [])
    if fatos:
        print("  Fatos Confirmados na Triagem:")
        for f in fatos:
            desc = f.get("descricao") if isinstance(f, dict) else f
            print(f"    ✓ {desc}")

    regras_at = explicacao.get("regras_ativadas", [])
    if regras_at:
        print("\n  Cadeia de Regras Ativadas:")
        for r in regras_at:
            print(f"    - [{r['id']}] {r['diagnostico']} ({r['probabilidade_percentual']}%)")

    # Registra no SQLite
    db.log_diagnostic(
        sistema=result.get("sistema", "Indefinido"),
        diagnostico=result["diagnostico"],
        regra_id=result.get("regra_principal"),
        probabilidade=result["probabilidade_percentual"],
        sintomas=confirmed,
        status=result["status"],
    )
    print("\n💾 Diagnóstico registrado com sucesso no banco de dados operacional.")
    print("=" * 68)


def run_backward_chaining_cli(engine: InferenceEngine, regra_id: str) -> None:
    print("\n" + "=" * 68)
    print(f"      ENCADEAMENTO PARA TRÁS (TESTE DA HIPÓTESE '{regra_id.upper()}')")
    print("=" * 68)

    target_rule = next((r for r in engine.rules if r["id"].upper() == regra_id.upper()), None)
    if not target_rule:
        print(f"❌ Hipótese '{regra_id}' não encontrada na base de conhecimento.")
        return

    print(f"• Hipótese     : [{target_rule['id']}] {target_rule['diagnostico']}")
    print(f"• Subsistema   : {target_rule['sistema']}")
    print(f"• Confiança Max: {int(target_rule.get('confianca', 0.85) * 100)}%")
    print("\nVerificando sintomas necessários para confirmar ou refutar a hipótese:\n")

    confirmed: list[str] = []
    denied: list[str] = []

    for s in target_rule["sintomas"]:
        pergunta = engine.symptoms_catalog.get(s, f"O veículo apresenta '{s}'?")
        print(f"• {pergunta}")
        try:
            resp = input("  (S/N): ").strip().upper()
        except (KeyboardInterrupt, EOFError):
            print("\nCancelado.")
            return

        if resp == "S":
            confirmed.append(s)
        else:
            denied.append(s)
            print(f"  ❌ Hipótese '{target_rule['id']}' refutada (sintoma obrigatório ausente).")
            break

    res = engine.backward_chaining(regra_id, confirmed, denied)
    print("\n" + "=" * 68)
    print(f"CONCLUSÃO DA HIPÓTESE: {res['status'].upper()}")
    print(f"Probabilidade: {res.get('probabilidade_percentual', 0)}%")
    if res['status'] == "confirmada":
        print(f"✅ Hipótese CONFIRMADA com sucesso! Diagnóstico: {res['diagnostico']}")
        print(f"Solução: {res.get('solucao', '')}")
    elif res['status'] == "refutada":
        print(f"🚫 Hipótese REFUTADA: {res.get('motivo', '')}")
    print("=" * 68)


def main() -> None:
    parser = argparse.ArgumentParser(description="CLI de Triagem do Sistema Especialista.")
    parser.add_argument("--csv", action="store_true", help="Carrega regras a partir do arquivo CSV.")
    parser.add_argument("--sistema", type=str, default=None, help="Filtra triagem por subsistema.")
    parser.add_argument("--hipotese", type=str, default=None, help="Executa backward chaining para uma regra específica (ex: R01).")
    args = parser.parse_args()

    if args.csv:
        csv_file = PROJECT_ROOT / "knowledge_base" / "regras_oficina.csv"
        kb = load_from_csv(csv_file)
        # carrega catálogo de perguntas do json
        if DEFAULT_KB.exists():
            kb_json = load_from_json(DEFAULT_KB)
            kb["sintomas_catalogo"] = kb_json.get("sintomas_catalogo", {})
    else:
        kb = load_from_json(DEFAULT_KB)

    engine = InferenceEngine(kb)
    db = DiagnosticDatabase(DEFAULT_DB)

    if args.hipotese:
        run_backward_chaining_cli(engine, args.hipotese)
    else:
        run_interactive_triage(engine, db, sistema=args.sistema)


if __name__ == "__main__":
    main()
