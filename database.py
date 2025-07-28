# database.py
import sqlite3
from typing import List, Dict, Any

DB_NAME = "hiphop_community.db"

def setup_database():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY, username TEXT, language TEXT DEFAULT 'lt',
            role TEXT, graffiti_points INTEGER DEFAULT 0
        )
    """)
    cursor.execute("CREATE TABLE IF NOT EXISTS invites (user_id INTEGER PRIMARY KEY, invited_by INTEGER)")
    # PAKEITIMAS: media_info išskaidytas į du atskirus laukus
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, date TEXT, place TEXT,
            photo_id TEXT,
            link TEXT
        )
    """)
    cursor.execute("CREATE TABLE IF NOT EXISTS pollglyga (id INTEGER PRIMARY KEY AUTOINCREMENT, options TEXT)")
    conn.commit()
    conn.close()

def add_event(name: str, date: str, place: str, photo_id: str = None, link: str = None):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # PAKEITIMAS: Įrašo į naujus laukus
    cursor.execute("INSERT INTO events (name, date, place, photo_id, link) VALUES (?, ?, ?, ?, ?)", (name, date, place, photo_id, link))
    conn.commit()
    conn.close()

def get_events() -> List[Dict[str, str]]:
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # PAKEITIMAS: Nuskaito iš naujų laukų
    cursor.execute("SELECT name, date, place, photo_id, link FROM events ORDER BY date ASC")
    events = [{"name": row[0], "date": row[1], "place": row[2], "photo_id": row[3], "link": row[4]} for row in cursor.fetchall()]
    conn.close()
    return events

# --- Likęs database.py kodas lieka toks pats ---
def add_or_update_user(user_id: int, username: str):
    conn = sqlite3.connect(DB_NAME); cursor = conn.cursor()
    cursor.execute("INSERT INTO users (user_id, username) VALUES (?, ?) ON CONFLICT(user_id) DO UPDATE SET username=excluded.username", (user_id, username))
    conn.commit(); conn.close()
def update_user_data(user_id: int, key: str, value: str):
    if key not in ['language', 'role']: return
    conn = sqlite3.connect(DB_NAME); cursor = conn.cursor()
    cursor.execute(f"UPDATE users SET {key} = ? WHERE user_id = ?", (value, user_id))
    conn.commit(); conn.close()
def get_user_language(user_id: int) -> str:
    conn = sqlite3.connect(DB_NAME); cursor = conn.cursor()
    cursor.execute("SELECT language FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone(); conn.close()
    return result[0] if result and result[0] else 'lt'
def get_user_info(user_id: int) -> Dict[str, Any]:
    conn = sqlite3.connect(DB_NAME); cursor = conn.cursor()
    cursor.execute("SELECT user_id, username, role FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone(); conn.close()
    if not row: return {}
    return {"user_id": row[0], "username": row[1], "role": row[2]}
def get_user_role(user_id: int) -> str: return get_user_info(user_id).get('role', '')
def get_all_members() -> List[Dict[str, Any]]:
    conn = sqlite3.connect(DB_NAME); cursor = conn.cursor()
    cursor.execute("SELECT user_id, username, role FROM users WHERE role IS NOT NULL")
    members = [{"user_id": row[0], "username": row[1], "role": row[2]} for row in cursor.fetchall()]; conn.close()
    return members
def save_invite(user_id: int, invited_by: int):
    conn = sqlite3.connect(DB_NAME); cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO invites (user_id, invited_by) VALUES (?, ?)", (user_id, invited_by))
    conn.commit(); conn.close()
def get_invite_leaderboard(limit=10) -> List[Dict[str, Any]]:
    conn = sqlite3.connect(DB_NAME); cursor = conn.cursor()
    cursor.execute("SELECT u.username, COUNT(i.user_id) as invites FROM invites i JOIN users u ON i.invited_by = u.user_id GROUP BY i.invited_by ORDER BY invites DESC LIMIT ?", (limit,))
    result = [{"username": row[0], "count": row[1]} for row in cursor.fetchall()]; conn.close()
    return result
def add_graffiti_score(user_id: int, points: int):
    conn = sqlite3.connect(DB_NAME); cursor = conn.cursor()
    cursor.execute("UPDATE users SET graffiti_points = graffiti_points + ? WHERE user_id = ?", (points, user_id))
    conn.commit(); conn.close()
def get_user_score(user_id: int) -> int:
    conn = sqlite3.connect(DB_NAME); cursor = conn.cursor()
    cursor.execute("SELECT graffiti_points FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone(); conn.close()
    return result[0] if result else 0
def get_top_graffiti(limit=10) -> List[Dict[str, Any]]:
    conn = sqlite3.connect(DB_NAME); cursor = conn.cursor()
    cursor.execute("SELECT username, graffiti_points FROM users WHERE graffiti_points > 0 ORDER BY graffiti_points DESC LIMIT ?", (limit,))
    result = [{"username": row[0], "points": row[1]} for row in cursor.fetchall()]; conn.close()
    return result
def delete_event(name: str) -> int:
    conn = sqlite3.connect(DB_NAME); cursor = conn.cursor()
    cursor.execute("DELETE FROM events WHERE name = ?", (name,))
    changes = cursor.rowcount; conn.commit(); conn.close()
    return changes
def save_pollglyga(options: str):
    conn = sqlite3.connect(DB_NAME); cursor = conn.cursor()
    cursor.execute("DELETE FROM pollglyga"); cursor.execute("INSERT INTO pollglyga (options) VALUES (?)", (options,))
    conn.commit(); conn.close()
def clear_poll() -> None:
    conn = sqlite3.connect(DB_NAME); cursor = conn.cursor()
    cursor.execute("DELETE FROM pollglyga"); conn.commit(); conn.close()
def get_pollglyga() -> str:
    conn = sqlite3.connect(DB_NAME); cursor = conn.cursor()
    cursor.execute("SELECT options FROM pollglyga ORDER BY id DESC LIMIT 1")
    row = cursor.fetchone(); conn.close()
    return row[0] if row else ""