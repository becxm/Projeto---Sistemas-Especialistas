"""Configurações centrais do Sistema Especialista para Oficina Mecânica."""
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Valores padrão. Podem ser sobrescritos por variáveis de ambiente ou por create_app(config)."""

    DATABASE_PATH = os.environ.get("OFICINA_DB", os.path.join(BASE_DIR, "instance", "oficina.db"))
    REGRAS_PATH = os.environ.get("OFICINA_REGRAS", os.path.join(BASE_DIR, "data", "regras.json"))
    FATOS_PATH = os.environ.get("OFICINA_FATOS", os.path.join(BASE_DIR, "data", "fatos.json"))
    # Índice mínimo para que uma hipótese parcial seja listada como alternativa.
    LIMIAR_ALTERNATIVA = 0.25
    # Limite de segurança de perguntas por triagem.
    MAX_PERGUNTAS = 20
    JSON_AS_ASCII = False
    JSON_SORT_KEYS = False
    DEBUG = False
