# CLAUDE.md — 7주차 바이브코딩 쇼케이스 하네스

> 강사가 Claude에게 **자연어로 데모를 시키면** 이 문서의 규칙이 자동 적용되도록 한다.
> 5개 데모(A/B/D/F1/F2)는 각자 서브폴더에 폴백 스크립트 포함.
> 수강생은 코드를 직접 쓰지 않는다.

---

## 프로젝트 구조

```
week07-hands-on/
├── CLAUDE.md                      ← 이 문서 (하네스)
├── README.md                      ← 데모 프롬프트 모음 + 시간표 (강사용)
├── 막힘카드.md                    ← 수강생용 치트시트
├── 검증체크리스트.md              ← 수강생용 결과 검증 가이드
├── 수강생과제_CLAUDE_템플릿.md    ← 개인지도에서 수강생이 채울 하네스
├── 강사용_순회체크.md             ← 워크숍 진단 카드
├── 강사_리허설가이드.md           ← 수업 전 드라이런 체크리스트
├── 슬라이드_구성안.md             ← pptx 제작용 아웃라인
├── prep/                          ← 강사 사전 준비 스크립트
│   ├── .env.example               ← Gmail·DART 인증정보 템플릿
│   ├── send_sample_inbox_emails.py  (F1용 샘플 메일 기본 2통, --count 8로 전체)
│   ├── make_receipt_samples.py      (A용 영수증 PNG 8장 생성)
│   ├── make_abnormal_shipments.py   (F2용 이상거래 xlsx 생성)
│   └── make_overseas_sales.py       (D용 40법인 xlsx 생성)
└── demos/
    ├── receipt_ocr/               ← 데모 A: 영수증 OCR (Claude Vision)
    │   ├── samples/*.png            (영수증 이미지 8장)
    │   └── fallback_extract.py
    ├── dart_samsung/              ← 데모 B: DART 삼성전자 분석
    │   └── fallback_analysis.py
    ├── dashboard_3format/         ← 데모 D: PPT + HTML + JSX 3종
    │   ├── data/overseas_sales.xlsx
    │   └── fallback_build_all.py
    ├── email_receive/             ← 데모 F1: 법인 회신 메일 취합 (MCP Gmail)
    │   └── fallback_imap.py
    └── email_send/                ← 데모 F2: 이상거래 알림 메일 (SMTP)
        ├── data/shipments.xlsx
        └── fallback_detect_and_send.py
```

---

## 이어쓰는 자산 (week04/week05)

이번 주도 **새로 만들지 않는다**. 기존 자산을 조회하고 가공한다.

### week05 DB에서 이어쓰는 것 (주 데이터 소스)
- **경로**: `../week05-hands-on/data/sales.db` (상위 폴더 참조)
- **테이블 목록 (실제 있는 것)**:
  - `corporations` — 법인 마스터 8건 (PK: `corp_code`)
  - `monthly_sales` — 월별 매출 48건 (법인 8 × 월 6)
  - `exchange_rates` — 환율 (복합 PK: `currency`, `rate_date`)
  - `dart_financials` — DART 공시 재무 (week06 fetch_dart 결과, 이번 주 데모는 사용하지 않음)
- **DB가 없으면** 먼저 `../week05-hands-on/data/create_db.py` → 이어서 `../week06-hands-on/run_pipeline.py`.

### 법인/통화 규칙 (week05 DB 기준 — 8개)

week04는 5개 법인(CN/DE/JP/US/VN)만 엑셀로 있고, 나머지 3개(IN/GB/TH)는 week05 DB부터 추가되었다. **이번 주는 week05 DB의 8개를 기준**으로 삼는다.

- 법인코드 8개: `CN01`, `DE01`, `GB01`, `IN01`, `JP01`, `TH01`, `US01`, `VN01` (알파벳순)
- 통화 8개: `CNY`, `EUR`, `GBP`, `INR`, `JPY`, `THB`, `USD`, `VND`
- week04 엑셀 파일명 규칙(`법인_{code}_{country}.xlsx`, 시트명 `Sheet`, 컬럼 `월|계정과목|통화|금액|비고`)은 참조용으로만 유지 — 이번 주 데모는 DB에서 직접 조회.

---

## 공통 규칙 — 모든 데모에 적용

### 출력 경로
- **모든 생성 파일은 해당 데모 서브폴더의 `output/`에 저장한다.**
  - A 영수증 → `demos/receipt_ocr/output/`
  - B DART → `demos/dart_samsung/output/`
  - D 3종 → `demos/dashboard_3format/output/`
  - F1 수신 → `demos/email_receive/output/`
  - F2 발송 → `demos/email_send/output/`
