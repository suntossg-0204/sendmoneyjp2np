from database import init_db, get_connection

COMPANIES = [
    ("Wise", "https://wise.com/jp/send-money/nepal"),
    ("Panda Remit", "https://www.pandaremit.com/jp/"),
    ("SBI Remit", "https://www.remit.co.jp/kaigaisoukin/exchangeratecommission/"),
    ("World Remit", "https://www.worldremit.com/en/japan/send-money-to-nepal"),
    ("JRF", "https://jrf.co.jp/"),
    ("City Express", "https://www.cityexpressremit.com/jp"),
    ("Pay Forex", "https://payforex.co.jp/"),
    ("Yehey Remit", "https://www.yeheyremit.com/"),
    ("QS Remit", "https://qsremit.net/jp/index")
]

def seed_companies():
    init_db()
    conn = get_connection()
    cur = conn.cursor()

    for name, website in COMPANIES:
        cur.execute("""
        INSERT OR IGNORE INTO companies (name, website, active)
        VALUES (?, ?, 1)
        """, (name, website))

    conn.commit()

    cur.execute("SELECT id, name, website FROM companies ORDER BY id")
    rows = cur.fetchall()

    conn.close()

    print("Companies saved:")
    for row in rows:
        print(row)

if __name__ == "__main__":
    seed_companies()
