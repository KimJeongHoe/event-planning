#!/bin/bash
# 사용: fetch_all.sh <url목록> <저장폴더>  — 각 URL 원문 텍스트 저장 + 상태표(status.tsv)
L=$1; D=$2; mkdir -p $D
cat $L | xargs -P 8 -I{} sh -c 'out=$(python3 -I '"$(dirname $0)"'/fetchtext.py "{}" 0 '"$D"' | head -2 | tr "\n" " "); printf "%s\t%s\n" "{}" "$out"' >> $D/status.tsv
