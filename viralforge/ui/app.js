const DEFAULT_ORACLE_TUNNEL = "https://hydrogen-jesse-paxil-raleigh.trycloudflare.com";
let API_BASE = (localStorage.getItem("vf_api_base") || "").replace(/\/+$/, "");

if (!API_BASE && window.location.hostname.endsWith(".pages.dev")) {
  API_BASE = DEFAULT_ORACLE_TUNNEL;
}

function resolveUrl(path) {
  if (!path || path.startsWith("http://") || path.startsWith("https://")) return path;
  return `${API_BASE}${path}`;
}

function updateBackendLabel() {
  const el = document.getElementById("lblBackendMode");
  if (!el) return;
  if (!API_BASE) {
    el.textContent = "Local / Mismo Host";
  } else if (API_BASE.includes("trycloudflare.com")) {
    el.textContent = "Oracle VPS Tunnel";
  } else {
    el.textContent = API_BASE.replace(/^https?:\/\//, "").slice(0, 22);
  }
}

const state = {
  personas: [],
  products: [],
  library: { hooks: [], frameworks: [], angles: [] },
  scripts: [],
  variants: [],
  jobs: [],
};

async function api(path, opts = {}) {
  const res = await fetch(resolveUrl(path), {
    headers: { "Content-Type": "application/json", ...(opts.headers || {}) },
    ...opts,
  });
  if (!res.ok) {
    const txt = await res.text();
    throw new Error(txt || res.statusText);
  }
  return res.json();
}

function setupTabs() {
  document.querySelectorAll(".tab").forEach((btn) => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".tab").forEach((b) => b.classList.remove("active"));
      document.querySelectorAll(".tab-panel").forEach((p) => p.classList.remove("active"));
      btn.classList.add("active");
      document.getElementById(`tab-${btn.dataset.tab}`).classList.add("active");
    });
  });
}

async function loadAll() {
  const [status, lib, personas, products, variants, jobs, bandit, kg] = await Promise.all([
    api("/api/status"),
    api("/api/library"),
    api("/api/personas"),
    api("/api/products"),
    api("/api/variants"),
    api("/api/jobs"),
    api("/api/bandit/leaderboard"),
    api("/api/kaggle/catalog"),
  ]);
  state.library = lib;
  state.personas = personas;
  state.products = products;
  state.variants = variants;
  state.jobs = jobs;
  state.kaggle = kg;

  renderStats(status);
  renderSelectors();
  renderLibrary();
  renderPersonas();
  renderProducts();
  renderJobs();
  renderVariants();
  renderBandit(bandit);
  renderEngines(status.engines);
  renderKaggleCatalog(kg);
  checkOracleStatus();
  loadPosesCatalog();
}

function renderStats(status) {
  const c = status.counts || {};
  document.getElementById("statPersonas").textContent = c.personas ?? 0;
  document.getElementById("statProducts").textContent = c.products ?? 0;
  document.getElementById("statVariants").textContent = `${c.variants_done ?? 0}/${c.variants ?? 0}`;
  document.getElementById("statJobs").textContent = c.jobs_running ?? 0;
}

function renderSelectors() {
  const perSel = document.getElementById("stPersona");
  const prdSel = document.getElementById("stProduct");
  const perOpts = state.personas.map((p) => `<option value="${p.id}">${p.name} (${p.niche})</option>`).join("");
  const prdOpts = state.products.map((p) => `<option value="${p.id}">${p.title} ($${p.price ?? "-"})</option>`).join("");
  perSel.innerHTML = perOpts;
  prdSel.innerHTML = prdOpts;
  const posePer = document.getElementById("posePersonaSel");
  const posePrd = document.getElementById("poseProductSel");
  if (posePer) posePer.innerHTML = perOpts;
  if (posePrd) posePrd.innerHTML = prdOpts;

  const hookSel = document.getElementById("stHook");
  hookSel.innerHTML = `<option value="">Automático (Bandit Thompson Sampling)</option>` +
    state.library.hooks.map((h) => `<option value="${h.id}">${h.name} — ${h.trigger}</option>`).join("");

  const fwSel = document.getElementById("stFramework");
  fwSel.innerHTML = `<option value="">Automático (Bandit Thompson Sampling)</option>` +
    state.library.frameworks.map((f) => `<option value="${f.id}">${f.name}</option>`).join("");

  const angSel = document.getElementById("stAngle");
  angSel.innerHTML = `<option value="">Automático</option>` +
    state.library.angles.map((a) => `<option value="${a.id}">${a.id.toUpperCase()} — ${a.label}</option>`).join("");

  document.getElementById("cmpProducts").innerHTML = state.products.map((p) => `
    <label class="check-item"><input type="checkbox" class="cmp-prd" value="${p.id}" checked /> ${p.title}</label>
  `).join("");
  document.getElementById("cmpPersonas").innerHTML = state.personas.map((p) => `
    <label class="check-item"><input type="checkbox" class="cmp-per" value="${p.id}" checked /> ${p.name} (${p.niche})</label>
  `).join("");
}

