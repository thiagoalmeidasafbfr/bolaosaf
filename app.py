from flask import Flask, render_template, request, jsonify, redirect, url_for
from database import get_db, init_db
from scoring import calculate_points, BONUS_POINTS
from seed_data import seed

app = Flask(__name__)


@app.before_request
def ensure_db():
    init_db()


# --- PAGES ---


@app.route("/")
def index():
    conn = get_db()
    ranking = conn.execute("""
        SELECT u.id, u.name,
            COALESCE(SUM(p.points_earned), 0) + COALESCE(bp.bonus, 0) AS total_points,
            COUNT(p.id) AS total_preds,
            SUM(CASE WHEN p.points_earned = 25 THEN 1
                      WHEN p.points_earned >= 37 THEN 1
                      ELSE 0 END) AS exact_hits
        FROM users u
        LEFT JOIN predictions p ON p.user_id = u.id
        LEFT JOIN (
            SELECT user_id, SUM(COALESCE(points_earned, 0)) AS bonus
            FROM bonus_predictions
            GROUP BY user_id
        ) bp ON bp.user_id = u.id
        GROUP BY u.id
        ORDER BY total_points DESC
    """).fetchall()
    conn.close()
    return render_template("index.html", ranking=ranking)


@app.route("/matches")
def matches():
    conn = get_db()
    user_id = request.args.get("user_id", type=int)

    users = conn.execute("SELECT * FROM users ORDER BY name").fetchall()

    rows = conn.execute("""
        SELECT m.id, m.match_date, m.match_time, m.stage, m.group_name,
               m.home_score, m.away_score, m.is_finished,
               ht.name AS home_team, ht.flag_emoji AS home_flag,
               at.name AS away_team, at.flag_emoji AS away_flag
        FROM matches m
        JOIN teams ht ON ht.id = m.home_team_id
        JOIN teams at ON at.id = m.away_team_id
        ORDER BY m.match_date, m.match_time
    """).fetchall()

    predictions = {}
    if user_id:
        preds = conn.execute(
            "SELECT match_id, home_score, away_score, points_earned FROM predictions WHERE user_id = ?",
            (user_id,),
        ).fetchall()
        for p in preds:
            predictions[p["match_id"]] = p

    conn.close()
    return render_template(
        "matches.html", matches=rows, users=users, user_id=user_id, predictions=predictions
    )


@app.route("/bonus")
def bonus_page():
    conn = get_db()
    user_id = request.args.get("user_id", type=int)
    users = conn.execute("SELECT * FROM users ORDER BY name").fetchall()
    teams = conn.execute("SELECT * FROM teams ORDER BY name").fetchall()

    bonus_preds = {}
    if user_id:
        rows = conn.execute(
            "SELECT category, value, points_earned FROM bonus_predictions WHERE user_id = ?",
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
    rows = conn.execute("""
        SELECT m.id, m.match_date, m.match_time, m.stage, m.group_name,
               m.home_score, m.away_score, m.is_finished,
               ht.name AS home_team, ht.flag_emoji AS home_flag,
               at.name AS away_team, at.flag_emoji AS away_flag
        FROM matches m
        JOIN teams ht ON ht.id = m.home_team_id
        JOIN teams at ON at.id = m.away_team_id
        ORDER BY m.match_date, m.match_time
    """).fetchall()
    teams = conn.execute("SELECT * FROM teams ORDER BY name").fetchall()

    results = {}
    for r in conn.execute("SELECT category, value FROM bonus_results").fetchall():
        results[r["category"]] = r["value"]

    conn.close()
    return render_template("admin.html", matches=rows, teams=teams, results=results)


# --- API ---


@app.route("/api/register", methods=["POST"])
def register():
    data = request.get_json() or request.form
    name = data.get("name", "").strip()
    if not name:
        return jsonify({"error": "Nome é obrigatório"}), 400
    conn = get_db()
    try:
        conn.execute("INSERT INTO users (name) VALUES (?)", (name,))
        conn.commit()
    except Exception:
        conn.close()
        return jsonify({"error": "Nome já existe"}), 409
    conn.close()
    return jsonify({"ok": True})


@app.route("/api/predict", methods=["POST"])
def predict():
    data = request.get_json() or request.form
    user_id = int(data["user_id"])
    match_id = int(data["match_id"])
    home_score = int(data["home_score"])
    away_score = int(data["away_score"])

    if home_score < 0 or away_score < 0:
        return jsonify({"error": "Placar não pode ser negativo"}), 400

    conn = get_db()
    match = conn.execute("SELECT is_finished FROM matches WHERE id = ?", (match_id,)).fetchone()
    if match and match["is_finished"]:
        conn.close()
        return jsonify({"error": "Jogo já encerrado, não pode apostar"}), 400

    conn.execute("""
        INSERT INTO predictions (user_id, match_id, home_score, away_score)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(user_id, match_id)
        DO UPDATE SET home_score = excluded.home_score, away_score = excluded.away_score
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
        return jsonify({"error": "Categoria inválida"}), 400

    conn = get_db()
    conn.execute("""
        INSERT INTO bonus_predictions (user_id, category, value)
        VALUES (?, ?, ?)
        ON CONFLICT(user_id, category)
        DO UPDATE SET value = excluded.value
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
    match = conn.execute("SELECT stage FROM matches WHERE id = ?", (match_id,)).fetchone()
    if not match:
        conn.close()
        return jsonify({"error": "Jogo não encontrado"}), 404

    conn.execute(
        "UPDATE matches SET home_score = ?, away_score = ?, is_finished = 1 WHERE id = ?",
        (home_score, away_score, match_id),
    )

    preds = conn.execute(
        "SELECT id, home_score, away_score FROM predictions WHERE match_id = ?",
        (match_id,),
    ).fetchall()
    for p in preds:
        pts = calculate_points(p["home_score"], p["away_score"], home_score, away_score, match["stage"])
        conn.execute("UPDATE predictions SET points_earned = ? WHERE id = ?", (pts, p["id"]))

    conn.commit()
    conn.close()
    return jsonify({"ok": True})


@app.route("/api/admin/bonus_result", methods=["POST"])
def set_bonus_result():
    data = request.get_json() or request.form
    category = data["category"]
    value = data["value"].strip()

    if category not in BONUS_POINTS:
        return jsonify({"error": "Categoria inválida"}), 400

    conn = get_db()
    conn.execute("""
        INSERT INTO bonus_results (category, value) VALUES (?, ?)
        ON CONFLICT(category) DO UPDATE SET value = excluded.value
    """, (category, value))

    preds = conn.execute(
        "SELECT id, user_id, value FROM bonus_predictions WHERE category = ?",
        (category,),
    ).fetchall()
    for p in preds:
        pts = BONUS_POINTS[category] if p["value"].strip().lower() == value.strip().lower() else 0
        conn.execute("UPDATE bonus_predictions SET points_earned = ? WHERE id = ?", (pts, p["id"]))

    conn.commit()
    conn.close()
    return jsonify({"ok": True})


@app.route("/api/admin/add_match", methods=["POST"])
def add_match():
    data = request.get_json() or request.form
    conn = get_db()
    conn.execute(
        "INSERT INTO matches (home_team_id, away_team_id, match_date, match_time, stage, group_name) VALUES (?, ?, ?, ?, ?, ?)",
        (int(data["home_team_id"]), int(data["away_team_id"]), data["match_date"], data.get("match_time", ""), data["stage"], data.get("group_name", "")),
    )
    conn.commit()
    conn.close()
    return jsonify({"ok": True})


if __name__ == "__main__":
    seed()
    app.run(debug=True, host="0.0.0.0", port=5000)
