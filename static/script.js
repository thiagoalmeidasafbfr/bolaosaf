document.addEventListener("DOMContentLoaded", () => {
    const regForm = document.getElementById("register-form");
    if (regForm) {
        regForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const name = document.getElementById("reg-name").value.trim();
            const msg = document.getElementById("reg-msg");
            const res = await fetch("/api/register", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ name }),
            });
            const data = await res.json();
            if (res.ok) {
                msg.textContent = `${name} entrou no bolão!`;
                msg.className = "msg success";
                setTimeout(() => location.reload(), 800);
            } else {
                msg.textContent = data.error || "Erro ao cadastrar";
                msg.className = "msg error";
            }
        });
    }

    document.querySelectorAll(".predict-form").forEach((form) => {
        form.addEventListener("submit", async (e) => {
            e.preventDefault();
            const params = new URLSearchParams(window.location.search);
            const userId = params.get("user_id");
            if (!userId) return alert("Selecione seu nome primeiro!");
            const matchId = form.dataset.match;
            const homeScore = form.querySelector('[name="home_score"]').value;
            const awayScore = form.querySelector('[name="away_score"]').value;
            const res = await fetch("/api/predict", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    user_id: userId,
                    match_id: matchId,
                    home_score: homeScore,
                    away_score: awayScore,
                }),
            });
            const data = await res.json();
            if (res.ok) {
                const btn = form.querySelector("button");
                btn.textContent = "Salvo ✓";
                setTimeout(() => (btn.textContent = "Atualizar"), 1500);
            } else {
                alert(data.error || "Erro ao salvar aposta");
            }
        });
    });

    document.querySelectorAll(".bonus-form").forEach((form) => {
        form.addEventListener("submit", async (e) => {
            e.preventDefault();
            const params = new URLSearchParams(window.location.search);
            const userId = params.get("user_id");
            if (!userId) return;
            const category = form.dataset.category;
            const value = form.querySelector('[name="value"]').value;
            const res = await fetch("/api/bonus_predict", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ user_id: userId, category, value }),
            });
            if (res.ok) {
                const btn = form.querySelector("button");
                btn.textContent = "Salvo ✓";
                setTimeout(() => (btn.textContent = "Atualizar"), 1500);
            }
        });
    });

    document.querySelectorAll(".result-form").forEach((form) => {
        form.addEventListener("submit", async (e) => {
            e.preventDefault();
            const matchId = form.dataset.match;
            const homeScore = form.querySelector('[name="home_score"]').value;
            const awayScore = form.querySelector('[name="away_score"]').value;
            if (!confirm(`Confirmar resultado: ${homeScore} x ${awayScore}?`)) return;
            const res = await fetch("/api/admin/result", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ match_id: matchId, home_score: homeScore, away_score: awayScore }),
            });
            if (res.ok) location.reload();
            else alert("Erro ao salvar resultado");
        });
    });

    document.querySelectorAll(".bonus-result-form").forEach((form) => {
        form.addEventListener("submit", async (e) => {
            e.preventDefault();
            const category = form.dataset.category;
            const value = form.querySelector('[name="value"]').value;
            if (!confirm(`Definir ${category}: ${value}?`)) return;
            const res = await fetch("/api/admin/bonus_result", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ category, value }),
            });
            if (res.ok) location.reload();
            else alert("Erro ao salvar");
        });
    });

    const addMatchForm = document.getElementById("add-match-form");
    if (addMatchForm) {
        addMatchForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const fd = new FormData(addMatchForm);
            const body = Object.fromEntries(fd.entries());
            const msg = document.getElementById("add-match-msg");
            const res = await fetch("/api/admin/add_match", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(body),
            });
            if (res.ok) {
                msg.textContent = "Jogo adicionado!";
                msg.className = "msg success";
                setTimeout(() => location.reload(), 800);
            } else {
                msg.textContent = "Erro ao adicionar jogo";
                msg.className = "msg error";
            }
        });
    }
});
