# Week 07 — 바이브코딩 쇼케이스 + 본인 업무 워크숍

> 전반 30분: 강사가 Claude에게 자연어로 시켜 **"이런 것도 됩니다"**를 체감시킵니다.
> 후반 90분: 수강생이 **본인 업무**를 가져와 Claude와 함께 자동화합니다.
> 오늘의 핵심은 결과물이 아니라 **"Claude에게 말하는 감각"**입니다.

---

## 오늘 할 것

```
┌────────── 전반 (30분) ──────────┐    ┌─────────── 후반 (90분) ───────────┐
│   강사 시연 쇼케이스 데모 3개    │ →  │  수강생이 본인 업무 자동화 워크숍  │
│   "이게 된다고?" 느끼기          │    │  "나도 시키면 되는구나" 체험       │
└──────────────────────────────────┘    └────────────────────────────────────┘
                                                        ↓
                                              ┌─────── 마무리 (15분) ─────┐
                                              │  공유 + 8주차 결과물 예고  │
                                              └────────────────────────────┘
```

---

## 시간표

| 시간 | 구성 | 내용 | 문서 |
|------|------|------|------|
| 0~30분 | **쇼케이스** | 강사가 Claude에게 데모 3개 시연 (데모 3 → 1 → 6) | [exercises/step0-showcase-intro.md](exercises/step0-showcase-intro.md) |
| 30~45분 | **워크숍 설계** | CLAUDE.md 템플릿 채우기 | [수강생과제_CLAUDE_템플릿.md](수강생과제_CLAUDE_템플릿.md) |
| 45~105분 | **워크숍 구현** | Claude에게 자동화 요청 + 반복 수정 | [exercises/step1-bring-your-work.md](exercises/step1-bring-your-work.md) |
| ☕ | 쉬는 시간 (필요 시 중간 10분) | | |
| 105~120분 | **워크숍 검증** | 검증체크리스트 5개 통과 | [검증체크리스트.md](검증체크리스트.md) |
| 120~135분 | **마무리** | 공유 발표 1~2명 + 8주차 예고 | — |

여유 있으면 [exercises/step2-verify-and-iterate.md](exercises/step2-verify-and-iterate.md) (심화 검증)로 확장.

---

## 전반 — 쇼케이스 데모 프롬프트 (강사용)

Claude Code에 **그대로 복붙**하세요. 이게 수강생이 관찰할 "프롬프트 패턴" 자체입니다.

### 데모 3: 자연어 데이터 분석 (5분) — **가장 먼저**

```
week05-hands-on/data/sales.db에서 매출이 가장 높은 법인 3개를 알려줘.
```

```
전월 대비 매출이 가장 많이 늘어난 법인과 월을 알려줘.
```

```
법인별 원화 환산 매출 합계를 보여줘. 최신 환율 기준으로.
```

**포인트**: "SQL 몰라도 된다"를 첫 인상으로. 수강생이 SQL을 읽을 필요 없다는 걸 강조.

---

### 데모 1: 두 엑셀 비교 (7분)

```
week07-hands-on/demos/output/ 폴더에
3월_매출.xlsx와 4월_매출.xlsx 샘플 데이터를 만들어줘.
법인 8개의 매출 금액이 들어있고, 4월에는 몇 개 법인의 금액이 바뀌어있어.

그다음 두 파일을 비교해서:
- 금액이 바뀐 법인만 추출
- 이전 금액, 이후 금액, 차이, 변동률을 계산
- 결과를 "비교결과.xlsx"로 저장 (증가는 빨간색, 감소는 초록색)
```

**포인트**: "매달 눈으로 비교하던 게 한마디로 끝난다"를 체감.

---

### 데모 6: 반복 보고서 템플릿 (7분)

```
week05-hands-on/data/sales.db에서 2026년 4월, 5월, 6월
월별 매출 보고서를 각각 만들어줘.

각 보고서에 들어갈 내용:
- 타이틀: "월별 매출 보고서 — YYYY-MM"
- 작성일시 자동 표시
- 법인별: 당월 매출, 전월 매출, 증감, 증감률, 원화 환산
- 증감률은 퍼센트 서식 (증가 빨강, 감소 초록)
- 합계 행 (파란 배경)
- 하단에 작성/검토/승인 서명란
- 3개 파일을 한 번에 week07-hands-on/demos/output/ 폴더에 저장
```

**포인트**: "매달 같은 양식에 숫자만 바꾸는 일이 끝난다" — 자동화의 진짜 보상.

---

### 시간 남으면 데모 4·2·5

나머지 3개는 후반 워크숍에서 필요한 사람이 [demos/README.md](demos/README.md)를 참고하거나, 수업 후 복습으로.

---

## 후반 — 수강생 워크숍

### 워크숍 흐름 (상세는 [exercises/step1-bring-your-work.md](exercises/step1-bring-your-work.md))

