"""
영수증 샘플 PNG 8장 생성 (A 데모: 멀티모달 OCR 시연용)

한국 재경팀 경비 처리 맥락의 다양한 영수증(카페·편의점·주유소·사무용품·식당·택시·KTX·호텔)을
사진 찍은 것 같은 느낌으로 8장 생성한다.

시연 중 Claude가 이 이미지들을 직접 읽어서(멀티모달 비전)
항목/금액/결제방식 추출 → 경비 엑셀 자동 생성하는 흐름을 보여준다.

실행:
  py week07-hands-on/prep/make_receipt_samples.py

출력:
  week07-hands-on/demos/receipt_ocr/samples/*.png (8개)
"""

from __future__ import annotations

import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


HERE = Path(__file__).parent
OUT_DIR = HERE.parent / "demos" / "receipt_ocr" / "samples"
OUT_DIR.mkdir(parents=True, exist_ok=True)

KOR_FONT = "C:/Windows/Fonts/malgun.ttf"
KOR_FONT_BOLD = "C:/Windows/Fonts/malgunbd.ttf"


RECEIPTS = [
    {
        "filename": "01_스타벅스.png",
        "store": "스타벅스 강남역점",
        "address": "서울 강남구 테헤란로 152",
        "biz_no": "220-81-62517",
        "tel": "02-3461-5823",
        "datetime": "2026-03-05 14:23",
        "receipt_no": "20260305-00234",
        "items": [
            ("아메리카노 Tall", 2, 4500),
            ("카페라떼 Tall", 1, 5000),
            ("블루베리 머핀", 1, 4200),
        ],
        "payment": "법인카드",
        "card": "신한 BC **-**-**-56",
        "approval": "49283712",
    },
    {
        "filename": "02_GS25편의점.png",
        "store": "GS25 역삼중앙점",
        "address": "서울 강남구 역삼동 748-9",
        "biz_no": "135-81-22341",
        "tel": "02-568-1125",
        "datetime": "2026-03-08 19:47",
        "receipt_no": "GS-20260308-8821",
        "items": [
            ("삼각김밥 전주비빔", 2, 1500),
            ("박카스D", 3, 900),
            ("오리온 초코파이", 1, 4800),
            ("생수 2L", 2, 1200),
        ],
        "payment": "개인카드",
        "card": "삼성카드 **-**-**-19",
        "approval": "71823455",
    },
    {
        "filename": "03_GS칼텍스주유소.png",
        "store": "GS칼텍스 양재주유소",
        "address": "서울 서초구 양재대로 101",
        "biz_no": "214-86-55918",
        "tel": "02-571-8900",
        "datetime": "2026-03-12 08:15",
        "receipt_no": "GSCX-20260312-0412",
        "items": [
            ("휘발유 (45.2L)", 1, 68900),
        ],
        "payment": "법인카드",
        "card": "하나 BC **-**-**-82",
        "approval": "30118765",
        "extra": {"차량번호": "12가 3456", "주행거리": "74,521 km"},
    },
    {
        "filename": "04_오피스디포.png",
        "store": "오피스디포 여의도점",
        "address": "서울 영등포구 여의대로 108",
        "biz_no": "106-81-44729",
        "tel": "02-761-3388",
        "datetime": "2026-03-15 11:02",
        "receipt_no": "OD-20260315-1029",
        "items": [
            ("A4 복사용지 2500매", 1, 28000),
            ("모나미 볼펜 검정 12개입", 2, 9600),
            ("포스트잇 노랑 대용량", 3, 15000),
            ("바인더 클립 中 100개", 1, 8500),
            ("프린터 토너 HP 26A", 1, 89000),
        ],
        "payment": "법인카드",
        "card": "신한 BC **-**-**-56",
        "approval": "88291034",
    },
    {
        "filename": "05_본죽.png",
        "store": "본죽 여의도점",
        "address": "서울 영등포구 국회대로 76길 18",
        "biz_no": "129-86-71824",
        "tel": "02-785-9911",
        "datetime": "2026-03-18 12:38",
        "receipt_no": "BJ-20260318-0237",
        "items": [
            ("전복죽", 2, 14000),
            ("야채죽", 1, 9000),
            ("동치미", 1, 3000),
        ],
        "payment": "개인카드",
        "card": "국민카드 **-**-**-04",
        "approval": "55412988",
    },
    {
        "filename": "06_택시영수증.png",
        "store": "개인택시 (영업용)",
        "address": "서울 운수 12가 3456",
        "biz_no": "481-80-99231",
        "tel": "",
        "datetime": "2026-03-19 22:41",
        "receipt_no": "TX-20260319-2241",
        "items": [
            ("서울역 → 여의도 KBS별관", 1, 8700),
        ],
        "payment": "법인카드",
        "card": "신한 BC **-**-**-56",
        "approval": "19273841",
        "extra": {"승차시각": "22:18", "하차시각": "22:41", "거리": "7.2km"},
    },
    {
        "filename": "07_KTX승차권.png",
        "store": "코레일 (한국철도공사)",
        "address": "KTX 서울 → 부산",
        "biz_no": "124-82-00126",
        "tel": "1544-7788",
        "datetime": "2026-03-20 06:00",
        "receipt_no": "KTX-20260320-HY112",
        "items": [
            ("서울(06:00) → 부산(08:47) 특실 12호차 3A", 1, 79800),
        ],
        "payment": "법인카드",
        "card": "하나 BC **-**-**-82",
        "approval": "66128309",
        "extra": {"열차번호": "KTX-산천 112", "출장지": "부산지사 방문"},
    },
    {
        "filename": "08_호텔.png",
        "store": "베스트웨스턴 부산 해운대",
        "address": "부산 해운대구 우동 1388",
        "biz_no": "617-81-33271",
        "tel": "051-743-2220",
        "datetime": "2026-03-21 12:00",
        "receipt_no": "BW-20260320-R447",
        "items": [
            ("스탠다드 더블룸 1박", 1, 168000),
            ("조식 뷔페", 1, 28000),
            ("부가세 및 봉사료 포함", 0, 0),
        ],
        "payment": "법인카드",
        "card": "신한 BC **-**-**-56",
        "approval": "90451223",
        "extra": {"체크인": "2026-03-20 15:00", "체크아웃": "2026-03-21 11:30"},
    },
]


