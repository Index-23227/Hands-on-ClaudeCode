"""
DART(전자공시) API → dart_financials 테이블 UPSERT
주요 상장기업의 재무제표(매출액, 영업이익, 당기순이익)를 자동 수집.

현실 함정:
  1. corp_code(8자리)는 종목코드(6자리)와 다름 — DART 전용 코드
  2. 금액에 천단위 콤마가 들어있음 → int 변환 전 제거 필요
  3. 연결재무제표(CFS) vs 별도재무제표(OFS) 구분 필요 — 우리는 CFS만 사용
  4. 최신 보고서가 아직 공시되지 않았을 수 있음 → 직전 연도 폴백
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

API_URL = "https://opendart.fss.or.kr/api/fnlttSinglAcnt.json"

# 조회 대상 기업 (corp_code, 기업명)
TARGET_CORPS = [
    ("00126380", "삼성전자"),
    ("00164779", "SK하이닉스"),
    ("00164742", "현대자동차"),
    ("00258801", "네이버"),
    ("00401731", "LG전자"),
]

# 추출할 계정과목 (연결재무제표 손익계산서 기준)
TARGET_ACCOUNTS = ["매출액", "영업이익", "당기순이익(손실)"]

# 보고서 코드: 사업보고서(연간)
REPRT_CODE = "11011"


def load_env():
    """week06-hands-on/.env 수동 파싱."""
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


def ensure_table(conn):
    """dart_financials 테이블이 없으면 생성."""
    conn.execute("""
        CREATE TABLE IF NOT EXISTS dart_financials (
            corp_code   TEXT NOT NULL,
            corp_name   TEXT NOT NULL,
            bsns_year   TEXT NOT NULL,
            account_nm  TEXT NOT NULL,
            amount      INTEGER,
            fetched_at  TEXT,
            PRIMARY KEY (corp_code, bsns_year, account_nm)
        )
    """)


def parse_amount(s):
    """'300,870,903,000,000' → int. 빈 값이면 None."""
    if not s or s.strip() == "":
        return None
    try:
        return int(s.replace(",", ""))
    except ValueError:
        return None


def fetch_financials(api_key, corp_code, bsns_year):
    """DART API에서 단일회사 주요계정 조회."""
    params = {
        "crtfc_key": api_key,
        "corp_code": corp_code,
        "bsns_year": bsns_year,
        "reprt_code": REPRT_CODE,
    }
    url = f"{API_URL}?{urlencode(params)}"
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    try:
        req = Request(url, headers={"User-Agent": "week06-pipeline/1.0"})
        with urlopen(req, context=ctx, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except (URLError, TimeoutError, ssl.SSLError) as e:
        print(f"    [경고] API 호출 실패: {e}")
        return None

    if data.get("status") != "000":
        return None
    return data.get("list", [])


def extract_accounts(raw_list):
    """API 응답에서 연결재무제표(CFS) + 손익계산서(IS)의 주요 계정만 추출."""
    result = {}
    for item in raw_list:
        # 연결재무제표 + 손익계산서만
        if item.get("fs_div") != "CFS" or item.get("sj_div") != "IS":
            continue
        name = item.get("account_nm", "")
        if name in TARGET_ACCOUNTS:
            result[name] = parse_amount(item.get("thstrm_amount"))
    return result


def main(bsns_year=None):
    """메인 로직. bsns_year 기본값은 작년."""
    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(
            f"DB not found: {DB_PATH}\n"
            "week05-hands-on/data/create_db.py 를 먼저 실행하세요."
        )

    env = load_env()
    api_key = env.get("DART_API_KEY") or env.get("KOREAEXIM_AUTHKEY") or os.environ.get("DART_API_KEY")
    if not api_key:
        raise RuntimeError(
            "DART_API_KEY가 설정되지 않았습니다.\n"
            f".env 파일에 DART_API_KEY=... 를 추가하세요 ({ENV_PATH})"
        )

    if bsns_year is None:
        bsns_year = str(dt.date.today().year - 1)  # 최신 사업보고서는 보통 전년도

    print(f"  [DART 조회] 사업연도={bsns_year}, 대상={len(TARGET_CORPS)}개 기업")

    conn = sqlite3.connect(DB_PATH)
    ensure_table(conn)

    now_iso = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    success = 0
    failed_corps = []
    results = {}

    for corp_code, corp_name in TARGET_CORPS:
        raw = fetch_financials(api_key, corp_code, bsns_year)

        # 함정 4: 최신 보고서 미공시 → 직전 연도 폴백
        if raw is None:
            prev_year = str(int(bsns_year) - 1)
            print(f"    {corp_name}: {bsns_year}년 데이터 없음, {prev_year}년으로 폴백")
            raw = fetch_financials(api_key, corp_code, prev_year)
            if raw is None:
                print(f"    {corp_name}: 폴백도 실패, 건너뜀")
                failed_corps.append(corp_name)
                continue
            bsns_year_actual = prev_year
        else:
            bsns_year_actual = bsns_year

        accounts = extract_accounts(raw)
        if not accounts:
            print(f"    {corp_name}: 연결재무제표 데이터 없음, 건너뜀")
            failed_corps.append(corp_name)
            continue

        for account_nm, amount in accounts.items():
            conn.execute(
                "INSERT OR REPLACE INTO dart_financials "
                "(corp_code, corp_name, bsns_year, account_nm, amount, fetched_at) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (corp_code, corp_name, bsns_year_actual, account_nm, amount, now_iso),
            )

        success += 1
        results[corp_name] = accounts

        # 터미널 출력
        revenue = accounts.get("매출액")
        op_income = accounts.get("영업이익")
        net_income = accounts.get("당기순이익(손실)")
        print(f"    {corp_name:10s} | 매출 {revenue or 0:>20,} | 영업이익 {op_income or 0:>18,} | 순이익 {net_income or 0:>18,}")

    conn.commit()
    total = conn.execute("SELECT COUNT(*) FROM dart_financials").fetchone()[0]
    conn.close()

    print(f"\n  성공: {success}/{len(TARGET_CORPS)}개 기업")
    if failed_corps:
        print(f"  실패: {', '.join(failed_corps)}")
    print(f"  dart_financials 총 행 수: {total}")

    return {
        "year": bsns_year,
        "success": success,
        "failed": failed_corps,
        "results": results,
        "total_rows": total,
    }


if __name__ == "__main__":
    main()
