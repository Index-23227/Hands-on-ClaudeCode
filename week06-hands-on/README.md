# Week 06 — 매달 반복되는 일을 한 방에: 자동화 파이프라인

> week04에서 엑셀로 정리하고, week05에서 DB·웹 대시보드로 올렸던 걸
> **매달 자동으로 돌아가는 하나의 파이프라인**으로 완성합니다.
> 여러분은 코드를 쓰지 않습니다. CLAUDE.md에 요구사항이 적혀있고, 자연어로 Claude에게 지시합니다.

## 오늘 만들 것

```
매일 오전 11:30
  ↓
[자동] 한국수출입은행에서 오늘 환율 받아오기
  ↓
[자동] 법인 엑셀 파일들을 DB에 반영
  ↓
[자동] 실행 로그 기록
  ↓
(여러분의 week05 대시보드가 알아서 최신 데이터로 갱신됨)
```

## 사전 준비

코드 실행은 Claude에게 시킵니다. 터미널을 직접 쓰지 않아도 됩니다.

**Claude에게 이렇게 말하세요:**

> "week06 실습 준비해줘. 필요한 라이브러리를 설치하고, week05 DB가 없으면 먼저 만들어줘."

Claude가 알아서 다음을 수행합니다:
- `openpyxl` (엑셀 읽기), `requests` (API 호출) 설치 (이미 있으면 건너뜀)
- `../week05-hands-on/data/sales.db` 존재 확인, 없으면 `week05-hands-on/data/create_db.py` 실행해 생성
- `data/incoming/`에 법인 엑셀 8개가 있는지 확인

## 환율 API 키 설정

한국수출입은행 환율 API는 **인증키(authkey)**가 필요합니다. 강사가 공용 키를 나눠드립니다.

1. 강사가 공유한 키를 받는다
2. `.env.example` 파일을 복사해서 `.env`로 이름을 바꾼다
3. `.env` 안의 `KOREAEXIM_AUTHKEY=` 뒤에 키를 붙여넣는다

**Claude에게 시키면 더 쉬워요:**

> "`.env.example`을 `.env`로 복사해줘. 키는 `여기_강사_키` 로 설정해줘."

> 강의가 끝난 뒤 본인 키를 직접 발급받고 싶으면 `https://www.koreaexim.go.kr/` → 공개API 메뉴에서 무료로 신청할 수 있습니다 (보통 영업일 1일 이내 승인).

## 실습 순서

| Step | 내용 | 시간 | 배우는 것 |
|------|------|------|----------|
| **Step 0** | [파이프라인 개념](exercises/step0-pipeline-concept.md) | 15분 | 왜 자동화가 필요한지 + 오늘의 전체 그림 |
| **Step 1** | [Excel → DB 자동 반영](exercises/step1-excel-to-db.md) | 25분 | **멱등성** — 같은 파일 두 번 넣어도 중복되지 않음 |
| ☕ | 쉬는 시간 | 10분 | |
| **Step 2** | [환율 API 자동 갱신](exercises/step2-exchange-api.md) | 25분 | **외부 API** — 우리 바깥 세상과 대화하기 |
| **Step 3** | [파이프라인 묶기 + 로그](exercises/step3-orchestrate.md) | 20분 | **여러 스크립트를 하나로** + 실행 기록 |
| ☕ | 쉬는 시간 | 10분 | |
| **Step 4** | [Windows 작업 스케줄러](exercises/step4-schedule.md) | 20분 | **주기 실행** — 사람이 버튼 안 눌러도 돌아감 |
| **Step 5** | [모니터링](exercises/step5-monitoring.md) | 15분 | **실패 알림** — 망가지면 눈에 보이게 |
| **정리** | 오늘 배운 것 + 다음 과제 | 10분 | "내 업무 중 하나를 자동화해 오세요" |

## 핵심 파일

| 파일 | 용도 | 누가 만드나 |
|------|------|-------------|
| `CLAUDE.md` | 하네스 — API 스펙, 멱등성 규칙, 통화 매핑 등 전부 | **이미 준비돼 있음** |
| `data/incoming/법인_*.xlsx` | 매월 받는 엑셀 8개 (8법인 x 6개월) | week04 것을 복사해둠 |
| `import_sales.py` | 엑셀 → DB | **Claude가 Step 1에서 생성** |
| `fetch_rates.py` | 환율 API → DB | **Claude가 Step 2에서 생성** |
| `run_pipeline.py` | 전체 파이프라인 | **Claude가 Step 3에서 생성** |
| `logs/YYYYMMDD.log` | 실행 로그 | 파이프라인이 자동 생성 |

## 자주 나는 에러

| 에러 | 원인 | 해결 |
|------|------|------|
| `No module named 'openpyxl'` | 라이브러리 미설치 | Claude에게 "openpyxl 설치해줘" |
| `No module named 'requests'` | 라이브러리 미설치 | Claude에게 "requests 설치해줘" |
| `KOREAEXIM_AUTHKEY 환경변수가 없음` | `.env` 파일 없음 | 위 "환율 API 키 설정" 참고 |
| `unable to open database file` | week05 DB 없음 | Claude에게 "week05 DB 만들어줘" |
| `connection refused` / API 타임아웃 | 네트워크 문제 | 잠시 후 재시도 |
| 환율이 비어있음 | 주말·공휴일 또는 오전 11시 이전 | **에러 아님** — 파이프라인이 직전 영업일 환율을 재사용함 |

**에러 메시지를 그대로 Claude에게 붙여넣으면 고쳐줍니다.**
