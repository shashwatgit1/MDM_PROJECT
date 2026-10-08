import { api, sidebar, toast } from "./common.js";
sidebar();
const f = document.getElementById("f"), id = new URLSearchParams(location.search).get("id");
const showErrors = fields => {
  f.querySelectorAll(".err").forEach(e => { const m = fields[e.dataset.for] || ""; e.textContent = m; f.elements[e.dataset.for].classList.toggle("bad", !!m); });
  const first = Object.keys(fields)[0]; if (first && f.elements[first]) f.elements[first].focus();
};
// Frontend validation mirrors the backend rules for instant feedback.
function check(d) {
  const e = {};
  if (!/^[A-Za-z][A-Za-z .'-]{1,59}$/.test(d.name.trim())) e.name = "Enter a name of 2-60 letters.";
  if (!/^[A-Za-z0-9-]{1,20}$/.test(d.roll_no.trim())) e.roll_no = "Use letters, digits and hyphens only (max 20).";
  if (!/^[A-Za-z0-9 -]{1,20}$/.test(d.class_name.trim())) e.class_name = "Enter a class such as 10-A.";
  if (d.marks === "" || isNaN(d.marks) || d.marks < 0 || d.marks > 100) e.marks = "Marks must be a number from 0 to 100.";
  if (!/^[6-9]\d{9}$/.test(d.contact.replace(/[\s-]/g, "").replace(/^(\+91|0)/, ""))) e.contact = "Enter a 10-digit mobile number starting with 6-9.";
  return e;
}
if (id) {
  document.getElementById("title").textContent = "Edit student";
  try { const s = await api(`/students/${id}`); for (const k of ["name", "roll_no", "class_name", "marks", "contact"]) f.elements[k].value = s[k]; }
  catch { toast("That student no longer exists.", true); setTimeout(() => (location.href = "students.html"), 1200); }
}
f.addEventListener("submit", async e => {
  e.preventDefault();
  const data = Object.fromEntries(new FormData(f));
  const errs = check(data); showErrors(errs); if (Object.keys(errs).length) return;
  try {
    await api(id ? `/students/${id}` : "/students", { method: id ? "PUT" : "POST", body: data });
    toast(id ? "Changes saved" : "Student added");
    if (id) setTimeout(() => (location.href = "students.html"), 700); else { f.reset(); f.elements.name.focus(); }
  } catch (err) { showErrors(err.fields); if (!Object.keys(err.fields).length) toast(err.message, true); }
});
