"""
Motor de Inferência (Encadeamento para Frente + Tratamento de Incertezas).

Responsabilidade (Membro 1 & Membro 5):
- Receber fatos confirmados e negados pelo usuário durante a triagem.
- Avaliar quais regras da base de conhecimento são ativadas (parcial ou totalmente).
- Calcular a probabilidade/certeza combinando cobertura dos sintomas e confiança da regra.
- Sugerir dinamicamente a próxima pergunta mais relevante na triagem interativa.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class MatchResult:
    rule: dict[str, Any]
    matched_symptoms: list[str]
    missing_symptoms: list[str]
    coverage: float
    probability: float


class InferenceEngine:
    """Motor de inferência baseado em regras SE-ENTÃO com fator de certeza."""

    def __init__(self, knowledge_base: dict[str, Any], min_probability: float = 0.50) -> None:
        self.rules: list[dict[str, Any]] = knowledge_base.get("regras", [])
        self.symptoms_catalog: dict[str, str] = knowledge_base.get("sintomas_catalogo", {})
        self.min_probability = min_probability

    def evaluate(
        self,
        confirmed_facts: list[str],
        denied_facts: list[str] | None = None,
    ) -> list[MatchResult]:
        """Executa encadeamento para frente sobre os fatos informados."""
        confirmed = set(confirmed_facts)
        denied = set(denied_facts or [])
        results: list[MatchResult] = []

        for rule in self.rules:
            rule_symptoms = rule["sintomas"]
            # Se algum sintoma obrigatório da regra foi explicitamente negado, descarta a regra
            if any(s in denied for s in rule_symptoms):
                continue

            matched = [s for s in rule_symptoms if s in confirmed]
            if not matched:
                continue

            missing = [s for s in rule_symptoms if s not in confirmed]
            coverage = len(matched) / len(rule_symptoms)
            base_confidence = float(rule.get("confianca", 0.85))
            probability = round(coverage * base_confidence, 4)

            if probability >= self.min_probability:
                results.append(
                    MatchResult(
                        rule=rule,
                        matched_symptoms=matched,
                        missing_symptoms=missing,
                        coverage=round(coverage, 4),
                        probability=probability,
                    )
                )

        results.sort(key=lambda r: (r.coverage, r.probability), reverse=True)
        return results

    def next_question(
        self,
        confirmed_facts: list[str],
        denied_facts: list[str] | None = None,
    ) -> dict[str, str] | None:
        """
        Determina dinamicamente a próxima pergunta para a triagem interativa.
        Prioriza sintomas de regras ainda candidatas (não descartadas).
        """
        confirmed = set(confirmed_facts)
        denied = set(denied_facts or [])
        asked = confirmed | denied

        # Se já existe uma regra com 100% de cobertura, não precisa perguntar mais
        current_matches = self.evaluate(confirmed_facts, denied_facts)
        if current_matches and current_matches[0].coverage == 1.0:
            return None

        # Prioriza completar regras parcialmente ativadas
        for match in current_matches:
            for symptom in match.missing_symptoms:
                if symptom not in asked:
                    return {
                        "sintoma": symptom,
                        "pergunta": self.symptoms_catalog.get(
                            symptom, f"O veículo apresenta '{symptom}'?"
                        ),
                    }

        # Caso nenhuma regra tenha sido ativada ainda, busca o próximo sintoma não perguntado
        for rule in self.rules:
            if any(s in denied for s in rule["sintomas"]):
                continue
            for symptom in rule["sintomas"]:
                if symptom not in asked:
                    return {
                        "sintoma": symptom,
                        "pergunta": self.symptoms_catalog.get(
                            symptom, f"O veículo apresenta '{symptom}'?"
                        ),
                    }

        return None