- 프롬프트에 경로가 명시되지 않아도 이 규칙을 따른다.
- `output/` 폴더는 `.gitignore` 처리됨 (재생성 가능).

### 라이브러리 정책
- 엑셀 처리: **`openpyxl`만** 사용 (pandas 금지 — 수강생 환경 부담)
- PDF 처리: 필요 시 `pdfplumber` 설치 안내
- DB: `sqlite3` (표준 라이브러리)
- 차트: `openpyxl.chart` 내장 기능
- 기타 모든 표준 라이브러리 우선, 외부 패키지는 최소화

### 엑셀 서식 — 한국 재경팀 관행

모든 보고서/출력 엑셀에 아래 규칙을 기본 적용한다. 프롬프트에 없어도 적용.

| 요소 | 규칙 |
|---|---|
| 헤더 행 | 배경 짙은 남색 (`#1F4E78`), 글자 흰색, 볼드 |
| 합계 행 | 배경 연회색 (`#D9D9D9`), 볼드 |
| 숫자 컬럼 | 천단위 콤마, 우측 정렬 |
| 금액 음수 | 빨간색 글자 또는 `△` 접두사 |
| 날짜 | `YYYY-MM-DD` 형식 (텍스트 아닌 날짜 타입) |
| 퍼센트 | 소수점 1자리 + `%` (예: `12.3%`) |
| 열 너비 | 내용에 맞춰 `auto_size` 또는 명시적 너비 |
| 틀 고정 | 헤더 행 고정 (`freeze_panes='A2'`) |

### 증감 색상 (한국 관행)
- **증가 = 빨강** (`#C00000` 또는 `#FF0000`)
- **감소 = 초록** (`#00B050` 또는 `#008000`)
- 서양식(증가=초록)과 반대. 혼동 금지.

### 통화 처리
- 법인별 외화 합계는 **통화별로 분리**해서 보여준다. 통화가 다른 금액을 그냥 더하지 않는다.
- 원화 환산 결과 컬럼명은 `원화환산(KRW)`.

### 환율 기준일 규칙 (중요 — 데모마다 다름)

`exchange_rates` 테이블에는 **월말 기준 6개(`2026-01-31`, `02-28`, `03-31`, `04-30`, `05-31`, `06-30`)** + **비월말 일자 몇 개(예: `2026-01-04`, `04-17`)**가 섞여 있다. week06 파이프라인 실행 결과가 축적되면서 월중 날짜가 추가됨. **이 차이를 무시하고 `MAX(rate_date)`만 쓰면 엉뚱한 날이 잡힐 수 있다.**

| 용도 | 기준 SQL | 이유 |
|---|---|---|
| **"최신/오늘 환율" 원화 환산** (데모 3) | `WHERE rate_date = (SELECT MAX(rate_date) FROM exchange_rates WHERE rate_date <= DATE('now'))` | "현재 시점까지의 최신 게시 환율" — 미래 날짜 제외 |
| **월별 매출 환산** (데모 4·6) | `WHERE rate_date = (SELECT MAX(r.rate_date) FROM exchange_rates r WHERE r.currency = e.currency AND r.rate_date <= ms.month \|\| '-末일')` 방식으로 **해당 월말 이전의 가장 최근 환율**을 통화별로 조인 | "월 마감 환율" 재경 관행. 월중 환율(예: 04-17)이 있어도 해당 월 월말(04-30) 또는 그 이전 직전 가용값을 사용 |
| **전월 대비 증감 계산** (데모 6) | 증감은 **외화 원금액 기준으로 먼저 계산**, 그 다음 각 월 환율로 환산 | 환율 변동이 증감률에 섞이지 않도록 |

Claude에게 환산 요청 시 **"어떤 환율 기준인지"** 반드시 명시. 모호하면 "월말 기준인지, 최신 기준인지 물어봐줘"라고 Claude가 되묻도록 유도.

**간이 대안 (교육용으로 충분할 때)**: 위 SQL이 어려우면 Python에서 `rate_date`를 파싱해서 `YYYY-MM-30` 또는 `YYYY-MM-31`로 끝나는 것만 필터링해도 됨. 설명이 더 쉬움.

### 빈 값 vs 0
- DB나 엑셀의 `NULL`/빈 칸은 `0`으로 치환하지 않는다. `"N/A"` 또는 빈 셀 유지.
- 합계 계산 시에도 `NULL`은 제외 (0 취급 금지).

