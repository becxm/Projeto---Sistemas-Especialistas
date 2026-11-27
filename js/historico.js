(function () {
  const $ = (id) => document.getElementById(id);
  let pagina = 1, paginas = 1;

  async function carregarCategorias() {
    try {
      const d = await api("/api/categorias");
      $("f-categoria").innerHTML += d.categorias.map((c) => `<option value="${esc(c.id)}">${esc(c.nome)}</option>`).join("");
    } catch (e) { mostrarAviso(e.message); }
  }

  async function carregar() {
    const params = new URLSearchParams({ pagina, limite: 10 });
    if ($("f-q").value.trim()) params.set("q", $("f-q").value.trim());
    if ($("f-categoria").value) params.set("categoria", $("f-categoria").value);
    if ($("f-status").value) params.set("status", $("f-status").value);
    try {
      const d = await api(`/api/diagnosticos?${params}`);
      paginas = d.paginas;
      $("total").textContent = `${d.total} diagnóstico(s) encontrado(s).`;
      $("linhas").innerHTML = d.itens.length ? d.itens.map((i) => `
        <tr><td>#${i.id}</td><td>${esc(fmtData(i.data_hora))}</td><td>${esc(i.veiculo || "–")}</td><td>${esc(i.categoria_nome || i.categoria || "–")}</td>
        <td>${esc(i.diagnostico || "Inconclusivo")}</td><td>${i.status === "conclusivo" ? pct(i.indice_compatibilidade) : "–"}</td>
        <td>${badgeStatus(i.status)}</td><td><a href="/resultado/${i.id}">Ver explicação</a></td></tr>`).join("")
        : '<tr><td colspan="8" class="empty">Nenhum diagnóstico encontrado com esses filtros.</td></tr>';
      $("pagina-info").textContent = `Página ${d.pagina} de ${d.paginas}`;
      $("btn-ant").disabled = d.pagina <= 1;
      $("btn-prox").disabled = d.pagina >= d.paginas;
      mostrarAviso("");
    } catch (e) { mostrarAviso(e.message); }
  }

  let timerBusca = null;
  function aplicarFiltros() { pagina = 1; carregar(); }

  $("form-filtros").addEventListener("submit", (ev) => { ev.preventDefault(); aplicarFiltros(); });
  $("f-categoria").addEventListener("change", aplicarFiltros);
  $("f-status").addEventListener("change", aplicarFiltros);
  $("f-q").addEventListener("input", () => { clearTimeout(timerBusca); timerBusca = setTimeout(aplicarFiltros, 250); });
  $("btn-limpar").addEventListener("click", () => { $("form-filtros").reset(); aplicarFiltros(); });
  $("btn-ant").addEventListener("click", () => { if (pagina > 1) { pagina--; carregar(); } });
  $("btn-prox").addEventListener("click", () => { if (pagina < paginas) { pagina++; carregar(); } });
  carregarCategorias().then(carregar);
})();
