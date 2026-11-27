(function () {
  const $ = (id) => document.getElementById(id);
  const op = { "==": "=", "!=": "≠", "<": "<", "<=": "≤", ">": ">", ">=": "≥" };

  function abas() {
    document.querySelectorAll(".aba").forEach((b) => b.addEventListener("click", () => {
      document.querySelectorAll(".aba").forEach((x) => x.setAttribute("aria-selected", x === b));
      ["regras", "fatos", "importar"].forEach((n) => { $("aba-" + n).hidden = n !== b.dataset.aba; });
      if (b.dataset.aba === "fatos") carregarFatos();
    }));
  }

  function textoCond(c) {
    if (typeof c.valor === "boolean") return c.valor ? c.descricao : `NÃO (${c.descricao})`;
    return `${c.descricao} ${op[c.op] || c.op} ${String(c.valor).replace(".", ",")}`;
  }

  function textoConclusao(c) {
    const desc = c.descricao || c.fato;
    const val = typeof c.valor === "boolean" ? (c.valor ? "Sim" : "Não") : String(c.valor).replace(".", ",");
    return `${desc} (${val})`;
  }

  function rotuloTipoFato(f) {
    if (f.derivado) return "Derivado";
    return f.tipo === "booleano" ? "Sim / Não" : f.tipo === "numerico" ? "Numérico" : f.tipo;
  }

  async function carregarRegras() {
    const params = new URLSearchParams();
    if ($("r-q").value.trim()) params.set("q", $("r-q").value.trim());
    if ($("r-categoria").value) params.set("categoria", $("r-categoria").value);
    if ($("r-tipo").value) params.set("tipo", $("r-tipo").value);
    try {
      const d = await api(`/api/regras?${params}`);
      const r = d.resumo;
      $("resumo").textContent = `Versão ${r.versao}: ${r.regras_diagnostico} regras de diagnóstico, ${r.regras_intermediarias} intermediárias (extensão), ${r.total_fatos} fatos, ${r.categorias} categorias. Exibindo ${d.total}.`;
      $("lista-regras").innerHTML = d.itens.length ? d.itens.map((x) => `
        <details class="painel"><summary>${esc(x.id)} · ${esc(x.nome)} <span class="badge">${esc(x.categoria_nome)}</span>
          <span class="badge ${x.origem === "extensao" ? "origem-extensao" : ""}">${x.origem === "extensao" ? "extensão" : esc(x.origem || "")}</span> <span class="badge">CF ${String(x.cf).replace(".", ",")}</span></summary>
          <div class="conteudo"><p><strong>SE</strong></p><ul class="lista-limpa">${x.condicoes.map((c) => `<li>${esc(textoCond(c))}</li>`).join("")}</ul>
            <p style="margin-top:.6rem"><strong>ENTÃO</strong> ${x.tipo === "diagnostico" ? "diagnóstico: " + esc(x.diagnostico) : "conclui " + esc(textoConclusao(x.conclusao))}</p>
            ${x.explicacao ? `<p class="muted">${esc(x.explicacao)}</p>` : ""}
            ${x.recomendacoes && x.recomendacoes.length ? `<p><strong>Recomendações:</strong> ${esc(x.recomendacoes.join("; "))}</p>` : ""}
            ${x.especialista ? `<p><strong>Especialista:</strong> ${esc(x.especialista)}</p>` : ""}</div></details>`).join("")
        : '<div class="card empty">Nenhuma regra encontrada.</div>';
      mostrarAviso("");
    } catch (e) { mostrarAviso(e.message); }
  }

  async function carregarFatos() {
    try {
      const d = await api("/api/fatos");
      $("linhas-fatos").innerHTML = d.itens.map((f) => `<tr><td><code>${esc(f.id)}</code></td><td>${esc(f.descricao)}</td><td>${esc(f.categoria_nome || f.categoria)}</td><td>${esc(rotuloTipoFato(f))}</td></tr>`).join("");
    } catch (e) { mostrarAviso(e.message); }
  }

  async function importar() {
    let regras;
    try { regras = JSON.parse($("json-regras").value); } catch (e) { mostrarAviso("O texto informado não é um JSON válido: " + e.message); return; }
    if (!Array.isArray(regras)) regras = regras && regras.regras ? regras.regras : [regras];
    try {
      const r = await api("/api/regras/importar", { method: "POST", body: { regras, substituir: $("substituir").checked } });
      mostrarAviso(`${r.mensagem} Adicionadas: ${r.adicionadas}; substituídas: ${r.substituidas}; total: ${r.total_regras}.`, "ok");
      carregarRegras();
    } catch (e) { mostrarAviso(e.message); }
  }

  $("arquivo").addEventListener("change", (ev) => {
    const f = ev.target.files[0];
    if (!f) return;
    const leitor = new FileReader();
    leitor.onload = () => { $("json-regras").value = leitor.result; };
    leitor.onerror = () => mostrarAviso("Não foi possível ler o arquivo selecionado.");
    leitor.readAsText(f, "utf-8");
  });
  let timerRegra = null;
  $("btn-importar").addEventListener("click", importar);
  $("form-regras").addEventListener("submit", (ev) => { ev.preventDefault(); carregarRegras(); });
  $("r-categoria").addEventListener("change", carregarRegras);
  $("r-tipo").addEventListener("change", carregarRegras);
  $("r-q").addEventListener("input", () => { clearTimeout(timerRegra); timerRegra = setTimeout(carregarRegras, 250); });
  abas();
  api("/api/categorias").then((d) => {
    $("r-categoria").innerHTML += d.categorias.map((c) => `<option value="${esc(c.id)}">${esc(c.nome)}</option>`).join("");
  }).catch((e) => mostrarAviso(e.message));
  carregarRegras();
})();