def money(amount: int) -> str:
    return f"{amount:,}"


def draw_receipt(receipt: dict, out_path: Path) -> None:
    W, H = 640, 960
    img = Image.new("RGB", (W, H), (252, 250, 245))  # 약간 누런 영수증 종이색
    draw = ImageDraw.Draw(img)

    f_title = ImageFont.truetype(KOR_FONT_BOLD, 28)
    f_sub = ImageFont.truetype(KOR_FONT, 16)
    f_body = ImageFont.truetype(KOR_FONT, 18)
    f_body_bold = ImageFont.truetype(KOR_FONT_BOLD, 18)
    f_total = ImageFont.truetype(KOR_FONT_BOLD, 24)
    f_small = ImageFont.truetype(KOR_FONT, 13)

    margin = 40
    y = 40

    # 매장명 (중앙 정렬)
    title = receipt["store"]
    bbox = draw.textbbox((0, 0), title, font=f_title)
    draw.text(((W - bbox[2]) / 2, y), title, font=f_title, fill=(30, 30, 30))
    y += 42

    # 주소·사업자번호·전화
    for label, key in [("", "address"), ("사업자번호", "biz_no"), ("Tel", "tel")]:
        val = receipt.get(key, "")
        if not val:
            continue
        text = val if not label else f"{label}: {val}"
        bbox = draw.textbbox((0, 0), text, font=f_sub)
        draw.text(((W - bbox[2]) / 2, y), text, font=f_sub, fill=(60, 60, 60))
        y += 22

    # 구분선
    y += 10
    draw.line([(margin, y), (W - margin, y)], fill=(120, 120, 120), width=1)
    y += 15

    # 거래정보
    for label, key in [("거래일시", "datetime"), ("거래번호", "receipt_no")]:
        text = f"{label}: {receipt[key]}"
        draw.text((margin, y), text, font=f_small, fill=(60, 60, 60))
        y += 20

    # extra 정보(차량번호·주행거리 등)
    for k, v in receipt.get("extra", {}).items():
        draw.text((margin, y), f"{k}: {v}", font=f_small, fill=(60, 60, 60))
        y += 20

    y += 10
    draw.line([(margin, y), (W - margin, y)], fill=(120, 120, 120), width=1)
    y += 15

    # 품목 헤더
    draw.text((margin, y), "품목", font=f_body_bold, fill=(30, 30, 30))
    draw.text((W - margin - 200, y), "수량", font=f_body_bold, fill=(30, 30, 30))
    draw.text((W - margin - 110, y), "금액", font=f_body_bold, fill=(30, 30, 30))
    y += 26

    draw.line([(margin, y), (W - margin, y)], fill=(180, 180, 180), width=1)
    y += 10

    # 품목 행들
    total = 0
    for name, qty, price in receipt["items"]:
        if qty == 0:  # 부가세 안내 같은 설명 행
            draw.text((margin, y), f"  * {name}", font=f_small, fill=(120, 120, 120))
            y += 22
            continue
        line_total = qty * price
        total += line_total
        # 품목명 (길면 자르기)
        name_display = name if len(name) < 22 else name[:21] + "…"
        draw.text((margin, y), name_display, font=f_body, fill=(30, 30, 30))
        draw.text((W - margin - 200, y), f"{qty}", font=f_body, fill=(30, 30, 30))
        price_text = money(line_total)
        bbox = draw.textbbox((0, 0), price_text, font=f_body)
        draw.text((W - margin - bbox[2], y), price_text, font=f_body, fill=(30, 30, 30))
        y += 26

    y += 10
    draw.line([(margin, y), (W - margin, y)], fill=(120, 120, 120), width=2)
    y += 18

    # 합계
    supply = int(total / 1.1)  # 공급가액
    vat = total - supply
    for label, value in [("공급가액", supply), ("부가세", vat)]:
        draw.text((margin, y), label, font=f_body, fill=(60, 60, 60))
        text = money(value)
        bbox = draw.textbbox((0, 0), text, font=f_body)
        draw.text((W - margin - bbox[2], y), text, font=f_body, fill=(60, 60, 60))
        y += 24

    y += 6
    draw.text((margin, y), "합계", font=f_total, fill=(20, 20, 20))
    total_text = money(total) + " 원"
    bbox = draw.textbbox((0, 0), total_text, font=f_total)
    draw.text((W - margin - bbox[2], y), total_text, font=f_total, fill=(20, 20, 20))
    y += 36

    draw.line([(margin, y), (W - margin, y)], fill=(120, 120, 120), width=1)
    y += 15

    # 결제 정보
    draw.text((margin, y), f"결제수단: {receipt['payment']}", font=f_body_bold, fill=(30, 30, 30))
    y += 26
    draw.text((margin, y), f"카드번호: {receipt['card']}", font=f_small, fill=(80, 80, 80))
    y += 20
    draw.text((margin, y), f"승인번호: {receipt['approval']}", font=f_small, fill=(80, 80, 80))
    y += 30

    # 하단 감사 멘트
    thank_you = "감사합니다. 안녕히 가십시오."
    bbox = draw.textbbox((0, 0), thank_you, font=f_sub)
    draw.text(((W - bbox[2]) / 2, y), thank_you, font=f_sub, fill=(100, 100, 100))

    # 사진 느낌 — 약간의 회전과 노이즈
    # (너무 과하면 OCR 어려우므로 미묘하게만)
    rotation = random.uniform(-1.2, 1.2)
    img = img.rotate(rotation, resample=Image.BICUBIC, expand=False, fillcolor=(230, 225, 215))

    img.save(out_path, "PNG", optimize=True)


def main() -> None:
    random.seed(20260319)  # 재현 가능한 미묘 회전각

    print(f"[시작] 영수증 샘플 {len(RECEIPTS)}장 생성 → {OUT_DIR}")
    print()

    for receipt in RECEIPTS:
        out_path = OUT_DIR / receipt["filename"]
        draw_receipt(receipt, out_path)
        total = sum(q * p for _, q, p in receipt["items"] if q > 0)
        print(f"  [OK] {receipt['filename']:<30} {receipt['store']:<22} {total:>7,}원 ({receipt['payment']})")

    print()
    print(f"[완료] {len(RECEIPTS)}장 생성됨. A 데모에서 이 이미지들을 Claude에게 직접 붙여 시연.")


if __name__ == "__main__":
    main()