function renderLibrary() {
  const el = document.getElementById("libraryBrowser");
  el.innerHTML = state.library.hooks.map((h) => `
    <div class="item-card">
      <div class="row-between">
        <strong>${h.name} <span class="badge badge-hook">${h.id}</span></strong>
        <span class="badge">Prior: ${Math.round(h.prior * 100)}%</span>
      </div>
      <div class="muted" style="margin:4px 0">Disparador: ${h.trigger}</div>
      <div style="font-size:13px">"${h.example}"</div>
    </div>
  `).join("");
}

function renderScripts() {
  const box = document.getElementById("scriptsList");
  if (!state.scripts.length) {
    box.innerHTML = `<p class="muted">Aún no hay guiones generados.</p>`;
    return;
  }
  box.innerHTML = state.scripts.map((sc, idx) => `
    <div class="item-card">
      <div class="row-between">
        <div>
          <span class="badge badge-hook">Gancho: ${sc.hook_formula}</span>
          <span class="badge">Estructura: ${sc.framework.toUpperCase()}</span>
          <span class="badge">Ángulo: ${sc.angle || "auto"}</span>
        </div>
        <span class="badge badge-score">Hook Score: ${sc.hook_score}/100</span>
      </div>
      <div class="beat-list">
        ${sc.beats.map((b) => `
          <div class="beat-row">
            <span class="beat-role">${b.role} [${b.visual}]</span>
            <span>${b.text}</span>
            ${b.on_screen ? `<span class="badge" style="margin-left:6px">${b.on_screen}</span>` : ""}
          </div>
        `).join("")}
      </div>
      <div class="btn-row">
        <button class="btn btn-primary btn-sm" onclick="renderFromScript(${idx})">Renderizar Reel 9:16 (MP4)</button>
      </div>
    </div>
  `).join("");
}

async function generateScripts() {
  const product_id = document.getElementById("stProduct").value;
  const persona_id = document.getElementById("stPersona").value;
  const hook = document.getElementById("stHook").value;
  const fw = document.getElementById("stFramework").value;
  const angle = document.getElementById("stAngle").value;
  const target_seconds = parseInt(document.getElementById("stSeconds").value || "24", 10);
  const count = parseInt(document.getElementById("stCount").value || "3", 10);

  const btn = document.getElementById("btnGenScripts");
  btn.disabled = true;
  btn.textContent = "Generando...";
  try {
    state.scripts = await api("/api/scripts/generate", {
      method: "POST",
      body: JSON.stringify({
        product_id,
        persona_id,
        count,
        hook_formulas: hook ? [hook] : null,
        frameworks: fw ? [fw] : null,
        angles: angle ? [angle] : null,
        target_seconds,
      }),
    });
    renderScripts();
  } finally {
    btn.disabled = false;
    btn.textContent = "Generar Guiones Ganadores";
  }
}

window.renderFromScript = async function (idx) {
  const sc = state.scripts[idx];
  const product_id = document.getElementById("stProduct").value;
  const persona_id = document.getElementById("stPersona").value;
  await api("/api/variants", {
    method: "POST",
    body: JSON.stringify({ product_id, persona_id, script: sc, render_now: true }),
  });
  await refreshJobsAndVariants();
};

let _lastVariantSig = "";

async function refreshJobsAndVariants() {
  const [status, jobs, variants] = await Promise.all([
    api("/api/status"),
    api("/api/jobs"),
    api("/api/variants"),
  ]);
  state.jobs = jobs;
  state.variants = variants;
  renderStats(status);
  renderJobs();

  const sig = variants.map((v) => `${v.id}:${v.status}:${v.duration}`).join("|");
  if (sig !== _lastVariantSig) {
    _lastVariantSig = sig;
    renderVariants();
  }
}

