#!/usr/bin/env python3
"""시행일 장부(판 11): 법 근거 키마다 law_src 원문 파일에서 시행일을 뽑아 spec/법근거_시행일.json 과 비교한다.

사용:
  python3 -I scripts/law_dates.py                 # law_src에서 다시 뽑아 장부와 비교, 바뀐 것만 출력(장부는 그대로)
  python3 -I scripts/law_dates.py --쓰기           # 비교 뒤 장부를 새 값으로 덮어씀
  python3 -I scripts/law_dates.py --받기 <폴더>    # 장부에 쓰인 원문을 lawfetch.py로 <폴더>에 다시 받아(법령·행정규칙만)
                                                  #   받은 판의 시행일을 장부와 비교해 출력(law_src는 고치지 않음)
근거 파일: spec/법근거_판8.json(필수) + spec/법근거_판11_추가.json(있으면).
시행일 찾는 순서(키의 file 칸에 적힌 파일 순서대로):
  1) 본문 머리의 「[시행 YYYY. M. D.]」 줄(법령·행정규칙 본문)
  2) 없으면 별표 파일의 「본문: …efYd=YYYYMMDD」(그 별표가 딸린 법령 판의 시행일),
     행정규칙 별표처럼 efYd도 없으면 딸린 본문 파일(이름의 「__별표」 앞)의 [시행] 줄
  3) 둘 다 없으면(보도자료·해석례·판례·누리집 정책 등) 빈 값
"""
import json, os, re, sys, subprocess

B = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(B, "law_src")
LEDGER = os.path.join(B, "spec", "법근거_시행일.json")
BASES = [os.path.join(B, "spec", "법근거_판8.json"), os.path.join(B, "spec", "법근거_판11_추가.json")]
RE_SI = re.compile(r"\[시행\s*(\d{4})\.\s*(\d{1,2})\.\s*(\d{1,2})\.?\]")
RE_EF = re.compile(r"efYd=(\d{4})(\d{2})(\d{2})")

_index = None
def index():
    """law_src 안의 파일을 이름(확장자 포함)으로 찾는 표. 같은 이름이 여러 곳이면 최상위를 우선."""
    global _index
    if _index is None:
        _index = {}
        for root, _, files in os.walk(SRC):
            for f in files:
                p = os.path.join(root, f)
                rel = os.path.relpath(p, SRC)
                if f not in _index or rel.count(os.sep) < _index[f].count(os.sep):
                    _index[f] = rel
    return _index

def resolve(piece):
    """file 칸의 한 조각 → law_src 기준 상대 경로(없으면 None). 이전 창의 임시 경로·law_src_new 머리는 이름으로 찾음."""
    piece = piece.strip()
    if not piece or piece.startswith("원문 ") or piece.startswith("http"):
        return None
    if os.path.isabs(piece):   # 이전 창의 임시 폴더 경로 → law_src 안에서 이름으로 찾음(밖은 보지 않음)
        return index().get(os.path.basename(piece))
    direct = os.path.join(SRC, piece)
    if os.path.isfile(direct):
        return piece
    sub = os.path.join("별표", os.path.basename(piece)) if "/별표/" in piece or piece.startswith("별표/") else None
    if sub and os.path.isfile(os.path.join(SRC, sub)):
        return sub
    return index().get(os.path.basename(piece))

def date_of(text):
    """(시행일, 근거줄, 방식) — 머리 40줄 안의 [시행 …] 우선, 없으면 efYd."""
    head = text.splitlines()[:40]
    for ln in head:
        m = RE_SI.search(ln)
        if m:
            y, mo, d = m.groups()
            return f"{y}-{int(mo):02d}-{int(d):02d}", ln.strip()[:80], "시행"
    for ln in head:
        m = RE_EF.search(ln)
        if m and ln.startswith("본문"):
            y, mo, d = m.groups()
            return f"{y}-{mo}-{d}", f"본문 주소 efYd={y}{mo}{d}(별표가 딸린 법령 판의 시행일)", "efYd"
    return "", "", ""

def file_date(rel):
    try:
        t = open(os.path.join(SRC, rel), encoding="utf-8", errors="ignore").read()
    except OSError:
        return "", "", ""
    d = date_of(t)
    if not d[0] and "__별표" in rel:   # 행정규칙 별표(본문 주소에 efYd 없음) → 딸린 본문 파일의 [시행] 줄
        parent = index().get(os.path.basename(rel).split("__별표")[0] + ".txt")
        if parent:
            pd = date_of(open(os.path.join(SRC, parent), encoding="utf-8", errors="ignore").read())
            if pd[0]:
                return pd[0], f"딸린 본문 {parent}: {pd[1]}"[:100], "efYd"
    return d

