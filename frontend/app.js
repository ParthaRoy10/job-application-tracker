// ==========================================================
// Config — point this at wherever your FastAPI backend runs.
// ==========================================================
const API_BASE_URL = "http://localhost:8000";

// ==========================================================
// Tiny state
// ==========================================================
const state = {
  token: localStorage.getItem("pt_token") || null,
  user: null,
  companies: [],
  applications: [],
};

// ==========================================================
// DOM refs
// ==========================================================
const authScreen = document.getElementById("authScreen");
const appScreen = document.getElementById("appScreen");
const loginForm = document.getElementById("loginForm");
const registerForm = document.getElementById("registerForm");
const companyForm = document.getElementById("companyForm");
const userGreeting = document.getElementById("userGreeting");
const logoutBtn = document.getElementById("logoutBtn");
const toastEl = document.getElementById("toast");

// ==========================================================
// Toast helper
// ==========================================================
let toastTimer = null;
function showToast(message, kind = "ok") {
  clearTimeout(toastTimer);
  toastEl.textContent = message;
  toastEl.className = `toast is-${kind}`;
  toastEl.classList.remove("hidden");
  toastTimer = setTimeout(() => toastEl.classList.add("hidden"), 3200);
}

function setFormMsg(formEl, message, kind) {
  const el = document.querySelector(`[data-msg-for="${formEl.id}"]`);
  if (!el) return;
  el.textContent = message || "";
  el.className = `form-msg ${message ? `is-${kind}` : ""}`;
}

// ==========================================================
// API helper
// ==========================================================
async function api(path, { method = "GET", body, auth = true } = {}) {
  const headers = { "Content-Type": "application/json" };
  if (auth && state.token) headers["Authorization"] = `Bearer ${state.token}`;

  let res;
  try {
    res = await fetch(`${API_BASE_URL}${path}`, {
      method,
      headers,
      body: body ? JSON.stringify(body) : undefined,
    });
  } catch (networkErr) {
    throw new Error(
      `Couldn't reach the server at ${API_BASE_URL}. Is the backend running, and does it allow requests from this page (CORS)?`
    );
  }

  let data = null;
  const text = await res.text();
  if (text) {
    try { data = JSON.parse(text); } catch { /* non-json response */ }
  }

  if (!res.ok) {
    if (res.status === 401 && auth) {
      // token expired/invalid — send the user back to the door
      clearSession();
      showAuthScreen();
    }
    const detail = data && data.detail ? data.detail : `Request failed (${res.status})`;
    throw new Error(typeof detail === "string" ? detail : JSON.stringify(detail));
  }
  return data;
}

// ==========================================================
// Session
// ==========================================================
function saveSession(token) {
  state.token = token;
  localStorage.setItem("pt_token", token);
}
function clearSession() {
  state.token = null;
  state.user = null;
  localStorage.removeItem("pt_token");
}

function showAuthScreen() {
  appScreen.classList.add("hidden");
  authScreen.classList.remove("hidden");
}
function showAppScreen() {
  authScreen.classList.add("hidden");
  appScreen.classList.remove("hidden");
}

// ==========================================================
// Auth tab switching (login / register)
// ==========================================================
document.querySelectorAll("[data-auth-tab]").forEach((btn) => {
  btn.addEventListener("click", () => {
    document.querySelectorAll("[data-auth-tab]").forEach((b) => {
      b.classList.remove("is-active");
      b.setAttribute("aria-selected", "false");
    });
    btn.classList.add("is-active");
    btn.setAttribute("aria-selected", "true");

    const mode = btn.dataset.authTab;
    loginForm.classList.toggle("hidden", mode !== "login");
    registerForm.classList.toggle("hidden", mode !== "register");
  });
});

// ==========================================================
// Login
// ==========================================================
loginForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  setFormMsg(loginForm, "", null);
  const fd = new FormData(loginForm);
  const payload = { email: fd.get("email"), password: fd.get("password") };

  try {
    const data = await api("/users/login", { method: "POST", body: payload, auth: false });
    saveSession(data.access_token);
    await bootApp();
  } catch (err) {
    setFormMsg(loginForm, err.message, "error");
  }
});

