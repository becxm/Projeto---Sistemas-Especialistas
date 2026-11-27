"""
Motor de Inferência (Encadeamento para Frente, Encadeamento para Trás e Tratamento de Incertezas).

Responsabilidade (Membro 1 & Membro 5):
- Receber fatos confirmados e negados pelo usuário durante a triagem.
- Avaliar quais regras da base de conhecimento são ativadas (parcial ou totalmente via forward chaining).
- Testar e refutar hipóteses específicas via backward chaining (encadeamento para trás).
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
        system_filter: str | None = None,
    ) -> list[MatchResult]:
        """
        Executa encadeamento para frente (forward chaining) sobre os fatos informados.
        Permite filtro opcional por subsistema do veículo.
        """
        confirmed = set(confirmed_facts)
        denied = set(denied_facts or [])
        results: list[MatchResult] = []

        for rule in self.rules:
            if system_filter and rule.get("sistema", "").lower() != system_filter.lower():
                continue

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

        # Resolução de conflito / desempate:
        # 1º maior cobertura percentual
        # 2º maior probabilidade calculada
        # 3º maior confiança intrínseca da regra
        # 4º maior número absoluto de sintomas correspondentes
        results.sort(
            key=lambda r: (
                r.coverage,
                r.probability,
                float(r.rule.get("confianca", 0.0)),
                len(r.matched_symptoms),
            ),
            reverse=True,
        )
        return results

    def backward_chaining(
        self,
        hypothesis_rule_id: str,
        confirmed_facts: list[str],
        denied_facts: list[str] | None = None,
    ) -> dict[str, Any]:
        """
        Executa encadeamento para trás (backward chaining) guiado por hipótese (Goal-Driven).
        Verifica se a hipótese diagnóstica indicada está confirmada, refutada ou pendente
        de perguntas complementares.
        """
        target_rule = next((r for r in self.rules if r["id"].upper() == hypothesis_rule_id.upper()), None)
        if not target_rule:
            return {
                "hipotese": hypothesis_rule_id,
                "status": "inexistente",
                "mensagem": f"Regra de hipótese '{hypothesis_rule_id}' não encontrada na base de conhecimento.",
            }

        confirmed = set(confirmed_facts)
        denied = set(denied_facts or [])
        rule_symptoms = target_rule["sintomas"]

        # Se algum sintoma requerido está negado, a hipótese é refutada
        refuting_symptoms = [s for s in rule_symptoms if s in denied]
        if refuting_symptoms:
            return {
                "hipotese": target_rule["id"],
                "sistema": target_rule["sistema"],
                "diagnostico": target_rule["diagnostico"],
                "status": "refutada",
                "motivo": f"A hipótese foi refutada porque os seguintes sintomas foram negados: {refuting_symptoms}",
                "sintomas_negados": refuting_symptoms,
                "probabilidade_percentual": 0,
            }

        matched = [s for s in rule_symptoms if s in confirmed]
        missing = [s for s in rule_symptoms if s not in confirmed]
        coverage = len(matched) / len(rule_symptoms)
        probability = round(coverage * float(target_rule.get("confianca", 0.85)) * 100)

        if not missing:
            return {
                "hipotese": target_rule["id"],
                "sistema": target_rule["sistema"],
                "diagnostico": target_rule["diagnostico"],
                "solucao": target_rule.get("solucao", ""),
                "especialista": target_rule.get("especialista", ""),
                "status": "confirmada",
                "probabilidade_percentual": probability,
                "sintomas_confirmados": matched,
                "sintomas_faltantes": [],
            }

        # Hipótese pendente: retorna quais perguntas específicas devem ser feitas
        proximas_perguntas = [
            {
                "sintoma": s,
                "pergunta": self.symptoms_catalog.get(s, f"O veículo apresenta '{s}'?"),
            }
            for s in missing
        ]

        return {
            "hipotese": target_rule["id"],
            "sistema": target_rule["sistema"],
            "diagnostico": target_rule["diagnostico"],
            "status": "pendente",
            "probabilidade_percentual": probability,
            "sintomas_confirmados": matched,
            "sintomas_faltantes": missing,
            "perguntas_para_confirmacao": proximas_perguntas,
        }

    def next_question(
        self,
        confirmed_facts: list[str],
        denied_facts: list[str] | None = None,
        system_filter: str | None = None,
    ) -> dict[str, str] | None:
        """
        Determina dinamicamente a próxima pergunta para a triagem interativa.
        Prioriza sintomas de regras ainda candidatas (não descartadas).
        """
        confirmed = set(confirmed_facts)
        denied = set(denied_facts or [])
        asked = confirmed | denied

        # Se já existe uma regra com 100% de cobertura, não precisa perguntar mais
        current_matches = self.evaluate(confirmed_facts, denied_facts, system_filter=system_filter)
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
            if system_filter and rule.get("sistema", "").lower() != system_filter.lower():
                continue
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

    def get_systems(self) -> list[str]:
        """Retorna lista única dos sistemas mecânicos cadastrados na base."""
        return sorted({rule.get("sistema", "Geral") for rule in self.rules})

    def get_rules_by_system(self, sistema: str | None = None) -> list[dict[str, Any]]:
        """Retorna todas as regras ou filtradas por subsistema do veículo."""
        if not sistema:
            return list(self.rules)
        return [r for r in self.rules if r.get("sistema", "").lower() == sistema.lower()]
