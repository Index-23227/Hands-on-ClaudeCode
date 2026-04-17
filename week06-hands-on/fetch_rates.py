"""
한국수출입은행 API → exchange_rates UPSERT
현실 함정 4종 처리:
  1. JPY(100) → JPY ÷100
  2. CNH → CNY
  3. VND 미제공 → 폴백
  4. 주말·공휴일·11시 이전 빈 응답 → 직전 영업일 재사용
"""
import os
import sqlite3
import ssl
import json
import datetime as dt
from urllib.parse import urlencode
from urllib.request import urlopen, Request
from urllib.error import URLError

HERE = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.normpath(os.path.join(HERE, "..", "week05-hands-on", "data", "sales.db"))
ENV_PATH = os.path.join(HERE, ".env")

API_URL = "https://www.koreaexim.go.kr/site/program/financial/exchangeJSON"
TARGET_CURRENCIES = ["USD", "JPY", "CNY", "EUR", "VND", "INR", "GBP", "THB"]
VND_HARDCODED_FALLBACK = 0.056


def load_env():
    """week06-hands-on/.env 수동 파싱 (python-dotenv 없이)."""
    env = {}
    if not os.path.exists(ENV_PATH):
        return env
    with open(ENV_PATH, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            k, _, v = line.partition("=")
            env[k.strip()] = v.strip().strip('"').strip("'")
    return env


def fetch_from_api(authkey, searchdate):
    """한국수출입은행 API 호출. 빈 배열 또는 result!=1이면 [] 반환."""
    params = {"authkey": authkey, "searchdate": searchdate, "data": "AP01"}
    url = f"{API_URL}?{urlencode(params)}"
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    try:
        req = Request(url, headers={"User-Agent": "week06-pipeline/1.0"})
        with urlopen(req, context=ctx, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except (URLError, TimeoutError, ssl.SSLError) as e:
        print(f"  [경고] API 호출 실패: {e}")
        return []

    if not isinstance(data, list) or not data:
        return []
    if any(item.get("result") != 1 for item in data if isinstance(item, dict)):
        return []
    return data


def parse_api_response(raw):
    """API 응답 → {USD: 1350.0, JPY: 9.2, ...} 매핑."""
    out = {}
    for item in raw:
        cur_unit = item.get("cur_unit", "")
        bas_r = item.get("deal_bas_r", "")
        if not cur_unit or not bas_r:
            continue
        try:
            rate = float(str(bas_r).replace(",", ""))
        except ValueError:
            continue

        if cur_unit == "USD":
            out["USD"] = rate
        elif cur_unit == "JPY(100)":
            out["JPY"] = rate / 100.0  # 함정 1: 100엔 → 1엔
        elif cur_unit == "CNH":
            out["CNY"] = rate           # 함정 2: CNH → CNY
        elif cur_unit == "EUR":
            out["EUR"] = rate
        elif cur_unit in ("INR", "GBP", "THB"):
            out[cur_unit] = rate
    return out


def get_latest_rates(conn, currencies):
    """DB에서 각 통화의 가장 최근 환율 조회."""
    result = {}
    for cur in currencies:
        row = conn.execute(
            "SELECT rate FROM exchange_rates WHERE currency=? "
            "ORDER BY rate_date DESC LIMIT 1",
            (cur,),
        ).fetchone()
        if row is not None:
            result[cur] = float(row[0])
    return result


def apply_fallbacks(api_rates, db_latest):
    """API 응답에 없는 통화를 폴백으로 채운다."""
    final = dict(api_rates)
    fallback_notes = []

    for cur in TARGET_CURRENCIES:
        if cur in final:
            continue
        if cur in db_latest:
            final[cur] = db_latest[cur]
            fallback_notes.append(f"{cur}=직전 환율 재사용 ({db_latest[cur]})")
        elif cur == "VND":
            final[cur] = VND_HARDCODED_FALLBACK
            fallback_notes.append(f"VND=하드코딩 폴백 ({VND_HARDCODED_FALLBACK})")
        else:
            fallback_notes.append(f"{cur}=값 없음, 건너뜀")

    return final, fallback_notes


def upsert_rates(conn, rates, rate_date):
    """exchange_rates 에 UPSERT. 복합 PK (currency, rate_date)로 멱등."""
    count = 0
    for currency, rate in rates.items():
        conn.execute(
            "INSERT OR REPLACE INTO exchange_rates (currency, rate_date, rate) "
            "VALUES (?, ?, ?)",
            (currency, rate_date, rate),
        )
        count += 1
    return count


def main(searchdate=None):
    """메인 로직. searchdate는 YYYYMMDD. 기본값은 오늘."""
    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(
            f"DB not found: {DB_PATH}\n"
            "week05-hands-on/data/create_db.py 를 먼저 실행하세요."
        )

    env = load_env()
    authkey = env.get("KOREAEXIM_AUTHKEY") or os.environ.get("KOREAEXIM_AUTHKEY")
    if not authkey or authkey == "여기에_인증키를_붙여넣으세요":
        raise RuntimeError(
            "KOREAEXIM_AUTHKEY가 설정되지 않았습니다.\n"
            f".env 파일에 키를 설정하세요 ({ENV_PATH})"
        )

    if searchdate is None:
        searchdate = dt.date.today().strftime("%Y%m%d")
    rate_date_iso = f"{searchdate[:4]}-{searchdate[4:6]}-{searchdate[6:]}"

    print(f"  [환율 조회] searchdate={searchdate}")
    raw = fetch_from_api(authkey, searchdate)

    api_rates = parse_api_response(raw) if raw else {}
    if not raw:
        print("  [환율 조회] 응답이 비어있음 (주말/공휴일/11시 이전). 폴백 진입.")

    conn = sqlite3.connect(DB_PATH)
    db_latest = get_latest_rates(conn, TARGET_CURRENCIES)
    final_rates, fallback_notes = apply_fallbacks(api_rates, db_latest)

    inserted = upsert_rates(conn, final_rates, rate_date_iso)
    conn.commit()
    conn.close()

    for cur in TARGET_CURRENCIES:
        if cur in final_rates:
            marker = " (폴백)" if cur not in api_rates else ""
            print(f"    {cur}: {final_rates[cur]:.4f}{marker}")
    for note in fallback_notes:
        print(f"  [폴백] {note}")
    print(f"  exchange_rates UPSERT: {inserted}건")

    return {
        "date": rate_date_iso,
        "rates": final_rates,
        "fallback": fallback_notes,
        "api_empty": not raw,
    }


if __name__ == "__main__":
    main()
