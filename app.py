"""Ponto de entrada: Sistema Especialista para Oficina Mecânica (Flask)."""
from flask import Flask

from backend.routes import Servicos, bp, registrar_erros
from config import Config


def create_app(config=None):
    app = Flask(__name__)
    app.config.from_object(Config)
    if config:
        app.config.update(config)
    app.extensions["oficina"] = Servicos(app.config)
    app.register_blueprint(bp)
    registrar_erros(app)
    return app


if __name__ == "__main__":
    aplicacao = create_app()
    print("Sistema Especialista para Oficina Mecânica -> http://127.0.0.1:5000")
    aplicacao.run(host="127.0.0.1", port=5000, debug=aplicacao.config["DEBUG"])
