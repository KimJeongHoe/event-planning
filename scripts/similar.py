#!/usr/bin/env python3
"""유사 사례 묶음 계산 → spec/유사묶음.json
기준: 같은 성격(nature) 안에서 이름+요약 글자 2-gram 코사인 ≥ 0.4, 또는 notes의 [유사 사례 묶음: ...] 표시. 묶음 대표: 참고제외 아님 → 원문 확인함 → 한국 → 실제 → 채운 칸 수 많은 순 → 번호 작은 순.
사용: python3 scripts/merge.py 뒤에 python3 scripts/similar.py, 다시 merge.py (merge가 이 파일을 읽어 칸을 채움)"""
import json,re,math,collections,os,sys
BASE=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TH=float(sys.argv[1]) if len(sys.argv)>1 else 0.4
rs=[json.loads(l) for l in open(f"{BASE}/merged/사례DB.jsonl",encoding="utf-8")]
byid={r["id"]:r for r in rs}
def vec(t):
    t=re.sub(r"\s+","",t); return collections.Counter(t[i:i+2] for i in range(len(t)-1))
V={r["id"]:vec(r["name"]+" "+r["summary"]) for r in rs}
N={k:math.sqrt(sum(x*x for x in v.values())) or 1 for k,v in V.items()}
def cos(a,b):
    va,vb=V[a],V[b]
    if len(va)>len(vb): va,vb=vb,va
    return sum(c*vb.get(k,0) for k,c in va.items())/(N[a]*N[b])
par={i:i for i in byid}
def f(x):
    while par[x]!=x: par[x]=par[par[x]]; x=par[x]
    return x
def u(a,b):
    if a in par and b in par: par[f(a)]=f(b)
why=collections.defaultdict(set)
blk=collections.defaultdict(list)
for r in rs: blk[r["nature"]].append(r["id"])
for k,ids in blk.items():
    for i in range(len(ids)):
        for j in range(i+1,len(ids)):
            if cos(ids[i],ids[j])>=TH: u(ids[i],ids[j]); why[ids[i]].add("글자 유사"); why[ids[j]].add("글자 유사")
rv=json.load(open(f"{BASE}/spec/중복검토.json",encoding="utf-8"))["중복아님"]
# '중복아님' 묶음(같은 기사 속 서로 다른 가게·아이디어)은 비슷함의 근거로 쓰지 않음. 글자 유사로 묶인 경우에만 묶임.
tag=collections.defaultdict(list)
for r in rs:
    m=re.search(r"\[유사 사례 묶음:\s*([^\]—]+)",r["notes"])
    if m: tag[m.group(1).strip()].append(r["id"])
for t,g in tag.items():
    for x in g[1:]: u(g[0],x)
    for x in g: why[x].add("묶음 표시")
grp=collections.defaultdict(list)
for i in byid: grp[f(i)].append(i)
def score(i):
    r=byid[i]; filled=sum(1 for v in r.values() if str(v).strip())
    return (r["ref_exclude"]!="", r["verify_status"]!="확인함", r["country"]!="한국", r["kind"]!="실제", -filled, i)
out=[]
for g in sorted([sorted(g) for g in grp.values() if len(g)>1],key=lambda g:g[0]):
    rep=min(g,key=score)
    out.append({"members":g,"rep":rep,"basis":sorted(set().union(*[why[x] for x in g])),"rep_name":byid[rep]["name"]})
for n,o in enumerate(out,1): o["group"]=f"G{n:03d}"
json.dump({"설명":__doc__,"기준값":TH,"묶음":out},open(f"{BASE}/spec/유사묶음.json","w",encoding="utf-8"),ensure_ascii=False,indent=1)
sz=collections.Counter(len(o["members"]) for o in out)
print("묶음",len(out),"사례",sum(len(o["members"]) for o in out),"크기분포",sorted(sz.items()))