```
1. 폴더 만들기 (바탕화면/내업무자동화/)
   ↓
2. 수강생과제_CLAUDE_템플릿.md를 CLAUDE.md로 복사
   ↓
3. Claude에게 "내가 설명할 테니 빈칸 채워줘" → 말로 설명
   ↓
4. "8번 오늘 목표"에 적은 것만 Claude에게 요청
   ↓
5. 결과 받으면 검증체크리스트 5개 돌리기
   ↓
6. 통과 못 하면 "거의 맞는데 X만 고쳐줘" 반복
   ↓
7. 80% 맞으면 오늘은 OK. 나머지는 8주차 숙제.
```

### 본인 업무 없는 수강생용 대체 실습

[practice_cases/](practice_cases/) 3개 중 선택:

- [Case 1 — 경비 집계](practice_cases/case1_경비집계.md) (재경팀 연관성 ★★★)
- [Case 2 — 회의록 추출](practice_cases/case2_회의록추출.md) (난이도 ★☆☆)
- [Case 3 — 이메일 일괄 생성](practice_cases/case3_이메일일괄.md) (실무적 ★★☆)

---

## 사전 준비 (강사)

수업 시작 전 반드시 확인:

- [ ] **week05 DB 생성됨**: `../week05-hands-on/data/sales.db` 존재 확인. 없으면 `py ../week05-hands-on/data/create_db.py`
- [ ] **week04 경비 엑셀**: `../week04-hands-on/data/경비내역.xlsx` (Case 1에서 쓰임)
- [ ] **데모 폴백 스크립트**: `demos/*.py` 한 번씩 사전 실행해 결과 확인 → [demos/README.md](demos/README.md)
- [ ] **`demos/output/` 정리**: 사전 실행 후 **수업 전에 비우거나, 모든 수강생에게 보여줄 파일만 남기기**. 기존 생성물이 남아있으면 Claude가 라이브로 만드는 것과 혼동됨
- [ ] **openpyxl 설치됨**: `pip show openpyxl`
- [ ] **Python 인코딩**: 한글 파일명 처리 문제없는지 (한국어 Windows에서 `cp949` 이슈 자주 발생)
- [ ] **환율 SQL 테스트**: 데모 3 "최신 환율" 프롬프트 실행 시 Claude가 `MAX(rate_date) <= DATE('now')` 조건을 제대로 거는지 확인 (DB에 미래·월중 날짜가 섞여있어서 `MAX()`만으론 엉뚱한 값 나올 수 있음 — [CLAUDE.md 환율 기준일 규칙](CLAUDE.md) 참고)

---

## 문서 맵 — 이 주차의 모든 자료

### 수강생용
| 문서 | 언제 봐야 하나 |
|------|----------------|
| [README.md](README.md) | 지금 (오늘 전체 흐름) |
| [exercises/step0-showcase-intro.md](exercises/step0-showcase-intro.md) | 전반 30분 쇼케이스 관찰 시 |
| [exercises/step1-bring-your-work.md](exercises/step1-bring-your-work.md) | 후반 90분 워크숍 시작 시 |
| [수강생과제_CLAUDE_템플릿.md](수강생과제_CLAUDE_템플릿.md) | 워크숍 15분차 — 본인 업무 설계 |
| [막힘카드.md](막힘카드.md) | 워크숍 중 막혔을 때 |
| [검증체크리스트.md](검증체크리스트.md) | 결과물 받고 업무 투입 전 |
| [practice_cases/](practice_cases/) | 본인 업무 없는 경우 |
| [exercises/step2-verify-and-iterate.md](exercises/step2-verify-and-iterate.md) | Step 1 일찍 끝난 수강생 심화 |

### 강사용
| 문서 | 용도 |
|------|------|
| [CLAUDE.md](CLAUDE.md) | 7주차 공통 규칙 (서식·정렬·환율) — 모든 데모에 자동 적용됨 |
| [demos/README.md](demos/README.md) | 6개 데모 폴백 정답 사용법 |
| [강사용_순회체크.md](강사용_순회체크.md) | 워크숍 90분 동안 수강생 진단 |
| [슬라이드_구성안.md](슬라이드_구성안.md) | `Week07_Hands_On.pptx` 제작용 18장 아웃라인 |
| [강사_리허설가이드.md](강사_리허설가이드.md) | **수업 전 드라이런 필수** — 80~90분 리허설 체크리스트 |

---

## 자주 나는 에러 — 한눈 표

워크숍 중 가장 흔히 나오는 에러. **에러 메시지를 그대로 Claude에게 붙여넣으면 70%는 자동 해결**됩니다.

