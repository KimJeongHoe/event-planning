#!/usr/bin/env python3
"""에이전트 결과(한 줄에 {"case":..,"edits":[{field,after,reason?}]...})를 edit_raw.py로 반영.
사용: apply_edits.py <이유 접두어> <허용칸,콤마> <결과파일...>
 - 특수: 줄에 verify_status/verify_note/source_urls/source_dates/ref_exclude 키가 있으면 그것도 반영(허용칸에 있을 때)."""
import json,sys,os,subprocess,tempfile
BASE=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
pre=sys.argv[1]; allow=set(sys.argv[2].split(",")); files=sys.argv[3:]
ed=[];skip=0;n=0
for fp in files:
    for l in open(fp,encoding="utf-8"):
        if not l.strip(): continue
        x=json.loads(l); c=x["case"]; n+=1
        for k in ("verify_status","verify_note","source_urls","source_dates","ref_exclude"):
            if k in x and x[k]!="" and k in allow:
                ed.append({"case":c,"field":k,"after":x[k],"reason":pre,"log":k not in("verify_status","verify_note")})
        for e in x.get("edits",[]) or []:
            if e.get("field") in allow and "after" in e:
                r=pre+(": "+e["reason"] if e.get("reason") else "")+(" [확인 조항: "+e["laws_checked"]+"]" if e.get("laws_checked") else "")
                ed.append({"case":c,"field":e["field"],"after":e["after"],"reason":r,"source_url":e.get("source_url","")})
            else: skip+=1
t=tempfile.NamedTemporaryFile("w",suffix=".json",delete=False,encoding="utf-8"); json.dump(ed,t,ensure_ascii=False); t.close()
print(f"사례 {n}줄, 수정 {len(ed)}, 허용 밖 건너뜀 {skip}")
subprocess.run([sys.executable,"-I",f"{BASE}/scripts/edit_raw.py",t.name])
