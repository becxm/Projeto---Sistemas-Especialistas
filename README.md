# Sistema Especialista — Triagem e Diagnóstico para Oficina Mecânica

Projeto da disciplina **Programação de Sistemas Especialistas** (Prazo: 28/11/2026).
O sistema realiza a triagem interativa de sintomas relatados por clientes de uma oficina mecânica, calcula probabilidades de falha, explica **por que/como** chegou ao diagnóstico e registra o histórico em banco de dados para alimentar um dashboard estatístico.
> **Grupo:** IASMIM DA SILVA MANN JOSÉ - 1250109566, REBECA MACHADO DE LIMA - 1250103657, SARAH GABRIELLA VIRGÍNIA DA SILVA - 1250106978,  SILVANA GOMES DA SILVA - 1250109767.  

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
python -m backend.app
```

Acesse no navegador: `http://127.0.0.1:5000`

### Como rodar os testes automatizados

```bash
python -m unittest discover -s tests -v
```
*(Ou, se preferir usar pytest: `pytest -v`)*

---

## 2. Estrutura de Pastas e O Que Entregar em Cada Uma

Este guia foi pensado para que qualquer integrante da equipe saiba exatamente onde mexer e o que entregar.

```text
projeto-sistemas-especialistas/
├── .gitignore
├── README.md
├── requirements.txt
├── backend/
│   ├── app.py
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
│   └── regras_oficina.json
├── data/
│   └── .gitkeep
├── frontend/
│   ├── index.html
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   └── app.js
│   └── assets/
├── tests/
│   └── test_engine.py
└── docs/
    └── .gitkeep
```

### Detalhamento por Pasta

#### `knowledge_base/` — Engenharia de Conhecimento (**Responsável: Membro 2**)
- **Para que serve:** Armazena as regras (`SE [sintomas] ENTÃO [diagnóstico]`) e o catálogo de perguntas em arquivos externos (`.json` ou `.csv`), permitindo atualizar o sistema sem alterar código Python.
- **O que já existe:** `regras_oficina.json` com as **20 regras iniciais** do plano de projeto.
- **O que entregar/manter:**
  - Garantir que todas as 20+ regras estejam bem descritas, com `sintomas`, `diagnostico`, `solucao`, `especialista` e `confianca` (de `0.0` a `1.0`).
  - Se quiserem adicionar mais regras (ex: `R21`, `R22`...) ou criar uma versão em `.csv` para demonstrar extensibilidade, basta colocar nesta pasta.

#### `backend/engine/` — Motor de Inferência (**Responsável: Membro 1 + Membro 5**)
- **Para que serve:** Contém a lógica de inteligência do sistema especialista.
- **O que já existe:** `inference.py` com a classe `InferenceEngine` (encadeamento para frente, cálculo de probabilidade/certeza e seleção dinâmica da próxima pergunta).
- **O que entregar/manter:**
  - Melhorar ou expandir o encadeamento (ex: adicionar suporte a encadeamento para trás ou desempate entre regras).
  - Refinar o cálculo de incerteza/probabilidade quando apenas parte dos sintomas é confirmada.

#### `backend/explanation/` — Módulo de Explicação e Exceções (**Responsável: Membro 3**)
- **Para que serve:** É um dos critérios com **maior peso na avaliação**. Explica ao usuário **por que/como** o sistema chegou àquela conclusão e protege contra entradas inválidas.
- **O que já existe:** `explainer.py` com `validate_facts()` (validação de entradas) e `build_explanation()` (lista regras ativadas, fatos confirmados e fallback `"Diagnóstico Inconclusivo"`).
- **O que entregar/manter:**
  - Garantir mensagens claras de erro caso alguém envie dados inválidos para a API.
  - Garantir que a explicação detalhada mostre exatamente quais regras e fatos foram ativados.

#### `backend/loaders/` — Leitura de JSON/CSV (**Responsável: Membro 5**)
- **Para que serve:** Lê e valida os arquivos da pasta `knowledge_base/`.
- **O que já existe:** `kb_loader.py` com `load_from_json()` e `load_from_csv()`.
- **O que entregar/manter:**
  - Validar se faltam campos obrigatórios ao carregar novos arquivos.
  - Se o grupo usar `.csv` na interface, conectar `load_from_csv()` na API ou em um script de importação.

