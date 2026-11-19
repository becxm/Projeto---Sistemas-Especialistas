const API_BASE = "/api";

let confirmedFacts = [];
let deniedFacts = [];
let currentSymptom = null;

const elQuestion = document.getElementById("triage-question");
const elActions = document.getElementById("triage-actions");
const elChips = document.getElementById("confirmed-chips");
const elResultSection = document.getElementById("result-section");

async function loadDashboard() {
  try {
    const res = await fetch(`${API_BASE}/stats`);
    const data = await res.json();
    document.getElementById("stat-total").textContent = data.total_diagnosticos ?? 0;

    const topSistema = data.por_sistema?.[0];
    document.getElementById("stat-top-sistema").textContent = topSistema
      ? `${topSistema.sistema} (${topSistema.percentual}%)`
      : "—";

    const list = document.getElementById("history-list");
    list.innerHTML = "";
    if (!data.recentes || data.recentes.length === 0) {
      list.innerHTML = '<li class="muted">Nenhum diagnóstico registrado ainda.</li>';
      return;
    }

    for (const item of data.recentes) {
      const li = document.createElement("li");
      li.textContent = `[${item.sistema}] ${item.diagnostico} (${item.probabilidade}%)`;
      list.appendChild(li);
    }
  } catch (err) {
    console.error("Erro ao carregar dashboard:", err);
  }
}

async function fetchNextQuestion() {
  const res = await fetch(`${API_BASE}/triage/next`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      sintomas_confirmados: confirmedFacts,
      sintomas_negados: deniedFacts,
    }),
  });
  const data = await res.json();

  if (data.finalizado || !data.proxima_pergunta) {
    await runDiagnosis();
    return;
  }

  currentSymptom = data.proxima_pergunta.sintoma;
  elQuestion.textContent = data.proxima_pergunta.pergunta;
}

async function runDiagnosis() {
  elActions.hidden = true;
  elQuestion.textContent = "Triagem finalizada.";

  const res = await fetch(`${API_BASE}/diagnose`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      sintomas_confirmados: confirmedFacts,
      sintomas_negados: deniedFacts,
    }),
  });
  const data = await res.json();

  elResultSection.hidden = false;
  const badge = document.getElementById("result-badge");
  if (!res.ok) {
    badge.textContent = "Erro de Validação";
    badge.className = "badge inconclusivo";
    document.getElementById("result-diagnostico").textContent = data.erro || "Entrada inválida.";
    return;
  }

  badge.textContent =
    data.status === "concluido"
      ? `${data.sistema} • ${data.probabilidade_percentual}% de certeza`
      : "Inconclusivo";
  badge.className = data.status === "concluido" ? "badge" : "badge inconclusivo";

  document.getElementById("result-diagnostico").textContent = data.diagnostico;
  document.getElementById("result-solucao").textContent = data.solucao;
  document.getElementById("result-especialista").textContent = data.especialista;
  document.getElementById("explanation-why").textContent = data.explicacao.por_que;

  const rulesList = document.getElementById("explanation-rules");
  rulesList.innerHTML = "";
  for (const r of data.explicacao.regras_ativadas) {
    const li = document.createElement("li");
    li.textContent = `Regra ${r.id} (${r.probabilidade_percentual}%): ${r.diagnostico} — Fatos: ${r.fatos_correspondentes.join(", ")}`;
    rulesList.appendChild(li);
  }

  await loadDashboard();
}

function renderChips() {
  elChips.innerHTML = "";
  for (const fact of confirmedFacts) {
    const span = document.createElement("span");
    span.className = "chip";
    span.textContent = fact;
    elChips.appendChild(span);
  }
}

document.getElementById("btn-nova-triagem").addEventListener("click", async () => {
  confirmedFacts = [];
  deniedFacts = [];
  currentSymptom = null;
  elResultSection.hidden = true;
  elActions.hidden = false;
  renderChips();
  await fetchNextQuestion();
});

document.getElementById("btn-sim").addEventListener("click", async () => {
  if (!currentSymptom) return;
  confirmedFacts.push(currentSymptom);
  renderChips();
  await fetchNextQuestion();
});

document.getElementById("btn-nao").addEventListener("click", async () => {
  if (!currentSymptom) return;
  deniedFacts.push(currentSymptom);
  await fetchNextQuestion();
});

document.getElementById("btn-finalizar").addEventListener("click", runDiagnosis);

loadDashboard();