### 정렬 원칙 (week04 상속)

모든 출력 엑셀·표에 일관되게 적용:

- **법인 순서**: 가나다순 (독일 → 미국 → 베트남 → 영국 → 인도 → 일본 → 중국 → 태국)
  - 단, 한 번 정한 순서는 모든 데모에서 동일 유지 (수강생이 "왜 순서가 다르지?" 혼란 방지)
- **날짜/월**: 오름차순 (`2026-01` → `2026-06`)
- **합계 행은 항상 마지막** (중간에 넣지 않음)
- **통화 순서**: 법인 순서와 연동 (법인이 먼저 정렬되면 통화는 자동으로 따라감)

---

## 데모별 출력 파일명

Claude가 자유롭게 이름을 짓지 않도록 고정한다. 수강생이 재현 확인하기 쉽게.

| 데모 | 출력 파일명 | 출력 위치 |
|---|---|---|
| A — 영수증 OCR | `경비정리_2026-03.xlsx` | `demos/receipt_ocr/output/` |
| B — DART 삼성전자 | `삼성전자_재무비교.xlsx` | `demos/dart_samsung/output/` |
| D — 3종 대시보드 | `매출보고서.pptx`, `dashboard.html`, `dashboard_react.html`, `DashBoard.jsx` | `demos/dashboard_3format/output/` |
| F1 — 메일 수신 취합 | `매출취합_2026-03.xlsx` | `demos/email_receive/output/` |
| F2 — 이상거래 알림 | `detection_report.txt` + SMTP 실제 발송 | `demos/email_send/output/` |

---

## 시연 시 지켜야 할 것 (강사용)

1. **프롬프트는 README.md에 있는 것을 그대로 복붙**한다. 즉석에서 수정하면 기대 결과가 흔들림.
2. Claude가 엉뚱한 경로에 저장하면 각 데모의 `output/`로 옮기도록 즉시 지시.
3. 데모가 실패하면 각 서브폴더의 `fallback_*.py` 폴백 실행.
   - A: `py demos/receipt_ocr/fallback_extract.py`
   - B: `py demos/dart_samsung/fallback_analysis.py`
   - D: `py demos/dashboard_3format/fallback_build_all.py`
   - F1: `py demos/email_receive/fallback_imap.py`
   - F2: `py demos/email_send/fallback_detect_and_send.py`

### F1 MCP Gmail 제약 (중요)

Claude.ai 네이티브 Gmail 커넥터(`mcp__claude_ai_Gmail__*`)는 `search_threads`·`get_thread`는
제공하지만 **첨부 바이너리 다운로드는 지원하지 않는다**. F1 시연은 이 제약을 전제로 설계됨:

- 샘플 메일 본문에 `매출액: 875,000 CNY` 형식으로 금액이 **본문에** 박혀있음 (발송 스크립트 설계)
- Claude는 본문만 파싱해서 8법인 데이터 취합 → week05 DB 환율 조인 → xlsx 생성
- 첨부까지 필요하면 `fallback_imap.py` 경로로 전환 (F2 쇼케이스에서 IMAP 자동화 시연)

시연 시 Claude가 "첨부를 다운로드하겠다"고 하면 **"본문만 파싱해"** 로 유도.
4. 각 데모 후 참가자에게 **"이거 지금 하시는 업무 중 어느 부분에 적용될까요?"** 질문.
5. 소규모 수업이라 **질문 무제한 허용**. 대규모에서 불가능한 대화형 시연 활용.
6. 후반 개인 지도 시 수강생에게 **`수강생과제_CLAUDE_템플릿.md`** 안내.

---

## 개인지도 전환 (강사 체크포인트)

쇼케이스 60분 + 쉬는 시간 끝난 뒤 개인지도(참가자당 15분)로 전환할 때:

1. 수강생 각자의 업무 폴더(예: `내업무_자동화/`)를 만들게 한다.
2. `수강생과제_CLAUDE_템플릿.md` 내용을 복사해서 해당 폴더의 `CLAUDE.md`로 저장시킨다.
3. 템플릿의 빈칸을 Claude에게 **말로 설명하면서** 채우게 한다 ("Claude, 내가 설명할 테니 CLAUDE.md 빈칸을 채워줘").
4. 빈칸이 채워지면 그때부터 실제 자동화 요청 시작.

**막히면**: `막힘카드.md`
**결과 받으면**: `검증체크리스트.md` 반드시 통과시킬 것
