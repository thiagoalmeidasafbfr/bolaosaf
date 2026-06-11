from database import get_db, init_db

GROUPS = {
    "A": [
        ("Marrocos", "🇲🇦"),
        ("Peru", "🇵🇪"),
        ("Portugal", "🇵🇹"),
        ("Argentina", "🇦🇷"),
    ],
    "B": [
        ("Austrália", "🇦🇺"),
        ("Dinamarca", "🇩🇰"),
        ("França", "🇫🇷"),
        ("Indonésia", "🇮🇩"),
    ],
    "C": [
        ("Egito", "🇪🇬"),
        ("Colômbia", "🇨🇴"),
        ("Bolívia", "🇧🇴"),
        ("Senegal", "🇸🇳"),
    ],
    "D": [
        ("Japão", "🇯🇵"),
        ("Costa Rica", "🇨🇷"),
        ("Alemanha", "🇩🇪"),
        ("Quênia", "🇰🇪"),
    ],
    "E": [
        ("Espanha", "🇪🇸"),
        ("Turquia", "🇹🇷"),
        ("Equador", "🇪🇨"),
        ("Bahrain", "🇧🇭"),
    ],
    "F": [
        ("Brasil", "🇧🇷"),
        ("Itália", "🇮🇹"),
        ("Nigéria", "🇳🇬"),
        ("Paraguai", "🇵🇾"),
    ],
    "G": [
        ("México", "🇲🇽"),
        ("Honduras", "🇭🇳"),
        ("Uruguai", "🇺🇾"),
        ("País de Gales", "🏴󠁧󠁢󠁷󠁬󠁳󠁿"),
    ],
    "H": [
        ("EUA", "🇺🇸"),
        ("Canadá", "🇨🇦"),
        ("Sérvia", "🇷🇸"),
        ("Irã", "🇮🇷"),
    ],
    "I": [
        ("Holanda", "🇳🇱"),
        ("Cameroun", "🇨🇲"),
        ("Chile", "🇨🇱"),
        ("Catar", "🇶🇦"),
    ],
    "J": [
        ("Inglaterra", "🏴󠁧󠁢󠁥󠁮󠁧󠁿"),
        ("Arábia Saudita", "🇸🇦"),
        ("Bélgica", "🇧🇪"),
        ("Trinidad e Tobago", "🇹🇹"),
    ],
    "K": [
        ("Coreia do Sul", "🇰🇷"),
        ("Panamá", "🇵🇦"),
        ("Croácia", "🇭🇷"),
        ("Jamaica", "🇯🇲"),
    ],
    "L": [
        ("Suíça", "🇨🇭"),
        ("Escócia", "🏴󠁧󠁢󠁳󠁣󠁴󠁿"),
        ("Costa do Marfim", "🇨🇮"),
        ("Rep. Democrática do Congo", "🇨🇩"),
    ],
}

