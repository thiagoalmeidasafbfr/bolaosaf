from werkzeug.security import generate_password_hash
from database import get_db, init_db

GROUPS = {
    "A": [
        ("Mexico", "\U0001f1f2\U0001f1fd"),
        ("Africa do Sul", "\U0001f1ff\U0001f1e6"),
        ("Coreia do Sul", "\U0001f1f0\U0001f1f7"),
        ("Tchequia", "\U0001f1e8\U0001f1ff"),
    ],
    "B": [
        ("Canada", "\U0001f1e8\U0001f1e6"),
        ("Bosnia", "\U0001f1e7\U0001f1e6"),
        ("Catar", "\U0001f1f6\U0001f1e6"),
        ("Suica", "\U0001f1e8\U0001f1ed"),
    ],
    "C": [
        ("Brasil", "\U0001f1e7\U0001f1f7"),
        ("Marrocos", "\U0001f1f2\U0001f1e6"),
        ("Haiti", "\U0001f1ed\U0001f1f9"),
        ("Escocia", "\U0001f3f4\U000e0067\U000e0062\U000e0073\U000e0063\U000e0074\U000e007f"),
    ],
    "D": [
        ("EUA", "\U0001f1fa\U0001f1f8"),
        ("Paraguai", "\U0001f1f5\U0001f1fe"),
        ("Australia", "\U0001f1e6\U0001f1fa"),
        ("Turquia", "\U0001f1f9\U0001f1f7"),
    ],
    "E": [
        ("Alemanha", "\U0001f1e9\U0001f1ea"),
        ("Curacao", "\U0001f1e8\U0001f1fc"),
        ("Costa do Marfim", "\U0001f1e8\U0001f1ee"),
        ("Equador", "\U0001f1ea\U0001f1e8"),
    ],
    "F": [
        ("Holanda", "\U0001f1f3\U0001f1f1"),
        ("Japao", "\U0001f1ef\U0001f1f5"),
        ("Suecia", "\U0001f1f8\U0001f1ea"),
        ("Tunisia", "\U0001f1f9\U0001f1f3"),
    ],
    "G": [
        ("Belgica", "\U0001f1e7\U0001f1ea"),
        ("Egito", "\U0001f1ea\U0001f1ec"),
        ("Ira", "\U0001f1ee\U0001f1f7"),
        ("Nova Zelandia", "\U0001f1f3\U0001f1ff"),
    ],
    "H": [
        ("Espanha", "\U0001f1ea\U0001f1f8"),
        ("Cabo Verde", "\U0001f1e8\U0001f1fb"),
        ("Arabia Saudita", "\U0001f1f8\U0001f1e6"),
        ("Uruguai", "\U0001f1fa\U0001f1fe"),
    ],
    "I": [
        ("Franca", "\U0001f1eb\U0001f1f7"),
        ("Senegal", "\U0001f1f8\U0001f1f3"),
        ("Noruega", "\U0001f1f3\U0001f1f4"),
        ("Iraque", "\U0001f1ee\U0001f1f6"),
    ],
    "J": [
        ("Argentina", "\U0001f1e6\U0001f1f7"),
        ("Austria", "\U0001f1e6\U0001f1f9"),
        ("Argelia", "\U0001f1e9\U0001f1ff"),
        ("Jordania", "\U0001f1ef\U0001f1f4"),
    ],
    "K": [
        ("Portugal", "\U0001f1f5\U0001f1f9"),
        ("Rep. Dem. do Congo", "\U0001f1e8\U0001f1e9"),
        ("Uzbequistao", "\U0001f1fa\U0001f1ff"),
        ("Colombia", "\U0001f1e8\U0001f1f4"),
    ],
    "L": [
        ("Inglaterra", "\U0001f3f4\U000e0067\U000e0062\U000e0065\U000e006e\U000e0067\U000e007f"),
        ("Croacia", "\U0001f1ed\U0001f1f7"),
        ("Gana", "\U0001f1ec\U0001f1ed"),
        ("Panama", "\U0001f1f5\U0001f1e6"),
    ],
}

