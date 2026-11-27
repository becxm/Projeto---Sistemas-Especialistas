"""
Testes automatizados do Motor de Inferência e Persistência do Sistema Especialista.

Executar na raiz do projeto:
    python -m unittest discover -s tests -v
ou com pytest:
    pytest -v
"""

import tempfile
import unittest
from pathlib import Path

from backend.database.db import DiagnosticDatabase
from backend.engine.inference import InferenceEngine
from backend.explanation.explainer import InvalidInputError, build_explanation, validate_facts
from backend.loaders.kb_loader import load_from_csv, load_from_json

KB_JSON_PATH = Path(__file__).resolve().parent.parent / "knowledge_base" / "regras_oficina.json"
KB_CSV_PATH = Path(__file__).resolve().parent.parent / "knowledge_base" / "regras_oficina.csv"


class TestExpertSystem(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.kb = load_from_json(KB_JSON_PATH)
        cls.engine = InferenceEngine(cls.kb)

    def test_knowledge_base_has_at_least_20_rules(self) -> None:
        self.assertGreaterEqual(len(self.kb["regras"]), 20)

    def test_rule_01_battery_diagnosis(self) -> None:
        facts = ["motor_nao_gira", "luzes_fracas", "clique_ao_virar_chave"]
        matches = self.engine.evaluate(facts)
        self.assertTrue(matches)
        self.assertEqual(matches[0].rule["id"], "R01")
        self.assertEqual(matches[0].coverage, 1.0)

        explanation = build_explanation(matches, facts, self.kb["sintomas_catalogo"])
        self.assertEqual(explanation["status"], "concluido")
        self.assertIn("R01", explanation["explicacao"]["por_que"])

    def test_backward_chaining_confirmed(self) -> None:
        facts = ["motor_nao_gira", "luzes_fracas", "clique_ao_virar_chave"]
        res = self.engine.backward_chaining("R01", facts)
        self.assertEqual(res["status"], "confirmada")
        self.assertEqual(res["hipotese"], "R01")
        self.assertEqual(res["sintomas_faltantes"], [])

    def test_backward_chaining_refuted(self) -> None:
        confirmed = ["motor_nao_gira"]
        denied = ["luzes_fracas"]
        res = self.engine.backward_chaining("R01", confirmed, denied)
        self.assertEqual(res["status"], "refutada")
        self.assertIn("luzes_fracas", res["sintomas_negados"])

    def test_backward_chaining_pending(self) -> None:
        confirmed = ["motor_nao_gira"]
        res = self.engine.backward_chaining("R01", confirmed)
        self.assertEqual(res["status"], "pendente")
        self.assertIn("luzes_fracas", res["sintomas_faltantes"])
        self.assertIn("clique_ao_virar_chave", res["sintomas_faltantes"])

    def test_system_filtering(self) -> None:
        systems = self.engine.get_systems()
        self.assertIn("Freios", systems)
        freio_rules = self.engine.get_rules_by_system("Freios")
        self.assertTrue(all(r["sistema"] == "Freios" for r in freio_rules))

    def test_csv_loader_parity(self) -> None:
        kb_csv = load_from_csv(KB_CSV_PATH)
        self.assertGreaterEqual(len(kb_csv["regras"]), 20)
        csv_engine = InferenceEngine(kb_csv)
        matches = csv_engine.evaluate(["ruido_agudo_freio"])
        self.assertTrue(matches)
        self.assertEqual(matches[0].rule["id"], "R09")

    def test_inconclusive_fallback(self) -> None:
        matches = self.engine.evaluate([])
        explanation = build_explanation(matches, [], self.kb["sintomas_catalogo"])
        self.assertEqual(explanation["status"], "inconclusivo")
        self.assertIn("Diagnóstico Inconclusivo", explanation["diagnostico"])

    def test_invalid_input_raises_error(self) -> None:
        with self.assertRaises(InvalidInputError):
            validate_facts("nao_e_lista")

        with self.assertRaises(InvalidInputError):
            validate_facts(["sintoma_inexistente"], valid_symptoms=set(self.kb["sintomas_catalogo"]))

    def test_database_logs_and_stats(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            db = DiagnosticDatabase(Path(tmpdir) / "test.db")
            db.log_diagnostic("Freios", "Pastilhas gastas", "R09", 90, ["ruido_agudo_freio"], "concluido")
            db.log_diagnostic("Motor", "Vela gasta", "R05", 85, ["carro_engasgando"], "concluido")

            stats = db.get_stats()
            self.assertEqual(stats["total_diagnosticos"], 2)
            self.assertEqual(stats["taxa_resolucao_percentual"], 100.0)

            history = db.get_history(limit=10, sistema="Freios")
            self.assertEqual(history["total"], 1)
            self.assertEqual(history["registros"][0]["regra_id"], "R09")


if __name__ == "__main__":
    unittest.main()
