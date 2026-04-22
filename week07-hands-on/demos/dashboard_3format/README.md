# 데모 D — 같은 데이터, 3가지 출력 (PPT · HTML · React/JSX)

> **수강생이 느낄 것**: "PPT만 되는 줄 알았는데 HTML도, React도. 내 규칙 한 번만 쓰면 출력은 자유네"
> **핵심 메시지**: CLAUDE.md에 요구사항(서식·색·정렬)을 한 번 써두면, **같은 데이터를 여러 포맷**으로 자유자재 변환 가능
> **시연 시간**: 15~17분

---

## 시연 흐름 (3단계, 점진적 확장)

### 사전 — 데이터 확인
`data/overseas_sales.xlsx` 존재 확인. 없으면:
```bash
py week07-hands-on/prep/make_overseas_sales.py
```

---

### Step 1 — PPT 생성 (5~6분)

```
week07-hands-on/demos/dashboard_3format/data/overseas_sales.xlsx를 읽어서
40개 해외법인 2026년 상반기 매출 보고서를 PPT로 만들어줘.

슬라이드 1 — 전체 요약
  - 제목: "해외법인 매출 현황 (2026년 상반기)"
  - KPI 3개 (총매출/총원가/총영업이익) — KRW 원화 환산
  - 지역별 매출 바 차트 (Americas/APAC/EMEA/Oceania)

슬라이드 2 — 상위 10개 법인
  - 테이블: 법인명/국가/매출(원화)/영업이익률/담당자
  - 영업이익률 20% 이상은 빨간색 강조

서식 규칙:
  - 제목·헤더: 짙은 남색 (#1F4E78), 볼드
  - 16:9 와이드 슬라이드
  - 숫자는 "조원/억원" 표기 (예: 258.9조원)
  - 환율: data/overseas_sales.xlsx의 "환율" 시트 사용 (통화별 KRW)

라이브러리: python-pptx
저장: week07-hands-on/demos/dashboard_3format/output/매출보고서.pptx
```

### Step 2 — HTML 대시보드 변환 (4~5분)

```
같은 데이터로 HTML 대시보드도 만들어줘.
- Chart.js CDN 사용 (설치 없이 브라우저만 있으면 되게)
- 지역별 매출 차트 (Step 1과 동일 로직)
- 법인별 매출 테이블 (전체 40개)
- 추가 기능: 상단에 지역 드롭다운 필터 (선택 시 테이블 실시간 변화)
- 영업이익률 20% 이상은 빨간 굵은 글씨

단일 HTML 파일로 자체완결.
저장: output/dashboard.html
```

### Step 3 — React/JSX 변환 (5~6분)

```
이걸 React 컴포넌트로도 변환해줘.

출력 2개:
① output/dashboard_react.html
   - React + Babel을 CDN으로 포함 (빌드 도구 없이 브라우저 즉시 실행)
   - Step 2와 같은 인터랙션, useState로 상태 관리

② output/DashBoard.jsx
   - 순수 컴포넌트 (import/export 포함)
   - 사내 React 웹앱 프로젝트에 **복붙해서 바로 쓸 수 있는** 형태
   - 데이터는 상수로 inline (실 서비스에서는 API로 바꾸면 됨)
```

---

## 기대 결과

4개 파일 생성:
- `output/매출보고서.pptx` (Slide 2장)
- `output/dashboard.html` (Chart.js 대시보드)
- `output/dashboard_react.html` (React 단독 실행)
- `output/DashBoard.jsx` (이식용 컴포넌트)

### 검증
- PPT 파일 → 파워포인트로 열어서 차트·테이블 확인
- HTML 파일 → 브라우저로 열기 → 필터 동작 확인
- React HTML → 브라우저로 열기 → 동일 동작 확인
- JSX 파일 → 텍스트 에디터로 열어서 코드만 보여주기 ("이걸 개발팀에 줘도 됨")

---

## 수강생에게 강조할 포인트

### 1. **"같은 데이터, 다른 매체"** — 방법론 핵심
- Step 1 끝나고 Step 2 시작 때: "데이터를 다시 설명할 필요 없었죠?"
- Step 3 끝나고: "React 코드 직접 쓴 적 없으시죠? 이해도 못 하셔도 됩니다"

### 2. **육아름 차장님 업무와 직접 연결**
- 지금 Streamlit 대시보드 만드신 것과 같은 구조
- 같은 데이터를 **PPT(경영회의)·HTML(내부 포털)·React(Netra 이식)** 세 매체로
- 목적에 맞게 골라 쓰면 됨

### 3. **CLAUDE.md의 힘**
- 서식 규칙(헤더 남색, 영업이익률 20% 빨강)을 CLAUDE.md에 써두면
- PPT 차트도, HTML 테이블도, React 컴포넌트도 **전부 자동으로 같은 규칙 적용**
- 규칙이 한 번 정립되면 출력은 값싸게 다양화 가능

---

## 방법론 4가지 (시연 중 명시)

### ① 스펙을 먼저 글로
> "뭘 만들어줘"로 시작하지 말고 **"무엇을 / 어떤 모양으로 / 어느 경로에"** 다 쓰고 시작.
> Step 1 프롬프트가 구체적이라서 Step 2·3이 쉬워짐.

### ② 반복 수정 루프
> "처음부터 다시 해줘" 금지. **"거의 맞는데 X만 바꿔줘"** 패턴.
> 예: "차트 색깔만 남색으로 바꿔줘", "테이블에 담당자 컬럼 추가"

### ③ 재사용 가능한 템플릿
> 서식 규칙을 CLAUDE.md에 한 번 쓰면 PPT·HTML·JSX에 공통 적용.
> 이 데모의 핵심 메시지.

### ④ 검증 5단계 필수
> 결과가 "그럴듯" 해도 반드시 검증:
> - PPT: 차트 숫자와 원본 xlsx 합계 일치?
> - HTML: 필터 동작하나?
> - 법인 수 40개 맞나? (누락 없나)
> - 영업이익률 계산이 수기 계산과 일치?

---

## 확장 아이디어

### 차트 종류 다양화
```
지역별 차트를 파이 차트로도 바꿔보고, 월별 추이는 꺾은선으로도 그려줘.
```

### 인터랙티브 강화
```
테이블에서 법인을 클릭하면 해당 법인의 월별 추이 차트가 뜨도록.
```

### 필터 추가
```
통화별 필터, 영업이익률 최소값 슬라이더도 추가해줘.
```

---

## 폴백 정답

3종 전부 한 번에 생성:
```bash
py week07-hands-on/demos/dashboard_3format/fallback_build_all.py
```

→ 4개 파일 일괄 생성 (PPT 1 + HTML 1 + React HTML 1 + JSX 1)

---

## 사전 준비 (강사)

### 1. python-pptx 설치
```bash
pip install python-pptx
```

### 2. 데이터 생성
```bash
py week07-hands-on/prep/make_overseas_sales.py
```

### 3. 리허설
```bash
py week07-hands-on/demos/dashboard_3format/fallback_build_all.py
```
→ 4개 파일 생성 확인 + 각각 열어서 문제없는지.

---

## 폴더 구조

```
dashboard_3format/
├── README.md                    ← 이 문서
├── fallback_build_all.py        ← 3종 일괄 생성 폴백
├── data/
│   └── overseas_sales.xlsx      ← prep 스크립트가 생성한 40법인 데이터
└── output/                      ← 생성물
    ├── 매출보고서.pptx          ← Step 1
    ├── dashboard.html           ← Step 2
    ├── dashboard_react.html     ← Step 3 (단독 실행)
    └── DashBoard.jsx            ← Step 3 (이식용)
```