# Horarios em BRT (Brasilia, UTC-3)
# Fonte: FIFA.com - schedule oficial convertido de ET para BRT
MATCHES = [
    # ===== RODADA 1 =====
    # 11/jun
    ("Mexico", "Africa do Sul", "2026-06-11", "16:00", "group", "A"),
    ("Coreia do Sul", "Tchequia", "2026-06-11", "23:00", "group", "A"),
    # 12/jun
    ("Canada", "Bosnia", "2026-06-12", "16:00", "group", "B"),
    ("EUA", "Paraguai", "2026-06-12", "22:00", "group", "D"),
    # 13/jun (01h = meia-noite ET do dia 12)
    ("Australia", "Turquia", "2026-06-13", "01:00", "group", "D"),
    ("Catar", "Suica", "2026-06-13", "16:00", "group", "B"),
    ("Brasil", "Marrocos", "2026-06-13", "19:00", "group", "C"),
    ("Haiti", "Escocia", "2026-06-13", "22:00", "group", "C"),
    # 14/jun
    ("Alemanha", "Curacao", "2026-06-14", "14:00", "group", "E"),
    ("Holanda", "Japao", "2026-06-14", "17:00", "group", "F"),
    ("Costa do Marfim", "Equador", "2026-06-14", "20:00", "group", "E"),
    ("Suecia", "Tunisia", "2026-06-14", "23:00", "group", "F"),
    # 15/jun
    ("Espanha", "Cabo Verde", "2026-06-15", "13:00", "group", "H"),
    ("Belgica", "Egito", "2026-06-15", "16:00", "group", "G"),
    ("Arabia Saudita", "Uruguai", "2026-06-15", "19:00", "group", "H"),
    ("Ira", "Nova Zelandia", "2026-06-15", "22:00", "group", "G"),
    # 16/jun
    ("Franca", "Senegal", "2026-06-16", "14:00", "group", "I"),
    ("Iraque", "Noruega", "2026-06-16", "17:00", "group", "I"),
    ("Argentina", "Argelia", "2026-06-16", "20:00", "group", "J"),
    ("Austria", "Jordania", "2026-06-16", "23:00", "group", "J"),
    # 17/jun
    ("Portugal", "Rep. Dem. do Congo", "2026-06-17", "14:00", "group", "K"),
    ("Inglaterra", "Croacia", "2026-06-17", "17:00", "group", "L"),
    ("Gana", "Panama", "2026-06-17", "20:00", "group", "L"),
    ("Uzbequistao", "Colombia", "2026-06-17", "23:00", "group", "K"),

    # ===== RODADA 2 =====
    # 18/jun
    ("Tchequia", "Africa do Sul", "2026-06-18", "13:00", "group", "A"),
    ("Suica", "Bosnia", "2026-06-18", "16:00", "group", "B"),
    ("Canada", "Catar", "2026-06-18", "19:00", "group", "B"),
    ("Mexico", "Coreia do Sul", "2026-06-18", "22:00", "group", "A"),
    # 19/jun
    ("EUA", "Australia", "2026-06-19", "16:00", "group", "D"),
    ("Escocia", "Marrocos", "2026-06-19", "19:00", "group", "C"),
    ("Brasil", "Haiti", "2026-06-19", "22:00", "group", "C"),
    ("Turquia", "Paraguai", "2026-06-19", "22:00", "group", "D"),
    # 20/jun
    ("Holanda", "Suecia", "2026-06-20", "14:00", "group", "F"),
    ("Alemanha", "Costa do Marfim", "2026-06-20", "17:00", "group", "E"),
    ("Equador", "Curacao", "2026-06-20", "21:00", "group", "E"),
    ("Tunisia", "Japao", "2026-06-20", "23:00", "group", "F"),
    # 21/jun
    ("Espanha", "Arabia Saudita", "2026-06-21", "13:00", "group", "H"),
    ("Belgica", "Ira", "2026-06-21", "16:00", "group", "G"),
    ("Uruguai", "Cabo Verde", "2026-06-21", "19:00", "group", "H"),
    ("Nova Zelandia", "Egito", "2026-06-21", "22:00", "group", "G"),
    # 22/jun
    ("Argentina", "Austria", "2026-06-22", "14:00", "group", "J"),
    ("Franca", "Iraque", "2026-06-22", "18:00", "group", "I"),
    ("Noruega", "Senegal", "2026-06-22", "21:00", "group", "I"),
    # 23/jun (inclui jogo de 22/jun 11PM ET = 00h BRT)
    ("Jordania", "Argelia", "2026-06-23", "00:00", "group", "J"),
    ("Portugal", "Uzbequistao", "2026-06-23", "14:00", "group", "K"),
    ("Inglaterra", "Gana", "2026-06-23", "17:00", "group", "L"),
    ("Panama", "Croacia", "2026-06-23", "20:00", "group", "L"),
    ("Colombia", "Rep. Dem. do Congo", "2026-06-23", "23:00", "group", "K"),

    # ===== RODADA 3 (jogos simultaneos por grupo) =====
    # 24/jun
    ("Tchequia", "Mexico", "2026-06-24", "22:00", "group", "A"),
    ("Africa do Sul", "Coreia do Sul", "2026-06-24", "22:00", "group", "A"),
    ("Suica", "Canada", "2026-06-24", "22:00", "group", "B"),
    ("Bosnia", "Catar", "2026-06-24", "22:00", "group", "B"),
    ("Escocia", "Brasil", "2026-06-24", "22:00", "group", "C"),
    ("Marrocos", "Haiti", "2026-06-24", "22:00", "group", "C"),
    # 25/jun
    ("Equador", "Alemanha", "2026-06-25", "17:00", "group", "E"),
    ("Curacao", "Costa do Marfim", "2026-06-25", "17:00", "group", "E"),
    ("Tunisia", "Holanda", "2026-06-25", "20:00", "group", "F"),
    ("Japao", "Suecia", "2026-06-25", "20:00", "group", "F"),
    ("Turquia", "EUA", "2026-06-25", "23:00", "group", "D"),
    ("Paraguai", "Australia", "2026-06-25", "23:00", "group", "D"),
    # 26/jun
    ("Noruega", "Franca", "2026-06-26", "16:00", "group", "I"),
    ("Senegal", "Iraque", "2026-06-26", "16:00", "group", "I"),
    ("Cabo Verde", "Arabia Saudita", "2026-06-26", "21:00", "group", "H"),
    ("Uruguai", "Espanha", "2026-06-26", "21:00", "group", "H"),
    # 27/jun (inclui jogos de 26/jun 11PM ET = 00h BRT)
    ("Egito", "Ira", "2026-06-27", "00:00", "group", "G"),
    ("Nova Zelandia", "Belgica", "2026-06-27", "00:00", "group", "G"),
    ("Argelia", "Austria", "2026-06-27", "17:00", "group", "J"),
    ("Jordania", "Argentina", "2026-06-27", "17:00", "group", "J"),
    ("Colombia", "Portugal", "2026-06-27", "20:00", "group", "K"),
    ("Rep. Dem. do Congo", "Uzbequistao", "2026-06-27", "20:00", "group", "K"),
    ("Panama", "Inglaterra", "2026-06-27", "23:00", "group", "L"),
    ("Croacia", "Gana", "2026-06-27", "23:00", "group", "L"),
]


