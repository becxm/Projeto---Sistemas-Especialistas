"""
Rotas da API REST (Flask Blueprint).

Responsabilidade (Membro 1 & Membro 4):
- Expor endpoints para triagem interativa (forward chaining) e teste de hipóteses (backward chaining).
- Gerenciar recarga dinâmica da base de conhecimento (JSON e CSV).
- Fornecer métricas analíticas e histórico paginado para o frontend.
"""

from __future__ import annotations

from pathlib import Path
from flask import Blueprint, current_app, jsonify, request

from backend.explanation.explainer import (
    InvalidInputError,
    build_explanation,
    validate_facts,
)
from backend.loaders.kb_loader import KnowledgeBaseError, load_from_csv, load_from_json

api_bp = Blueprint("api", __name__, url_prefix="/api")


@api_bp.get("/health")
def health():
    """Verifica a integridade da API e informa o total de regras ativas."""
    engine = current_app.config["ENGINE"]
    return jsonify({
        "status": "ok",
        "total_regras": len(engine.rules),
        "total_sintomas": len(engine.symptoms_catalog),
        "sistemas_mapeados": engine.get_systems(),
    })


@api_bp.get("/symptoms")
def list_symptoms():
    """Retorna o catálogo completo de sintomas disponíveis com suas perguntas."""
    engine = current_app.config["ENGINE"]
    return jsonify({"sintomas": engine.symptoms_catalog})


@api_bp.get("/systems")
def list_systems():
    """Retorna os subsistemas veiculares contemplados pela base de regras."""
    engine = current_app.config["ENGINE"]
    return jsonify({"sistemas": engine.get_systems()})


@api_bp.post("/triage/next")
def triage_next():
    """
    Retorna dinamicamente a próxima pergunta da triagem interativa ou indica finalização.
    Suporta filtro opcional por sistema mecânico.
    """
    payload = request.get_json(silent=True) or {}
    confirmed = payload.get("sintomas_confirmados", [])
    denied = payload.get("sintomas_negados", [])
    system_filter = payload.get("sistema")

    if not isinstance(confirmed, list) or not isinstance(denied, list):
        return jsonify({"erro": "Os campos de sintomas devem ser listas."}), 400

    engine = current_app.config["ENGINE"]
    next_q = engine.next_question(confirmed, denied, system_filter=system_filter)
    if next_q is None:
        return jsonify({"finalizado": True, "proxima_pergunta": None})

    return jsonify({"finalizado": False, "proxima_pergunta": next_q})


@api_bp.post("/triage/hypothesis")
def triage_hypothesis():
    """
    Executa encadeamento para trás (backward chaining) para testar uma hipótese diagnóstica.
    Informa se a hipótese está confirmada, refutada ou quais sintomas faltam checar.
    """
    payload = request.get_json(silent=True) or {}
    regra_id = payload.get("regra_id")
    if not regra_id:
        return jsonify({"erro": "O campo 'regra_id' é obrigatório para testar uma hipótese."}), 400

    confirmed = payload.get("sintomas_confirmados", [])
    denied = payload.get("sintomas_negados", [])

    if not isinstance(confirmed, list) or not isinstance(denied, list):
        return jsonify({"erro": "Os campos de sintomas devem ser listas."}), 400

    engine = current_app.config["ENGINE"]
    result = engine.backward_chaining(regra_id, confirmed, denied)
    return jsonify(result)


@api_bp.post("/diagnose")
def diagnose():
    """
    Executa o motor de inferência, gera explicação técnica ('Por que / Como')
    e registra o diagnóstico no SQLite.
    """
    payload = request.get_json(silent=True) or {}
    engine = current_app.config["ENGINE"]
    db = current_app.config["DB"]
    system_filter = payload.get("sistema")

    try:
        confirmed, denied = validate_facts(
            payload.get("sintomas_confirmados"),
            payload.get("sintomas_negados"),
            valid_symptoms=set(engine.symptoms_catalog.keys()) or None,
        )
    except InvalidInputError as exc:
        return jsonify({"erro": str(exc)}), 400

    matches = engine.evaluate(confirmed, denied, system_filter=system_filter)
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
    """Retorna métricas analíticas consolidadas para o Dashboard da oficina."""
    db = current_app.config["DB"]
    return jsonify(db.get_stats())


@api_bp.get("/diagnostics/history")
def history():
    """Retorna o histórico paginado de diagnósticos com suporte a filtros e limites seguros."""
    db = current_app.config["DB"]
    try:
        limit = request.args.get("limit", default=20, type=int)
        offset = request.args.get("offset", default=0, type=int)
    except (ValueError, TypeError):
        limit = 20
        offset = 0

    # Sanitização de parâmetros de paginação contra DoS / valores negativos
    limit = max(1, min(limit, 100))
    offset = max(0, offset)
    sistema = request.args.get("sistema", default=None, type=str)
    status = request.args.get("status", default=None, type=str)

    data = db.get_history(limit=limit, offset=offset, sistema=sistema, status=status)
    return jsonify(data)


@api_bp.post("/knowledge-base/reload")
def reload_knowledge_base():
    """
    Recarrega a base de conhecimento a partir de arquivo JSON ou CSV
    sem necessidade de reiniciar a aplicação Flask.
    Protegido contra Directory Traversal (LFI).
    """
    payload = request.get_json(silent=True) or {}
    format_type = payload.get("formato", "json").lower()
    custom_path = payload.get("arquivo")

    base_dir = Path(current_app.root_path).parent
    allowed_dirs = [
        (base_dir / "knowledge_base").resolve(),
        (base_dir / "data").resolve(),
    ]

    if custom_path:
        target_path = (base_dir / custom_path).resolve()
        is_safe = any(target_path.is_relative_to(d) for d in allowed_dirs)
        if not is_safe:
            return jsonify({
                "erro": "Acesso negado: o arquivo deve estar dentro das pastas 'knowledge_base' ou 'data'."
            }), 403
    elif format_type == "csv":
        target_path = base_dir / "knowledge_base" / "regras_oficina.csv"
    else:
        target_path = base_dir / "knowledge_base" / "regras_oficina.json"

    try:
        if format_type == "csv":
            kb = load_from_csv(target_path)
            # Reutiliza o catálogo de sintomas já carregado se o CSV não tiver catálogo próprio
            current_engine = current_app.config.get("ENGINE")
            if current_engine and not kb.get("sintomas_catalogo"):
                kb["sintomas_catalogo"] = current_engine.symptoms_catalog
        else:
            kb = load_from_json(target_path)

        from backend.engine.inference import InferenceEngine
        current_app.config["ENGINE"] = InferenceEngine(kb)
        return jsonify({
            "status": "sucesso",
            "mensagem": f"Base de conhecimento recarregada com sucesso a partir de '{target_path.name}'.",
            "total_regras": len(kb["regras"]),
        })
    except KnowledgeBaseError as exc:
        return jsonify({"erro": str(exc)}), 400
