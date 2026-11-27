# Sistema Especialista — Triagem e Diagnóstico para Oficina Mecânica

Projeto da disciplina **Programação de Sistemas Especialistas** (Prazo: 28/11/2026).
O sistema realiza a triagem interativa de sintomas relatados por clientes de uma oficina mecânica, calcula probabilidades de falha, explica **por que/como** chegou ao diagnóstico e registra o histórico em banco de dados para alimentar um dashboard estatístico.
> **Grupo:** GUSTAVO FERREIRA BALDOINO - 1250109373, IASMIM DA SILVA MANN JOSÉ - 1250109566, REBECA MACHADO DE LIMA - 1250103657, SARAH GABRIELLA VIRGÍNIA DA SILVA - 1250106978,  SILVANA GOMES DA SILVA - 1250109767.  

---

## 1. Como Rodar o Projeto (Passo a Passo)

Abra o terminal na pasta raiz do projeto e execute:

```bash
# 1. Criar ambiente virtual (apenas na primeira vez)
python -m venv .venv

# 2. Ativar o ambiente virtual
# No Windows (PowerShell):
.\.venv\Scripts\Activate.ps1
# No Linux/Mac:
# source .venv/bin/activate

# 3. Instalar dependências
pip install -r requirements.txt

# 4. Rodar a aplicação (Backend + Frontend)
python app.py
# ou:
# python -m backend.app
```

Acesse no navegador: `http://127.0.0.1:5000`

### Como rodar os testes automatizados

```bash
python -m unittest discover -s tests -v
```
*(Ou com pytest: `pytest -v`)*

### Como rodar os scripts utilitários do repositório

```bash
# 1. Validar e auditar integridade da Base de Conhecimento (JSON e CSV):
python scripts/validar_base.py

# 2. Executar a Triagem Interativa diretamente no Terminal (CLI):
python scripts/cli_triagem.py

# 3. Testar uma hipótese diagnóstica específica via Encadeamento para Trás (Backward Chaining):
python scripts/cli_triagem.py --hipotese R01

# 4. Popular o SQLite com histórico simulado para testes do Dashboard:
python scripts/popular_historico.py --qtd 40 --reset
# ou script de demonstração:
python scripts/popular_demo.py

# 5. Gerar dicionário de regras e documentação automática:
python scripts/gerar_docs_regras.py

# 6. Converter a base entre formatos JSON e CSV:
python scripts/converter_kb.py --json-to-csv
python scripts/converter_kb.py --csv-to-json
```

---

## 2. Estrutura de Pastas e O Que Entregar em Cada Uma

```text
projeto-sistemas-especialistas/
├── .gitignore
├── app.py
├── README.md
├── requirements.txt
├── backend/
│   ├── app.py
│   ├── demo.py
│   ├── api/
│   │   └── routes.py
│   ├── engine/
│   │   └── inference.py
│   ├── explanation/
│   │   └── explainer.py
│   ├── loaders/
│   │   └── kb_loader.py
│   └── database/
│       └── db.py
├── knowledge_base/
│   ├── regras_oficina.json
│   └── regras_oficina.csv
├── data/
│   ├── fatos.json
│   ├── regras.json
│   └── oficina.db
├── scripts/
│   ├── validar_base.py
│   ├── cli_triagem.py
│   ├── converter_kb.py
│   ├── popular_historico.py
│   ├── popular_demo.py
│   └── gerar_docs_regras.py
├── templates/
│   ├── base.html
│   ├── triagem.html
│   ├── resultado.html
│   ├── historico.html
│   ├── dashboard.html
│   ├── conhecimento.html
│   └── erro.html
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       ├── common.js
│       ├── triagem.js
│       ├── resultado.js
│       ├── historico.js
│       ├── dashboard.js
│       └── conhecimento.js
├── frontend/
│   ├── index.html
│   ├── css/style.css
│   └── js/app.js
├── tests/
│   ├── test_engine.py
│   └── test_api.py
└── docs/
    └── regras.md
```

