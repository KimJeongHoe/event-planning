#!/usr/bin/env python3
"""막힌 사이트 통합 목록: src_cache/status.tsv + raw/*_log.md 의 응답코드 언급 → reports/막힌사이트.tsv"""
import re,glob,os,collections
BASE=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
hosts=collections.defaultdict(lambda: {"codes":set(),"n":0,"src":set()})
for l in open(f"{BASE}/src_cache/status.tsv",encoding="utf-8"):
    p=l.rstrip("\n").split("\t")
    if len(p)<2: continue
    m=re.match(r"CODE (\d+)",p[1]); c=m.group(1) if m else "000"
    if c!="200":
        h=re.sub(r"^https?://","",p[0]).split("/")[0]; hosts[h]["codes"].add(c); hosts[h]["n"]+=1; hosts[h]["src"].add("기존출처 일괄받기")
for fp in glob.glob(f"{BASE}/raw/*_log.md"):
    t=open(fp,encoding="utf-8",errors="ignore").read()
    for line in t.splitlines():
        for m in re.finditer(r"([a-z0-9][a-z0-9.-]+\.(?:com|kr|net|org|jp|co\.uk|uk|gov|af\.mil|io|in|ca|tv|nz))\S*[^\n]{0,40}?\b(000|403|404|406|410|429|302|400|5\d\d)\b",line):
            h=m.group(1); hosts[h]["codes"].add(m.group(2)); hosts[h]["n"]+=1; hosts[h]["src"].add(os.path.basename(fp))
rows=sorted(hosts.items(),key=lambda x:-x[1]["n"])
with open(f"{BASE}/reports/막힌사이트.tsv","w",encoding="utf-8") as w:
    w.write("호스트\t응답코드\t건수\t어디서\n")
    for h,v in rows: w.write(f"{h}\t{','.join(sorted(v['codes']))}\t{v['n']}\t{', '.join(sorted(v['src']))}\n")
print(len(rows))
