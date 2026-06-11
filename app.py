from datetime import datetime, timedelta, timezone

from flask import Flask, render_template, request, jsonify
from database import get_db, init_db
from scoring import calculate_points, BONUS_POINTS, STAGE_LABELS, STAGE_ORDER
from seed_data import seed, force_reseed

app = Flask(__name__)

BRT = timezone(timedelta(hours=-3))

_db_ready = False


@app.before_request
def ensure_db():
    global _db_ready
    if not _db_ready:
        init_db()
        seed()
        _db_ready = True


def now_brt():
    return datetime.now(BRT)


def match_deadline(match_date, match_time):
    t = match_time or "00:00"
    dt = datetime.strptime(f"{match_date} {t}", "%Y-%m-%d %H:%M").replace(tzinfo=BRT)
    return dt - timedelta(hours=1)


def is_match_locked(match_date, match_time):
    return now_brt() >= match_deadline(match_date, match_time)


def get_active_stages(conn):
    rows = conn.execute(
        "SELECT stage, MIN(match_date) AS first_date FROM matches GROUP BY stage ORDER BY first_date"
    ).fetchall()
    stages = [r["stage"] for r in rows]
    return sorted(stages, key=lambda s: STAGE_ORDER.index(s) if s in STAGE_ORDER else 99)


# --- PAGES ---


@app.route("/")
def index():
    conn = get_db()
    stage_filter = request.args.get("stage", "")
    active_stages = get_active_stages(conn)

    stage_clause = ""
    params = []
    if stage_filter:
        stage_clause = "AND m.stage = %s"
        params = [stage_filter]

    ranking = conn.execute(f"""
        SELECT u.id, u.name,
            COALESCE(SUM(p.points_earned), 0) + COALESCE(MAX(bp.bonus), 0) AS total_points,
            COUNT(p.id) AS total_preds,
            SUM(CASE WHEN p.points_earned IS NOT NULL AND p.points_earned >= 25 THEN 1 ELSE 0 END) AS exact_hits
        FROM users u
        LEFT JOIN predictions p ON p.user_id = u.id
            LEFT JOIN matches m ON m.id = p.match_id {stage_clause}
        LEFT JOIN (
            SELECT user_id, SUM(COALESCE(points_earned, 0)) AS bonus
            FROM bonus_predictions
            GROUP BY user_id
        ) bp ON bp.user_id = u.id
        WHERE u.is_approved = 1
        GROUP BY u.id, u.name
        ORDER BY total_points DESC
    """, params).fetchall()
    conn.close()
    return render_template(
        "index.html", ranking=ranking, active_stages=active_stages,
        stage_filter=stage_filter, stage_labels=STAGE_LABELS,
    )


@app.route("/matches")
def matches_page():
    conn = get_db()
    user_id = request.args.get("user_id", type=int)
    stage_filter = request.args.get("stage", "group")
    active_stages = get_active_stages(conn)

    users = conn.execute(
        "SELECT * FROM users WHERE is_approved = 1 ORDER BY name"
    ).fetchall()

    rows = conn.execute("""
        SELECT m.id, m.match_date, m.match_time, m.stage, m.group_name,
               m.home_score, m.away_score, m.is_finished,
               ht.name AS home_team, ht.flag_emoji AS home_flag,
               at.name AS away_team, at.flag_emoji AS away_flag
        FROM matches m
        JOIN teams ht ON ht.id = m.home_team_id
        JOIN teams at ON at.id = m.away_team_id
        WHERE m.stage = %s
        ORDER BY m.match_date, m.match_time
    """, (stage_filter,)).fetchall()

    locked_ids = set()
    for m in rows:
        if m["is_finished"] or is_match_locked(m["match_date"], m["match_time"]):
            locked_ids.add(m["id"])

    predictions = {}
    if user_id:
        preds = conn.execute(
            "SELECT match_id, home_score, away_score, points_earned FROM predictions WHERE user_id = %s",
            (user_id,),
        ).fetchall()
        for p in preds:
            predictions[p["match_id"]] = p

    conn.close()
    return render_template(
        "matches.html", matches=rows, users=users, user_id=user_id,
        predictions=predictions, locked_ids=locked_ids,
        active_stages=active_stages, stage_filter=stage_filter,
        stage_labels=STAGE_LABELS, now=now_brt(),
    )


