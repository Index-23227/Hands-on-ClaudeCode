# Week 07 — "이런 것도 됩니다" 데모 쇼케이스

> Claude Code로 재경팀이 할 수 있는 다양한 업무 자동화를 빠르게 시연합니다.
> 각 데모는 5~10분이면 보여줄 수 있습니다.

## 데모 목록

| # | 데모 | 핵심 메시지 | 실행 |
|---|------|-----------|------|
| 1 | **두 엑셀 비교** | 매달 눈으로 비교하던 걸 3초에 | `py demos/demo1_compare_excel.py` |
| 2 | **PDF → 엑셀 추출** | 세금계산서 손으로 옮기던 걸 자동으로 | `py demos/demo2_pdf_extract.py` |
| 3 | **자연어 데이터 분석** | SQL 몰라도 한국어로 질문 가능 | `py demos/demo3_natural_query.py` |
| 4 | **엑셀 서식 자동화** | 보고서 포맷팅 30분 → 자동 | `py demos/demo4_format_report.py` |
| 5 | **데이터 정합성 체크** | 감사 자료 대조를 코드가 | `py demos/demo5_data_check.py` |
| 6 | **보고서 템플릿 채우기** | 매월 같은 양식에 숫자만 바꾸기 | `py demos/demo6_template_fill.py` |

## 실행 방법

```bash
cd week07-hands-on
py demos/demo1_compare_excel.py
```

결과 파일은 `demos/output/` 폴더에 생성됩니다. 엑셀을 열어서 서식/차트/색상을 직접 확인하세요.

## 데모 3은 week05 DB가 필요합니다

`demo3_natural_query.py`와 `demo4_format_report.py`, `demo6_template_fill.py`는 `week05-hands-on/data/sales.db`를 사용합니다. 없으면:

```bash
py week05-hands-on/data/create_db.py
```

## 강사 사용 가이드

- 자투리 시간에 골라서 1~2개씩 시연
- "이건 여러분 업무 중 어떤 것과 비슷한가요?" 질문으로 연결
- 학생이 관심 보이는 데모를 Claude Code로 **라이브 변형**해서 보여주면 효과적
  - 예: "비교 기준을 법인 대신 계정과목으로 바꿔줘"
  - 예: "이 보고서에 차트 추가해줘"
