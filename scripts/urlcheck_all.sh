#!/bin/bash
# 사용: urlcheck_all.sh <URL목록> <출력tsv>
: > "$2"
cat "$1" | xargs -P 10 -I{} timeout 45 python3 -I "$(dirname "$0")/urlcheck.py" "{}" >> "$2" 2>/dev/null
