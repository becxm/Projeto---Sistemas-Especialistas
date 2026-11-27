(function () {
  const descricoes = {};
  const estado = { categoria: null, veiculo: "", respostas: {}, historico: [], pergunta: null, categorias: [] };
  const $ = (id) => document.getElementById(id);

  async function carregarCategorias() {
    try {
      const dados = await api("/api/categorias");
      estado.categorias = dados.categorias;
      $("categorias").innerHTML = dados.categorias.map((c) => `
        <label class="cat-opt"><input type="radio" name="categoria" value="${esc(c.id)}">
        <span class="corpo"><span class="icone" aria-hidden="true">${esc(c.icone)}</span><strong>${esc(c.nome)}</strong><span class="muted">${esc(c.descricao)}</span></span></label>`).join("");
      document.querySelectorAll("input[name=categoria]").forEach((r) => r.addEventListener("change", escolherCategoria));
    } catch (e) { $("categorias").innerHTML = ""; mostrarAviso(e.message); }
  }

  function escolherCategoria(ev) {
    estado.categoria = ev.target.value;
    const cat = estado.categorias.find((c) => c.id === estado.categoria);
    const sel = $("sintoma-inicial");
    sel.disabled = false;
    sel.innerHTML = '<option value="">Nenhum (o sistema perguntará)</option>' +
      cat.sintomas.map((s) => `<option value="${esc(s.id)}">${esc(s.descricao)}</option>`).join("");
    $("btn-iniciar").disabled = false;
    mostrarAviso("");
  }

  function mostrar(etapa) {
    ["etapa-inicio", "etapa-perguntas", "etapa-final"].forEach((id) => { $(id).hidden = id !== etapa; });
  }

  async function iniciar() {
    if (!estado.categoria) { mostrarAviso("Selecione uma categoria para começar."); return; }
    estado.veiculo = $("veiculo").value.trim();
    estado.respostas = {};
    estado.historico = [];
    const inicial = $("sintoma-inicial").value;
    const catAtual = estado.categorias.find((c) => c.id === estado.categoria);
    catAtual.sintomas.forEach((s) => { descricoes[s.id] = s.descricao; });
    if (inicial) { estado.respostas[inicial] = "sim"; estado.historico.push(inicial); }
    await proxima();
  }

  async function proxima() {
    try {
      const r = await api("/api/triagem/proxima", { method: "POST", body: { categoria: estado.categoria, respostas: estado.respostas } });
      if (r.concluido) { return finalizar(); }
      estado.pergunta = r.pergunta;
      desenhar(r);
      mostrar("etapa-perguntas");
      mostrarAviso("");
    } catch (e) {
      mostrarAviso(e.message);
      if (Object.keys(estado.respostas).length === 0) mostrar("etapa-inicio");
    }
  }

  function desenhar(r) {
    const p = r.pergunta;
    $("pergunta").textContent = p.texto;
    $("ajuda").textContent = p.ajuda || "";
    $("por-que").textContent = p.por_que;
    const n = Object.keys(estado.respostas).length;
    $("contador").textContent = `Pergunta ${n + 1} · ${r.progresso.regras_candidatas} hipótese(s) ainda compatível(is)`;
    $("barra").style.width = `${Math.min(95, 12 + n * 14)}%`;
    const ctr = $("controles");
    if (p.tipo === "numerico") {
      ctr.innerHTML = `<div class="campo"><label for="valor-num">Valor${p.unidade ? " (" + esc(p.unidade) + ")" : ""}</label>
        <input type="number" id="valor-num" step="0.1" min="${p.min ?? ""}" max="${p.max ?? ""}" inputmode="decimal"></div>
        <div class="acoes"><button class="btn primario grande" id="b-enviar">Confirmar valor</button><button class="btn grande" id="b-nsei">Não sei</button></div>`;
      $("b-enviar").onclick = () => {
        const v = $("valor-num").value.trim().replace(",", ".");
        if (v === "" || isNaN(Number(v))) { mostrarAviso("Informe um número válido ou escolha “Não sei”."); return; }
        if ((p.min !== null && Number(v) < p.min) || (p.max !== null && Number(v) > p.max)) { mostrarAviso(`O valor deve estar entre ${p.min} e ${p.max} ${p.unidade || ""}.`); return; }
        responder(Number(v));
      };
      $("b-nsei").onclick = () => responder("nao_sei");
      $("valor-num").addEventListener("keydown", (ev) => { if (ev.key === "Enter") { ev.preventDefault(); $("b-enviar").click(); } });
      $("valor-num").focus();
    } else {
      ctr.innerHTML = `<div class="acoes"><button class="btn sim grande" data-r="sim">Sim</button><button class="btn nao grande" data-r="nao">Não</button><button class="btn grande" data-r="nao_sei">Não sei</button></div>`;
      ctr.querySelectorAll("button").forEach((b) => (b.onclick = () => responder(b.dataset.r)));
    }
    desenharRespondidas();
    $("resumo-prog").textContent = `${r.progresso.regras_satisfeitas} regra(s) já satisfeita(s).`;
  }

  function rotuloResposta(v) { return v === "sim" ? "Sim" : v === "nao" ? "Não" : v === "nao_sei" ? "Não sei" : String(v).replace(".", ","); }

  function desenharRespondidas() {
    const itens = Object.entries(estado.respostas);
    $("respondidas").innerHTML = itens.length ? itens.map(([f, v]) => `<li><span>${esc(descricao(f))}</span><strong>${esc(rotuloResposta(v))}</strong></li>`).join("")
      : '<li class="muted">Nenhuma resposta ainda.</li>';
  }

  function descricao(f) { return descricoes[f] || f; }

  async function responder(valor) {
    const p = estado.pergunta;
    descricoes[p.fato] = p.descricao;
    estado.respostas[p.fato] = valor;
    estado.historico.push(p.fato);
    try {
      const r = await api("/api/triagem/proxima", { method: "POST", body: { categoria: estado.categoria, respostas: estado.respostas } });
      if (r.concluido) return finalizar();
      estado.pergunta = r.pergunta; desenhar(r); mostrarAviso("");
    } catch (e) {
      delete estado.respostas[p.fato];
      estado.historico.pop();
      mostrarAviso(e.message, e.tipo === "contradicao" ? "aviso" : "erro");
    }
  }

  async function voltar() {
    if (!estado.historico.length) { mostrar("etapa-inicio"); return; }
    const ultimo = estado.historico.pop();
    delete estado.respostas[ultimo];
    if (!estado.historico.length && !Object.keys(estado.respostas).length) { mostrar("etapa-inicio"); return; }
    await proxima();
  }

  async function finalizar() {
    mostrar("etapa-final");
    try {
      if (!Object.keys(estado.respostas).length) throw new Error("Nenhuma resposta foi informada.");
      const r = await api("/api/diagnostico", { method: "POST", body: { categoria: estado.categoria, respostas: estado.respostas, veiculo: estado.veiculo } });
      if (r.id) { window.location.href = `/resultado/${r.id}`; return; }
      sessionStorage.setItem("diagnostico_temporario", JSON.stringify(r));
      mostrar("etapa-inicio");
      mostrarAviso(r.aviso || "O diagnóstico não pôde ser salvo.", "aviso");
    } catch (e) {
      mostrar("etapa-inicio");
      mostrarAviso(e.message);
    }
  }

  $("btn-iniciar").addEventListener("click", iniciar);
  $("btn-voltar").addEventListener("click", voltar);
  $("btn-cancelar").addEventListener("click", () => { estado.respostas = {}; estado.historico = []; mostrar("etapa-inicio"); mostrarAviso(""); });
  carregarCategorias();
})();
