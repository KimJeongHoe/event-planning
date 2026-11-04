#!/usr/bin/env python3
"""위험 칸 결과 반영: 현재 빈 칸만 채운다(이미 채워진 칸은 건너뜀). 사용: apply_risk.py <결과파일...>"""
import json,sys,os,subprocess,tempfile
BASE=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
F={"legal_risk","business_risk","ops_risk","reputation_risk"}
cur={json.loads(l)["orig_id"]:json.loads(l) for l in open(f"{BASE}/merged/사례DB.jsonl",encoding="utf-8")}
ed=[];skip=0
for fp in sys.argv[1:]:
    for l in open(fp,encoding="utf-8"):
        if not l.strip(): continue
        x=json.loads(l); c=x["case"]
        for e in x.get("edits",[]):
            f=e.get("field")
            if f not in F or not str(e.get("after","")).strip(): skip+=1; continue
            if c in cur and str(cur[c].get(f,"")).strip(): skip+=1; continue
            r="위험 칸 보강(회차4)"+(" [확인 조항: "+e["laws_checked"]+"]" if e.get("laws_checked") else "")
            ed.append({"case":c,"field":f,"after":e["after"],"reason":r})
t=tempfile.NamedTemporaryFile("w",suffix=".json",delete=False,encoding="utf-8"); json.dump(ed,t,ensure_ascii=False); t.close()
print(f"채움 {len(ed)}, 건너뜀 {skip}")
subprocess.run([sys.executable,"-I",f"{BASE}/scripts/edit_raw.py",t.name])
