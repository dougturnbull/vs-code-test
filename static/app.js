const expressionEl = document.getElementById("expression");
const resultEl = document.getElementById("result");
const themeToggleEl = document.getElementById("themeToggle");
const rootEl = document.documentElement;

let expression = "";
let lastResult = "0";

function setDisplay(nextExpression, nextResult = null) {
  expression = nextExpression;
  expressionEl.textContent = expression;
  if (nextResult !== null) {
    lastResult = String(nextResult);
    resultEl.textContent = lastResult;
  }
}

function appendValue(value) {
  setDisplay(expression + value);
}

function backspace() {
  setDisplay(expression.slice(0, -1));
}

function clearAll() {
  setDisplay("", "0");
}

function normalizeForApi(expr) {
  return expr.trim();
}

async function compute() {
  const expr = normalizeForApi(expression);
  if (!expr) {
    return;
  }

  resultEl.textContent = "…";

  try {
    const resp = await fetch("/api/calc", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ expression: expr }),
    });

    const data = await resp.json();
    if (!resp.ok) {
      const message = data?.detail || "Error";
      resultEl.textContent = message;
      return;
    }

    // Render integers cleanly when possible.
    const num = data.result;
    const formatted = Number.isInteger(num) ? String(num) : String(num);
    setDisplay("", formatted);
  } catch {
    resultEl.textContent = "Network error";
  }
}

function isAllowedChar(ch) {
  return /[0-9+\-*/().^]/.test(ch);
}

function currentTheme() {
  const v = rootEl.dataset.theme;
  return v === "light" || v === "dark" ? v : null;
}

function setTheme(mode) {
  rootEl.dataset.theme = mode;
  localStorage.setItem("theme", mode);
  themeToggleEl.textContent = mode === "dark" ? "Dark" : "Light";
}

function toggleTheme() {
  const mode = currentTheme() || "light";
  setTheme(mode === "dark" ? "light" : "dark");
}

document.addEventListener("click", (e) => {
  if (e.target === themeToggleEl) {
    toggleTheme();
    return;
  }

  const btn = e.target.closest("button[data-value], button[data-action]");
  if (!btn) return;

  const value = btn.getAttribute("data-value");
  const action = btn.getAttribute("data-action");

  if (value) {
    appendValue(value);
    return;
  }

  if (action === "clear") clearAll();
  if (action === "backspace") backspace();
  if (action === "equals") compute();
});

document.addEventListener("keydown", (e) => {
  if (e.key === "Enter") {
    e.preventDefault();
    compute();
    return;
  }
  if (e.key === "Backspace") {
    backspace();
    return;
  }
  if (e.key === "Escape") {
    clearAll();
    return;
  }

  if (e.key.length === 1 && isAllowedChar(e.key)) {
    appendValue(e.key);
  }
});

clearAll();

(() => {
  const saved = localStorage.getItem("theme");
  if (saved === "light" || saved === "dark") {
    setTheme(saved);
  } else {
    // Default label reflects the system mode (without forcing it).
    const prefersDark = window.matchMedia &&
      window.matchMedia("(prefers-color-scheme: dark)").matches;
    themeToggleEl.textContent = prefersDark ? "Dark" : "Light";
  }
})();