function renderJobs() {
  const box = document.getElementById("jobsLiveList");
  if (!state.jobs.length) {
    box.innerHTML = `<p class="muted">No hay trabajos en la cola. Renderiza un guion o lanza una campaña.</p>`;
    return;
  }
  box.innerHTML = state.jobs.slice(0, 10).map((j) => {
    const pct = Math.round((j.progress || 0) * 100);
    const lastLog = (j.log && j.log.length) ? j.log[j.log.length - 1] : j.stage;
    const isDone = j.status === "done";
    const isErr = j.status === "error";
    const badgeClass = isDone ? "badge-score" : (isErr ? "badge-hook" : "badge");
    return `
      <div class="item-card">
        <div class="row-between">
          <strong>Job ${j.id} — Etapa: <code>${j.stage || j.status}</code></strong>
          <span class="badge ${badgeClass}">${j.status.toUpperCase()} (${pct}%)</span>
        </div>
        <div class="progress-bar"><div class="progress-fill" style="width:${pct}%"></div></div>
        <div class="muted" style="margin-top:6px;margin-bottom:0">${lastLog || ""}</div>
        ${isDone && j.variant_id ? `
          <div class="btn-row" style="margin-top:10px">
            <button class="btn btn-sm btn-primary" onclick="goToReel('${j.variant_id}')">▶️ Ver Reel en Galería</button>
            <a class="btn btn-sm" href="${resolveUrl(`/media/variants/${j.variant_id}/video`)}" download="${j.variant_id}.mp4">⬇️ Descargar MP4</a>
          </div>
        ` : ""}
      </div>
    `;
  }).join("");
}

window.goToReel = function (variantId) {
  const tab = document.querySelector('[data-tab="reels"]');
  if (tab) tab.click();
};

function renderVariants() {
  const grid = document.getElementById("variantsGrid");
  if (!state.variants.length) {
    grid.innerHTML = `<p class="muted">Todavía no hay reels renderizados.</p>`;
    return;
  }
  const perMap = Object.fromEntries(state.personas.map((p) => [p.id, p]));
  const prdMap = Object.fromEntries(state.products.map((p) => [p.id, p]));

  grid.innerHTML = state.variants.map((v) => {
    const per = perMap[v.persona_id] || { name: v.persona_id };
    const prd = prdMap[v.product_id] || { title: v.product_id };
    const m = v.metrics || {};
    return `
      <div class="reel-card" id="card-${v.id}">
        ${v.status === "done"
          ? `<video controls preload="metadata" poster="${resolveUrl(`/media/variants/${v.id}/thumb`)}" src="${resolveUrl(`/media/variants/${v.id}/video`)}"></video>`
          : `<div style="aspect-ratio:9/16;display:flex;align-items:center;justify-content:center;background:#0d101a;padding:18px;text-align:center" class="muted">Estado: <strong>${v.status.toUpperCase()}</strong></div>`
        }
        <div class="reel-body">
          <div class="row-between">
            <span class="badge badge-hook">${v.script.hook_formula}</span>
            <span class="badge badge-score">Score ${v.script.hook_score}</span>
          </div>
          <strong>${prd.title}</strong>
          <div class="muted" style="margin:0">Creadora: ${per.name} • ${v.script.framework.toUpperCase()} • ${v.duration ? v.duration + "s" : ""}</div>
          <div style="font-size:12px;color:#cbd5e1">"${v.script.beats[0]?.text || ""}"</div>
          ${m.views ? `<div class="badge">👁 ${m.views.toLocaleString()} • Hold 3s: ${m.hold_3s}% • Ventas: ${m.sales}</div>` : ""}
          <div class="btn-row">
            ${v.status === "done" ? `<a class="btn btn-sm btn-primary" href="${resolveUrl(`/media/variants/${v.id}/video`)}" download="${v.id}.mp4">Descargar MP4</a>` : ""}
            <button class="btn btn-sm" onclick="rerenderVariant('${v.id}')">Re-renderizar</button>
          </div>
        </div>
      </div>
    `;
  }).join("");
}

window.rerenderVariant = async function (id) {
  await api(`/api/variants/${id}/render`, { method: "POST" });
  await refreshJobsAndVariants();
};

