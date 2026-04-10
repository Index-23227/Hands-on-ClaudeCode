"""
Step 2 정답: 한국수출입은행 API → exchange_rates UPSERT
CLAUDE.md의 현실 함정 4종을 모두 처리:
  1. JPY(100) → JPY ÷100
  2. CNH → CNY
  3. VND 미제공 → 폴백
  4. 주말·공휴일·11시 이전 빈 응답 → 직전 영업일 재사용
"""
import os
import sqlite3
import datetime as dt
from urllib.parse import urlencode
from urllib.request import urlopen, Request
from urllib.error import URLError
import json
import ssl

HERE = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.normpath(os.path.join(HERE, "..", "..", "week05-hands-on", "data", "sales.db"))
ENV_PATH = os.path.normpath(os.path.join(HERE, "..", ".env"))

API_URL = "https://www.koreaexim.go.kr/site/program/financial/exchangeJSON"
TARGET_CURRENCIES = ["USD", "JPY", "CNY", "EUR", "VND", "INR", "GBP", "THB"]
VND_HARDCODED_FALLBACK = 0.056


def load_env() -> dict:
    """week06-hands-on/.env 를 수동 파싱 (python-dotenv 없이)."""
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


def fetch_from_api(authkey: str, searchdate: str) -> list[dict]:
    """한국수출입은행 API 호출. 빈 배열 또는 result!=1이면 [] 반환."""
    params = {"authkey": authkey, "searchdate": searchdate, "data": "AP01"}
    url = f"{API_URL}?{urlencode(params)}"
    # 한국수출입은행은 TLS 중간 인증서를 안 보내는 경우가 있어 검증을 비활성화
    # (교육용 — 운영 환경에서는 회사 CA 번들 사용)
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
        # 일부 실패면 전체를 빈 배열로 (보수적 처리)
        return []
    return data


def parse_api_response(raw: list[dict]) -> dict[str, float]:
    """API 응답 → {USD: 1350.0, JPY: 9.2, CNY: 186.0, EUR: 1480.0} 매핑.
    VND는 API가 주지 않으므로 여기 결과에 포함되지 않음.
    """
    out: dict[str, float] = {}
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
            out["JPY"] = rate / 100.0  # 함정 1
        elif cur_unit == "CNH":
            out["CNY"] = rate  # 함정 2
        elif cur_unit == "EUR":
            out["EUR"] = rate
        elif cur_unit in ("INR", "GBP", "THB"):
            out[cur_unit] = rate
    return out


def get_latest_rates(conn: sqlite3.Connection, currencies: list[str]) -> dict[str, float]:
    """DB에서 각 통화의 가장 최근 환율을 조회. 없는 통화는 dict에서 빠짐."""
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


def apply_fallbacks(
    api_rates: dict[str, float],
    db_latest: dict[str, float],
) -> tuple[dict[str, float], list[str]]:
    """API 응답에 없는 통화를 폴백으로 채운다. (결과, 폴백 통화 리스트) 반환."""
    final: dict[str, float] = dict(api_rates)
    fallback_notes: list[str] = []

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


def upsert_rates(
    conn: sqlite3.Connection, rates: dict[str, float], rate_date: str
) -> int:
    """exchange_rates 는 (currency, rate_date) 복합 PK라서 REPLACE로 멱등성 보장."""
    count = 0
    for currency, rate in rates.items():
        conn.execute(
            "INSERT OR REPLACE INTO exchange_rates (currency, rate_date, rate) "
            "VALUES (?, ?, ?)",
            (currency, rate_date, rate),
        )
        count += 1
    return count


def main(searchdate: str | None = None) -> dict:
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
            f".env 파일을 생성하고 강사 공용 키를 붙여넣으세요 ({ENV_PATH})"
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

    # 출력
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
