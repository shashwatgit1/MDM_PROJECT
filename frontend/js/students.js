import { api, esc, sidebar, toast, band } from "./common.js";
sidebar();
const $ = id => document.getElementById(id), q = $("q"), cls = $("cls"), rows = $("rows");
let timer;
const hl = (t, term) => term ? esc(t).replace(new RegExp(`(${term.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")})`, "gi"), "<mark class='hit'>$1</mark>") : esc(t);

async function loadClasses() {
  const keep = cls.value;
  cls.innerHTML = `<option value="">All classes</option>` + (await api("/classes")).map(c => `<option>${esc(c)}</option>`).join("");
  cls.value = keep;
}
async function load() {
  const term = q.value.trim();
  try {
    const list = await api(`/students?q=${encodeURIComponent(term)}&class=${encodeURIComponent(cls.value)}`);
    $("count").textContent = `${list.length} ${list.length === 1 ? "student" : "students"}${term ? ` matching “${term}”` : ""}`;
    rows.innerHTML = list.length ? list.map(s => `<tr>
      <td>${hl(s.roll_no, term)}</td><td>${hl(s.name, term)}</td><td>${esc(s.class_name)}</td>
      <td><div class="marks" style="--c:${band(s.marks)}"><span>${s.marks}</span><div class="track"><div class="fill" style="width:${s.marks}%"></div></div></div></td>
      <td>${esc(s.contact)}</td>
      <td class="act"><a class="btn sm" href="form.html?id=${s.id}">Edit</a><button class="btn sm danger" data-id="${s.id}" data-name="${esc(s.name)}">Delete</button></td></tr>`).join("")
      : `<tr><td colspan="6" class="empty">${term ? `No student matches “${esc(term)}”. Check the spelling or try a roll number.` : "No students yet. Add one to get started."}</td></tr>`;
  } catch { toast("Can't reach the server. Is Flask running?", true); }
}
q.addEventListener("input", () => { clearTimeout(timer); timer = setTimeout(load, 200); });
cls.addEventListener("change", load);
rows.addEventListener("click", e => {
  const b = e.target.closest("button[data-id]"); if (!b) return;
  $("dlgText").textContent = `${b.dataset.name} will be removed permanently.`;
  const dlg = $("dlg"); dlg.showModal();
  dlg.onclose = async () => {
    if (dlg.returnValue !== "yes") return;
    try { await api(`/students/${b.dataset.id}`, { method: "DELETE" }); toast("Student deleted"); await loadClasses(); load(); }
    catch (err) { toast(err.message, true); }
  };
});
await loadClasses(); load();
