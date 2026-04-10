"""
Step 3 정답: fetch_rates + import_sales를 함수 import로 묶는 오케스트레이터.
실행 로그를 logs/YYYYMMDD.log 에 append.
실패 시 flag 파일 + 바탕화면 알림 생성 (모니터링).
"""
import os
import sys
import time
import pathlib
import datetime as dt

HERE = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.normpath(os.path.join(HERE, "..", "logs"))
DATA_DIR = os.path.normpath(os.path.join(HERE, "..", "data"))

# 같은 answers 폴더의 정답 모듈을 import
sys.path.insert(0, HERE)
import fetch_rates_answer  # noqa: E402
import import_sales_answer  # noqa: E402


def log_line(fp, message: str) -> None:
    """파일과 stdout 양쪽에 한 줄 기록."""
    fp.write(message + "\n")
    fp.flush()
    print(message)


def main() -> int:
    """파이프라인 실행. 전부 성공이면 0, 한 단계라도 실패하면 1 반환."""
    os.makedirs(LOG_DIR, exist_ok=True)
    today = dt.date.today()
    log_path = os.path.join(LOG_DIR, today.strftime("%Y%m%d") + ".log")

    overall_start = time.time()
    ok = True

    with open(log_path, "a", encoding="utf-8") as fp:
        log_line(fp, f"===== {dt.datetime.now():%Y-%m-%d %H:%M:%S} 파이프라인 시작 =====")

        # Step A: 환율 갱신
        log_line(fp, "[환율 갱신] 시작")
        step_start = time.time()
        try:
            result = fetch_rates_answer.main()
            rates = result.get("rates", {})
            rates_summary = "  ".join(f"{k}={v:.4f}" for k, v in rates.items())
            log_line(fp, f"[환율 갱신] {rates_summary}")
            if result.get("fallback"):
                for note in result["fallback"]:
                    log_line(fp, f"[환율 갱신] 폴백: {note}")
            log_line(fp, f"[환율 갱신] 완료 ({time.time() - step_start:.1f}초)")
        except Exception as e:
            log_line(fp, f"[환율 갱신] 실패: {type(e).__name__}: {e}")
            log_line(fp, f"[환율 갱신] 소요: {time.time() - step_start:.1f}초")
            ok = False

        # Step B: 매출 import (환율 실패해도 진행할지는 정책 결정; 여기선 진행)
        log_line(fp, "[매출 import] 시작")
        step_start = time.time()
        try:
            result = import_sales_answer.main()
            log_line(
                fp,
                f"[매출 import] {result['files']}개 파일 처리: "
                f"UPSERT {result['processed']}건, SKIP {result['skipped']}건 "
                f"(monthly_sales 총 {result['total_rows']}행)",
            )
            log_line(fp, f"[매출 import] 완료 ({time.time() - step_start:.1f}초)")
        except Exception as e:
            log_line(fp, f"[매출 import] 실패: {type(e).__name__}: {e}")
            log_line(fp, f"[매출 import] 소요: {time.time() - step_start:.1f}초")
            ok = False

        total = time.time() - overall_start
        status = "완료" if ok else "실패"
        log_line(
            fp,
            f"===== {dt.datetime.now():%Y-%m-%d %H:%M:%S} 파이프라인 {status} ({total:.1f}초) =====",
        )

        # ── 모니터링: 실패 시 flag + 바탕화면 알림 ──
        flag_path = os.path.join(DATA_DIR, f"failure_{today.strftime('%Y%m%d')}.flag")
        if not ok:
            with open(flag_path, "w", encoding="utf-8") as ff:
                ff.write(f"파이프라인 실패: {dt.datetime.now():%Y-%m-%d %H:%M:%S}\n")
                ff.write(f"로그: {log_path}\n")
            log_line(fp, f"[알림] 실패 flag 생성: {flag_path}")

            desktop = pathlib.Path.home() / "Desktop"
            if desktop.exists():
                summary = desktop / f"파이프라인_실패_{today.strftime('%Y%m%d')}.txt"
                with open(summary, "w", encoding="utf-8") as sf:
                    sf.write(f"파이프라인 실패 알림\n")
                    sf.write(f"날짜: {today}\n")
                    sf.write(f"로그 확인: {log_path}\n")
                log_line(fp, f"[알림] 바탕화면 요약: {summary}")
        else:
            if os.path.exists(flag_path):
                os.remove(flag_path)
                log_line(fp, f"[알림] 실패 flag 제거 (복구 성공): {flag_path}")

    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
