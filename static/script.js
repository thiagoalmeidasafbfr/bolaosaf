document.addEventListener("DOMContentLoaded", () => {
    // --- RESEED ---
    const reseedBtn = document.getElementById("btn-reseed");
    if (reseedBtn) {
        reseedBtn.addEventListener("click", async () => {
            if (!confirm("ATENCAO: Isso apaga TODOS os jogos, times e apostas e recria do zero. Continuar?")) return;
            const msg = document.getElementById("reseed-msg");
            reseedBtn.disabled = true;
            reseedBtn.textContent = "Recriando...";
            const res = await fetch("/api/admin/reseed", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
            });
            if (res.ok) {
                msg.textContent = "Dados recriados com sucesso!";
                msg.className = "msg success";
                setTimeout(() => location.reload(), 1000);
            } else {
                msg.textContent = "Erro ao recriar dados";
                msg.className = "msg error";
                reseedBtn.disabled = false;
                reseedBtn.textContent = "Recriar Tudo";
            }
        });
    }

    // --- APROVACAO / REJEICAO ---
    document.querySelectorAll(".btn-approve").forEach((btn) => {
        btn.addEventListener("click", async () => {
            const userId = btn.dataset.user;
            const res = await fetch("/api/admin/approve_user", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ user_id: userId }),
            });
            if (res.ok) location.reload();
        });
    });

    document.querySelectorAll(".btn-reject").forEach((btn) => {
        btn.addEventListener("click", async () => {
            const userId = btn.dataset.user;
            if (!confirm("Recusar este participante?")) return;
            const res = await fetch("/api/admin/reject_user", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ user_id: userId }),
            });
            if (res.ok) location.reload();
        });
    });

    // --- APOSTAS EM JOGOS ---
    document.querySelectorAll(".predict-form").forEach((form) => {
        form.addEventListener("submit", async (e) => {
            e.preventDefault();
            const matchId = form.dataset.match;
            const homeScore = form.querySelector('[name="home_score"]').value;
            const awayScore = form.querySelector('[name="away_score"]').value;
            const res = await fetch("/api/predict", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    match_id: matchId,
                    home_score: homeScore,
                    away_score: awayScore,
                }),
            });
            const data = await res.json();
            if (res.ok) {
                const btn = form.querySelector("button");
                btn.textContent = "Salvo!";
                setTimeout(() => (btn.textContent = "Atualizar"), 1500);
            } else {
                alert(data.error || "Erro ao salvar aposta");
            }
        });
    });

    // --- APOSTAS BONUS ---
    document.querySelectorAll(".bonus-form").forEach((form) => {
        form.addEventListener("submit", async (e) => {
            e.preventDefault();
            const category = form.dataset.category;
            const value = form.querySelector('[name="value"]').value;
            const res = await fetch("/api/bonus_predict", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ category, value }),
            });
            if (res.ok) {
                const btn = form.querySelector("button");
                btn.textContent = "Salvo!";
                setTimeout(() => (btn.textContent = "Atualizar"), 1500);
            } else {
                const data = await res.json();
                alert(data.error || "Erro ao salvar");
            }
        });
    });

    // --- ADMIN: RESULTADOS ---
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

    // --- ADMIN: BONUS ---
    document.querySelectorAll(".bonus-result-form").forEach((form) => {
        form.addEventListener("submit", async (e) => {
            e.preventDefault();
            const category = form.dataset.category;
            const value = form.querySelector('[name="value"]').value;
            if (!confirm(`Definir resultado: ${value}?`)) return;
            const res = await fetch("/api/admin/bonus_result", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ category, value }),
            });
            if (res.ok) location.reload();
            else alert("Erro ao salvar");
        });
    });

    // --- ADMIN: ADICIONAR JOGO ---
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