// ==========================================================
// Register
// ==========================================================
registerForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  setFormMsg(registerForm, "", null);
  const fd = new FormData(registerForm);
  const payload = {
    name: fd.get("name"),
    email: fd.get("email"),
    password: fd.get("password"),
  };

  try {
    await api("/users/", { method: "POST", body: payload, auth: false });
    // Registered — log them straight in.
    const data = await api("/users/login", {
      method: "POST",
      body: { email: payload.email, password: payload.password },
      auth: false,
    });
    saveSession(data.access_token);
    await bootApp();
  } catch (err) {
    setFormMsg(registerForm, err.message, "error");
  }
});

// ==========================================================
// Logout
// ==========================================================
logoutBtn.addEventListener("click", () => {
  clearSession();
  showAuthScreen();
  loginForm.reset();
  registerForm.reset();
});

// ==========================================================
// Folder tab navigation
// ==========================================================
document.querySelectorAll(".folder-tab").forEach((tab) => {
  tab.addEventListener("click", () => {
    document.querySelectorAll(".folder-tab").forEach((t) => t.classList.remove("is-active"));
    tab.classList.add("is-active");
    document.querySelectorAll(".view").forEach((v) => v.classList.remove("is-active"));
    document.getElementById(`view-${tab.dataset.view}`).classList.add("is-active");
  });
});

// ==========================================================
// Formatting helpers
// ==========================================================
const currencyFmt = new Intl.NumberFormat("en-IN", {
  style: "currency",
  currency: "INR",
  maximumFractionDigits: 0,
});
function formatDate(d) {
  return new Date(d).toLocaleDateString("en-IN", { day: "numeric", month: "short", year: "numeric" });
}

const STATUS_LABEL = {
  APPLIED: "Filed",
  ACTIVE: "In process",
  REJECTED: "Rejected",
  SELECTED: "Selected",
};
const STATUS_CLASS = {
  APPLIED: "stamp--applied",
  ACTIVE: "stamp--active",
  REJECTED: "stamp--rejected",
  SELECTED: "stamp--selected",
};

// ==========================================================
// Load data
// ==========================================================
async function loadCompanies() {
  state.companies = await api("/companies/", { auth: false });
  renderCompanies();
}
async function loadApplications() {
  state.applications = await api("/applications/");
  renderApplications();
}

// ==========================================================
// Render: companies
// ==========================================================
function renderCompanies() {
  const grid = document.getElementById("companiesGrid");
  const emptyNote = document.querySelector('[data-empty-for="companies"]');
  grid.innerHTML = "";

  if (!state.companies.length) {
    emptyNote.classList.remove("hidden");
    return;
  }
  emptyNote.classList.add("hidden");

  const appliedCompanyIds = new Set(state.applications.map((a) => a.company_id));

  state.companies.forEach((c) => {
    const alreadyApplied = appliedCompanyIds.has(c.id);
    const card = document.createElement("article");
    card.className = "card item-card";
    card.innerHTML = `
      <div class="tack"></div>
      <h3 class="item-title">${escapeHtml(c.company_name)}</h3>
      <p class="item-position">${escapeHtml(c.position)}</p>
      <ul class="item-meta">
        <li><span>Location</span><span>${escapeHtml(c.location)}</span></li>
        <li><span>CTC</span><span>${currencyFmt.format(c.ctc)}</span></li>
        <li><span>Visiting</span><span>${formatDate(c.date_visiting)}</span></li>
      </ul>
      <div class="item-actions">
        ${
          alreadyApplied
            ? `<span class="stamp stamp--applied">Filed</span>`
            : `<button class="btn btn--small" data-apply="${c.id}">Apply</button>`
        }
      </div>
    `;
    grid.appendChild(card);
  });

  grid.querySelectorAll("[data-apply]").forEach((btn) => {
    btn.addEventListener("click", () => applyToCompany(Number(btn.dataset.apply)));
  });
}

async function applyToCompany(companyId) {
  try {
    const today = new Date().toISOString().slice(0, 10);
    await api("/applications/", {
      method: "POST",
      body: { company_id: companyId, status: "APPLIED", date_applied: today },
    });
    showToast("Application filed.", "ok");
    await Promise.all([loadApplications(), loadCompanies()]);
  } catch (err) {
    showToast(err.message, "error");
  }
}