| 에러 / 증상 | 원인 | 1줄 해결 |
|---|---|---|
| `ModuleNotFoundError: No module named 'openpyxl'` | 패키지 미설치 | Claude에게 "openpyxl 설치해줘" |
| `ModuleNotFoundError: No module named 'pdfplumber'` | PDF 처리 패키지 미설치 | Claude에게 "pdfplumber 설치해줘" (데모 2 실제 PDF 시) |
| `FileNotFoundError: ...\sales.db` | week05 DB 없음 | Claude에게 "week05-hands-on/data/create_db.py 실행해서 DB 만들어줘" |
| `FileNotFoundError` + 한글 경로 | Windows 경로 인코딩 | 영문 폴더로 이동 또는 절대경로 사용 |
| `PermissionError: ... file is being used` | 결과 엑셀이 이미 열려있음 | 엑셀 창 닫고 재실행 |
| `UnicodeDecodeError: 'utf-8' codec can't decode` | 파일 인코딩 다름 (흔히 `cp949`) | Claude에게 "`encoding='cp949'`로 열어서 다시 해줘" |
| Claude가 같은 에러 3번째 반복 | 프롬프트가 모호함 | CLAUDE.md 해당 섹션을 구체적으로 다시 쓰고 재요청 |
| 결과 엑셀이 비어있음 | 데이터 필터링 과다 | Claude에게 "원본 행 개수와 결과 행 개수를 비교하고 왜 줄었는지 알려줘" |
| 결과 숫자가 원본과 다름 | 반올림·NULL 처리·통화 혼재 | 검증체크리스트로 샘플 1~2건 수기 대조 |
| Claude 응답이 너무 오래 걸림 (30초+) | 복잡한 요청 | 스코프를 쪼개서 단계별 요청 |

---

## 전체 폴더 구조

```
week07-hands-on/
├── README.md                      ← 지금 이 문서
├── CLAUDE.md                      ← 7주차 공통 규칙 (강사 데모 자동 적용)
├── 수강생과제_CLAUDE_템플릿.md    ← 워크숍에서 본인 업무용으로 복사·채움
├── 막힘카드.md                    ← 수강생 구조용 치트
├── 검증체크리스트.md              ← 결과물 신뢰도 검증
├── 강사용_순회체크.md             ← 강사 워크숍 진단 카드
├── 슬라이드_구성안.md             ← pptx 제작용 18장 아웃라인
├── 강사_리허설가이드.md           ← 수업 전 드라이런 (80~90분)
├── exercises/                     ← 수강생 단계별 가이드
│   ├── step0-showcase-intro.md    ← 쇼케이스 관찰 포인트
│   ├── step1-bring-your-work.md   ← 본인 업무 워크숍
│   └── step2-verify-and-iterate.md ← 심화 검증
├── practice_cases/                ← 본인 업무 없는 분용 대체 실습
│   ├── README.md
│   ├── case1_경비집계.md
│   ├── case2_회의록추출.md
│   └── case3_이메일일괄.md
└── demos/                         ← 강사 쇼케이스 폴백 정답
    ├── README.md
    ├── demo1_compare_excel.py
    ├── demo2_pdf_extract.py
    ├── demo3_natural_query.py
    ├── demo4_format_report.py
    ├── demo5_data_check.py
    ├── demo6_template_fill.py
    └── output/                    ← 모든 생성물
```

---

## 8주차 예고

오늘 만든 **본인 업무 자동화의 완성본**이 8주차 최종 결과물입니다.
미완성도 괜찮습니다. 오늘 가장 중요한 것은:

1. **만든 것** (결과물 엑셀/스크립트)
2. **검증한 방법** (체크리스트 5개 어떻게 돌렸나)
3. **Claude가 틀렸던 에피소드** (어떻게 고쳐 말했나 — 이게 진짜 스킬)

이 세 가지를 8주차에 발표하세요. 완성도보다 **"Claude와 어떻게 대화했는가"**가 평가 포인트.

### 다음 주로 가져갈 확장 아이디어
수업 끝나고 **한 주 동안** 본인 자동화를 완성해올 때 시도할 만한 것:

- **주기 실행 붙이기** — 오늘 만든 스크립트를 week06에서 배운 Windows 작업 스케줄러로 등록 ([week06-hands-on/register_task.ps1](../week06-hands-on/register_task.ps1) 참고)
- **결과 자동 공유** — 생성된 엑셀을 특정 폴더로 이동 / 이메일 첨부 / Teams 공유
- **실패 알림** — 스크립트 실패 시 바탕화면 플래그 파일(week06 패턴) 또는 카톡/메일 알림
- **여러 단계 연결** — 오늘은 한 단계만 했지만, 본인 업무의 2~3단계를 한 번에 연결하는 파이프라인

### 수업 후 혼자 복습
- 각 데모의 폴백 스크립트 직접 실행: `py demos/demo1_compare_excel.py` 등 → 코드와 결과 비교
- 막혔던 프롬프트를 혼자 다시 시도 — 다른 방식으로 말해보기
- [exercises/step2-verify-and-iterate.md](exercises/step2-verify-and-iterate.md) 심화 검증 혼자 실습
