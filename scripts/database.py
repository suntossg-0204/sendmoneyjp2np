import json
import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path("database/rates.db")


def get_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(DB_PATH)


def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS companies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        website TEXT,
        active INTEGER DEFAULT 1
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS rate_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_id INTEGER,
        company_name TEXT NOT NULL,
        rate REAL NOT NULL,
        currency_pair TEXT DEFAULT 'JPY-NPR',
        service_fee INTEGER DEFAULT 0,
        atm_fee INTEGER DEFAULT 0,
        deposit_method TEXT DEFAULT 'Online',
        source_url TEXT,
        collected_at TEXT NOT NULL,
        metadata TEXT DEFAULT '{}',
        FOREIGN KEY(company_id) REFERENCES companies(id)
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS daily_summary (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        summary_date TEXT NOT NULL,
        company_id INTEGER,
        company_name TEXT NOT NULL,
        high_rate REAL,
        low_rate REAL,
        average_rate REAL,
        samples INTEGER,
        created_at TEXT NOT NULL,
        UNIQUE(summary_date, company_name)
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS scrape_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_name TEXT NOT NULL,
        status TEXT NOT NULL,
        message TEXT,
        logged_at TEXT NOT NULL
    )
    """)

    conn.commit()
    conn.close()
    print("Database initialized successfully.")


def get_company_id(company_name):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT id FROM companies WHERE name = ?", (company_name,))
    row = cur.fetchone()

    conn.close()
    return row[0] if row else None


def save_snapshot(snapshot):
    company_id = get_company_id(snapshot.company)

    conn = get_connection()
    cur = conn.cursor()

    # -------------------------------
    # Basic rate validation
    # -------------------------------
    rate = float(snapshot.rate)

    # Reject impossible rates
    if rate < 0.50 or rate > 2.00:
        print(f"[SKIPPED] {snapshot.company}: invalid rate {rate}")
        conn.close()
        return False

    # Compare with previous rate
    cur.execute("""
        SELECT rate
        FROM rate_history
        WHERE company_name = ?
        ORDER BY collected_at DESC
        LIMIT 1
    """, (snapshot.company,))

    row = cur.fetchone()

    if row:
        previous_rate = float(row[0])

        percent_change = abs(rate - previous_rate) / previous_rate * 100

        # Reject abnormal jumps (>10%)
        if percent_change > 10:
            print(
                f"[SKIPPED] {snapshot.company}: "
                f"{previous_rate:.6f} → {rate:.6f} "
                f"({percent_change:.2f}% change)"
            )
            conn.close()
            return False

    # -------------------------------
    # Save snapshot
    # -------------------------------
    cur.execute("""
    INSERT INTO rate_history
    (company_id, company_name, rate, currency_pair, service_fee,
     atm_fee, deposit_method, source_url, collected_at, metadata)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        company_id,
        snapshot.company,
        rate,
        snapshot.currency_pair,
        snapshot.service_fee,
        snapshot.atm_fee,
        snapshot.deposit_method,
        snapshot.source_url,
        snapshot.collected_at,
        json.dumps(snapshot.metadata, ensure_ascii=False)
    ))

    conn.commit()
    conn.close()

    print(f"Saved: {snapshot.company} = {rate:.6f}")
    return True


def log_scrape(company_name, status, message=""):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO scrape_log
    (company_name, status, message, logged_at)
    VALUES (?, ?, ?, ?)
    """, (
        company_name,
        status,
        message,
        now = datetime.now(ZoneInfo("Asia/Tokyo")).replace(tzinfo=None).isoformat(timespec="seconds")
    ))

    conn.commit()
    conn.close()


def generate_daily_summary():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    SELECT
        date(collected_at) as summary_date,
        company_id,
        company_name,
        MAX(rate),
        MIN(rate),
        AVG(rate),
        COUNT(*)
    FROM rate_history
    GROUP BY date(collected_at), company_name
    """)

    rows = cur.fetchall()

    for row in rows:
        cur.execute("""
        INSERT OR REPLACE INTO daily_summary
        (summary_date, company_id, company_name, high_rate, low_rate, average_rate, samples, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            row[0],
            row[1],
            row[2],
            row[3],
            row[4],
            row[5],
            row[6],
            now = datetime.now(ZoneInfo("Asia/Tokyo")).replace(tzinfo=None).isoformat(timespec="seconds")
        ))

    conn.commit()
    conn.close()
    print("Daily summary generated.")

def cleanup_old_data(days=31):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    DELETE FROM rate_history
    WHERE collected_at < datetime('now', ?)
    """, (f"-{days} days",))

    deleted = cur.rowcount

    cur.execute("""
    DELETE FROM scrape_log
    WHERE logged_at < datetime('now', ?)
    """, (f"-{days} days",))

    conn.commit()
    conn.close()

    print(f"Cleanup complete. Deleted {deleted} old rate records.")

if __name__ == "__main__":
    init_db()
    generate_daily_summary()