@app.route("/bonus")
def bonus_page():
    conn = get_db()
    user_id = request.args.get("user_id", type=int)
    users = conn.execute(
        "SELECT * FROM users WHERE is_approved = 1 ORDER BY name"
    ).fetchall()
    teams = conn.execute("SELECT * FROM teams ORDER BY name").fetchall()

    bonus_preds = {}
    if user_id:
        rows = conn.execute(
            "SELECT category, value, points_earned FROM bonus_predictions WHERE user_id = %s",
            (user_id,),
        ).fetchall()
        for r in rows:
            bonus_preds[r["category"]] = r

    results = {}
    for r in conn.execute("SELECT category, value FROM bonus_results").fetchall():
        results[r["category"]] = r["value"]

    conn.close()
    return render_template(
        "bonus.html", users=users, teams=teams, user_id=user_id,
        bonus_preds=bonus_preds, results=results,
    )


@app.route("/admin")
def admin():
    conn = get_db()
    stage_filter = request.args.get("stage", "group")
    active_stages = get_active_stages(conn)

    rows = conn.execute("""
        SELECT m.id, m.match_date, m.match_time, m.stage, m.group_name,
               m.home_score, m.away_score, m.is_finished,
               ht.name AS home_team, ht.flag_emoji AS home_flag,
               at.name AS away_team, at.flag_emoji AS away_flag
        FROM matches m
        JOIN teams ht ON ht.id = m.home_team_id
        JOIN teams at ON at.id = m.away_team_id
        WHERE m.stage = %s
        ORDER BY m.match_date, m.match_time
    """, (stage_filter,)).fetchall()

    teams = conn.execute("SELECT * FROM teams ORDER BY name").fetchall()
    pending_users = conn.execute(
        "SELECT * FROM users WHERE is_approved = 0 ORDER BY created_at"
    ).fetchall()
    approved_users = conn.execute(
        "SELECT * FROM users WHERE is_approved = 1 ORDER BY name"
    ).fetchall()

    results = {}
    for r in conn.execute("SELECT category, value FROM bonus_results").fetchall():
        results[r["category"]] = r["value"]

    conn.close()
    return render_template(
        "admin.html", matches=rows, teams=teams, results=results,
        pending_users=pending_users, approved_users=approved_users,
        active_stages=active_stages, stage_filter=stage_filter,
        stage_labels=STAGE_LABELS,
    )


# --- API ---


@app.route("/api/register", methods=["POST"])
def register():
    data = request.get_json() or request.form
    name = data.get("name", "").strip()
    if not name:
        return jsonify({"error": "Nome eh obrigatorio"}), 400
    conn = get_db()
    try:
        conn.execute("INSERT INTO users (name, is_approved) VALUES (%s, 0)", (name,))
        conn.commit()
    except Exception:
        conn.close()
        return jsonify({"error": "Nome ja existe"}), 409
    conn.close()
    return jsonify({"ok": True, "message": "Cadastro enviado! Aguarde aprovacao do administrador."})


@app.route("/api/admin/approve_user", methods=["POST"])
def approve_user():
    data = request.get_json() or request.form
    user_id = int(data["user_id"])
    conn = get_db()
    conn.execute("UPDATE users SET is_approved = 1 WHERE id = %s", (user_id,))
    conn.commit()
    conn.close()
    return jsonify({"ok": True})


@app.route("/api/admin/reject_user", methods=["POST"])
def reject_user():
    data = request.get_json() or request.form
    user_id = int(data["user_id"])
    conn = get_db()
    conn.execute("DELETE FROM users WHERE id = %s AND is_approved = 0", (user_id,))
    conn.commit()
    conn.close()
    return jsonify({"ok": True})


@app.route("/api/admin/reseed", methods=["POST"])
def reseed():
    global _db_ready
    force_reseed()
    _db_ready = True
    return jsonify({"ok": True, "message": "Dados recriados com sucesso."})


