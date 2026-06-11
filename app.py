import os
import traceback
from datetime import datetime, timedelta, timezone
from functools import wraps

from flask import Flask, render_template, request, jsonify, session, redirect, url_for, g
from werkzeug.security import generate_password_hash, check_password_hash
from database import get_db, init_db
from scoring import calculate_points, BONUS_POINTS, STAGE_LABELS, STAGE_ORDER
from seed_data import seed, force_reseed

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "bolao-copa-2026-mude-esta-chave")


@app.errorhandler(Exception)
def handle_error(e):
    tb = traceback.format_exc()
    return f"<h1>Erro</h1><pre>{tb}</pre>", 500

BRT = timezone(timedelta(hours=-3))
_db_ready = False


@app.before_request
def before():
    global _db_ready
    if not _db_ready:
        init_db()
        seed()
        _db_ready = True

    g.user = None
    uid = session.get("user_id")
    if uid:
        conn = get_db()
        g.user = conn.execute("SELECT id, name, email, is_approved, is_admin FROM users WHERE id = %s", (uid,)).fetchone()
        conn.close()


@app.context_processor
def inject_user():
    return {"current_user": g.user}


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not g.user:
            return redirect(url_for("login_page"))
        if not g.user["is_approved"]:
            return redirect(url_for("pending_page"))
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not g.user:
            return redirect(url_for("login_page"))
        if not g.user["is_admin"]:
            return redirect(url_for("index"))
        return f(*args, **kwargs)
    return decorated


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


# --- AUTH PAGES ---


@app.route("/login", methods=["GET", "POST"])
def login_page():
    if g.user:
        return redirect(url_for("index"))
    error = None
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        conn = get_db()
        user = conn.execute("SELECT * FROM users WHERE email = %s", (email,)).fetchone()
        conn.close()
        if user and check_password_hash(user["password_hash"], password):
            session["user_id"] = user["id"]
            if not user["is_approved"]:
                return redirect(url_for("pending_page"))
            return redirect(url_for("index"))
        error = "E-mail ou senha incorretos."
    return render_template("login.html", error=error)


@app.route("/register", methods=["GET", "POST"])
def register_page():
    if g.user:
        return redirect(url_for("index"))
    error = None
    success = False
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        if not name or not email or not password:
            error = "Preencha todos os campos."
        elif len(password) < 4:
            error = "Senha deve ter pelo menos 4 caracteres."
        else:
            conn = get_db()
            existing = conn.execute("SELECT id FROM users WHERE email = %s", (email,)).fetchone()
            if existing:
                conn.close()
                error = "Este e-mail ja esta cadastrado."
            else:
                conn.execute(
                    "INSERT INTO users (name, email, password_hash, is_approved, is_admin) VALUES (%s, %s, %s, 0, 0)",
                    (name, email, generate_password_hash(password)),
                )
                conn.commit()
                conn.close()
                success = True
    return render_template("register.html", error=error, success=success)


@app.route("/pending")
def pending_page():
    if not g.user:
        return redirect(url_for("login_page"))
    if g.user["is_approved"]:
        return redirect(url_for("index"))
    return render_template("pending.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login_page"))


# --- PAGES ---


@app.route("/")
@login_required
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
@login_required
def matches_page():
    conn = get_db()
    user_id = g.user["id"]
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

    locked_ids = set()
    for m in rows:
        if m["is_finished"] or is_match_locked(m["match_date"], m["match_time"]):
            locked_ids.add(m["id"])

    predictions = {}
    preds = conn.execute(
        "SELECT match_id, home_score, away_score, points_earned FROM predictions WHERE user_id = %s",
        (user_id,),
    ).fetchall()
    for p in preds:
        predictions[p["match_id"]] = p

    conn.close()
    return render_template(
        "matches.html", matches=rows, user_id=user_id,
        predictions=predictions, locked_ids=locked_ids,
        active_stages=active_stages, stage_filter=stage_filter,
        stage_labels=STAGE_LABELS,
    )


@app.route("/bonus")
@login_required
def bonus_page():
    conn = get_db()
    user_id = g.user["id"]
    teams = conn.execute("SELECT * FROM teams ORDER BY name").fetchall()

    bonus_preds = {}
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
        "bonus.html", teams=teams, user_id=user_id,
        bonus_preds=bonus_preds, results=results,
    )


@app.route("/admin")
@admin_required
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


@app.route("/api/admin/approve_user", methods=["POST"])
@admin_required
def approve_user():
    data = request.get_json() or request.form
    user_id = int(data["user_id"])
    conn = get_db()
    conn.execute("UPDATE users SET is_approved = 1 WHERE id = %s", (user_id,))
    conn.commit()
    conn.close()
    return jsonify({"ok": True})


@app.route("/api/admin/reject_user", methods=["POST"])
@admin_required
def reject_user():
    data = request.get_json() or request.form
    user_id = int(data["user_id"])
    conn = get_db()
    conn.execute("DELETE FROM users WHERE id = %s AND is_approved = 0", (user_id,))
    conn.commit()
    conn.close()
    return jsonify({"ok": True})


@app.route("/api/admin/reseed", methods=["POST"])
@admin_required
def reseed():
    global _db_ready
    force_reseed()
    _db_ready = True
    return jsonify({"ok": True})


@app.route("/api/predict", methods=["POST"])
@login_required
def predict():
    data = request.get_json() or request.form
    user_id = g.user["id"]
    match_id = int(data["match_id"])
    home_score = int(data["home_score"])
    away_score = int(data["away_score"])

    if home_score < 0 or away_score < 0:
        return jsonify({"error": "Placar nao pode ser negativo"}), 400

    conn = get_db()
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
@login_required
def bonus_predict():
    data = request.get_json() or request.form
    user_id = g.user["id"]
    category = data["category"]
    value = data["value"].strip()

    if category not in BONUS_POINTS:
        return jsonify({"error": "Categoria invalida"}), 400

    conn = get_db()
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
@admin_required
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
@admin_required
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
@admin_required
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
