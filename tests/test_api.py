"""
Testes automatizados da API REST do Sistema Especialista.

Cobre os endpoints:
- GET /api/health
- GET /api/symptoms
- GET /api/systems
- POST /api/triage/next
- POST /api/triage/hypothesis
- POST /api/diagnose
- GET /api/stats
- GET /api/diagnostics/history
- POST /api/knowledge-base/reload
"""

import tempfile
import unittest
from pathlib import Path

from backend.app import create_app

KB_PATH = Path(__file__).resolve().parent.parent / "knowledge_base" / "regras_oficina.json"


class TestAPIEndpoints(unittest.TestCase):
    def setUp(self) -> None:
        self.tmpdir = tempfile.TemporaryDirectory()
        self.test_db = Path(self.tmpdir.name) / "test_api.db"
        self.app = create_app(kb_path=KB_PATH, db_path=self.test_db)
        self.client = self.app.test_client()

    def tearDown(self) -> None:
        self.tmpdir.cleanup()

    def test_health_check(self) -> None:
        resp = self.client.get("/api/health")
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data["status"], "ok")
        self.assertGreaterEqual(data["total_regras"], 20)
        self.assertTrue(len(data["sistemas_mapeados"]) > 0)

    def test_list_symptoms_and_systems(self) -> None:
        resp_sym = self.client.get("/api/symptoms")
        self.assertEqual(resp_sym.status_code, 200)
        self.assertIn("motor_nao_gira", resp_sym.get_json()["sintomas"])

        resp_sys = self.client.get("/api/systems")
        self.assertEqual(resp_sys.status_code, 200)
        self.assertIn("Freios", resp_sys.get_json()["sistemas"])

    def test_triage_next_question(self) -> None:
        payload = {"sintomas_confirmados": ["motor_nao_gira"], "sintomas_negados": []}
        resp = self.client.post("/api/triage/next", json=payload)
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertFalse(data["finalizado"])
        self.assertIsNotNone(data["proxima_pergunta"])

    def test_triage_hypothesis_endpoint(self) -> None:
        # Testa hipótese R01 com sintomas parciais
        payload = {"regra_id": "R01", "sintomas_confirmados": ["motor_nao_gira"], "sintomas_negados": []}
        resp = self.client.post("/api/triage/hypothesis", json=payload)
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data["status"], "pendente")
        self.assertIn("luzes_fracas", data["sintomas_faltantes"])

    def test_diagnose_endpoint(self) -> None:
        payload = {
            "sintomas_confirmados": ["motor_nao_gira", "luzes_fracas", "clique_ao_virar_chave"],
            "sintomas_negados": [],
        }
        resp = self.client.post("/api/diagnose", json=payload)
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data["status"], "concluido")
        self.assertEqual(data["regra_principal"], "R01")
        self.assertGreaterEqual(data["probabilidade_percentual"], 90)

    def test_diagnose_invalid_input(self) -> None:
        resp = self.client.post("/api/diagnose", json={"sintomas_confirmados": ["sintoma_ficticio"]})
        self.assertEqual(resp.status_code, 400)
        self.assertIn("erro", resp.get_json())

    def test_stats_and_history(self) -> None:
        # Realiza um diagnóstico para popular
        self.client.post("/api/diagnose", json={
            "sintomas_confirmados": ["ruido_agudo_freio"],
            "sintomas_negados": [],
        })

        resp_stats = self.client.get("/api/stats")
        self.assertEqual(resp_stats.status_code, 200)
        self.assertEqual(resp_stats.get_json()["total_diagnosticos"], 1)

        resp_hist = self.client.get("/api/diagnostics/history?limit=10")
        self.assertEqual(resp_hist.status_code, 200)
        hist_data = resp_hist.get_json()
        self.assertEqual(hist_data["total"], 1)
        self.assertEqual(hist_data["registros"][0]["regra_id"], "R09")

    def test_reload_knowledge_base_json(self) -> None:
        resp = self.client.post("/api/knowledge-base/reload", json={"formato": "json"})
        self.assertEqual(resp.status_code, 200)
        self.assertIn("recarregada com sucesso", resp.get_json()["mensagem"])


if __name__ == "__main__":
    unittest.main()
