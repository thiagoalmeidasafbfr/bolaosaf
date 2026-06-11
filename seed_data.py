from database import get_db, init_db

GROUPS = {
    "A": [
        ("Marrocos", "\U0001f1f2\U0001f1e6"),
        ("Peru", "\U0001f1f5\U0001f1ea"),
        ("Portugal", "\U0001f1f5\U0001f1f9"),
        ("Argentina", "\U0001f1e6\U0001f1f7"),
    ],
    "B": [
        ("Australia", "\U0001f1e6\U0001f1fa"),
        ("Dinamarca", "\U0001f1e9\U0001f1f0"),
        ("Franca", "\U0001f1eb\U0001f1f7"),
        ("Indonesia", "\U0001f1ee\U0001f1e9"),
    ],
    "C": [
        ("Egito", "\U0001f1ea\U0001f1ec"),
        ("Colombia", "\U0001f1e8\U0001f1f4"),
        ("Bolivia", "\U0001f1e7\U0001f1f4"),
        ("Senegal", "\U0001f1f8\U0001f1f3"),
    ],
    "D": [
        ("Japao", "\U0001f1ef\U0001f1f5"),
        ("Costa Rica", "\U0001f1e8\U0001f1f7"),
        ("Alemanha", "\U0001f1e9\U0001f1ea"),
        ("Quenia", "\U0001f1f0\U0001f1ea"),
    ],
    "E": [
        ("Espanha", "\U0001f1ea\U0001f1f8"),
        ("Turquia", "\U0001f1f9\U0001f1f7"),
        ("Equador", "\U0001f1ea\U0001f1e8"),
        ("Bahrain", "\U0001f1e7\U0001f1ed"),
    ],
    "F": [
        ("Brasil", "\U0001f1e7\U0001f1f7"),
        ("Italia", "\U0001f1ee\U0001f1f9"),
        ("Nigeria", "\U0001f1f3\U0001f1ec"),
        ("Paraguai", "\U0001f1f5\U0001f1fe"),
    ],
    "G": [
        ("Mexico", "\U0001f1f2\U0001f1fd"),
        ("Honduras", "\U0001f1ed\U0001f1f3"),
        ("Uruguai", "\U0001f1fa\U0001f1fe"),
        ("Pais de Gales", "\U0001f3f4\U000e0067\U000e0062\U000e0077\U000e006c\U000e0073\U000e007f"),
    ],
    "H": [
        ("EUA", "\U0001f1fa\U0001f1f8"),
        ("Canada", "\U0001f1e8\U0001f1e6"),
        ("Servia", "\U0001f1f7\U0001f1f8"),
        ("Ira", "\U0001f1ee\U0001f1f7"),
    ],
    "I": [
        ("Holanda", "\U0001f1f3\U0001f1f1"),
        ("Cameroun", "\U0001f1e8\U0001f1f2"),
        ("Chile", "\U0001f1e8\U0001f1f1"),
        ("Catar", "\U0001f1f6\U0001f1e6"),
    ],
    "J": [
        ("Inglaterra", "\U0001f3f4\U000e0067\U000e0062\U000e0065\U000e006e\U000e0067\U000e007f"),
        ("Arabia Saudita", "\U0001f1f8\U0001f1e6"),
        ("Belgica", "\U0001f1e7\U0001f1ea"),
        ("Trinidad e Tobago", "\U0001f1f9\U0001f1f9"),
    ],
    "K": [
        ("Coreia do Sul", "\U0001f1f0\U0001f1f7"),
        ("Panama", "\U0001f1f5\U0001f1e6"),
        ("Croacia", "\U0001f1ed\U0001f1f7"),
        ("Jamaica", "\U0001f1ef\U0001f1f2"),
    ],
    "L": [
        ("Suica", "\U0001f1e8\U0001f1ed"),
        ("Escocia", "\U0001f3f4\U000e0067\U000e0062\U000e0073\U000e0063\U000e0074\U000e007f"),
        ("Costa do Marfim", "\U0001f1e8\U0001f1ee"),
        ("Rep. Democratica do Congo", "\U0001f1e8\U0001f1e9"),
    ],
}

