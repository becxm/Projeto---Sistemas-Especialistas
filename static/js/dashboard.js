(function () {
  async function carregar() {
    try {
      const e = await api("/api/estatisticas");
      document.getElementById("kpi-total").textContent = e.total;
      document.getElementById("kpi-conclusivos").textContent = e.conclusivos;
      document.getElementById("kpi-inconclusivos").textContent = e.inconclusivos;
      document.getElementById("kpi-indice").textContent = e.indice_medio === null ? "–" : pct(e.indice_medio);
      graficoRosca(document.getElementById("g-categorias"), e.por_categoria);
      graficoBarras(document.getElementById("g-falhas"), e.falhas_frequentes, (f) => f.diagnostico, (f) => f.total);

      const dias = document.getElementById("g-dias");
      if (!e.por_dia.length) {
        dias.innerHTML = '<p class="empty">Sem diagnósticos registrados.</p>';
      } else {
        const max = Math.max(...e.por_dia.map((d) => d.total));
        dias.innerHTML = `<div class="colunas">${e.por_dia.map((d) => `
          <div class="col"><em>${d.total}</em><span class="b" style="height:${(100 * d.total) / max}%"></span><small>${esc(d.dia.slice(8, 10) + "/" + d.dia.slice(5, 7))}</small></div>`).join("")}</div>`;
      }
      const corpo = document.getElementById("recentes");
      corpo.innerHTML = e.recentes.length ? e.recentes.map((d) => `
        <tr><td>#${d.id}</td><td>${esc(fmtData(d.data_hora))}</td><td>${esc(d.categoria_nome || d.categoria || "–")}</td>
        <td>${esc(d.diagnostico || "Inconclusivo")}</td><td>${badgeStatus(d.status)}</td>
        <td><a href="/resultado/${d.id}">Ver explicação</a></td></tr>`).join("")
        : '<tr><td colspan="6" class="empty">Nenhum diagnóstico ainda. Clique em “Iniciar novo diagnóstico”.</td></tr>';
    } catch (err) {
      mostrarAviso(err.message);
    }
  }

  const btnDemo = document.getElementById("btn-demo");
  if (btnDemo) {
    btnDemo.addEventListener("click", async () => {
      btnDemo.disabled = true;
      try {
        const r = await api("/api/demo", { method: "POST" });
        mostrarAviso(r.mensagem, "ok");
        await carregar();
      } catch (err) {
        mostrarAviso(err.message);
      } finally {
        btnDemo.disabled = false;
      }
    });
  }

  carregar();
})();
