"""
Rotas da API REST (Flask Blueprint).

Responsabilidade (Membro 1 & Membro 4):
- Expor endpoints para triagem interativa, diagnóstico, explicação e dashboard.
"""

from __future__ import annotations

from flask import Blueprint, current_app, jsonify, request

from backend.explanation.explainer import (
    InvalidInputError,
    build_explanation,
    validate_facts,
)

api_bp = Blueprint("api", __name__, url_prefix="/api")


@api_bp.get("/health")
def health():
    engine = current_app.config["ENGINE"]
    return jsonify({"status": "ok", "total_regras": len(engine.rules)})


@api_bp.get("/symptoms")
def list_symptoms():
    engine = current_app.config["ENGINE"]
    return jsonify({"sintomas": engine.symptoms_catalog})


@api_bp.post("/triage/next")
def triage_next():
    """Retorna a próxima pergunta da triagem interativa ou indica que já há conclusão."""
    payload = request.get_json(silent=True) or {}
    confirmed = payload.get("sintomas_confirmados", [])
    denied = payload.get("sintomas_negados", [])

    if not isinstance(confirmed, list) or not isinstance(denied, list):
        return jsonify({"erro": "Os campos de sintomas devem ser listas."}), 400

    engine = current_app.config["ENGINE"]
    next_q = engine.next_question(confirmed, denied)
    if next_q is None:
        return jsonify({"finalizado": True, "proxima_pergunta": None})

    return jsonify({"finalizado": False, "proxima_pergunta": next_q})


@api_bp.post("/diagnose")
def diagnose():
    """Executa o motor de inferência, gera explicação e registra no SQLite."""
    payload = request.get_json(silent=True) or {}
    engine = current_app.config["ENGINE"]
    db = current_app.config["DB"]

    try:
        confirmed, denied = validate_facts(
            payload.get("sintomas_confirmados"),
            payload.get("sintomas_negados"),
            valid_symptoms=set(engine.symptoms_catalog.keys()) or None,
        )
    except InvalidInputError as exc:
        return jsonify({"erro": str(exc)}), 400

    matches = engine.evaluate(confirmed, denied)
    result = build_explanation(matches, confirmed, engine.symptoms_catalog)

    db.log_diagnostic(
        sistema=result.get("sistema", "Indefinido"),
        diagnostico=result["diagnostico"],
        regra_id=result.get("regra_principal"),
        probabilidade=result["probabilidade_percentual"],
        sintomas=confirmed,
        status=result["status"],
    )

    return jsonify(result)


@api_bp.get("/stats")
def stats():
    """Retorna métricas e histórico recente para o Dashboard."""
    db = current_app.config["DB"]
    return jsonify(db.get_stats())