MATCHES = [
    ("Marrocos", "Peru", "2026-06-11", "12:00", "group", "A"),
    ("Portugal", "Argentina", "2026-06-11", "18:00", "group", "A"),
    ("Argentina", "Marrocos", "2026-06-15", "15:00", "group", "A"),
    ("Peru", "Portugal", "2026-06-15", "18:00", "group", "A"),
    ("Argentina", "Peru", "2026-06-19", "16:00", "group", "A"),
    ("Portugal", "Marrocos", "2026-06-19", "16:00", "group", "A"),
    ("Australia", "Dinamarca", "2026-06-12", "12:00", "group", "B"),
    ("Franca", "Indonesia", "2026-06-12", "15:00", "group", "B"),
    ("Dinamarca", "Franca", "2026-06-16", "12:00", "group", "B"),
    ("Indonesia", "Australia", "2026-06-16", "15:00", "group", "B"),
    ("Franca", "Australia", "2026-06-20", "16:00", "group", "B"),
    ("Dinamarca", "Indonesia", "2026-06-20", "16:00", "group", "B"),
    ("Egito", "Colombia", "2026-06-12", "18:00", "group", "C"),
    ("Bolivia", "Senegal", "2026-06-12", "21:00", "group", "C"),
    ("Colombia", "Senegal", "2026-06-16", "18:00", "group", "C"),
    ("Egito", "Bolivia", "2026-06-16", "21:00", "group", "C"),
    ("Senegal", "Egito", "2026-06-20", "19:00", "group", "C"),
    ("Colombia", "Bolivia", "2026-06-20", "19:00", "group", "C"),
    ("Japao", "Costa Rica", "2026-06-13", "12:00", "group", "D"),
    ("Alemanha", "Quenia", "2026-06-13", "15:00", "group", "D"),
    ("Costa Rica", "Alemanha", "2026-06-17", "12:00", "group", "D"),
    ("Quenia", "Japao", "2026-06-17", "15:00", "group", "D"),
    ("Alemanha", "Japao", "2026-06-21", "16:00", "group", "D"),
    ("Costa Rica", "Quenia", "2026-06-21", "16:00", "group", "D"),
    ("Espanha", "Turquia", "2026-06-13", "18:00", "group", "E"),
    ("Equador", "Bahrain", "2026-06-13", "21:00", "group", "E"),
    ("Turquia", "Equador", "2026-06-17", "18:00", "group", "E"),
    ("Bahrain", "Espanha", "2026-06-17", "21:00", "group", "E"),
    ("Espanha", "Equador", "2026-06-21", "19:00", "group", "E"),
    ("Turquia", "Bahrain", "2026-06-21", "19:00", "group", "E"),
    ("Brasil", "Italia", "2026-06-14", "12:00", "group", "F"),
    ("Nigeria", "Paraguai", "2026-06-14", "15:00", "group", "F"),
    ("Italia", "Nigeria", "2026-06-18", "12:00", "group", "F"),
    ("Paraguai", "Brasil", "2026-06-18", "15:00", "group", "F"),
    ("Brasil", "Nigeria", "2026-06-22", "16:00", "group", "F"),
    ("Italia", "Paraguai", "2026-06-22", "16:00", "group", "F"),
    ("Mexico", "Honduras", "2026-06-14", "18:00", "group", "G"),
    ("Uruguai", "Pais de Gales", "2026-06-14", "21:00", "group", "G"),
    ("Honduras", "Uruguai", "2026-06-18", "18:00", "group", "G"),
    ("Pais de Gales", "Mexico", "2026-06-18", "21:00", "group", "G"),
    ("Mexico", "Uruguai", "2026-06-22", "19:00", "group", "G"),
    ("Honduras", "Pais de Gales", "2026-06-22", "19:00", "group", "G"),
    ("EUA", "Canada", "2026-06-11", "15:00", "group", "H"),
    ("Servia", "Ira", "2026-06-11", "21:00", "group", "H"),
    ("Canada", "Servia", "2026-06-15", "12:00", "group", "H"),
    ("Ira", "EUA", "2026-06-15", "21:00", "group", "H"),
    ("EUA", "Servia", "2026-06-19", "19:00", "group", "H"),
    ("Canada", "Ira", "2026-06-19", "19:00", "group", "H"),
    ("Holanda", "Cameroun", "2026-06-12", "09:00", "group", "I"),
    ("Chile", "Catar", "2026-06-12", "12:00", "group", "I"),
    ("Cameroun", "Chile", "2026-06-16", "09:00", "group", "I"),
    ("Catar", "Holanda", "2026-06-16", "12:00", "group", "I"),
    ("Holanda", "Chile", "2026-06-20", "13:00", "group", "I"),
    ("Cameroun", "Catar", "2026-06-20", "13:00", "group", "I"),
    ("Inglaterra", "Arabia Saudita", "2026-06-13", "09:00", "group", "J"),
    ("Belgica", "Trinidad e Tobago", "2026-06-13", "12:00", "group", "J"),
    ("Arabia Saudita", "Belgica", "2026-06-17", "09:00", "group", "J"),
    ("Trinidad e Tobago", "Inglaterra", "2026-06-17", "12:00", "group", "J"),
    ("Inglaterra", "Belgica", "2026-06-21", "13:00", "group", "J"),
    ("Arabia Saudita", "Trinidad e Tobago", "2026-06-21", "13:00", "group", "J"),
    ("Coreia do Sul", "Panama", "2026-06-14", "09:00", "group", "K"),
    ("Croacia", "Jamaica", "2026-06-14", "12:00", "group", "K"),
    ("Panama", "Croacia", "2026-06-18", "09:00", "group", "K"),
    ("Jamaica", "Coreia do Sul", "2026-06-18", "12:00", "group", "K"),
    ("Coreia do Sul", "Croacia", "2026-06-22", "13:00", "group", "K"),
    ("Panama", "Jamaica", "2026-06-22", "13:00", "group", "K"),
    ("Suica", "Escocia", "2026-06-15", "09:00", "group", "L"),
    ("Costa do Marfim", "Rep. Democratica do Congo", "2026-06-15", "12:00", "group", "L"),
    ("Escocia", "Costa do Marfim", "2026-06-19", "09:00", "group", "L"),
    ("Rep. Democratica do Congo", "Suica", "2026-06-19", "12:00", "group", "L"),
    ("Suica", "Costa do Marfim", "2026-06-23", "13:00", "group", "L"),
    ("Escocia", "Rep. Democratica do Congo", "2026-06-23", "13:00", "group", "L"),
]


def seed():
    init_db()
    conn = get_db()

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


if __name__ == "__main__":
    seed()