### Detalhamento por Pasta

#### `knowledge_base/` e `data/` — Engenharia de Conhecimento (**Responsável: Rebeca**)
- **Para que serve:** Armazena as regras (`SE [sintomas] ENTÃO [diagnóstico]`), catálogo de fatos e perguntas em arquivos externos (`.json` e `.csv`), permitindo atualizar o sistema sem alterar código Python.
- **O que já existe:**
  - `knowledge_base/regras_oficina.json`: **26 regras de diagnóstico** cobrindo 9 subsistemas veiculares (Elétrica, Motor, Freios, Suspensão, Arrefecimento, Injeção, Transmissão, Escapamento e Turbo).
  - `knowledge_base/regras_oficina.csv`: Versão tabular estruturada para edição em planilhas e interoperabilidade.
  - `data/fatos.json` e `data/regras.json`: Base de regras e fatos integrados com templates HTML.
- **O que entregar/manter:**
  - Garantir que todas as regras possuam `sintomas`, `diagnostico`, `solucao`, `especialista` e `confianca` (de `0.0` a `1.0`).
  - Executar `python scripts/validar_base.py` antes de novos commits para assegurar ausência de sintomas órfãos ou IDs duplicados.

#### `scripts/` — Utilitários e Ferramentas Operacionais (**Responsável: Rebeca / Equipe**)
- **`validar_base.py`:** Auditor automatizado da consistência e integridade das bases JSON e CSV.
- **`cli_triagem.py`:** Simulador completo de triagem e teste de hipóteses por linha de comando.
- **`converter_kb.py`:** Utilitário de exportação e importação bidirecional JSON <-> CSV.
- **`popular_historico.py` / `popular_demo.py`:** Geradores de massa de dados realista para alimentar o SQLite e o Dashboard.
- **`gerar_docs_regras.py`:** Gerador automatizado do dicionário de regras em Markdown (`docs/regras.md`).

#### `backend/engine/` — Motor de Inferência (**Responsável: Iasmim**)
- **Para que serve:** Contém a inteligência do sistema especialista.
- **Capacidades implementadas:**
  - **Encadeamento para Frente (Forward Chaining):** Avaliação de sintomas confirmados/negados com cálculo de cobertura e probabilidade ponderada.
  - **Encadeamento para Trás (Backward Chaining):** Teste de hipóteses guiado por metas (`backward_chaining`), indicando se uma suspeita foi confirmada, refutada ou quais sintomas faltam checar.
  - **Resolução de Conflitos e Desempate:** Ordenação por cobertura, probabilidade e confiança da regra.
  - **Filtro por Subsistema:** Capacidade de focar a triagem em um sistema mecânico específico.

#### `backend/explanation/` — Módulo de Explicação e Exceções (**Responsável: Iasmim**)
- **Para que serve:** Explica ao usuário **por que/como** o sistema chegou àquela conclusão e protege contra entradas inválidas.
- **Capacidades implementadas:**
  - `validate_facts()`: Validação estrita de entradas com exceção customizada `InvalidInputError`.
  - `build_explanation()`: Painel detalhado de justificativa, listando sintomas confirmados, regras ativadas e fallback amigável para casos inconclusivos.

#### `backend/loaders/` — Leitura e Escrita de JSON/CSV (**Responsável: Rebeca / Silvana**)
- **Para que serve:** Manipulação de arquivos externos da base de conhecimento.
- **Capacidades implementadas:**
  - `load_from_json()` e `load_from_csv()`: Carga com validação rigorosa de campos obrigatórios.
  - `save_to_json()` e `save_to_csv()`: Exportação estruturada.

