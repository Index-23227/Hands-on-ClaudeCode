import re
import glob as glob_mod
import sqlite3
from datetime import datetime
from pathlib import Path
from flask import Flask, render_template, request, abort, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = "week05-dev-secret-change-me"

DB_PATH = Path(__file__).parent / "data" / "sales.db"
WEEK06_DATA = Path(__file__).parent.parent / "week06-hands-on" / "data"

SORT_ORDER = ["독일", "미국", "베트남", "영국", "인도", "일본", "중국", "태국"]


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def fetch_available_months(conn):
    """monthly_sales에 실제 존재하는 월 목록을 오름차순으로 반환."""
    rows = conn.execute(
        "SELECT DISTINCT month FROM monthly_sales ORDER BY month ASC"
    ).fetchall()
    return [r["month"] for r in rows]


def sort_key(row):
    name = row["corp_name"]
    for i, key in enumerate(SORT_ORDER):
        if name.startswith(key):
            return i
    return len(SORT_ORDER)


@app.route("/")
def index():
    selected_month = request.args.get("month", "").strip()

    conn = get_conn()
    try:
        available_months = fetch_available_months(conn)
        if selected_month and selected_month not in available_months:
            selected_month = ""

        # 매출 row를 그 달의 월말 환율과 매칭 (substr으로 'YYYY-MM' 추출)
        # 환율이 없는 row는 일관성을 위해 total/krw 양쪽에서 모두 제외
        # 가중 평균 환산율 = SUM(amount * rate) / SUM(amount[matched])
        base_sql = """
            SELECT
                c.corp_code, c.corp_name, c.currency,
                COALESCE(SUM(CASE WHEN r.rate IS NOT NULL THEN m.amount ELSE 0 END), 0) AS total,
                CASE WHEN SUM(CASE WHEN r.rate IS NOT NULL THEN m.amount ELSE 0 END) > 0
                     THEN SUM(m.amount * r.rate)
                          / SUM(CASE WHEN r.rate IS NOT NULL THEN m.amount ELSE 0 END)
                     ELSE NULL END AS rate,
                CAST(ROUND(COALESCE(SUM(m.amount * r.rate), 0)) AS INTEGER) AS krw
            FROM corporations c
            LEFT JOIN monthly_sales m
                ON c.corp_code = m.corp_code{month_filter}
            LEFT JOIN exchange_rates r
                ON r.currency = c.currency
               AND substr(r.rate_date, 1, 7) = m.month
            GROUP BY c.corp_code, c.corp_name, c.currency
        """
        if selected_month:
            sql = base_sql.format(month_filter=" AND m.month = ?")
            rows = conn.execute(sql, (selected_month,)).fetchall()
        else:
            sql = base_sql.format(month_filter="")
            rows = conn.execute(sql).fetchall()

        # 환율 매칭에 실패한 row 개수 확인 → 사용자에게 경고
        unmatched = conn.execute(
            """
            SELECT COUNT(*) AS cnt
            FROM monthly_sales m
            LEFT JOIN exchange_rates r
                ON r.currency = (SELECT currency FROM corporations WHERE corp_code = m.corp_code)
               AND substr(r.rate_date, 1, 7) = m.month
            WHERE r.rate IS NULL
            """
        ).fetchone()["cnt"]
    finally:
        conn.close()

    sorted_rows = sorted(rows, key=sort_key)
    total_krw = sum(r["krw"] for r in sorted_rows)

    # week06 파이프라인 실패 flag 확인
    pipeline_failure = None
    failure_flags = sorted(
        glob_mod.glob(str(WEEK06_DATA / "failure_*.flag")), reverse=True
    )
    if failure_flags:
        try:
            with open(failure_flags[0], encoding="utf-8") as ff:
                pipeline_failure = ff.read().strip()
        except OSError:
            pass

    return render_template(
        "index.html",
        rows=sorted_rows,
        total_krw=total_krw,
        months=available_months,
        selected_month=selected_month,
        unmatched=unmatched,
        pipeline_failure=pipeline_failure,
        now=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    )


@app.route("/corp/<corp_code>")
def corp_detail(corp_code):
    conn = get_conn()
    try:
        corp = conn.execute(
            "SELECT * FROM corporations WHERE corp_code = ?", (corp_code,)
        ).fetchone()
        if corp is None:
            abort(404)

        months = conn.execute(
            """
            SELECT
                m.month,
                SUM(m.amount) AS amount,
                COUNT(*) AS entry_count,
                GROUP_CONCAT(NULLIF(m.note, ''), ' / ') AS note,
                r.rate AS rate,
                CAST(ROUND(SUM(m.amount) * r.rate) AS INTEGER) AS krw
            FROM monthly_sales m
            LEFT JOIN exchange_rates r
                ON r.currency = ?
               AND substr(r.rate_date, 1, 7) = m.month
            WHERE m.corp_code = ?
            GROUP BY m.month, r.rate
            ORDER BY m.month ASC
            """,
            (corp["currency"], corp_code),
        ).fetchall()
    finally:
        conn.close()

    total = sum(m["amount"] for m in months)
    total_krw = sum((m["krw"] or 0) for m in months)
    # 가중 평균 환율 (표시용)
    rate = (total_krw / total) if total else 0

    return render_template(
        "detail.html",
        corp=corp,
        months=months,
        total=total,
        rate=rate,
        total_krw=total_krw,
        now=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    )