def seed():
    init_db()
    conn = get_db()

    admin_exists = conn.execute("SELECT COUNT(*) AS cnt FROM users WHERE is_admin = 1").fetchone()["cnt"]
    if admin_exists == 0:
        conn.execute(
            "INSERT INTO users (name, email, password_hash, is_approved, is_admin) VALUES (%s, %s, %s, 1, 1)",
            ("Admin", "admin@bolao.com", generate_password_hash("bolao2026")),
        )
        conn.commit()

    existing = conn.execute("SELECT COUNT(*) AS cnt FROM teams").fetchone()["cnt"]
    if existing > 0:
        conn.close()
        return

    for group_name, teams in GROUPS.items():
        for team_name, flag in teams:
            conn.execute(
                "INSERT INTO teams (name, group_name, flag_emoji) VALUES (%s, %s, %s)",
                (team_name, group_name, flag),
            )
    conn.commit()

    for home, away, date, time, stage, group in MATCHES:
        home_id = conn.execute("SELECT id FROM teams WHERE name = %s", (home,)).fetchone()["id"]
        away_id = conn.execute("SELECT id FROM teams WHERE name = %s", (away,)).fetchone()["id"]
        conn.execute(
            "INSERT INTO matches (home_team_id, away_team_id, match_date, match_time, stage, group_name) VALUES (%s, %s, %s, %s, %s, %s)",
            (home_id, away_id, date, time, stage, group),
        )
    conn.commit()
    conn.close()
    print(f"Seed completo: {len(GROUPS) * 4} selecoes e {len(MATCHES)} jogos inseridos.")


def force_reseed():
    conn = get_db()
    conn.execute("TRUNCATE predictions, bonus_predictions, bonus_results, matches, teams RESTART IDENTITY CASCADE")
    conn.commit()
    conn.close()
    seed()


if __name__ == "__main__":
    seed()
