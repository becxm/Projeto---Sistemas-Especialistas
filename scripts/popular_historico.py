#!/usr/bin/env python3
"""
Script de Carga e Geração de Dados Estatísticos no SQLite.

Popula a tabela 'diagnosticos' com um histórico de atendimentos
distribuídos realisticamente entre os sistemas do veículo,
permitindo a visualização imediata de gráficos no Dashboard.
"""

from __future__ import annotations

import random
import sys
from datetime import datetime, timedelta
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.database.db import DiagnosticDatabase
from backend.loaders.kb_loader import load_from_json

KB_PATH = PROJECT_ROOT / "knowledge_base" / "regras_oficina.json"
DB_PATH = PROJECT_ROOT / "data" / "oficina.db"


def popular_banco(total_registros: int = 40, reset: bool = False) -> None:
    print("=" * 65)
    print("      GERADOR DE MASSA DE DADOS PARA HISTÓRICO E DASHBOARD")
    print("=" * 65)

    kb = load_from_json(KB_PATH)
    regras = kb.get("regras", [])
    if not regras:
        print("❌ Nenhuma regra disponível na base de conhecimento.")
        return

    db = DiagnosticDatabase(DB_PATH)
    if reset:
        print("🧹 Limpando histórico anterior...")
        db.clear()

    now = datetime.now()
    print(f"⚙️  Inserindo {total_registros} diagnósticos simulados no banco '{DB_PATH.name}'...")

    with db._connect() as conn:
        for i in range(total_registros):
            # 85% de diagnósticos com conclusão positiva e 15% inconclusivos
            if random.random() < 0.88:
                regra = random.choice(regras)
                sistema = regra["sistema"]
                diagnostico = regra["diagnostico"]
                regra_id = regra["id"]
                probabilidade = random.randint(75, 98)
                sintomas = regra["sintomas"]
                status = "concluido"
            else:
                sistema = random.choice(["Elétrica & Ignição", "Motor & Câmbio", "Suspensão & Direção", "Freios"])
                diagnostico = "Diagnóstico Inconclusivo - Consulte especialista manual"
                regra_id = None
                probabilidade = random.randint(10, 45)
                sintomas = ["sintoma_generico_nao_conclusivo"]
                status = "inconclusivo"

            # Distribui datas ao longo dos últimos 30 dias
            dias_atras = random.randint(0, 30)
            horas_atras = random.randint(0, 23)
            minutos_atras = random.randint(0, 59)
            data_registro = (now - timedelta(days=dias_atras, hours=horas_atras, minutes=minutos_atras)).strftime("%Y-%m-%d %H:%M:%S")

            conn.execute(
                """
                INSERT INTO diagnosticos (sistema, diagnostico, regra_id, probabilidade, sintomas_json, status, criado_em)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    sistema,
                    diagnostico,
                    regra_id,
                    probabilidade,
                    str(sintomas),
                    status,
                    data_registro,
                ),
            )
        conn.commit()

    stats = db.get_stats()
    print("✅ Carga concluída com sucesso!")
    print(f"   • Total de registros acumulados : {stats['total_diagnosticos']}")
    print(f"   • Taxa de resolutividade geral : {stats['taxa_resolucao_percentual']}%")
    print("\n📊 Distribuição por Subsistema:")
    for s in stats["por_sistema"]:
        print(f"   - {s['sistema']:<25}: {s['quantidade']:>3} chamados ({s['percentual']}%)")
    print("=" * 65)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Popula histórico no SQLite.")
    parser.add_argument("--qtd", type=int, default=40, help="Quantidade de registros a inserir.")
    parser.add_argument("--reset", action="store_true", help="Limpa a tabela antes de popular.")
    args = parser.parse_args()

    popular_banco(total_registros=args.qtd, reset=args.reset)
