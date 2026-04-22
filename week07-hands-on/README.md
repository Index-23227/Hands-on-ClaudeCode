# Week 07 — 바이브코딩 쇼케이스 + 개인지도 워크숍

> **전반 60분**: 쇼케이스 5종 — 참가자 실무와 매핑되는 데모
> **후반 30분**: 개인지도 (참가자당 15분)
> **핵심 메시지**: 5개 데모 모두 "지금 하시는 업무의 한 단계"를 Claude가 어떻게 대체하는지 보여줌
>
> _현 기수 참가자 실무 매핑: 영업관리(이상출고 모니터링) · 해외관리(40법인 회신·Netra 대시보드)._

---

## 오늘 구성 한눈에

```
┌─ 0~5분   오프닝 ─┐
│  6주 여정 + 오늘 2부 구성 소개
└─────────────────┘
        ▼
┌─ 5~65분 쇼케이스 5종 (60분) ────────────────────────────┐
│ A. 영수증 OCR (10분)          — 멀티모달의 충격          │
│ B. DART 삼성전자 (12분)       — 외부 데이터 + AI 요약   │
│ D. PPT·HTML·JSX 3종 (15분)    — 해외관리 업무 직결 ⭐   │
│ F1. 메일 수신 취합 (12분)     — 해외관리 업무 직결 ⭐   │
│ F2. 이상거래 알림 (12분)      — 영업관리 업무 직결 ⭐   │
└─────────────────────────────────────────────────────┘
        ▼
┌─ 65~75분 쉬는 시간·질문 ─┐
└────────────────────────┘
        ▼
┌─ 75~105분 개인지도 (참가자당 15분) ─────┐
│ 본인 업무 가져와 Claude와 실제 자동화    │
│ 다른 참가자는 옆에서 관찰 (이것도 학습)  │
└─────────────────────────────────────────┘
        ▼
┌─ 105~120분 마무리 ─┐
│  공유 + 8주차 예고  │
└────────────────────┘
```

---

## 시간표

| 구간 | 내용 | 문서 |
|------|------|------|
| 0~5분 | 오프닝 — 6주 여정 / 오늘 의도 | — |
| 5~15분 | **데모 A** 영수증 OCR | [demos/receipt_ocr/](demos/receipt_ocr/) |
| 15~27분 | **데모 B** DART 삼성전자 | [demos/dart_samsung/](demos/dart_samsung/) |
| 27~42분 | **데모 D** PPT+HTML+JSX 3종 | [demos/dashboard_3format/](demos/dashboard_3format/) |
| 42~54분 | **데모 F1** 메일 수신 취합 (MCP) | [demos/email_receive/](demos/email_receive/) |
| 54~66분 | **데모 F2** 이상거래 알림 (SMTP) | [demos/email_send/](demos/email_send/) |
| 66~75분 | 쉬는 시간 + 자유 질문 | — |
| 75~90분 | **개인 지도 ①** (영업관리 — 이상거래 탐지 + F2 응용) | [수강생과제_CLAUDE_템플릿.md](수강생과제_CLAUDE_템플릿.md) |
| 90~105분 | **개인 지도 ②** (해외관리 — Netra/40법인 + D/F1 응용) | 위와 동일 |
| 105~120분 | 마무리 + 8주차 예고 | — |

---

## 데모 5종 — 강사 라이브 프롬프트

각 데모의 상세 프롬프트는 **각 서브폴더 README** 참고. 여기는 요약.

### 데모 A — 영수증 OCR (10분) [상세](demos/receipt_ocr/README.md)
**"사진이 엑셀이 되네"** — 멀티모달 충격 첫인상

```
week07-hands-on/demos/receipt_ocr/samples/ 폴더의 영수증 8장을 모두 읽어서
각 영수증에서 날짜·매장명·항목요약·합계·결제방식을 추출,
"경비정리_2026-03.xlsx"로 정리해줘. 법인카드/개인카드 분리 + 각 소계.
저장: week07-hands-on/demos/receipt_ocr/output/
```