@app.route("/api/predict", methods=["POST"])
def predict():
    data = request.get_json() or request.form
    user_id = int(data["user_id"])
    match_id = int(data["match_id"])
    home_score = int(data["home_score"])
    away_score = int(data["away_score"])

    if home_score < 0 or away_score < 0:
        return jsonify({"error": "Placar nao pode ser negativo"}), 400

    conn = get_db()

    user = conn.execute("SELECT is_approved FROM users WHERE id = %s", (user_id,)).fetchone()
    if not user or not user["is_approved"]:
        conn.close()
        return jsonify({"error": "Usuario nao aprovado"}), 403

    match = conn.execute(
        "SELECT is_finished, match_date, match_time FROM matches WHERE id = %s", (match_id,)
    ).fetchone()
    if not match:
        conn.close()
        return jsonify({"error": "Jogo nao encontrado"}), 404
    if match["is_finished"]:
        conn.close()
        return jsonify({"error": "Jogo ja encerrado"}), 400
    if is_match_locked(match["match_date"], match["match_time"]):
        conn.close()
        return jsonify({"error": "Apostas encerradas! Fecha 1h antes do jogo."}), 400

    conn.execute("""
        INSERT INTO predictions (user_id, match_id, home_score, away_score)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT(user_id, match_id)
        DO UPDATE SET home_score = EXCLUDED.home_score, away_score = EXCLUDED.away_score
    """, (user_id, match_id, home_score, away_score))
    conn.commit()
    conn.close()
    return jsonify({"ok": True})


@app.route("/api/bonus_predict", methods=["POST"])
def bonus_predict():
    data = request.get_json() or request.form
    user_id = int(data["user_id"])
    category = data["category"]
    value = data["value"].strip()

    if category not in BONUS_POINTS:
        return jsonify({"error": "Categoria invalida"}), 400

    conn = get_db()
    user = conn.execute("SELECT is_approved FROM users WHERE id = %s", (user_id,)).fetchone()
    if not user or not user["is_approved"]:
        conn.close()
        return jsonify({"error": "Usuario nao aprovado"}), 403

    conn.execute("""
        INSERT INTO bonus_predictions (user_id, category, value)
        VALUES (%s, %s, %s)
        ON CONFLICT(user_id, category)
        DO UPDATE SET value = EXCLUDED.value
    """, (user_id, category, value))
    conn.commit()
    conn.close()
    return jsonify({"ok": True})


@app.route("/api/admin/result", methods=["POST"])
def set_result():
    data = request.get_json() or request.form
    match_id = int(data["match_id"])
    home_score = int(data["home_score"])
    away_score = int(data["away_score"])

    conn = get_db()
    match = conn.execute("SELECT stage FROM matches WHERE id = %s", (match_id,)).fetchone()
    if not match:
        conn.close()
        return jsonify({"error": "Jogo nao encontrado"}), 404

    conn.execute(
        "UPDATE matches SET home_score = %s, away_score = %s, is_finished = 1 WHERE id = %s",
        (home_score, away_score, match_id),
    )

    preds = conn.execute(
        "SELECT id, home_score, away_score FROM predictions WHERE match_id = %s",
        (match_id,),
    ).fetchall()
    for p in preds:
        pts = calculate_points(p["home_score"], p["away_score"], home_score, away_score, match["stage"])
        conn.execute("UPDATE predictions SET points_earned = %s WHERE id = %s", (pts, p["id"]))

    conn.commit()
    conn.close()
    return jsonify({"ok": True})


@app.route("/api/admin/bonus_result", methods=["POST"])
def set_bonus_result():
    data = request.get_json() or request.form
    category = data["category"]
    value = data["value"].strip()

    if category not in BONUS_POINTS:
        return jsonify({"error": "Categoria invalida"}), 400

    conn = get_db()
    conn.execute("""
        INSERT INTO bonus_results (category, value) VALUES (%s, %s)
        ON CONFLICT(category) DO UPDATE SET value = EXCLUDED.value
    """, (category, value))

    preds = conn.execute(
        "SELECT id, user_id, value FROM bonus_predictions WHERE category = %s",
        (category,),
    ).fetchall()
    for p in preds:
        pts = BONUS_POINTS[category] if p["value"].strip().lower() == value.strip().lower() else 0
        conn.execute("UPDATE bonus_predictions SET points_earned = %s WHERE id = %s", (pts, p["id"]))

    conn.commit()
    conn.close()
    return jsonify({"ok": True})


@app.route("/api/admin/add_match", methods=["POST"])
def add_match():
    data = request.get_json() or request.form
    conn = get_db()
    conn.execute(
        "INSERT INTO matches (home_team_id, away_team_id, match_date, match_time, stage, group_name) VALUES (%s, %s, %s, %s, %s, %s)",
        (int(data["home_team_id"]), int(data["away_team_id"]), data["match_date"],
         data.get("match_time", "00:00"), data["stage"], data.get("group_name", "")),
    )
    conn.commit()
    conn.close()
    return jsonify({"ok": True})


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
