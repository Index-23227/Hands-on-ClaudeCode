# demos/ — 5개 쇼케이스 데모

> 각 데모는 **독립된 서브폴더**. 자체 README·폴백 스크립트·출력 폴더를 가진다.
> 수강생에게 보여주지 않음. 수강생은 `../README.md`의 프롬프트를 보고, 강사가 Claude에게 시키는 모습만 관찰.

---

## 데모 목록

| 폴더 | 데모 | 핵심 메시지 | 수강생 매칭 | 시간 |
|---|---|---|---|---|
| [receipt_ocr/](receipt_ocr/) | A. 영수증 OCR | 멀티모달 이미지 직접 처리 | 전원 공통 (경비) | 10분 |
| [dart_samsung/](dart_samsung/) | B. DART 삼성전자 | 외부 데이터 + AI 요약 체인 | 전원 공통 (외부 조회) | 12분 |
| [dashboard_3format/](dashboard_3format/) | D. PPT·HTML·JSX 3종 | 같은 데이터, 여러 출력 매체 | **해외관리** (사내 대시보드) | 15분 |
| [email_receive/](email_receive/) | F1. 메일 수신 취합 | MCP로 Gmail 직접 접근 | **해외관리** (40법인 회신) | 12분 |
| [email_send/](email_send/) | F2. 이상거래 알림 | SMTP 무인 발송 파이프라인 | **영업관리** (이상출고) | 12분 |

---

## 사용 원칙

### 1. 라이브 시연 우선
각 데모 서브폴더 README의 **"시연 프롬프트"**를 Claude Code에 그대로 복붙.
수강생이 관찰하는 건 **Claude의 생성 과정** — 이게 오늘의 학습 자산.

### 2. 폴백은 백업
Claude가 실패·시간 초과·멀티모달 오작동 시 각 폴더의 `fallback_*.py`:

```bash
py demos/receipt_ocr/fallback_extract.py          # A
py demos/dart_samsung/fallback_analysis.py        # B
py demos/dashboard_3format/fallback_build_all.py  # D
py demos/email_receive/fallback_imap.py           # F1
py demos/email_send/fallback_detect_and_send.py   # F2
```

폴백 실행 시 수강생에게:
> "Claude가 방금 만들려 했던 결과를 미리 준비한 버전으로 보여드릴게요. 같은 모양입니다."

### 3. 사전 데이터 준비 필수
Phase 1 prep 스크립트들이 먼저 실행되어 있어야 함:

```bash
py week07-hands-on/prep/make_receipt_samples.py      # A 입력
py week07-hands-on/prep/make_abnormal_shipments.py   # F2 입력
py week07-hands-on/prep/make_overseas_sales.py       # D 입력
py week07-hands-on/prep/send_sample_inbox_emails.py  # F1 입력 (수업 1~2시간 전)
```

---

## 5개 데모 연결 흐름

데모가 서로 연결되어 메시지가 누적됨:

```
A (멀티모달)     — "이미지도 직접 처리"
    ↓
B (외부 데이터)  — "인터넷도 간다"
    ↓
D (3종 출력)     — "같은 데이터, 다른 매체" + 방법론 4가지
    ↓
F1 (메일 수신)   — "받은편지함도 직접 본다" (대화형 MCP)
    ↓
F2 (메일 발송)   — "주기 실행·자동 파이프라인" (스크립트 SMTP)
    ↓
쉬는 시간 → 개인 지도로 전환
```

F1·F2 비교가 오늘의 정점: **"같은 목적이라도 방식은 둘 — 무엇을 쓸지는 업무 성격에 따라"**.

---

## 출력 파일 맵

모든 생성물은 각 데모 서브폴더의 `output/`:

| 데모 | 출력 |
|---|---|
| A | `receipt_ocr/output/경비정리_2026-03.xlsx` |
| B | `dart_samsung/output/삼성전자_재무비교.xlsx` |
| D | `dashboard_3format/output/매출보고서.pptx` + `dashboard.html` + `dashboard_react.html` + `DashBoard.jsx` |
| F1 | `email_receive/output/매출취합_2026-03.xlsx` |
| F2 | `email_send/output/detection_report.txt` + 실제 SMTP 발송 |

`output/` 폴더는 `.gitignore` 처리됨 (각자 재생성 가능).

---

## 레거시 데모(demo1~6.py)

이전 설계의 6개 폴백 스크립트(`demo1_compare_excel.py` ~ `demo6_template_fill.py`)는
**본 재설계로 대체되어 삭제**됨 (git 히스토리에서 복구 가능).

- 기존 엑셀 비교·정합성·서식·반복 템플릿 패턴은 **워크숍 참고 템플릿**이 필요하면
  수강생 업무 맥락에서 재활용 가능. 하지만 쇼케이스에는 포함하지 않음.
- 기존 자연어 DB 질의(demo3)는 B의 외부 데이터 + 분석 메시지에 흡수됨.
