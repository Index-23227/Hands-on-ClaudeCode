"""
F1 시연용 샘플 메일 발송 (강사 사전 준비)

강사 Gmail → 강사 Gmail (자기 자신 앞으로) 으로
"법인 담당자가 보낸 월말 매출 보고" 메일을 발송한다.

시연 중 Claude(MCP Gmail 또는 IMAP)가 강사 받은편지함을 열어
이 메일들을 자동으로 읽고 첨부 취합하는 흐름을 보여준다.

사전 준비:
  1. Gmail 2FA 활성화 + 앱 비밀번호 발급 (→ Gmail_자동화_설정.md)
  2. prep/.env.example → prep/.env 복사 후 값 입력

실행:
  py week07-hands-on/prep/send_sample_inbox_emails.py             # 기본 2통 (테스트용)
  py week07-hands-on/prep/send_sample_inbox_emails.py --count 8   # 8통 전체 (시연용)
  py week07-hands-on/prep/send_sample_inbox_emails.py --count 5   # 앞에서 5통

재실행:
  반복 실행하면 같은 수만큼 추가로 쌓인다(중복 체크 안 함).
  불필요한 경우 Gmail에서 직접 삭제하고 재발송.
"""

import smtplib
import ssl
import sys
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from io import BytesIO
from pathlib import Path

from openpyxl import Workbook

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")  # cp949 → utf-8 (한글·대시 안전 출력)


HERE = Path(__file__).parent


def load_env() -> dict[str, str]:
    """prep/.env 수동 파싱 (python-dotenv 불필요)"""
    env_path = HERE / ".env"
    if not env_path.exists():
        print(f"[에러] .env 파일이 없습니다: {env_path}")
        print(f"       .env.example을 .env로 복사한 뒤 Gmail 인증정보를 채워주세요.")
        sys.exit(1)

    env: dict[str, str] = {}
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        env[k.strip()] = v.strip().strip('"').strip("'")
    return env


# 법인별 가상 담당자 + 2026-03 매출 (week05 DB 실제값 재사용)
LEGIONS = [
    ("CN01", "중국법인",   "김준호", "CNY", 875_000,         ""),
    ("DE01", "독일법인",   "박서연", "EUR", 101_000,         ""),
    ("GB01", "영국법인",   "이민재", "GBP", 75_000,          ""),
    ("IN01", "인도법인",   "정하늘", "INR", 8_800_000,       ""),
    ("JP01", "일본법인",   "윤지우", "JPY", 14_900_000,      ""),
    ("TH01", "태국법인",   "최영훈", "THB", 4_100_000,       ""),
    ("US01", "미국법인",   "송예림", "USD", 118_000,         "신규 거래처 2곳 추가"),
    ("VN01", "베트남법인", "강태우", "VND", 3_120_000_000,   ""),
]


def make_mock_excel(currency: str, amount: int, note: str) -> bytes:
    """첨부용 매출 엑셀 생성 (메모리상, openpyxl)"""
    wb = Workbook()
    ws = wb.active
    ws.title = "매출"
    ws.append(["월", "계정과목", "통화", "금액", "비고"])
    ws.append(["2026-03", "매출액", currency, amount, note])
    ws.column_dimensions["A"].width = 12
    ws.column_dimensions["B"].width = 10
    ws.column_dimensions["C"].width = 8
    ws.column_dimensions["D"].width = 18
    ws.column_dimensions["E"].width = 24

    bio = BytesIO()
    wb.save(bio)
    return bio.getvalue()


def build_email(
    sender: str,
    recipient: str,
    code: str,
    country: str,
    contact: str,
    currency: str,
    amount: int,
    note: str,
) -> MIMEMultipart:
    msg = MIMEMultipart()
    msg["From"] = sender
    msg["To"] = recipient
    msg["Subject"] = f"[{country}] 2026년 3월 매출 보고"

    body_lines = [
        "안녕하십니까, 재경팀장님.",
        "",
        f"{country} 담당 {contact}입니다.",
        "",
        "2026년 3월 매출 보고드립니다. 첨부 파일 확인 부탁드립니다.",
        "",
        f"- 매출액: {amount:,} {currency}",
        f"- 특이사항: {note if note else '없음'}",
        "",
        "감사합니다.",
        "",
        f"{contact} 올림",
        country,
    ]
    msg.attach(MIMEText("\n".join(body_lines), "plain", "utf-8"))

    excel_bytes = make_mock_excel(currency, amount, note)
    part = MIMEBase(
        "application",
        "vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    part.set_payload(excel_bytes)
    encoders.encode_base64(part)
    filename = f"법인_{code}_2026-03.xlsx"
    # RFC 2231 방식으로 UTF-8 파일명 지정 (RFC 2047은 Content-Disposition에 부적절)
    part.add_header(
        "Content-Disposition",
        "attachment",
        filename=("utf-8", "", filename),
    )
    msg.attach(part)

    return msg


def parse_count() -> int:
    """CLI --count N 파싱. 기본 2."""
    count = 2
    for i, arg in enumerate(sys.argv):
        if arg == "--count" and i + 1 < len(sys.argv):
            try:
                count = int(sys.argv[i + 1])
            except ValueError:
                print(f"[에러] --count 뒤에 정수가 와야 합니다: {sys.argv[i + 1]}")
                sys.exit(1)
    count = max(1, min(count, len(LEGIONS)))
    return count


def main() -> None:
    env = load_env()
    user = env.get("GMAIL_USER", "")
    password = env.get("GMAIL_APP_PASSWORD", "")

    if not user or user == "your.email@gmail.com":
        print("[에러] .env의 GMAIL_USER를 실제 Gmail 주소로 바꿔주세요.")
        sys.exit(1)
    if not password or "xxxx" in password:
        print("[에러] .env의 GMAIL_APP_PASSWORD를 앱 비밀번호로 바꿔주세요.")
        print("       발급: https://myaccount.google.com/apppasswords")
        sys.exit(1)

    password = password.replace(" ", "")  # 공백 제거 (Gmail 앱 비밀번호 포맷 관용)
    count = parse_count()
    subset = LEGIONS[:count]

    print(f"[시작] {user} → {user}로 샘플 법인 매출 메일 {count}통 발송")
    if count < len(LEGIONS):
        print(f"       (전체 {len(LEGIONS)}통 중 앞에서 {count}개만 — 시연 시 '--count {len(LEGIONS)}' 로 전체)")
    print()

    context = ssl.create_default_context()
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as smtp:
            smtp.login(user, password)
            for code, country, contact, currency, amount, note in subset:
                msg = build_email(user, user, code, country, contact, currency, amount, note)
                smtp.sendmail(user, [user], msg.as_string())
                print(f"  [OK] [{country}] {contact} — {amount:,} {currency}")
    except smtplib.SMTPAuthenticationError as e:
        print(f"[에러] Gmail 인증 실패: {e}")
        print("       앱 비밀번호가 맞는지, 2FA가 활성화됐는지 확인.")
        sys.exit(1)
    except Exception as e:
        print(f"[에러] 발송 중 예외: {e}")
        sys.exit(1)

    print()
    print(f"[완료] {count}통 발송 완료. {user} 받은편지함 확인하세요.")
    print(f"       제목 패턴: '[법인명] 2026년 3월 매출 보고'")
    print(f"       첨부 파일: '법인_{{코드}}_2026-03.xlsx'")


if __name__ == "__main__":
    main()
