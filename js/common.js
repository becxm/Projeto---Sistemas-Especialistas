/* Utilitários compartilhados pelas páginas. */
const CORES = ["#f5a524", "#38c6b4", "#5aa9ff", "#ef5b5b", "#b58cff", "#3ccf7a"];

function esc(valor) {
  return String(valor ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}

async function api(url, opcoes = {}) {
  const config = { headers: { "Content-Type": "application/json" }, ...opcoes };
  if (config.body && typeof config.body !== "string") config.body = JSON.stringify(config.body);
  let resp;
  try {
    resp = await fetch(url, config);
  } catch (e) {
    throw new Error("Não foi possível contatar o servidor. Verifique se a aplicação está em execução.");
  }
  let dados = null;
  try { dados = await resp.json(); } catch (e) { /* resposta sem JSON */ }
  if (!resp.ok) {
    const erro = new Error((dados && dados.erro) || `Erro ${resp.status} ao acessar a API.`);
    erro.status = resp.status;
    erro.tipo = dados && dados.tipo;
    throw erro;
  }
  return dados;
}

function mostrarAviso(mensagem, tipo = "erro") {
  const area = document.getElementById("aviso");
  if (!area) return;
  area.innerHTML = mensagem ? `<div class="alerta ${tipo}" role="alert">${esc(mensagem)}</div>` : "";
  if (mensagem) area.scrollIntoView({ behavior: "smooth", block: "nearest" });
}

function fmtData(iso) {
  if (!iso) return "";
  const [d, h] = iso.split("T");
  const [a, m, di] = d.split("-");
  return `${di}/${m}/${a} ${h || ""}`.trim();
}

function pct(v) { return `${Math.round((v || 0) * 100)}%`; }

function badgeStatus(status) {
  const rotulo = status === "conclusivo" ? "Conclusivo" : "Inconclusivo";
  return `<span class="badge ${esc(status)}">${rotulo}</span>`;
}

function graficoBarras(el, itens, rotulo, valor) {
  if (!itens.length) { el.innerHTML = '<p class="empty">Sem dados ainda. Realize um diagnóstico para ver o gráfico.</p>'; return; }
  const max = Math.max(...itens.map(valor));
  el.innerHTML = itens.map((i) => `
    <div class="bar-row"><span class="rot" title="${esc(rotulo(i))}">${esc(rotulo(i))}</span>
      <span class="trilho"><span class="barra" style="display:block;width:${(100 * valor(i)) / max}%"></span></span>
      <span class="num">${valor(i)}</span></div>`).join("");
}

function graficoRosca(el, itens) {
  if (!itens.length) { el.innerHTML = '<p class="empty">Sem dados ainda.</p>'; return; }
  const total = itens.reduce((s, i) => s + i.total, 0);
  const r = 15.9155, c = 2 * Math.PI * r;
  let acum = 0, arcos = "";
  itens.forEach((i, idx) => {
    const frac = (i.total / total) * c;
    arcos += `<circle r="${r}" cx="21" cy="21" fill="transparent" stroke="${CORES[idx % CORES.length]}" stroke-width="6"
      stroke-dasharray="${frac} ${c - frac}" stroke-dashoffset="${-acum}" transform="rotate(-90 21 21)"></circle>`;
    acum += frac;
  });
  el.innerHTML = `<div class="donut-wrap"><svg viewBox="0 0 42 42" width="160" height="160" role="img" aria-label="Diagnósticos por categoria">
    <circle r="${r}" cx="21" cy="21" fill="transparent" stroke="#0f1318" stroke-width="6"></circle>${arcos}
    <text x="21" y="22.5" text-anchor="middle" fill="#e8ecf1" font-size="7">${total}</text></svg>
    <ul class="legenda">${itens.map((i, idx) => `<li><i style="background:${CORES[idx % CORES.length]}"></i>${esc(i.nome)}: <strong>${i.total}</strong> (${i.percentual}%)</li>`).join("")}</ul></div>`;
}