function renderBandit(data) {
  const box = document.getElementById("banditBoards");
  const sections = [
    { key: "hook", title: "Top Fórmulas de Gancho (Thompson Sampling)" },
    { key: "fw", title: "Top Estructuras de Venta" },
    { key: "persona", title: "Rendimiento por AI Influencer" },
  ];
  box.innerHTML = sections.map((sec) => {
    const items = (data[sec.key] || []).slice(0, 8);
    return `
      <div class="item-card">
        <h3>${sec.title}</h3>
        <div class="stack">
          ${items.map((it, i) => `
            <div class="row-between" style="font-size:13px">
              <span><strong>#${i + 1}</strong> ${it.arm.replace(/^[^:]+:/, "")}</span>
              <span class="badge ${i === 0 ? "badge-score" : ""}">Media: ${(it.mean * 100).toFixed(1)}% (n=${it.pulls})</span>
            </div>
          `).join("") || `<span class="muted">Sin datos aún</span>`}
        </div>
      </div>
    `;
  }).join("");
}

function renderPersonas() {
  const box = document.getElementById("personasList");
  box.innerHTML = state.personas.map((p) => `
    <div class="item-card media-row">
      <img class="avatar-thumb" src="${resolveUrl(`/media/personas/${p.id}?t=${Math.floor(p.created_at)}`)}" alt="${p.name}" />
      <div style="flex:1">
        <div class="row-between">
          <strong>${p.name} <span class="badge">${p.niche}</span></strong>
          <span class="badge">${p.voice}</span>
        </div>
        <div class="muted" style="margin:4px 0">${p.bio || p.tone}</div>
        <div class="btn-row">
          <button class="btn btn-sm" onclick="previewVoice('${p.id}')">🔊 Escuchar Voz</button>
          <button class="btn btn-sm" onclick="regenAvatar('${p.id}')">🎨 Nuevo Retrato</button>
        </div>
      </div>
    </div>
  `).join("");
}

window.previewVoice = async function (id) {
  const res = await fetch(resolveUrl(`/api/personas/${id}/voice-preview`), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text: "Para de hacer scroll si quieres ver el producto más viral de nuestra tienda." }),
  });
  const blob = await res.blob();
  const audio = new Audio(URL.createObjectURL(blob));
  audio.play();
};

window.regenAvatar = async function (id) {
  await api(`/api/personas/${id}/regenerate-avatar`, { method: "POST" });
  await loadAll();
};

function renderProducts() {
  const box = document.getElementById("productsList");
  box.innerHTML = state.products.map((p) => `
    <div class="item-card media-row">
      <img class="prod-thumb" src="${resolveUrl(`/media/products/${p.id}/0`)}" alt="${p.title}" />
      <div style="flex:1">
        <div class="row-between">
          <strong>${p.title}</strong>
          <div>
            <span class="badge badge-score">$${p.price ?? "-"} ${p.currency}</span>
            ${p.is_wearable ? `<span class="badge badge-hook">Try-On Activo</span>` : ""}
          </div>
        </div>
        <div class="muted" style="margin:4px 0">${(p.benefits || []).slice(0, 2).join(" • ")}</div>
      </div>
    </div>
  `).join("");
}

function renderEngines(eng) {
  if (!eng) return;
  const grid = document.getElementById("enginesStatusGrid");
  grid.innerHTML = Object.entries(eng).map(([k, v]) => `
    <div class="item-card">
      <h3>Motor: ${k.toUpperCase()}</h3>
      <pre style="font-size:12px;color:#cbd5e1;white-space:pre-wrap;margin-top:8px">${JSON.stringify(v, null, 2)}</pre>
    </div>
  `).join("");
}

function renderKaggleCatalog(kg) {
  if (!kg) return;
  const sel = document.getElementById("kgAccountSelect");
  if (sel) {
    sel.innerHTML = (kg.accounts || []).map((a) => `
      <option value="${a.slot}">${a.slot} — @${a.username}</option>
    `).join("") || `<option value="cuenta_1">cuenta_1 — @juanxaviercasa</option>`;
  }
  const grid = document.getElementById("kaggleDatasetsGrid");
  if (grid) {
    grid.innerHTML = (kg.datasets || []).map((d) => `
      <div class="item-card">
        <div class="row-between">
          <strong>${d.title}</strong>
          <span class="badge badge-score">${d.size_gb} GB</span>
        </div>
        <div style="margin:4px 0"><span class="badge badge-hook">${d.pack}</span> <code>${d.slug}</code></div>
        <div class="muted" style="margin:0">${d.use}</div>
      </div>
    `).join("");
  }
}

