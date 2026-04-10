# Step 1: Excel → DB 자동 반영 (25분)

> `data/incoming/` 폴더의 법인 엑셀 8개를 자동으로 DB에 넣는 스크립트를 만듭니다.
> **핵심 학습**: 멱등성 — 같은 파일을 두 번 넣어도 DB가 오염되지 않아야 합니다.

---

## 1단계: 어떤 파일을 다룰지 확인

`data/incoming/` 폴더를 열어보세요:

```
data/incoming/
├── 법인_US01_미국.xlsx
├── 법인_JP01_일본.xlsx
├── 법인_CN01_중국.xlsx
├── 법인_DE01_독일.xlsx
├── 법인_VN01_베트남.xlsx
├── 법인_IN01_인도.xlsx
├── 법인_GB01_영국.xlsx
└── 법인_TH01_태국.xlsx
```

이 파일들은 week04에서 봤던 그 엑셀입니다. 컬럼은 `월, 계정과목, 통화, 금액, 비고`. 각 파일에 6개월치(2026-01 ~ 2026-06) 데이터가 들어있습니다.

**"매월 1일 아침에 이 폴더로 새 파일이 복사된다"**고 상상하면 됩니다.

---

## 2단계: AI에게 시켜보기

### Claude에게 입력

```
data/incoming/ 폴더의 법인 엑셀 8개를 읽어서
../week05-hands-on/data/sales.db의 monthly_sales 테이블에 반영하는
import_sales.py를 만들어줘.

중요: 같은 (법인코드, 월) 조합이 이미 DB에 있으면 덮어쓰기로.
두 번 돌려도 행이 중복되지 않아야 해.

파일명에서 법인코드 파싱하는 규칙은 CLAUDE.md에 있어.
```

Claude가 파일을 만들어주면 **실행도 Claude에게 시키세요**:

```
import_sales.py를 실행해서 결과를 보여줘.
```

---

## 3단계: 멱등성 검증 — 두 번 돌려보기

이게 Step 1의 핵심입니다. Claude에게:

```
import_sales.py를 한 번 더 돌려줘.
그리고 monthly_sales의 행 수가 그대로인지 확인해줘.
```

### 기대하는 결과

```
[1회차 실행]
  처리 파일: 8개
  처리 행:  48건 (UPSERT)
  monthly_sales 총 행 수: 48

[2회차 실행]
  처리 파일: 8개
  처리 행:  48건 (UPSERT)
  monthly_sales 총 행 수: 48   ← 그대로!
```

> **핵심은 "총 행 수가 그대로다"**. 같은 엑셀을 두 번 넣어도 `monthly_sales`가 30행으로 부풀지 않습니다.
>
> **왜 INSERT/UPDATE를 따로 안 세나요?** 현업의 UPSERT(`INSERT ... ON CONFLICT DO UPDATE`)는 "있으면 덮어쓰고 없으면 넣는다"를 한 SQL로 끝냅니다. 행마다 SELECT로 존재 여부를 확인하지 않기 때문에 카운트도 따로 안 나옵니다. 그게 정상입니다 — race condition 없고, 빠르고, 코드도 단순합니다.
>
> **이게 멱등성입니다.** 같은 입력으로 여러 번 돌려도 결과는 같음.
> 재경팀에서 "실수로 한 번 더 돌렸는데 괜찮은지" 걱정할 필요가 없어집니다.

---

## 4단계: "새 데이터가 왔다"고 가정하고 시뮬레이션

현실감을 살려봅니다. Claude에게:

```
미국법인의 2026-03 금액을 118000에서 200000으로 바꾸고 싶어.
엑셀을 직접 수정하지 말고, import_sales.py가 동작하는 걸 보여줘.

방법: data/incoming/법인_US01_미국.xlsx의 2026-03 행 금액을 200000으로
수정한 뒤, import_sales.py를 다시 돌려줘.
그리고 DB에 잘 반영됐는지 SELECT로 확인해줘.
```

기대:
- 엑셀의 값이 바뀜
- `import_sales.py` 실행 → UPDATE 1건
- DB SELECT 결과: 미국법인 2026-03 = 200000

**여러분이 체감할 것:**
- "엑셀 하나 고치고 → 스크립트 한 번 → DB 반영"
- 복사-붙여넣기, 수식 수정, 피벗 새로고침 같은 것 없음
- 같은 엑셀을 실수로 10번 돌려도 DB는 멀쩡함

---

## 여기서 잠깐 — UNIQUE 인덱스라는 게 뭐예요?

멱등성을 위해 Claude가 DB에 **UNIQUE 인덱스**라는 걸 추가했을 겁니다.

```sql
CREATE UNIQUE INDEX ux_sales_corp_month
ON monthly_sales(corp_code, month);
```

쉽게 말하면:

> "`corp_code`랑 `month`가 같은 행은 DB에 오직 한 개만 존재할 수 있다."

이 규칙이 있으니까 **"똑같은 건 자동으로 거부되거나 업데이트된다"**가 보장됩니다. DB가 지켜주는 안전장치입니다.

**이것도 Claude가 CLAUDE.md 보고 알아서 넣어줍니다. 여러분이 SQL을 쓰지 않아도 됩니다.**

---

## 에러가 나면?

| 에러 | 원인 | 해결 (Claude에게 붙여넣기) |
|------|------|--------|
| `unable to open database file` | week05 DB 없음 | "week05의 create_db.py 돌려서 DB 만들어줘" |
| `No module named 'openpyxl'` | 라이브러리 미설치 | "openpyxl 설치해줘" |
| `UNIQUE constraint failed` | 인덱스 없이 INSERT 중 | "monthly_sales에 (corp_code, month) UNIQUE 인덱스를 먼저 만들고 INSERT ... ON CONFLICT로 upsert 해줘" |

---

## 여기까지 하면

- `import_sales.py` 파일이 생겼고
- 같은 스크립트를 반복 실행해도 DB가 오염되지 않음을 확인했고
- "매달 엑셀 8개를 사람이 직접 DB에 옮길 필요가 없다"는 걸 체감했습니다

하지만 환율은 여전히 **기존 월말 기준 값**이 박혀있죠. 다음 단계에서 이걸 **매일 자동으로 갱신**합니다.

→ [Step 2: 환율 API 자동 갱신](step2-exchange-api.md)으로 이동