#### `backend/database/` e `data/` — Histórico e Dados Estatísticos (**Responsável: Membro 1 + Membro 5**)
- **Para que serve:** Salva todos os diagnósticos feitos no balcão em um banco **SQLite** (`data/oficina.db`) para gerar métricas (ex: *"45% dos chamados foram no sistema elétrico"*).
- **O que já existe:** `db.py` com `DiagnosticDatabase` (cria tabela `diagnosticos`, grava registros e calcula estatísticas).
- **O que entregar/manter:**
  - A pasta `data/` guarda o arquivo `.db` gerado automaticamente (ela é ignorada no Git pelo `.gitignore` para não subir banco local).
  - Adicionar novas consultas estatísticas em `db.py` se o dashboard precisar de mais gráficos/filtros (ex: por semana).

#### `backend/api/` e `backend/app.py` — API Web (**Responsável: Membro 1 + Membro 4**)
- **Para que serve:** Conecta o Frontend ao Motor de Inferência, Explicação e Banco de Dados via HTTP/JSON.
- **O que já existe:**
  - `GET /api/health` — verifica se a API está no ar e quantas regras estão carregadas.
  - `GET /api/symptoms` — lista o catálogo de sintomas.
  - `POST /api/triage/next` — devolve a próxima pergunta da triagem interativa.
  - `POST /api/diagnose` — executa o diagnóstico, gera a explicação e salva no SQLite.
  - `GET /api/stats` — devolve os dados para o Dashboard.
- **O que entregar/manter:** Novas rotas que a interface precisar (ex: upload/recarga de JSON, filtros no histórico).

#### `frontend/` — Interface Web e UX (**Responsável: Membro 4**)
- **Para que serve:** Tela visual da oficina (em **dark mode**), dividida em:
  1. **Dashboard Inicial:** métricas gerais e histórico recente.
  2. **Triagem Interativa:** perguntas uma a uma (sem formulário gigante).
  3. **Resultado + Explicação:** diagnóstico, solução, especialista e painel "Por que / Como".
- **O que já existe:** `index.html`, `css/style.css` e `js/app.js` integrados com a API.
- **O que entregar/manter:**
  - Evoluir o visual em `css/style.css` e adicionar imagens/ícones em `frontend/assets/`.
  - Garantir validação visual e tratamento amigável de erros no `js/app.js`.

#### `tests/` — Testes Automatizados (**Responsável: Membro 5 + Todos**)
- **Para que serve:** Garante que mudanças no código não quebrem diagnósticos existentes.
- **O que já existe:** `test_engine.py` cobrindo base de 20 regras, Regra R01, fallback inconclusivo, validação de entrada e SQLite.
- **O que entregar/manter:** Criar casos de teste para outras regras (ex: Freios, Suspensão, Arrefecimento) e para os endpoints da API.

#### `docs/` — Documentação e Apresentação (**Responsável: Membro 5 + Todos**)
- **Para que serve:** Guardar diagramas, roteiro da apresentação (reunião simulada de **9 a 11 minutos**) e o PDF final com nomes, link do GitHub e link da gravação.

---

## 3. Divisão da Equipe e Regras de Git

| Membro | Papel Principal | Pastas Principais |
| :--- | :--- | :--- |
| **Membro 1 (Líder)** | Arquitetura, Integração e Revisão | `backend/app.py`, `backend/api/`, `backend/engine/`, `backend/database/` |
| **Membro 2** | Engenharia de Conhecimento | `knowledge_base/` |
| **Membro 3** | Exceções e Módulo de Explicação | `backend/explanation/` |
| **Membro 4** | Interface Web e UX | `frontend/` |
| **Membro 5** | Diferenciais, Qualidade e Docs | `backend/loaders/`, `tests/`, `docs/`, `README.md` |

### Boas Práticas no GitHub (Avaliado pelo Professor)
1. **Nunca commitar direto na `main`:** Crie sempre uma branch para sua tarefa (ex: `feature/api-motor`, `feature/ui-dashboard`, `feature/regras-freios`).
2. **Commits pequenos e frequentes:** O histórico de commits comprova a participação de cada integrante.
3. **Pull Requests (PRs):** Ao terminar sua tarefa, abra um PR no GitHub e peça para outro colega revisar antes do merge.