async function checkOracleStatus() {
  const box = document.getElementById("oracleStatusBox");
  if (!box) return;
  box.innerHTML = `<p class="muted">Consultando VPS de Oracle por SSH...</p>`;
  try {
    const res = await api("/api/oracle/status");
    const inv = (res.instances_inventory || []).map((inst) => `
      <div class="item-card">
        <div class="row-between">
          <strong>${inst.name} (${inst.ip})</strong>
          <span class="badge badge-score">${inst.shape}</span>
        </div>
        <div class="muted" style="margin:4px 0">Disco: ${inst.disk} • Rol: ${inst.role}</div>
      </div>
    `).join("");
    box.innerHTML = `
      <div class="item-card">
        <div class="row-between">
          <strong>Host: ${res.host} (${res.hostname || "forjavia-pilot"})</strong>
          <span class="badge ${res.online ? "badge-score" : "badge-hook"}">${res.online ? "SSH ONLINE" : "OFFLINE"}</span>
        </div>
        <div class="muted" style="margin:6px 0 0">RAM: <b>${res.memory || "-"}</b> • Disco: <b>${res.disk || "-"}</b></div>
      </div>
      ${inv}
    `;
  } catch (e) {
    box.innerHTML = `<div class="item-card muted">Error SSH: ${e.message}</div>`;
  }
}

