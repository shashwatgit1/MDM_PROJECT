import { api, esc, sidebar, toast } from "./common.js";
sidebar();
try {
  const s = await api("/stats");
  document.getElementById("stats").innerHTML =
    [["Students", s.total], ["Class average", s.average + "%"], ["Highest marks", s.highest + "%"], ["Classes", s.by_class.length]]
      .map(([l, v]) => `<div class="stat"><b>${v}</b><span>${l}</span></div>`).join("");
  document.getElementById("classes").innerHTML = s.by_class.length
    ? s.by_class.map(c => `<div class="row-bar"><span>${esc(c.name)}</span><div class="track"><div class="fill" style="width:${c.avg}%"></div></div><span>${c.avg}% · ${c.n} ${c.n === 1 ? "student" : "students"}</span></div>`).join("")
    : `<p class="empty">No classes yet. <a href="form.html">Add your first student</a>.</p>`;
  document.getElementById("topper").innerHTML = s.topper
    ? `<h2>Top scorer</h2><p><strong>${esc(s.topper.name)}</strong> (${esc(s.topper.class_name)}, roll ${esc(s.topper.roll_no)}) scored ${s.topper.marks}%.</p>`
    : "";
} catch { toast("Can't reach the server. Is Flask running?", true); }
