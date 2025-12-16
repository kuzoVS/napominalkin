from datetime import datetime
import pytz
from bot.config import TIMEZONE
from bot.database.db import get_connection

moscow_tz = pytz.timezone(TIMEZONE)


def create_user(user_id, username=None, first_name=None, timezone="Europe/Moscow"):
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT OR REPLACE INTO users (user_id, username, first_name, timezone)
        VALUES (?, ?, ?, ?)
    """, (user_id, username, first_name, timezone))
    
    conn.commit()
    conn.close()


def get_user(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()
    
    conn.close()
    return user


def get_user_by_username(username: str):
    conn = get_connection()
    cursor = conn.cursor()
    
    clean = username.lstrip("@").lower()
    cursor.execute(
        "SELECT * FROM users WHERE LOWER(username) = ?",
        (clean,)
    )
    user = cursor.fetchone()
    conn.close()
    return user


def create_reminder(user_id, text, remind_at, sender_id=None, is_daily=False):
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO reminders (user_id, sender_id, text, remind_at, is_daily, is_active)
        VALUES (?, ?, ?, ?, ?, 1)
    """, (user_id, sender_id, text, remind_at, is_daily))
    
    reminder_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return reminder_id


def get_user_reminders(user_id, active_only=True):
    conn = get_connection()
    cursor = conn.cursor()
    
    if active_only:
        cursor.execute("""
            SELECT * FROM reminders 
            WHERE user_id = ? AND is_active = 1
            ORDER BY remind_at ASC
        """, (user_id,))
    else:
        cursor.execute("""
            SELECT * FROM reminders 
            WHERE user_id = ?
            ORDER BY remind_at ASC
        """, (user_id,))
    
    reminders = cursor.fetchall()
    conn.close()
    
    return reminders


def get_due_reminders():
    conn = get_connection()
    cursor = conn.cursor()
    
    now_moscow = datetime.now(moscow_tz)
    now = now_moscow.strftime("%Y-%m-%d %H:%M:%S")
    
    cursor.execute("""
        SELECT * FROM reminders 
        WHERE is_active = 1 
        AND remind_at <= ?
        ORDER BY remind_at ASC
    """, (now,))
    
    reminders = cursor.fetchall()
    conn.close()
    
    return reminders


def delete_reminder(reminder_id, user_id):
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        DELETE FROM reminders 
        WHERE id = ? AND user_id = ?
    """, (reminder_id, user_id))
    
    deleted = cursor.rowcount > 0
    conn.commit()
    conn.close()
    
    return deleted


def deactivate_reminder(reminder_id, user_id):
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE reminders 
        SET is_active = 0 
        WHERE id = ? AND user_id = ?
    """, (reminder_id, user_id))
    
    updated = cursor.rowcount > 0
    conn.commit()
    conn.close()
    
    return updated


def update_daily_reminder(reminder_id):
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT remind_at FROM reminders WHERE id = ?", (reminder_id,))
    result = cursor.fetchone()
    
    if result:
        cursor.execute("""
            UPDATE reminders 
            SET remind_at = datetime(remind_at, '+1 day')
            WHERE id = ?
        """, (reminder_id,))
        
        conn.commit()
    
    conn.close()
