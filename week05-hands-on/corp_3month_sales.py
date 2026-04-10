import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "data" / "sales.db"

SORT_ORDER = ["독일", "미국", "베트남", "영국", "인도", "일본", "중국", "태국"]

def fetch_sales():
    conn = sqlite3.connect(DB_PATH)
    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT
                c.corp_name,
                c.currency,
                COALESCE(SUM(m.amount), 0) AS total,
                r.rate,
                CAST(ROUND(COALESCE(SUM(m.amount), 0) * r.rate) AS INTEGER) AS krw
            FROM corporations c
            LEFT JOIN monthly_sales m
                ON c.corp_code = m.corp_code
               AND m.month BETWEEN '2026-01' AND '2026-03'
            LEFT JOIN (
                SELECT currency, rate
                FROM exchange_rates
                WHERE rate_date = (SELECT MAX(rate_date) FROM exchange_rates)
            ) r ON r.currency = c.currency
            GROUP BY c.corp_code, c.corp_name, c.currency, r.rate
            """
        )
        rows = cur.fetchall()
    finally:
        conn.close()

    def sort_key(row):
        name = row[0]
        for i, key in enumerate(SORT_ORDER):
            if name.startswith(key):
                return i
        return len(SORT_ORDER)

    return sorted(rows, key=sort_key)

def print_table(rows):
    headers = ["법인명", "통화", "3개월 매출 합계", "환율", "원화 환산"]
    data = [
        [name, cur, f"{total:,.0f}", f"{rate:,.1f}", f"{krw:,}"]
        for name, cur, total, rate, krw in rows
    ]

    widths = [max(len(str(r[i])) for r in [headers] + data) for i in range(len(headers))]
    numeric_cols = {2, 3, 4}

    def fmt(row, header=False):
        cells = []
        for i, val in enumerate(row):
            if i in numeric_cols and not header:
                cells.append(str(val).rjust(widths[i]))
            else:
                cells.append(str(val).ljust(widths[i]))
        return " | ".join(cells)

    sep = "-+-".join("-" * w for w in widths)
    print(fmt(headers, header=True))
    print(sep)
    for row in data:
        print(fmt(row))

    total_krw = sum(r[4] for r in rows)
    print(sep)
    print(f"원화 환산 총합: {total_krw:,} 원")

if __name__ == "__main__":
    rows = fetch_sales()
    print_table(rows)
