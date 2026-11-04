#!/usr/bin/env python3
"""verify_results/*.jsonl 를 raw 에 반영(edit_raw.py 경유). 사용: apply_verify.py <결과파일...>"""
import json, sys, os, subprocess, tempfile
BASE=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ALLOW={"name","summary","condition","benefit","staging","duration","limit","known_result","source_dates","scale","country","era","sub_industry","notes"}
edits=[]; n=0; st={}
for fp in sys.argv[1:]:
    for l in open(fp,encoding="utf-8"):
        if not l.strip(): continue
        x=json.loads(l); c=x["case"]; n+=1
        vs=x.get("verify_status","검색요약만"); vs = vs if vs in ("확인함","막힘","원문 불일치") else ("막힘" if vs=="검색요약만" else "막힘")
        st[vs]=st.get(vs,0)+1
        edits.append({"case":c,"field":"verify_status","after":vs})
        edits.append({"case":c,"field":"verify_note","after":x.get("verify_note","")})
        for e in x.get("edits",[]) or []:
            if e.get("field") in ALLOW and "after" in e:
                edits.append({"case":c,"field":e["field"],"after":e["after"],"reason":"원문 확인 후 정정: "+e.get("reason",""),"source_url":e.get("source_url","")})
tmp=tempfile.NamedTemporaryFile("w",suffix=".json",delete=False,encoding="utf-8"); json.dump(edits,tmp,ensure_ascii=False); tmp.close()
print("사례",n,st)
subprocess.run([sys.executable,"-I",f"{BASE}/scripts/edit_raw.py",tmp.name])
