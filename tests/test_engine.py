"""
Testes automatizados do Sistema Especialista.

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
from backend.loaders.kb_loader import load_from_json

KB_PATH = Path(__file__).resolve().parent.parent / "knowledge_base" / "regras_oficina.json"


class TestExpertSystem(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.kb = load_from_json(KB_PATH)
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
            stats = db.get_stats()
            self.assertEqual(stats["total_diagnosticos"], 1)
            self.assertEqual(stats["por_sistema"][0]["sistema"], "Freios")


if __name__ == "__main__":
    unittest.main()