def build():
    out = {}
    for bp in BASES:
        if not os.path.exists(bp):
            continue
        tag = os.path.basename(bp).replace(".json", "")
        for it in json.load(open(bp, encoding="utf-8"))["items"]:
            pieces = [p for p in re.split(r";\s*", it.get("file", "") or "") if p.strip()]
            rels = [r for r in (resolve(p) for p in pieces) if r]
            rels = list(dict.fromkeys(rels))
            main = None
            others = []
            for r in rels:
                d, why, how = file_date(r)
                rec = {"파일": r, "시행일": d, "근거줄": why}
                if main is None and how == "시행":
                    main = rec
                else:
                    others.append(rec)
            if main is None:   # [시행] 줄이 하나도 없으면 efYd라도 있는 첫 파일, 그것도 없으면 첫 파일
                main = next((o for o in others if o["시행일"]), None) or (others[0] if others else None)
                if main:
                    others = [o for o in others if o is not main]
            if main is None:
                main = {"파일": "", "시행일": "", "근거줄": "law_src에 원문 파일 없음(누리집 정책·주소만)" if pieces else "file 칸 비어 있음"}
            elif not main["시행일"]:
                main["근거줄"] = "본문에 시행일 표시 없음(보도자료·해석례·판례 등)"
            rec = {"파일": main["파일"], "시행일": main["시행일"], "근거줄": main["근거줄"], "출처": tag}
            if others:
                rec["다른파일"] = [{"파일": o["파일"], "시행일": o["시행일"]} for o in others]
            out[it["key"]] = rec
    return out

def compare(old, new):
    ch = []
    for k in sorted(set(old) | set(new)):
        a, b = old.get(k), new.get(k)
        if a is None:
            ch.append(f"새 키  {k}: {b['시행일'] or '(없음)'}  {b['파일']}")
        elif b is None:
            ch.append(f"빠진 키 {k}")
        else:
            if a.get("시행일") != b.get("시행일") or a.get("파일") != b.get("파일"):
                ch.append(f"바뀜  {k}: {a.get('시행일') or '(없음)'} → {b.get('시행일') or '(없음)'}  {b['파일']}")
            ao = {o["파일"]: o["시행일"] for o in a.get("다른파일", [])}
            for o in b.get("다른파일", []):
                if o["파일"] in ao and ao[o["파일"]] != o["시행일"]:
                    ch.append(f"바뀜  {k} (다른 파일 {o['파일']}): {ao[o['파일']] or '(없음)'} → {o['시행일'] or '(없음)'}")
    return ch

def refetch(ledger, outdir):
    """장부에 쓰인 법령·행정규칙 파일을 lawfetch.py로 다시 받아 시행일 비교. law_src는 건드리지 않음."""
    files = {}
    for k, r in ledger.items():
        for rec in [r] + r.get("다른파일", []):
            p = rec.get("파일")
            if not p or p.startswith("별표") or p.startswith("참고") or p.startswith("해석례") or p.startswith("판례"):
                continue
            files.setdefault(p, rec.get("시행일", ""))
    fetch = os.path.join(B, "scripts", "lawfetch.py")
    os.makedirs(outdir, exist_ok=True)
    for p, old in sorted(files.items()):
        try:
            first = open(os.path.join(SRC, p), encoding="utf-8", errors="ignore").read(3000)
        except OSError:
            continue
        kind = "행정규칙" if ("admRulInfo" in first or "행정규칙" in first.split("\n")[0]) else "법령"
        name = os.path.splitext(os.path.basename(p))[0]
        subprocess.run([sys.executable, "-I", fetch, outdir, kind, name], capture_output=True)
        got = os.path.join(outdir, name.replace("/", "_") + ".txt")
        if not os.path.exists(got):
            print(f"받기 실패  {p}")
            continue
        d, _, _ = date_of(open(got, encoding="utf-8", errors="ignore").read())
        mark = "같음" if d == old else "바뀜"
        if mark == "바뀜":
            print(f"{mark}  {p}: 장부 {old or '(없음)'} → 새로 받은 판 {d or '(없음)'}")
    print("다시 받기 끝:", outdir, "(바뀐 파일만 출력. law_src에 넣을지는 사람이 정함)")

def main():
    args = sys.argv[1:]
    old = json.load(open(LEDGER, encoding="utf-8")) if os.path.exists(LEDGER) else {}
    old_items = {k: v for k, v in old.items() if not k.startswith("_")}
    if "--받기" in args:
        i = args.index("--받기")
        if i + 1 >= len(args):
            raise SystemExit("--받기 다음에 받을 폴더를 주세요")
        refetch(old_items or build(), args[i + 1])
        return
    new = build()
    ch = compare(old_items, new)
    print("\n".join(ch) if ch else "바뀐 것 없음")
    n = sum(1 for v in new.values() if v["시행일"])
    print(f"키 {len(new)}개 중 시행일 찾음 {n} / 못 찾음 {len(new) - n}")
    if "--쓰기" in args or not old:
        doc = {"_설명": "법 근거 키별 시행일 장부(scripts/law_dates.py가 만듦). 시행일 = law_src 원문 머리의 [시행 …] 줄, 없으면 별표 본문 주소의 efYd. 빈 값 = 원문에 시행일 표시 없음(보도자료·해석례·누리집 정책 등)."}
        doc.update(new)
        json.dump(doc, open(LEDGER, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print("장부 씀:", LEDGER)

if __name__ == "__main__":
    main()
