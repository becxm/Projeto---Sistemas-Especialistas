"""Gera docs/regras.md (dicionário de regras e fatos) a partir de data/regras.json e data/fatos.json."""
import json
import os

RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def main():
    with open(os.path.join(RAIZ, "data", "regras.json"), encoding="utf-8") as f:
        regras = json.load(f)["regras"]
    with open(os.path.join(RAIZ, "data", "fatos.json"), encoding="utf-8") as f:
        dados = json.load(f)
    fatos = {x["id"]: x for x in dados["fatos"]}
    cats = {c["id"]: c["nome"] for c in dados["categorias"]}
    op = {"==": "=", "!=": "≠", "<": "<", "<=": "≤", ">": ">", ">=": "≥"}

    def cond(c):
        d = fatos[c["fato"]]["descricao"]
        return d if c["valor"] is True else (f"NÃO ({d})" if c["valor"] is False else f"{d} {op[c['op']]} {str(c['valor']).replace('.', ',')}")

    L = ["# Dicionário de regras e fatos", "",
         "Gerado automaticamente por `python scripts/gerar_docs_regras.py` a partir de `data/regras.json` e `data/fatos.json`.",
         "O CF (fator de certeza) de cada regra é uma **estimativa heurística da equipe**, não um valor calibrado estatisticamente.",
         "Regras com origem **extensão** não constam do Plano de Projeto; foram criadas para o encadeamento em múltiplas etapas.", ""]
    for cid, nome in cats.items():
        L += [f"## {nome}", ""]
        for r in [x for x in regras if x["categoria"] == cid]:
            L += [f"### {r['id']} — {r['nome']}", "", f"- **Tipo:** {r['tipo']} · **Origem:** {r.get('origem', '')} · **CF:** {str(r['cf']).replace('.', ',')}"]
            L += ["- **SE:** " + " **E** ".join(cond(c) for c in r["condicoes"])]
            if r["tipo"] == "diagnostico":
                L += [f"- **ENTÃO diagnóstico =** {r['diagnostico']}", f"- **Explicação:** {r['explicacao']}",
                      "- **Possíveis causas:** " + "; ".join(r["causas"]), "- **Recomendações (complementares):** " + "; ".join(r["recomendacoes"]),
                      f"- **Especialista indicado:** {r['especialista']}"]
            else:
                L += [f"- **ENTÃO deduz:** `{r['conclusao']['fato']}` = {r['conclusao']['valor']}", f"- **Explicação:** {r['explicacao']}"]
            L.append("")
    L += ["## Fatos", "", "| Id | Descrição | Categoria | Tipo |", "|---|---|---|---|"]
    for f in dados["fatos"]:
        L.append(f"| `{f['id']}` | {f['descricao']} | {cats[f['categoria']]} | {'derivado' if f.get('derivado') else f['tipo']} |")
    with open(os.path.join(RAIZ, "docs", "regras.md"), "w", encoding="utf-8") as out:
        out.write("\n".join(L) + "\n")
    print("docs/regras.md gerado.")


if __name__ == "__main__":
    main()