#### `backend/database/` e `data/` — Histórico e Dados Estatísticos (**Responsável: Gustavo / Iasmim**)
- **Para que serve:** Salva os diagnósticos em banco **SQLite** (`data/oficina.db`) e gera métricas analíticas.
- **Capacidades implementadas:**
  - `log_diagnostic()`: Registro com timestamp, sintomas, probabilidade e status.
  - `get_stats()`: Métricas agregadas de taxa de resolutividade, distribuição por sistema e diagnósticos recentes.
  - `get_history()`: Consulta paginada com suporte a filtros dinâmicos por sistema e status.

#### `backend/api/`, `app.py` e `config.py` — Arquitetura e API Web (**Responsável: Gustavo / Iasmim**)
- **Para que serve:** Conecta a interface gráfica ao motor de inferência, módulo de explicação e banco de dados.
- **Endpoints disponíveis:**
  - `GET /api/health` — Status da API, total de regras e subsistemas mapeados.
  - `GET /api/symptoms` — Catálogo completo de sintomas com perguntas.
  - `GET /api/systems` — Lista de subsistemas veiculares contemplados.
  - `POST /api/triage/next` — Próxima pergunta relevante da triagem interativa.
  - `POST /api/triage/hypothesis` — Validação de hipótese diagnóstica (Backward Chaining).
  - `POST /api/diagnose` — Executa o diagnóstico, gera explicação e salva no banco.
  - `GET /api/stats` — Métricas consolidadas para o Dashboard.
  - `GET /api/diagnostics/history` — Histórico paginado e filtrado de atendimentos.
  - `POST /api/knowledge-base/reload` — Recarga dinâmica de regras (JSON ou CSV) sem reiniciar a aplicação.

#### `frontend/`, `templates/` e `static/` — Interface Web e UX (**Responsável: Sarah**)
- Telas da oficina em tema moderno (Dark Mode), com suporte tanto a Single Page Application (`frontend/`) quanto a páginas completas Jinja2 (`templates/` e `static/`), com navegação por abas: Triagem, Resultado com "Por que / Como", Histórico com filtros, Dashboard e Dicionário de Conhecimento.

#### `tests/` e `docs/` — Testes Automatizados e Documentação (**Responsável: Silvana**)
- **`test_engine.py`:** Testes unitários do motor (forward/backward chaining, filtros, CSV loader, banco SQLite).
- **`test_api.py`:** Testes de integração de todos os endpoints REST da aplicação Flask.
- **`docs/`:** Documentação detalhada da base de conhecimento e regras.

---

## 3. Divisão da Equipe e Regras de Git

### Divisão de Apresentação (Fontes: Gemini)

| Integrante | Tópico Principal | O Que Apresentar |
| :--- | :--- | :--- |
| **Gustavo** | Introdução, problema de negócio e arquitetura | Contexto do sistema especialista para oficina mecânica, problema no balcão, visão geral da aplicação (`app.py`, `config.py`) e fluxo no Git. |
| **Iasmim** | Motor de inferência e lógica principal | Como funciona o encadeamento para frente, triagem interativa, incerteza e estrutura do `backend/`. |
| **Rebeca** | Base de conhecimento e dados | Regras e fatos em JSON (`data/`), como os sintomas viram diagnóstico e scripts de apoio/população (`scripts/`). |
| **Sarah** | Interface e demonstração prática | Telas e interação pelo navegador (`templates/` e `static/`), mostrando uma triagem funcionando ao vivo. |
| **Silvana** | Testes, documentação e limitações | Como os testes (`tests/`) validam o sistema, organização da documentação (`docs/`, `README.md`) e limitações/próximos passos. |

### Boas Práticas no GitHub (Avaliado pelo Professor)
1. **Commits pequenos, frequentes e semânticos:** O histórico comprova a evolução de cada módulo (padrão Conventional Commits: `feat`, `fix`, `test`, `docs`).
2. **Branches por funcionalidade:** Crie sempre uma branch para sua tarefa (ex: `feature/api-motor`, `feature/ui-dashboard`, `feature/regras-freios`).
3. **Pull Requests (PRs):** Revise as alterações e execute a suite de testes antes de mesclar na `main`.
