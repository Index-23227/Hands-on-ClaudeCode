# 정답 스크립트

> 실습에서 AI가 생성해야 할 코드의 참고 정답입니다.
> 수강생에게 직접 보여주지 마세요. AI가 만들어주지 못할 때 강사용으로 사용합니다.

| 파일 | 대응 Step | 내용 |
|------|-----------|------|
| `step1_answer.py` | Step 1 | DB 조회 + 터미널 출력 |
| `step2_app_answer.py` | Step 2 | Flask 앱 (메인 + 상세) |
| `templates/index.html` | Step 2 | 메인 페이지 템플릿 |
| `templates/detail.html` | Step 2 | 상세 페이지 템플릿 |

## 사용법 (강사용)

코드 실행은 Claude가 담당합니다. 강사는 Claude에게 다음과 같이 지시하세요.

- **Step 1 확인**: "`answers/step1_answer.py`를 실행해서 결과를 보여줘."
- **Step 2 확인**: "`answers/step2_app_answer.py`를 띄우고 `/` 와 `/corp/US01` 응답을 확인해줘."
- **수강생에게 보여주기 전 검증용**: "`answers/`의 정답이 그대로 동작하는지 테스트해줘."

정답 파일은 `answers/` 폴더 안에서 **자기완결적으로** 동작합니다:
- `step2_app_answer.py`는 `../data/sales.db`를 참조하고,
- Flask는 `answers/templates/index.html`·`detail.html`을 자동으로 찾습니다.

수강생이 루트에 만들 `app.py` / `templates/`와 경로가 분리되어 있어 서로 충돌하지 않습니다.
