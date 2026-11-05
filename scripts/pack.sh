#!/bin/bash
# 이관용 묶음 만들기: merge 후 event_db 전체(캐시·작업 묶음 제외)를 zip으로. 사용: pack.sh <출력폴더>
set -e
cd "$(dirname "$0")/.."
python3 -I scripts/merge.py > /dev/null
python3 -I scripts/similar.py > /dev/null   # 유사 사례 묶음 다시 계산(새 사례 포함)
python3 -I scripts/merge.py > /dev/null
python3 -I scripts/export_tools.py merged/다른도구용 > /dev/null   # QR오더·디자인메이커용 CSV
python3 -I scripts/export_off9.py > /dev/null   # 판 9: 꺼 둔 기능 자료(배달 실수령·개업 순서표 도구용)
python3 -I scripts/pending.py > /dev/null   # 공식 판단 대기 목록
python3 -I scripts/col_doc.py > /dev/null   # 도구 CSV 칸 설명서
python3 -I scripts/checks.py > /dev/null   # 시행일·문구 은행 자동 검사(통계.md 맨 앞 경고)
python3 -I scripts/selftest_check_plan.py > /dev/null || { echo '생성 결과 검사 시험이 어긋남 — 묶음을 만들지 않음'; exit 1; }   # 고장 사본으로 검사가 실제로 잡는지 확인
OUT=${1:-..}; D=$(TZ=Asia/Seoul date +%Y%m%d_%H%M)  # 한국 기준
R=$(basename "$PWD"); cd ..; zip -qr "$OUT/event_db_이관_$D.zip" "$R" -x "*/src_cache/*" "*/verify_packets/*" "*.tmp" "*/.git/*"
cp $R/merged/사례DB.csv "$OUT/사례DB_$D.csv"; cp $R/merged/FAQ.csv "$OUT/FAQ_$D.csv"
cp $R/merged/다른도구용/QR오더용_사례.csv "$OUT/QR오더용_사례_$D.csv"; cp $R/merged/다른도구용/디자인메이커_공지물용_사례.csv "$OUT/디자인메이커_공지물용_사례_$D.csv"
for f in 공지문_문구은행 소상공인_확인표 시행일_점검목록 공식판단_대기목록 테이블오더_계약_점검표 FAQ_표시용 칸_설명; do cp "$R/merged/다른도구용/$f.csv" "$OUT/${f}_$D.csv"; done
ls -la "$OUT" | tail -4
