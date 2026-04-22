# prep/ — 강사 사전 준비 스크립트

수업 당일 전에 강사가 **1회 실행**하여 시연용 자산을 준비하는 스크립트 모음.
수강생은 이 폴더를 볼 필요 없음.

---

## 전체 사전 준비 흐름 (1회 세팅)

```bash
# 1. 환경
pip install openpyxl python-pptx Pillow
cp prep/.env.example prep/.env          # 값 채우기 (Gmail 앱 비밀번호 + SUB_ACCOUNTS + DART)

# 2. 4개 prep 스크립트로 시연 자산 생성
py week07-hands-on/prep/make_receipt_samples.py       # A: 영수증 PNG 8장
py week07-hands-on/prep/make_abnormal_shipments.py    # F2: 이상거래 xlsx
py week07-hands-on/prep/make_overseas_sales.py        # D: 40법인 xlsx
py week07-hands-on/prep/send_sample_inbox_emails.py   # F1: 샘플 메일 (기본 2통)
```

| 스크립트 | 용도 | 출력 |
|---|---|---|
| `make_receipt_samples.py` | A 데모용 영수증 이미지 | `demos/receipt_ocr/samples/*.png` (8장) |
| `make_abnormal_shipments.py` | F2 데모용 이상거래 Mock | `demos/email_send/data/shipments.xlsx` |
| `make_overseas_sales.py` | D 데모용 40법인 Mock | `demos/dashboard_3format/data/overseas_sales.xlsx` |
| `send_sample_inbox_emails.py` | F1 데모용 샘플 메일 발송 | 강사 Gmail 받은편지함 |

---

## 1. F1 시연용 샘플 메일 발송

### 스크립트
[send_sample_inbox_emails.py](send_sample_inbox_emails.py)

### 무엇을 하나
강사 Gmail → 강사 Gmail(자기 자신) 앞으로 **"법인 담당자의 월말 매출 보고"** 메일 발송.

- 제목: `[중국법인] 2026년 3월 매출 보고` 등
- 본문: 각 법인 가상 담당자가 쓴 것처럼 구성
- 첨부: `법인_{코드}_2026-03.xlsx` 각 1개 (RFC 2231 한글 파일명 인코딩)
- 매출 데이터: week05 DB의 실제 2026-03 수치 사용 (일관성)

**기본 2통** (테스트용). 시연 당일 **`--count 8`**로 전체 8법인 발송.

```bash
py send_sample_inbox_emails.py                 # 중국·독일 2통
py send_sample_inbox_emails.py --count 8       # 8법인 전체
py send_sample_inbox_emails.py --count 5       # 앞에서 5통
```

시연 중 Claude(MCP Gmail 또는 IMAP)가 받은편지함을 열어 이 메일들을 자동 처리.

### 사전 준비 (1회)

1. **Gmail 2FA 활성화**: https://myaccount.google.com/security
2. **앱 비밀번호 발급**: https://myaccount.google.com/apppasswords
3. **`.env` 파일 생성**:
   ```bash
   cp prep/.env.example prep/.env
   ```
   `.env` 열어서 `GMAIL_USER`와 `GMAIL_APP_PASSWORD` 입력.
   `.env`는 `.gitignore`에 포함되어 **커밋되지 않음**.

### 실행

```bash
py week07-hands-on/prep/send_sample_inbox_emails.py
```

예상 출력 (기본 2통):
```
[시작] your.email@gmail.com → your.email@gmail.com로 샘플 법인 매출 메일 2통 발송
       (전체 8통 중 앞에서 2개만 — 시연 시 '--count 8' 로 전체)

  [OK] [중국법인] 김준호 — 875,000 CNY
  [OK] [독일법인] 박서연 — 101,000 EUR

[완료] 2통 발송 완료.
```

`--count 8` 으로 실행 시 8법인 전체 발송 (시연 당일 권장).

### 시연 당일 권장 운영
- **수업 1~2시간 전**에 재발송 (받은편지함 최상단 유지)
- 리허설 때 1회 + 본 수업 전 1회 = 총 2회 발송 권장
- 기존 시연 메일을 미리 삭제할 필요는 없음. 받은편지함에서 최신 8통이 상단에 뜸.

### 재실행 주의
- 이 스크립트는 **중복 방지 로직 없음**. 실행할 때마다 8통이 추가됨.
- 너무 많이 쌓였으면 Gmail 검색창에서 `subject:"2026년 3월 매출 보고"`로 찾아 삭제.

---

## 2. 영수증 샘플 PNG 8장 생성 (A 데모용)

```bash
py make_receipt_samples.py
```
출력: `demos/receipt_ocr/samples/01_스타벅스.png` ~ `08_호텔.png`

한국식 재경 경비 영수증 다양성 (카페·편의점·주유소·사무용품·식당·택시·KTX·호텔).
미묘한 회전 각도까지 들어가 "사진 찍은 느낌". 법인카드 6장 + 개인카드 2장.

## 3. 이상거래 Mock 데이터 (F2 데모용)

```bash
py make_abnormal_shipments.py
```
출력: `demos/email_send/data/shipments.xlsx` (20 거래처 × 총 151행)

이상거래 5건 내장:
- CUST001 강남B치과 [높음] — 이상품목 3개, 반품 0%
- CUST002 판교Y치과 [높음] — 이상품목 2개, 반품 0%
- CUST003 잠실Z치과 [주의] — 반품 20%
- CUST004 성수K치과 [정상범위] — 반품 4.3% (발송 제외)
- CUST005 홍대M치과 [주의] — 반품 0%

## 4. 해외법인 40개 Mock 데이터 (D 데모용)

```bash
py make_overseas_sales.py
```
출력: `demos/dashboard_3format/data/overseas_sales.xlsx` (3시트)

- 시트1 법인마스터: 40법인 (Americas 10 / APAC 15 / EMEA 12 / Oceania 3)
- 시트2 월별매출: 720행 (40법인 × 6개월 × 3품목군)
- 시트3 환율: 24개 통화 월말 KRW 환율

---

## 트러블슈팅

| 증상 | 원인 | 해결 |
|---|---|---|
| `SMTPAuthenticationError` | 앱 비밀번호 오류 | .env의 `GMAIL_APP_PASSWORD` 재확인. 공백 포함해도 되고 없어도 됨 |
| `.env 파일이 없습니다` | .env 미생성 | `.env.example`을 `.env`로 복사 |
| `GMAIL_USER를 실제 Gmail 주소로` | 기본값 그대로 | `.env` 열어 본인 주소로 교체 |
| `ModuleNotFoundError: openpyxl` | 패키지 미설치 | `pip install openpyxl` |
| 메일은 갔는데 받은편지함에 없음 | Gmail 필터 처리 | 스팸함·전체 메일함 확인 |