**참가자 질문 유도**: "핸드폰으로 찍기만 하면 경비 정리 끝. 매달 얼마나 걸리세요?"

---

### 데모 B — DART 삼성전자 (12분) [상세](demos/dart_samsung/README.md)
**"Claude가 인터넷까지 쓰네"** — 외부 데이터 + AI 요약

```
DART에서 삼성전자(corp_code 00126380) 2024·2025 연결재무제표 가져와서
매출액·영업이익·당기순이익 비교표 만들고, 영업이익률 추가,
엑셀에 "주목 포인트 3줄 요약"까지 붙여줘.
저장: week07-hands-on/demos/dart_samsung/output/삼성전자_재무비교.xlsx
```

**참가자 질문 유도**: "환율 리포트와 원리 같죠? 외부에서 가져와 → AI 요약 → 보고서"

---

### 데모 D — 3종 대시보드 (15분) [상세](demos/dashboard_3format/README.md) ⭐ 해외관리 업무 직결
**"같은 데이터, 다른 매체"** — 방법론 4가지

Step 1 PPT → Step 2 HTML → Step 3 React/JSX 순차 변환:

```
Step 1: data/overseas_sales.xlsx로 40법인 매출 PPT 2장 만들어줘
  슬라이드1: 지역별 바 차트 + KPI 3개
  슬라이드2: 상위 10개 법인 테이블 (영업이익률 20% 이상 빨강)

Step 2: 같은 데이터로 HTML 대시보드도 (Chart.js CDN, 지역 필터 추가)

Step 3: React 컴포넌트로 변환 (CDN + Babel 단독 실행 HTML + DashBoard.jsx 이식용)
```

**해외관리 담당 유도**: "지금 Streamlit으로 만드시는 사내 대시보드(Netra)가 바로 이 구조. 같은 데이터로 경영회의용 PPT, 내부 포털 HTML, 대시보드 이식용 React까지 한 번에 뽑을 수 있어요"

---

### 데모 F1 — 메일 수신 취합 (12분) [상세](demos/email_receive/README.md) ⭐ 해외관리 업무 직결
**"받은편지함을 Claude가 직접 본다"** — MCP Gmail (Claude.ai 커넥터)

사전: `prep/send_sample_inbox_emails.py --count 8` 실행해 두어 8통 대기.

```
Claude, 내 Gmail 받은편지함에서 '매출 보고' 제목 메일 8통을 찾아서
각 메일 본문의 "매출액: 875,000 CNY" 표시를 파싱한 뒤,
week05 DB(../week05-hands-on/data/sales.db)의 2026-03-31 월말 환율로 KRW 환산해서
한 파일로 취합해줘. 저장: week07-hands-on/demos/email_receive/output/매출취합_2026-03.xlsx
(합계 기대값: 1,212,620,000 KRW)
```

**해외관리 담당 유도**: "지금 40개 법인 회신을 하나씩 여는 그 작업입니다. 로직은 동일, 숫자만 40으로 늘어나면 됨"

> ⚠️ **MCP 주의**: Claude.ai Gmail 커넥터는 첨부 바이너리 다운로드 미지원. 본문 파싱으로 우회.
> Claude가 "첨부를 다운로드할게요"라고 하면 **"본문만 파싱해"** 로 가볍게 교정.

---

### 데모 F2 — 이상거래 자동 알림 (12분) [상세](demos/email_send/README.md) ⭐ 영업관리 업무 직결
**"탐지 + 개인화 + 발송까지 1분"** — 무인 파이프라인

Step 1 탐지 → Step 2 초안 → Step 3 실제 발송:

```
Step 1: data/shipments.xlsx 읽고 이상거래처 자동 탐지
  기준: 품목 50개 초과 + 반품률 0% or 반품률 15% 초과

Step 2: 담당자별 경각심 메일 본문 개인화 작성 (각자 다른 내용)

Step 3: 확인 후 .env의 SUB_ACCOUNTS로 SMTP 실제 발송
```

**영업관리 담당 유도**: "지금 하시는 이상출고 감지 + 담당자 메일 알림이 완벽히 이것. Windows 스케줄러에 등록하면 매주 자동"

---

## 5개 데모 뒤 핵심 질문

각 데모 끝에 참가자들께 던질 질문 (소규모라 개인 답 가능):
- "지금 업무에서 이 구조와 가장 가까운 게 뭔가요?"
- "이걸 본인 업무에 적용하면 어느 부분부터 시도해 볼 만할까요?"

답이 **개인지도 15분의 주제**가 됨. 사전 정해두지 말고 대화 중에 도출.

---

## 개인지도 30분 (참가자당 15분)

각자 **본인 업무 + 가장 공감했던 데모** 접목으로 한 걸음:

| 업무 유형 | 추천 접목 방향 |
|---|---|
| **영업관리 (이상거래 모니터링)** | F2 (이상거래 알림) 변형 — 본인 SAP 기준으로 이상거래 추출 + 실제 Outlook 초안 작성 |
| **해외관리 (법인 대시보드)** | D (대시보드 3종) 변형 — 지금의 Streamlit을 PPT/React로도 변환 / 또는 F1 메일 취합 |

다른 참가자는 옆에서 관찰 → 15분 뒤 교체. 관찰하는 시간도 학습.

템플릿: [수강생과제_CLAUDE_템플릿.md](수강생과제_CLAUDE_템플릿.md)
막히면: [막힘카드.md](막힘카드.md)
결과 받으면: [검증체크리스트.md](검증체크리스트.md)

---

## 사전 준비 (강사)

### 1회 세팅 (수업 이전)
- [ ] `prep/.env.example` → `prep/.env` 복사 후 값 입력
  - `GMAIL_USER`, `GMAIL_APP_PASSWORD` (앱 비밀번호)
  - `SUB_ACCOUNTS` (부계정 3~5개)
  - `DART_API_KEY` (week06 `.env`에서 복사 OK — fallback도 week06 경로 자동 탐색)
- [ ] 필요 패키지 설치 (1회):
  ```bash
  py -m pip install openpyxl python-pptx Pillow
  ```
  - `openpyxl`: 모든 엑셀 데모
  - `python-pptx`: D 데모 (PPT 생성)
  - `Pillow`: A 데모 영수증 샘플 생성
- [ ] 4개 prep 스크립트 실행 (시연 자산 생성):
  ```bash
  py week07-hands-on/prep/make_receipt_samples.py
  py week07-hands-on/prep/make_abnormal_shipments.py
  py week07-hands-on/prep/make_overseas_sales.py
  ```
- [ ] Claude.ai Connectors에서 **Gmail 커넥터 연결** (OAuth 1회) — 툴명 `mcp__claude_ai_Gmail__*` 사용
  - 실패하거나 첨부까지 받아야 할 경우 IMAP 폴백(`fallback_imap.py`) 쓸지 결정

### 수업 당일 (1~2시간 전)
- [ ] `py week07-hands-on/prep/send_sample_inbox_emails.py --count 8` → 샘플 메일 8통 강사 Gmail에 발송
- [ ] 5개 데모 폴백 한 번씩 실행해 결과 확인 → [강사_리허설가이드.md](강사_리허설가이드.md)
- [ ] 각 `demos/*/output/` 폴더 비우기 (기존 생성물 제거)

### 직전 5분
- [ ] 받은편지함에 샘플 메일 8통 있는지 재확인
- [ ] Claude Code 열고 CLAUDE.md 로드됐는지 확인
- [ ] 참가자 앞에서 보여줄 브라우저 탭/프로젝터 연결

---

## 문서 맵

