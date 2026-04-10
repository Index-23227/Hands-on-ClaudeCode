"""
데모 3: 자연어 데이터 분석 — DB에 한국어로 질문하기
"SQL 몰라도 데이터 분석이 됩니다"

week05에서 만든 sales.db를 그대로 사용합니다.
"""
import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.normpath(os.path.join(HERE, "..", "..", "week05-hands-on", "data", "sales.db"))


def run_query(conn, title, sql):
    print(f"\n  Q: {title}")
    print(f"  SQL: {sql}")
    print(f"  {'─'*50}")
    rows = conn.execute(sql).fetchall()
    cols = [desc[0] for desc in conn.execute(sql).description] if rows else []
    if cols:
        header = "  " + " | ".join(f"{c:>12s}" for c in cols)
        print(header)
        print("  " + "─" * len(header))
    for row in rows:
        vals = []
        for v in row:
            if isinstance(v, float):
                vals.append(f"{v:>12,.0f}")
            elif v is None:
                vals.append(f"{'—':>12s}")
            else:
                vals.append(f"{str(v):>12s}")
        print("  " + " | ".join(vals))


if __name__ == "__main__":
    print("=== 데모 3: 자연어 → SQL 데이터 분석 ===")
    print()
    print("  아래는 Claude에게 자연어로 물어보면 만들어주는 SQL입니다.")
    print("  여러분은 SQL을 쓸 필요 없이, 질문만 하면 됩니다.")

    if not os.path.exists(DB_PATH):
        print(f"\n  [ERROR] DB not found: {DB_PATH}")
        print("  week05-hands-on/data/create_db.py를 먼저 실행하세요.")
        exit(1)

    conn = sqlite3.connect(DB_PATH)

    # 질문 1
    run_query(conn, "매출이 가장 높은 법인은?",
              """SELECT c.corp_name AS 법인, SUM(m.amount) AS 총매출
                 FROM monthly_sales m
                 JOIN corporations c ON c.corp_code = m.corp_code
                 GROUP BY m.corp_code
                 ORDER BY 총매출 DESC LIMIT 3""")

    # 질문 2
    run_query(conn, "전월 대비 매출이 가장 많이 늘어난 법인+월은?",
              """SELECT c.corp_name AS 법인, curr.month AS 월,
                        prev.amount AS 전월, curr.amount AS 이번달,
                        ROUND(curr.amount - prev.amount) AS 증감
                 FROM monthly_sales curr
                 JOIN monthly_sales prev
                   ON curr.corp_code = prev.corp_code
                  AND curr.month = printf('%04d-%02d',
                        CAST(substr(prev.month,1,4) AS INT),
                        CAST(substr(prev.month,6,2) AS INT) + 1)
                 JOIN corporations c ON c.corp_code = curr.corp_code
                 ORDER BY 증감 DESC LIMIT 5""")

    # 질문 3
    run_query(conn, "법인별 원화 환산 매출 합계 (최신 환율 기준)?",
              """SELECT c.corp_name AS 법인, c.currency AS 통화,
                        SUM(m.amount) AS 외화합계,
                        CAST(ROUND(SUM(m.amount) * r.rate) AS INT) AS 원화환산
                 FROM corporations c
                 JOIN monthly_sales m ON m.corp_code = c.corp_code
                 JOIN exchange_rates r ON r.currency = c.currency
                  AND r.rate_date = (SELECT MAX(rate_date) FROM exchange_rates WHERE currency = c.currency)
                 GROUP BY c.corp_code
                 ORDER BY 원화환산 DESC""")

    # 질문 4
    run_query(conn, "6월 매출이 1월보다 줄어든 법인은?",
              """SELECT c.corp_name AS 법인,
                        jan.amount AS '1월', jun.amount AS '6월',
                        ROUND((jun.amount - jan.amount) / jan.amount * 100, 1) AS '증감률(%)'
                 FROM monthly_sales jan
                 JOIN monthly_sales jun ON jan.corp_code = jun.corp_code
                 JOIN corporations c ON c.corp_code = jan.corp_code
                 WHERE jan.month = '2026-01' AND jun.month = '2026-06'
                   AND jun.amount < jan.amount""")

    conn.close()
    print("\n  → 실제 업무에서는 Claude에게 '이 DB에서 ○○ 알려줘'라고 시키면 SQL을 만들어줍니다.")
    print("  → 여러분은 결과만 보면 됩니다.")
