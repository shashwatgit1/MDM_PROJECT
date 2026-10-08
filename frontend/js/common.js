// Shared helpers: API wrapper, sidebar, toast, escaping.
export async function api(path, opts = {}) {
  const res = await fetch("/api" + path, {
    headers: { "Content-Type": "application/json" },
    ...opts, body: opts.body ? JSON.stringify(opts.body) : undefined,
  });
  const data = res.status === 204 ? null : await res.json().catch(() => ({}));
  if (!res.ok) throw Object.assign(new Error(data?.error || "Request failed"), { fields: data?.fields || {}, status: res.status });
  return data;
}
export const esc = s => String(s).replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
export function toast(msg, error = false) {
  let t = document.getElementById("toast");
  if (!t) { t = document.body.appendChild(Object.assign(document.createElement("div"), { id: "toast", role: "status" })); }
  t.textContent = msg; t.className = "show" + (error ? " error" : "");
  clearTimeout(t._h); t._h = setTimeout(() => (t.className = ""), 2800);
}
export function sidebar() {
  const page = location.pathname.split("/").pop() || "index.html";
  const link = (href, label) => `<a href="${href}" ${page === href ? 'aria-current="page"' : ""}>${label}</a>`;
  document.body.insertAdjacentHTML("afterbegin",
    `<aside><div class="brand">Roll Call<small>Student records</small></div>
     <nav>${link("index.html", "Overview")}${link("students.html", "All students")}${link("form.html", "Add student")}</nav></aside>`);
}
export const band = m => (m >= 75 ? "var(--good)" : m >= 50 ? "var(--mid)" : "var(--low)");