// Eventos
document.addEventListener("DOMContentLoaded", () => {
  setupTabs();
  updateBackendLabel();
  loadAll();

  const btnCfg = document.getElementById("btnConfigBackend");
  if (btnCfg) {
    btnCfg.addEventListener("click", async () => {
      const next = prompt(
        "URL del Backend API de ViralForge (deja vacío para usar el mismo servidor o pega tu túnel Cloudflare del VPS de Oracle):",
        API_BASE || DEFAULT_ORACLE_TUNNEL
      );
      if (next === null) return;
      API_BASE = next.trim().replace(/\/+$/, "");
      if (API_BASE) localStorage.setItem("vf_api_base", API_BASE);
      else localStorage.removeItem("vf_api_base");
      updateBackendLabel();
      await loadAll();
    });
  }

  document.getElementById("btnGenScripts").addEventListener("click", generateScripts);
  document.getElementById("btnRefreshJobs").addEventListener("click", refreshJobsAndVariants);
  document.getElementById("btnRefreshVariants").addEventListener("click", refreshJobsAndVariants);

  document.getElementById("btnRunOpenjutsu").addEventListener("click", async () => {
    const btn = document.getElementById("btnRunOpenjutsu");
    btn.disabled = true;
    btn.textContent = "Iniciando OpenJutsu...";
    try {
      const fd = new FormData();
      fd.append("persona_id", document.getElementById("stPersona").value);
      fd.append("product_id", document.getElementById("stProduct").value);
      fd.append("mode", document.getElementById("ojMode").value);
      fd.append("script_text", document.getElementById("ojScriptText").value);
      fd.append("keep_original_audio", document.getElementById("ojKeepAudio").checked ? "true" : "false");
      const fileInput = document.getElementById("ojVideoFile");
      if (fileInput.files && fileInput.files[0]) {
        fd.append("video", fileInput.files[0]);
      }
      const res = await fetch(resolveUrl("/api/openjutsu/reshoot"), { method: "POST", body: fd });
      if (!res.ok) throw new Error(await res.text());
      await refreshJobsAndVariants();
    } catch (e) {
      alert("Error en OpenJutsu: " + e.message);
    } finally {
      btn.disabled = false;
      btn.textContent = "⚡ Ejecutar OpenJutsu Video Swap (MP4)";
    }
  });

  document.getElementById("btnPushKaggle").addEventListener("click", async () => {
    const slot = document.getElementById("kgAccountSelect").value || "cuenta_1";
    const msg = document.getElementById("kgPushMsg");
    msg.textContent = `Generando y subiendo cuaderno GPU a Kaggle (${slot})...`;
    try {
      const res = await api("/api/kaggle/push-notebook", {
        method: "POST",
        body: JSON.stringify({ account_slot: slot }),
      });
      msg.innerHTML = `✅ Cuaderno desplegado en <b>${res.kernel_id}</b> — <a href="${res.url}" target="_blank" style="color:var(--accent)">Abrir en Kaggle</a>`;
    } catch (e) {
      msg.textContent = `Error: ${e.message}`;
    }
  });

  document.getElementById("btnConnectTunnel").addEventListener("click", async () => {
    const url = document.getElementById("kgTunnelUrl").value.trim();
    if (!url) return;
    const msg = document.getElementById("kgConnectMsg");
    try {
      const res = await api("/api/kaggle/connect-tunnel", {
        method: "POST",
        body: JSON.stringify({ url, roles: ["openjutsu", "llm", "lipsync", "tts"] }),
      });
      msg.textContent = `✅ Nodo GPU conectado en caliente: ${JSON.stringify(res.updated)}`;
      renderEngines(res.engines);
    } catch (e) {
      msg.textContent = `Error: ${e.message}`;
    }
  });

  document.getElementById("btnCheckOracle").addEventListener("click", checkOracleStatus);

  document.getElementById("btnScoreHook").addEventListener("click", async () => {
    const text = document.getElementById("hookTestInput").value.trim();
    if (!text) return;
    const res = await api("/api/hooks/score", { method: "POST", body: JSON.stringify({ text, lang: "es" }) });
    const box = document.getElementById("hookScoreResult");
    box.classList.remove("hidden");
    box.innerHTML = `<strong>Hook Score: ${res.score}/100</strong> — Desglose: ` +
      Object.entries(res.breakdown).map(([k, v]) => `${k}: <b>${v}</b>`).join(" | ");
  });

  document.getElementById("btnLaunchCampaign").addEventListener("click", async () => {
    const product_ids = [...document.querySelectorAll(".cmp-prd:checked")].map((el) => el.value);
    const persona_ids = [...document.querySelectorAll(".cmp-per:checked")].map((el) => el.value);
    if (!product_ids.length || !persona_ids.length) return alert("Selecciona al menos 1 producto y 1 influencer.");
    const name = document.getElementById("cmpName").value || "Campaña";
    const variants_per_combo = parseInt(document.getElementById("cmpVariants").value || "2", 10);
    const target_seconds = parseInt(document.getElementById("cmpSeconds").value || "24", 10);
    const exploration = parseFloat(document.getElementById("cmpExplore").value || "0.35");

    await api("/api/campaigns/launch", {
      method: "POST",
      body: JSON.stringify({ name, product_ids, persona_ids, variants_per_combo, target_seconds, exploration, render: true }),
    });
    document.querySelector('[data-tab="studio"]').click();
    await refreshJobsAndVariants();
  });

  document.getElementById("btnSimulateBandit").addEventListener("click", async () => {
    const res = await api("/api/bandit/simulate", { method: "POST" });
    renderBandit(res.leaderboard);
    await refreshJobsAndVariants();
  });

  document.getElementById("btnRefreshBandit").addEventListener("click", async () => {
    renderBandit(await api("/api/bandit/leaderboard"));
  });

  document.getElementById("btnCreatePersona").addEventListener("click", async () => {
    const name = document.getElementById("perName").value.trim();
    if (!name) return alert("Introduce un nombre para la influencer.");
    await api("/api/personas", {
      method: "POST",
      body: JSON.stringify({
        name,
        niche: document.getElementById("perNiche").value || "lifestyle",
        voice: document.getElementById("perVoice").value,
        gender: document.getElementById("perGender").value,
        tone: document.getElementById("perTone").value,
        catchphrases: document.getElementById("perCatch").value.split(",").map((s) => s.trim()).filter(Boolean),
        appearance_prompt: document.getElementById("perPrompt").value,
        brand_color: document.getElementById("perBrand").value,
        accent_color: document.getElementById("perAccent").value,
      }),
    });
    document.getElementById("perName").value = "";
    await loadAll();
  });

  document.getElementById("btnCreateProduct").addEventListener("click", async () => {
    const title = document.getElementById("prdTitle").value.trim();
    if (!title) return alert("Introduce el título del producto.");
    await api("/api/products", {
      method: "POST",
      body: JSON.stringify({
        title,
        product_type: document.getElementById("prdType").value.trim(),
        price: parseFloat(document.getElementById("prdPrice").value || "0") || null,
        compare_at_price: parseFloat(document.getElementById("prdOldPrice").value || "0") || null,
        currency: document.getElementById("prdCurrency").value.trim() || "USD",
        benefits: document.getElementById("prdBenefits").value.split("\n").map((s) => s.trim()).filter(Boolean),
        pain_points: document.getElementById("prdPains").value.split("\n").map((s) => s.trim()).filter(Boolean),
        audience: document.getElementById("prdAudience").value.trim(),
        is_wearable: document.getElementById("prdWearable").checked,
      }),
    });
    document.getElementById("prdTitle").value = "";
    await loadAll();
  });

  document.getElementById("btnImportShopify").addEventListener("click", async () => {
    const domain_or_url = document.getElementById("shopDomain").value.trim();
    const limit = parseInt(document.getElementById("shopLimit").value || "5", 10);
    if (!domain_or_url) return;
    const msg = document.getElementById("shopifyMsg");
    msg.textContent = "Importando productos e imágenes desde Shopify...";
    try {
      const res = await api("/api/shopify/import", {
        method: "POST",
        body: JSON.stringify({ domain_or_url, limit }),
      });
      msg.textContent = `¡Importados ${res.imported} productos con éxito!`;
      await loadAll();
    } catch (e) {
      msg.textContent = `Error: ${e.message}`;
    }
  });

  setInterval(async () => {
    const running = state.jobs.some((j) => j.status === "queued" || j.status === "running");
    if (running) await refreshJobsAndVariants();
  }, 2500);

  // Director de Poses (1,439 ControlNet)
  ["poseSystem", "poseAngle", "poseBeat"].forEach((id) => {
    const el = document.getElementById(id);
    if (el) el.addEventListener("change", () => { state.posePage = 0; filterAndRenderPoses(); });
  });
  const pq = document.getElementById("poseQuery");
  if (pq) pq.addEventListener("input", () => { state.posePage = 0; filterAndRenderPoses(); });

  const bpPrev = document.getElementById("btnPosePrev");
  const bpNext = document.getElementById("btnPoseNext");
  if (bpPrev) bpPrev.addEventListener("click", () => {
    if ((state.posePage || 0) > 0) { state.posePage--; filterAndRenderPoses(); }
  });
  if (bpNext) bpNext.addEventListener("click", () => {
    state.posePage = (state.posePage || 0) + 1;
    filterAndRenderPoses();
  });

  const btnCloseInsp = document.getElementById("btnClosePoseInspector");
  if (btnCloseInsp) btnCloseInsp.addEventListener("click", () => {
    document.getElementById("poseInspectorCard").classList.add("hidden");
  });

  const btnRenderPose = document.getElementById("btnRenderPoseLookbook");
  if (btnRenderPose) btnRenderPose.addEventListener("click", async () => {
    const group_id = state.activePoseGroup;
    if (!group_id) return;
    const persona_id = document.getElementById("posePersonaSel").value;
    const product_id = document.getElementById("poseProductSel").value;
    const script_text = document.getElementById("poseCustomScript").value.trim();
    const msg = document.getElementById("poseRenderMsg");
    btnRenderPose.disabled = true;
    msg.textContent = `Encolando Reel Lookbook 5 Ángulos (${group_id})...`;
    try {
      await api("/api/poses/lookbook-reel", {
        method: "POST",
        body: JSON.stringify({ group_id, persona_id, product_id, script_text }),
      });
      msg.textContent = "✅ Lookbook 5 Ángulos encolado. Redirigiendo a la cola en vivo...";
      await refreshJobsAndVariants();
      setTimeout(() => {
        document.querySelector('[data-tab="studio"]').click();
      }, 650);
    } catch (e) {
      msg.textContent = `Error: ${e.message}`;
    } finally {
      btnRenderPose.disabled = false;
    }
  });
});