MATCHES = [
    # --- GRUPO A ---
    ("Marrocos", "Peru", "2026-06-11", "12:00", "group", "A"),
    ("Portugal", "Argentina", "2026-06-11", "18:00", "group", "A"),
    ("Argentina", "Marrocos", "2026-06-15", "15:00", "group", "A"),
    ("Peru", "Portugal", "2026-06-15", "18:00", "group", "A"),
    ("Argentina", "Peru", "2026-06-19", "16:00", "group", "A"),
    ("Portugal", "Marrocos", "2026-06-19", "16:00", "group", "A"),
    # --- GRUPO B ---
    ("Austrália", "Dinamarca", "2026-06-12", "12:00", "group", "B"),
    ("França", "Indonésia", "2026-06-12", "15:00", "group", "B"),
    ("Dinamarca", "França", "2026-06-16", "12:00", "group", "B"),
    ("Indonésia", "Austrália", "2026-06-16", "15:00", "group", "B"),
    ("França", "Austrália", "2026-06-20", "16:00", "group", "B"),
    ("Dinamarca", "Indonésia", "2026-06-20", "16:00", "group", "B"),
    # --- GRUPO C ---
    ("Egito", "Colômbia", "2026-06-12", "18:00", "group", "C"),
    ("Bolívia", "Senegal", "2026-06-12", "21:00", "group", "C"),
    ("Colômbia", "Senegal", "2026-06-16", "18:00", "group", "C"),
    ("Egito", "Bolívia", "2026-06-16", "21:00", "group", "C"),
    ("Senegal", "Egito", "2026-06-20", "19:00", "group", "C"),
    ("Colômbia", "Bolívia", "2026-06-20", "19:00", "group", "C"),
    # --- GRUPO D ---
    ("Japão", "Costa Rica", "2026-06-13", "12:00", "group", "D"),
    ("Alemanha", "Quênia", "2026-06-13", "15:00", "group", "D"),
    ("Costa Rica", "Alemanha", "2026-06-17", "12:00", "group", "D"),
    ("Quênia", "Japão", "2026-06-17", "15:00", "group", "D"),
    ("Alemanha", "Japão", "2026-06-21", "16:00", "group", "D"),
    ("Costa Rica", "Quênia", "2026-06-21", "16:00", "group", "D"),
    # --- GRUPO E ---
    ("Espanha", "Turquia", "2026-06-13", "18:00", "group", "E"),
    ("Equador", "Bahrain", "2026-06-13", "21:00", "group", "E"),
    ("Turquia", "Equador", "2026-06-17", "18:00", "group", "E"),
    ("Bahrain", "Espanha", "2026-06-17", "21:00", "group", "E"),
    ("Espanha", "Equador", "2026-06-21", "19:00", "group", "E"),
    ("Turquia", "Bahrain", "2026-06-21", "19:00", "group", "E"),
    # --- GRUPO F ---
    ("Brasil", "Itália", "2026-06-14", "12:00", "group", "F"),
    ("Nigéria", "Paraguai", "2026-06-14", "15:00", "group", "F"),
    ("Itália", "Nigéria", "2026-06-18", "12:00", "group", "F"),
    ("Paraguai", "Brasil", "2026-06-18", "15:00", "group", "F"),
    ("Brasil", "Nigéria", "2026-06-22", "16:00", "group", "F"),
    ("Itália", "Paraguai", "2026-06-22", "16:00", "group", "F"),
    # --- GRUPO G ---
    ("México", "Honduras", "2026-06-14", "18:00", "group", "G"),
    ("Uruguai", "País de Gales", "2026-06-14", "21:00", "group", "G"),
    ("Honduras", "Uruguai", "2026-06-18", "18:00", "group", "G"),
    ("País de Gales", "México", "2026-06-18", "21:00", "group", "G"),
    ("México", "Uruguai", "2026-06-22", "19:00", "group", "G"),
    ("Honduras", "País de Gales", "2026-06-22", "19:00", "group", "G"),
    # --- GRUPO H ---
    ("EUA", "Canadá", "2026-06-11", "15:00", "group", "H"),
    ("Sérvia", "Irã", "2026-06-11", "21:00", "group", "H"),
    ("Canadá", "Sérvia", "2026-06-15", "12:00", "group", "H"),
    ("Irã", "EUA", "2026-06-15", "21:00", "group", "H"),
    ("EUA", "Sérvia", "2026-06-19", "19:00", "group", "H"),
    ("Canadá", "Irã", "2026-06-19", "19:00", "group", "H"),
    # --- GRUPO I ---
    ("Holanda", "Cameroun", "2026-06-12", "09:00", "group", "I"),
    ("Chile", "Catar", "2026-06-12", "12:00", "group", "I"),
    ("Cameroun", "Chile", "2026-06-16", "09:00", "group", "I"),
    ("Catar", "Holanda", "2026-06-16", "12:00", "group", "I"),
    ("Holanda", "Chile", "2026-06-20", "13:00", "group", "I"),
    ("Cameroun", "Catar", "2026-06-20", "13:00", "group", "I"),
    # --- GRUPO J ---
    ("Inglaterra", "Arábia Saudita", "2026-06-13", "09:00", "group", "J"),
    ("Bélgica", "Trinidad e Tobago", "2026-06-13", "12:00", "group", "J"),
    ("Arábia Saudita", "Bélgica", "2026-06-17", "09:00", "group", "J"),
    ("Trinidad e Tobago", "Inglaterra", "2026-06-17", "12:00", "group", "J"),
    ("Inglaterra", "Bélgica", "2026-06-21", "13:00", "group", "J"),
    ("Arábia Saudita", "Trinidad e Tobago", "2026-06-21", "13:00", "group", "J"),
    # --- GRUPO K ---
    ("Coreia do Sul", "Panamá", "2026-06-14", "09:00", "group", "K"),
    ("Croácia", "Jamaica", "2026-06-14", "12:00", "group", "K"),
    ("Panamá", "Croácia", "2026-06-18", "09:00", "group", "K"),
    ("Jamaica", "Coreia do Sul", "2026-06-18", "12:00", "group", "K"),
    ("Coreia do Sul", "Croácia", "2026-06-22", "13:00", "group", "K"),
    ("Panamá", "Jamaica", "2026-06-22", "13:00", "group", "K"),
    # --- GRUPO L ---
    ("Suíça", "Escócia", "2026-06-15", "09:00", "group", "L"),
    ("Costa do Marfim", "Rep. Democrática do Congo", "2026-06-15", "12:00", "group", "L"),
    ("Escócia", "Costa do Marfim", "2026-06-19", "09:00", "group", "L"),
    ("Rep. Democrática do Congo", "Suíça", "2026-06-19", "12:00", "group", "L"),
    ("Suíça", "Costa do Marfim", "2026-06-23", "13:00", "group", "L"),
    ("Escócia", "Rep. Democrática do Congo", "2026-06-23", "13:00", "group", "L"),
]


def seed():
    init_db()
    conn = get_db()

    existing = conn.execute("SELECT COUNT(*) FROM teams").fetchone()[0]
    if existing > 0:
        print("Banco já possui dados. Pulando seed.")
        conn.close()
        return

    for group_name, teams in GROUPS.items():
        for team_name, flag in teams:
            conn.execute(
                "INSERT INTO teams (name, group_name, flag_emoji) VALUES (?, ?, ?)",
                (team_name, group_name, flag),
            )
    conn.commit()

    for home, away, date, time, stage, group in MATCHES:
        home_id = conn.execute("SELECT id FROM teams WHERE name = ?", (home,)).fetchone()["id"]
        away_id = conn.execute("SELECT id FROM teams WHERE name = ?", (away,)).fetchone()["id"]
        conn.execute(
            "INSERT INTO matches (home_team_id, away_team_id, match_date, match_time, stage, group_name) VALUES (?, ?, ?, ?, ?, ?)",
            (home_id, away_id, date, time, stage, group),
        )
    conn.commit()
    conn.close()
    print(f"Seed completo: {len(GROUPS) * 4} seleções e {len(MATCHES)} jogos inseridos.")


if __name__ == "__main__":
    seed()
