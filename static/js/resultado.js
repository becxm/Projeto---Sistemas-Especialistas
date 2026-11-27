(async function () {
  const raiz = document.getElementById("resultado");
  const lista = (itens) => `<ul class="lista-limpa">${itens.map((i) => `<li>${esc(i)}</li>`).join("")}</ul>`;

  function painelExplicacao(ex) {
    const sint = ex.sintomas_informados.map((s) => `<li class="${s.confirmado ? "cond-ok" : "cond-viol"}">${esc(s.descricao)}: <strong>${esc(s.resposta)}</strong></li>`).join("");
    const naoSei = ex.nao_sei.length ? `<p class="muted">Respondidos como “não sei” (tratados como informação ausente): ${esc(ex.nao_sei.join("; "))}.</p>` : "";
    const derivados = ex.fatos_derivados.length ? `<ul class="lista-limpa">${ex.fatos_derivados.map((d) => `<li>${esc(d.descricao)} = <strong>${esc(d.valor)}</strong> (deduzido pela regra ${esc(d.regra)}, ciclo ${d.ciclo})</li>`).join("")}</ul>`
      : '<p class="muted">Nenhum fato foi derivado por regras intermediárias neste caso.</p>';
    const regras = ex.regras_ativadas.length ? ex.regras_ativadas.map((r) => `
      <div class="regra-box"><strong>${esc(r.regra)}</strong> · ${esc(r.nome)}
        <span class="badge ${r.origem === "extensao" ? "origem-extensao" : ""}">${r.origem === "extensao" ? "extensão" : "documento"}</span>
        <span class="badge">ciclo ${r.ciclo}</span>
        <div class="muted">${esc(r.explicacao)}</div>
        <div>Condições satisfeitas:</div>${r.condicoes_satisfeitas.map((c) => `<div class="cond-ok">${esc(c)}</div>`).join("")}
        <div><strong>${esc(r.resultado)}</strong></div></div>`).join("") : '<p class="muted">Nenhuma regra foi ativada.</p>';
    const etapas = `<ol class="timeline" style="list-style:none">${ex.etapas.map((e) => `
      <li class="${esc(e.tipo)}"><div class="meta">Etapa ${e.numero}${e.ciclo ? " · ciclo " + e.ciclo : ""}</div>${esc(e.texto)}</li>`).join("")}</ol>`;
    let calculo = '<p class="muted">Sem cálculo: nenhum diagnóstico foi concluído.</p>';
    if (ex.calculo_incerteza) {
      const c = ex.calculo_incerteza;
      calculo = `<span class="formula">${esc(c.formula)}</span>${lista(c.passos)}`;
    }
    const alt = ex.alternativas.length ? ex.alternativas.map((a) => `
      <div class="regra-box"><strong>${esc(a.regra)}</strong> · ${esc(a.diagnostico)} — índice ${pct(a.indice)} (${esc(a.nivel)})
        ${a.confirmadas.map((c) => `<div class="cond-ok">${esc(c)}</div>`).join("")}
        ${a.faltam.map((c) => `<div class="cond-falta">${esc(c)} (não confirmado)</div>`).join("")}
        <div class="muted">${esc(a.calculo.join(" "))}</div></div>`).join("") : '<p class="muted">Sem hipóteses parciais relevantes.</p>';
    const desc = ex.regras_descartadas.length ? ex.regras_descartadas.map((d) => `
      <div class="regra-box"><strong>${esc(d.regra)}</strong> · ${esc(d.diagnostico)}<div class="cond-viol">${esc(d.motivo)}</div></div>`).join("") : '<p class="muted">Nenhuma regra com evidência parcial foi descartada.</p>';
    return `
      <div class="card" style="margin-top:1.2rem"><h2>${esc(ex.titulo)}</h2>
        <p><strong>Justificativa:</strong> ${esc(ex.justificativa)}</p></div>
      <details class="painel" open><summary>Sintomas e fatos informados</summary><div class="conteudo"><ul class="lista-limpa" style="list-style:none;padding:0">${sint}</ul>${naoSei}
        <h3 style="margin-top:.8rem">Fatos derivados pelo motor</h3>${derivados}</div></details>
      <details class="painel" open><summary>Etapas da inferência (como)</summary><div class="conteudo">${etapas}</div></details>
      <details class="painel" open><summary>Regras ativadas e condições satisfeitas</summary><div class="conteudo">${regras}</div></details>
      <details class="painel"><summary>Cálculo do índice de compatibilidade</summary><div class="conteudo">${calculo}<p class="alerta aviso" style="margin-top:.75rem">${esc(ex.aviso_incerteza)}</p></div></details>
      <details class="painel"><summary>Diagnósticos alternativos</summary><div class="conteudo">${alt}</div></details>
      <details class="painel"><summary>Regras descartadas</summary><div class="conteudo">${desc}</div></details>`;
  }

  try {
    const d = await api(`/api/diagnosticos/${raiz.dataset.id}`);
    const r = d.resultado, dx = r.diagnostico;
    let topo;
    if (dx) {
      topo = `<div class="card resultado-topo"><div class="page-head" style="margin-bottom:.5rem"><div>
          <span class="muted">Diagnóstico #${d.id} · ${esc(fmtData(d.data_hora))} · ${esc(r.categoria_nome)}${d.veiculo ? " · " + esc(d.veiculo) : ""}</span>
          <h1 class="dx-titulo">${esc(dx.texto)}</h1></div>${badgeStatus(r.status)}</div>
        <div>Índice de compatibilidade (heurístico): <strong>${pct(dx.indice)}</strong> · confiança ${esc(dx.nivel)}</div>
        <div class="medidor" aria-hidden="true"><span style="width:${Math.round(dx.indice * 100)}%"></span></div>
        <div class="grid cols-3" style="margin-top:1rem">
          <div><h3>Possíveis causas</h3>${lista(dx.causas)}</div>
          <div><h3>Recomendações</h3>${lista(dx.recomendacoes)}</div>
          <div><h3>Especialista indicado</h3><p>${esc(dx.especialista)}</p></div></div></div>`;
      if (r.concorrentes.length) {
        topo += `<div class="alerta aviso" style="margin-top:1rem"><strong>Diagnósticos concorrentes${r.empate ? " (índices muito próximos)" : ""}:</strong>
          ${r.concorrentes.map((c) => `<div>${esc(c.regra_id)} · ${esc(c.texto)} — ${pct(c.indice)} · ${esc(c.especialista)}</div>`).join("")}</div>`;
      }
    } else {
      topo = `<div class="card resultado-topo inconclusivo"><div class="page-head" style="margin-bottom:.5rem"><div>
          <span class="muted">Diagnóstico #${d.id} · ${esc(fmtData(d.data_hora))} · ${esc(r.categoria_nome)}${d.veiculo ? " · " + esc(d.veiculo) : ""}</span>
          <h1 class="dx-titulo">Diagnóstico inconclusivo — consulte um especialista manual</h1></div>${badgeStatus(r.status)}</div>
        <p>${esc(r.motivo_inconclusivo || "Não foi possível concluir com as informações fornecidas.")}</p>
        <p class="muted">Você pode refazer a triagem com mais informações ou encaminhar o veículo para avaliação presencial.</p></div>`;
    }
    raiz.innerHTML = topo + painelExplicacao(r.explicacao) +
      `<div class="acoes no-print" style="margin-top:1.2rem"><a class="btn primario" href="/triagem">Nova triagem</a><a class="btn" href="/historico">Ver histórico</a><button class="btn" onclick="window.print()">Imprimir laudo</button></div>`;
    document.title = `Diagnóstico #${d.id} · Oficina Mecânica`;
  } catch (e) {
    raiz.innerHTML = `<div class="card empty"><h2>Não foi possível exibir o diagnóstico</h2><p>${esc(e.message)}</p><a class="btn primario" href="/historico">Voltar ao histórico</a></div>`;
  }
})();
