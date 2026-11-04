#!/usr/bin/env python3
"""빈 칸만 채우기. 사용: apply_fill.py <칸,콤마> <이유> <결과파일...>"""
import json,sys,os,subprocess,tempfile
BASE=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
F=set(sys.argv[1].split(",")); why=sys.argv[2]
cur={json.loads(l)["orig_id"]:json.loads(l) for l in open(f"{BASE}/merged/사례DB.jsonl",encoding="utf-8")}
ed=[];skip=0;flags=[]
for fp in sys.argv[3:]:
    for l in open(fp,encoding="utf-8"):
        if not l.strip(): continue
        x=json.loads(l); c=x["case"]
        if x.get("flag"): flags.append((c,x["flag"]))
        for e in x.get("edits",[]):
            f=e.get("field")
            if f not in F or not str(e.get("after","")).strip() or (c in cur and str(cur[c].get(f,"")).strip()): skip+=1; continue
            ed.append({"case":c,"field":f,"after":e["after"],"reason":why})
t=tempfile.NamedTemporaryFile("w",suffix=".json",delete=False,encoding="utf-8"); json.dump(ed,t,ensure_ascii=False); t.close()
print(f"채움 {len(ed)}, 건너뜀 {skip}, flag {len(flags)}")
for f in flags: print("  FLAG",f)
subprocess.run([sys.executable,"-I",f"{BASE}/scripts/edit_raw.py",t.name])