// ---------------------------------------------------------------------- Funciones del Director de Poses (1,439 Poses)
async function loadPosesCatalog() {
  if (state.posesAll && state.posesAll.length) return;
  try {
    const res = await fetch("/static/poses_1439.json");
    if (res.ok) {
      state.posesAll = await res.json();
    } else {
      const apiRes = await api("/api/poses?limit=1500");
      state.posesAll = apiRes.items || [];
    }
  } catch (_) {
    try {
      const apiRes = await api("/api/poses?limit=1500");
      state.posesAll = apiRes.items || [];
    } catch (__) {
      state.posesAll = [];
    }
  }
  state.posePage = 0;
  filterAndRenderPoses();
}

function filterAndRenderPoses() {
  const all = state.posesAll || [];
  const grid = document.getElementById("posesGrid");
  if (!grid) return;

  const sys = document.getElementById("poseSystem")?.value || "";
  const ang = document.getElementById("poseAngle")?.value || "";
  const beat = document.getElementById("poseBeat")?.value || "";
  const q = (document.getElementById("poseQuery")?.value || "").trim().toLowerCase();

  const filtered = all.filter((p) => {
    if (sys && p.system !== sys) return false;
    if (ang && p.angle !== ang) return false;
    if (beat && p.recommended_beat !== beat) return false;
    if (q) {
      const hay = `${p.id} ${p.pose_num} ${p.name_es} ${p.name_orig} ${p.category} ${p.system_es} ${p.angle_es}`.toLowerCase();
      if (!hay.includes(q)) return false;
    }
    return true;
  });

  const pageSize = 36;
  const maxPage = Math.max(0, Math.ceil(filtered.length / pageSize) - 1);
  if ((state.posePage || 0) > maxPage) state.posePage = maxPage;
  const page = state.posePage || 0;
  const slice = filtered.slice(page * pageSize, (page + 1) * pageSize);

  const badge = document.getElementById("poseCountBadge");
  if (badge) badge.textContent = `${filtered.length} poses filtradas (de ${all.length})`;
  const pageInfo = document.getElementById("posePageInfo");
  if (pageInfo) pageInfo.textContent = `Página ${page + 1} de ${maxPage + 1}`;

  if (!slice.length) {
    grid.innerHTML = `<p class="muted">No se encontraron poses con esos filtros.</p>`;
    return;
  }

  grid.innerHTML = slice.map((p) => `
    <div class="pose-card">
      <img class="pose-img" loading="lazy" src="${p.thumb_url}" onerror="this.onerror=null;this.src='${p.fallback_thumb_url}'" onclick="openPoseInspector('${p.group_id}')" alt="${p.name_es}" />
      <div class="pose-body">
        <div class="row-between">
          <span class="badge badge-hook">${p.pose_num} • ${p.angle.toUpperCase()}</span>
          <span class="badge badge-score">Beat: ${p.recommended_beat.toUpperCase()}</span>
        </div>
        <strong style="font-size:13px">${p.name_es}</strong>
        <div class="muted" style="margin:0;font-size:11.5px">${p.system_es} • ${p.angle_es}</div>
        <div class="btn-row" style="margin-top:6px">
          <button class="btn btn-sm btn-primary" onclick="openPoseInspector('${p.group_id}')">🎥 5 Ángulos & Lookbook</button>
          <a class="btn btn-sm" href="${p.image_url}" target="_blank" rel="noopener">🔍 PNG</a>
        </div>
      </div>
    </div>
  `).join("");
}