// ==========================================================
// Render: applications
// ==========================================================
function renderApplications() {
  const grid = document.getElementById("applicationsGrid");
  const emptyNote = document.querySelector('[data-empty-for="applications"]');
  grid.innerHTML = "";

  if (!state.applications.length) {
    emptyNote.classList.remove("hidden");
    return;
  }
  emptyNote.classList.add("hidden");

  const companyById = new Map(state.companies.map((c) => [c.id, c]));

  state.applications.forEach((a) => {
    const company = companyById.get(a.company_id);
    const card = document.createElement("article");
    card.className = "card item-card";
    card.innerHTML = `
      <div class="tack"></div>
      <h3 class="item-title">${escapeHtml(company ? company.company_name : `Company #${a.company_id}`)}</h3>
      <p class="item-position">${escapeHtml(company ? company.position : "")}</p>
      <ul class="item-meta">
        <li><span>Applied on</span><span>${formatDate(a.date_applied)}</span></li>
        <li><span>Last updated</span><span>${formatDate(a.updated_at)}</span></li>
      </ul>
      <div class="item-actions">
        <span class="stamp ${STATUS_CLASS[a.status]}">${STATUS_LABEL[a.status]}</span>
        <select class="status-select" data-status-for="${a.id}">
          ${Object.keys(STATUS_LABEL)
            .map((s) => `<option value="${s}" ${s === a.status ? "selected" : ""}>${STATUS_LABEL[s]}</option>`)
            .join("")}
        </select>
        <button class="btn btn--danger btn--small" data-withdraw="${a.id}">Withdraw</button>
      </div>
    `;
    grid.appendChild(card);
  });

  grid.querySelectorAll("[data-status-for]").forEach((sel) => {
    sel.addEventListener("change", () => updateApplicationStatus(Number(sel.dataset.statusFor), sel.value));
  });
  grid.querySelectorAll("[data-withdraw]").forEach((btn) => {
    btn.addEventListener("click", () => withdrawApplication(Number(btn.dataset.withdraw)));
  });
}

async function updateApplicationStatus(applicationId, status) {
  try {
    await api(`/applications/${applicationId}`, { method: "PATCH", body: { status } });
    showToast("Status updated.", "ok");
    await loadApplications();
  } catch (err) {
    showToast(err.message, "error");
    await loadApplications(); // revert the select to the real value
  }
}

async function withdrawApplication(applicationId) {
  if (!confirm("Withdraw this application? This can't be undone.")) return;
  try {
    await api(`/applications/${applicationId}`, { method: "DELETE" });
    showToast("Application withdrawn.", "ok");
    await Promise.all([loadApplications(), loadCompanies()]);
  } catch (err) {
    showToast(err.message, "error");
  }
}

// ==========================================================
// Add company
// ==========================================================
companyForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  setFormMsg(companyForm, "", null);
  const fd = new FormData(companyForm);
  const payload = {
    company_name: fd.get("company_name"),
    position: fd.get("position"),
    location: fd.get("location"),
    ctc: Number(fd.get("ctc")),
    date_visiting: fd.get("date_visiting"),
  };

  try {
    await api("/companies/", { method: "POST", body: payload });
    setFormMsg(companyForm, "Added to the board.", "ok");
    companyForm.reset();
    await loadCompanies();
  } catch (err) {
    setFormMsg(companyForm, err.message, "error");
  }
});

// ==========================================================
// Boot
// ==========================================================
function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str ?? "";
  return div.innerHTML;
}

async function bootApp() {
  try {
    state.user = await api("/users/me");
    userGreeting.textContent = `Hi, ${state.user.name}`;
    showAppScreen();
    await loadCompanies();
    await loadApplications();
    renderCompanies(); // re-render now that applications are known, to grey out "Filed" companies
  } catch (err) {
    clearSession();
    showAuthScreen();
    if (err.message) setFormMsg(loginForm, err.message, "error");
  }
}

// On load, try to resume a session if a token is already stored.
if (state.token) {
  bootApp();
} else {
  showAuthScreen();
}
