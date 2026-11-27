"""
Módulo de Explicação ("Por que / Como") e Tratamento de Exceções.

Responsabilidade (Membro 3):
- Validar entradas do usuário e lançar mensagens claras para dados inválidos.
- Gerar a explicação técnica detalhando quais regras e fatos foram ativados.
- Tratar graciosamente casos sem conclusão ("Diagnóstico Inconclusivo").
"""

from __future__ import annotations

from typing import Any

from backend.engine.inference import MatchResult


class InvalidInputError(ValueError):
    """Erro lançado quando os sintomas enviados não são válidos."""


def validate_facts(
    confirmed_facts: Any,
    denied_facts: Any = None,
    valid_symptoms: set[str] | None = None,
) -> tuple[list[str], list[str]]:
    """Valida se os fatos recebidos são listas de strings válidas."""
    if not isinstance(confirmed_facts, list):
        raise InvalidInputError("O campo 'sintomas_confirmados' deve ser uma lista.")
    if denied_facts is not None and not isinstance(denied_facts, list):
        raise InvalidInputError("O campo 'sintomas_negados' deve ser uma lista.")

    denied_list = denied_facts or []
    if not confirmed_facts and not denied_list:
        raise InvalidInputError("Informe ao menos um sintoma para iniciar o diagnóstico.")

    if valid_symptoms is not None:
        unknown = [s for s in confirmed_facts + denied_list if s not in valid_symptoms]
        if unknown:
            raise InvalidInputError(
                f"Sintomas desconhecidos informados: {', '.join(unknown)}"
            )

    return confirmed_facts, denied_list


def build_explanation(
    matches: list[MatchResult],
    confirmed_facts: list[str],
    symptoms_catalog: dict[str, str] | None = None,
) -> dict[str, Any]:
    """
    Constrói a resposta final com diagnóstico, probabilidade e painel de justificativa.
    Se nenhuma regra atingir o critério mínimo, retorna fallback inconclusivo.
    """
    catalog = symptoms_catalog or {}

    if not matches:
        return {
            "status": "inconclusivo",
            "diagnostico": "Diagnóstico Inconclusivo - Consulte especialista manual",
            "solucao": "Os sintomas informados não correspondem com segurança a nenhuma regra mapeada.",
            "especialista": "Líder Mecânico / Avaliação Presencial",
            "probabilidade_percentual": 0,
            "explicacao": {
                "por_que": "Nenhuma regra da base de conhecimento atingiu o limite mínimo de correspondência.",
                "fatos_confirmados": [catalog.get(f, f) for f in confirmed_facts],
                "regras_ativadas": [],
            },
        }

    top = matches[0]
    rule = top.rule
    prob_pct = round(top.probability * 100)

    regras_ativadas = []
    for m in matches[:3]:
        regras_ativadas.append(
            {
                "id": m.rule["id"],
                "sistema": m.rule["sistema"],
                "diagnostico": m.rule["diagnostico"],
                "probabilidade_percentual": round(m.probability * 100),
                "fatos_correspondentes": m.matched_symptoms,
                "fatos_faltantes": m.missing_symptoms,
            }
        )

    return {
        "status": "concluido",
        "regra_principal": rule["id"],
        "sistema": rule["sistema"],
        "diagnostico": rule["diagnostico"],
        "solucao": rule.get("solucao", "Encaminhar para revisão especializada."),
        "especialista": rule.get("especialista", "Mecânico Geral"),
        "probabilidade_percentual": prob_pct,
        "explicacao": {
            "por_que": (
                f"A regra {rule['id']} ({rule['sistema']}) foi ativada com {prob_pct}% de confiança "
                f"porque {len(top.matched_symptoms)} de {len(rule['sintomas'])} sintomas esperados "
                f"foram confirmados."
            ),
            "fatos_confirmados": [
                {"codigo": f, "descricao": catalog.get(f, f)} for f in top.matched_symptoms
            ],
            "regras_ativadas": regras_ativadas,
        },
    }