### 수강생용
| 문서 | 언제 | 목적 |
|---|---|---|
| [수강생과제_CLAUDE_템플릿.md](수강생과제_CLAUDE_템플릿.md) | 개인지도 시작 시 | 본인 업무 자동화 설계 |
| [막힘카드.md](막힘카드.md) | 막혔을 때 | 6유형 대응 |
| [검증체크리스트.md](검증체크리스트.md) | 결과 받은 후 | 5단계 검증 |
| [Gmail_자동화_설정.md](Gmail_자동화_설정.md) | 메일 자동화 적용 시 | 앱 비밀번호 발급 15분 가이드 |

### 강사용
| 문서 | 용도 |
|---|---|
| [CLAUDE.md](CLAUDE.md) | 공통 규칙 (서식·정렬·환율) |
| [강사용_순회체크.md](강사용_순회체크.md) | 개인지도 중 진단 |
| [강사_리허설가이드.md](강사_리허설가이드.md) | 수업 전 드라이런 |
| [슬라이드_구성안.md](슬라이드_구성안.md) | pptx 제작 아웃라인 |
| [demos/*/README.md](demos/) | 각 데모 상세 프롬프트 |
| [prep/README.md](prep/README.md) | 사전 준비 스크립트 사용법 |

---

## 자주 나는 에러

| 에러 | 원인 | 1줄 해결 |
|---|---|---|
| `ModuleNotFoundError: pptx` | python-pptx 미설치 | `py -m pip install python-pptx` |
| DART API 응답 비어있음 | 공시 아직 제출 안 됨 | 폴백 샘플 사용 (자동) |
| `SMTPAuthenticationError` | 앱 비밀번호 오류 | `.env` 재확인, 공백 제거 |
| MCP Gmail 연결 실패 | OAuth 미완료 | IMAP 폴백 (`fallback_imap.py`) |
| 받은편지함에 샘플 없음 | 메일 발송 안 됨 | `prep/send_sample_inbox_emails.py` 재실행 |
| Claude Vision 이미지 못 읽음 | 드래그앤드롭 실패 | 경로로 지정하거나 폴백 실행 |

---

## 폴더 전체 구조

```
week07-hands-on/
├── README.md                      ← 진입점
├── CLAUDE.md                      ← 공통 규칙
├── 수강생과제_CLAUDE_템플릿.md
├── 막힘카드.md
├── 검증체크리스트.md
├── 강사용_순회체크.md
├── 강사_리허설가이드.md
├── 슬라이드_구성안.md
├── Gmail_자동화_설정.md           ← 수강생용 앱 비밀번호 발급 가이드
├── prep/                          ← 사전 준비 (강사)
│   ├── .env.example
│   ├── send_sample_inbox_emails.py
│   ├── make_receipt_samples.py
│   ├── make_abnormal_shipments.py
│   ├── make_overseas_sales.py
│   └── README.md
└── demos/                         ← 5개 데모 서브폴더
    ├── receipt_ocr/               ← A
    ├── dart_samsung/              ← B
    ├── dashboard_3format/         ← D
    ├── email_receive/             ← F1
    └── email_send/                ← F2
```

---

## 8주차 예고

오늘 개인지도에서 **첫 한 단계**를 만드셨습니다. 8주차까지 1주일 동안:

1. **만든 것** 완성 (결과물)
2. **검증** (체크리스트 5단계)
3. **Claude가 틀렸다가 고친 에피소드** 1건 이상 기록

이 셋을 **5분 발표**로 준비해오세요. 평가 포인트는 완성도가 아니라 **"Claude와 어떻게 대화했는가"**.

확장 방향 (여유 되시면):
- Windows 작업 스케줄러 등록 (week06 패턴, [register_task.ps1](../week06-hands-on/register_task.ps1))
- 실패 시 알림 (week06 실패 flag 패턴)
- 결과를 PPT/HTML 자동 발송 (D + F2 조합)