window.openPoseInspector = function (groupId) {
  state.activePoseGroup = groupId;
  const all = state.posesAll || [];
  const order = { front: 0, diag: 1, side: 2, high: 3, low: 4 };
  const group = all.filter((p) => p.group_id === groupId).sort((a, b) => (order[a.angle] ?? 9) - (order[b.angle] ?? 9));
  if (!group.length) return;

  const card = document.getElementById("poseInspectorCard");
  card.classList.remove("hidden");
  document.getElementById("poseInspTitle").textContent = `🎥 Inspector Multi-Ángulo: ${group[0].pose_num} — ${group[0].name_es} (${group[0].system_es})`;
  document.getElementById("poseRenderMsg").textContent = "";

  const box = document.getElementById("poseInspectorAngles");
  box.innerHTML = group.map((g) => `
    <div class="pose-card">
      <a href="${g.image_url}" target="_blank" rel="noopener">
        <img class="pose-img" src="${g.image_url}" onerror="this.onerror=null;this.src='${g.fallback_image_url}'" alt="${g.angle_es}" />
      </a>
      <div class="pose-body">
        <span class="badge badge-score">${g.angle_es}</span>
        <div class="muted" style="margin:0;font-size:11px">ControlNet 900×1200 PNG</div>
      </div>
    </div>
  `).join("");

  card.scrollIntoView({ behavior: "smooth", block: "start" });
};