MONTH_RE = re.compile(r"^\d{4}-(0[1-9]|1[0-2])$")


@app.route("/add", methods=["GET", "POST"])
def add_sale():
    conn = get_conn()
    try:
        corps = conn.execute(
            "SELECT corp_code, corp_name, currency FROM corporations ORDER BY corp_name"
        ).fetchall()

        if request.method == "POST":
            corp_code = (request.form.get("corp_code") or "").strip()
            month     = (request.form.get("month") or "").strip()
            amount_s  = (request.form.get("amount") or "").strip().replace(",", "")
            note      = (request.form.get("note") or "").strip()

            errors = []
            valid_codes = {c["corp_code"] for c in corps}
            if corp_code not in valid_codes:
                errors.append("법인을 선택해 주세요.")
            if not MONTH_RE.match(month):
                errors.append("월 형식이 올바르지 않습니다 (예: 2026-04).")
            try:
                amount = float(amount_s)
                if amount <= 0:
                    errors.append("금액은 0보다 커야 합니다.")
            except ValueError:
                amount = None
                errors.append("금액은 숫자여야 합니다.")

            if errors:
                for e in errors:
                    flash(e, "error")
                return render_template(
                    "add.html",
                    corps=corps,
                    form={"corp_code": corp_code, "month": month, "amount": amount_s, "note": note},
                    now=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                )

            now_iso = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            conn.execute(
                """INSERT INTO monthly_sales (corp_code, month, amount, note, created_at)
                   VALUES (?, ?, ?, ?, ?)""",
                (corp_code, month, amount, note or None, now_iso),
            )
            conn.commit()

            corp_name = next(c["corp_name"] for c in corps if c["corp_code"] == corp_code)

            # 같은 법인+월에 기존 행이 있었는지 확인 → 누적인지 신규인지 메시지 분기
            prior = conn.execute(
                "SELECT COUNT(*) AS cnt, SUM(amount) AS s FROM monthly_sales WHERE corp_code = ? AND month = ?",
                (corp_code, month),
            ).fetchone()
            if prior["cnt"] > 1:
                flash(
                    f"{corp_name}의 {month}에 {amount:,.0f} 추가 (누적 합계 {prior['s']:,.0f}, 이력 {prior['cnt']}건)",
                    "success",
                )
            else:
                flash(f"{corp_name}의 {month} 매출 {amount:,.0f} 등록 완료", "success")
            return redirect(url_for("index"))
    finally:
        conn.close()

    return render_template(
        "add.html",
        corps=corps,
        form={"corp_code": "", "month": "", "amount": "", "note": ""},
        now=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    )


@app.route("/history")
def history():
    conn = get_conn()
    try:
        entries = conn.execute(
            """
            SELECT
                m.id, m.corp_code, m.month, m.amount, m.note, m.created_at,
                c.corp_name, c.currency
            FROM monthly_sales m
            JOIN corporations c ON c.corp_code = m.corp_code
            ORDER BY
                CASE WHEN m.created_at IS NULL THEN 1 ELSE 0 END,
                m.created_at DESC,
                m.id DESC
            """
        ).fetchall()
    finally:
        conn.close()
    return render_template(
        "history.html",
        entries=entries,
        now=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    )


@app.route("/history/delete/<int:entry_id>", methods=["POST"])
def delete_entry(entry_id):
    conn = get_conn()
    try:
        row = conn.execute(
            """SELECT m.amount, m.month, c.corp_name
               FROM monthly_sales m
               JOIN corporations c ON c.corp_code = m.corp_code
               WHERE m.id = ?""",
            (entry_id,),
        ).fetchone()
        if row is None:
            flash("이미 삭제되었거나 존재하지 않는 이력입니다.", "error")
            return redirect(url_for("history"))

        conn.execute("DELETE FROM monthly_sales WHERE id = ?", (entry_id,))
        conn.commit()
        flash(
            f"{row['corp_name']}의 {row['month']} 매출 {row['amount']:,.0f} 삭제됨",
            "success",
        )
    finally:
        conn.close()
    return redirect(url_for("history"))


@app.template_filter("comma")
def comma_filter(value):
    if value is None:
        return "-"
    if isinstance(value, float):
        return f"{value:,.3f}".rstrip("0").rstrip(".")
    return f"{value:,}"


if __name__ == "__main__":
    app.run(debug=True, port=5000)
