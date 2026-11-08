// Mobile menu
const btn = document.querySelector(".menu-btn"), nav = document.querySelector(".nav");
if (btn && nav) btn.addEventListener("click", () => {
  const open = nav.classList.toggle("open");
  btn.setAttribute("aria-expanded", open);
});

// Live total and grade while a teacher types scores
const grade = t => t >= 70 ? "A" : t >= 60 ? "B" : t >= 50 ? "C" : t >= 45 ? "D" : t >= 40 ? "E" : "F";
document.querySelectorAll("tr[data-row]").forEach(row => {
  const inputs = row.querySelectorAll("input.score");
  const total = row.querySelector(".live-total"), g = row.querySelector(".live-grade");
  const update = () => {
    if (![...inputs].some(i => i.value !== "")) { total.textContent = ""; g.textContent = ""; g.className = "grade live-grade"; return; }
    const t = [...inputs].reduce((s, i) => s + (parseInt(i.value, 10) || 0), 0);
    total.textContent = t; g.textContent = grade(t); g.className = "grade live-grade g-" + grade(t);
  };
  inputs.forEach(i => i.addEventListener("input", update));
});
