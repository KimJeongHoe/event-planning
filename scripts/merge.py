#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Merge raw JSONL case files into 사례DB.csv / FAQ.csv, validate, number, and produce stats."""
import json, glob, os, sys, re, csv, difflib, datetime, collections
import pandas as pd

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = f"{BASE}/raw"
OUT = f"{BASE}/merged"
SPEC = f"{BASE}/spec"
os.makedirs(OUT, exist_ok=True)

cols = json.load(open(f"{SPEC}/columns.json", encoding="utf-8"))
CASE_COLS = cols["case_columns"]
FAQ_COLS = cols["faq_columns"]
CASE_KEYS = [k for k, _ in CASE_COLS]
FAQ_KEYS = [k for k, _ in FAQ_COLS]

ENUMS = {
    "kind": ["실제", "응용"],
    "nature": ["오픈행사", "홍보형행사", "상시서비스", "가격구조형", "리뉴얼·신메뉴", "N주년", "위기회복", "양도·폐업정리"],
    "stage": ["오픈전", "가오픈", "그랜드오픈", "오픈N일", "정착기", "상시", "비수기", "리뉴얼", "신메뉴", "N주년", "위기회복", "폐업정리", "해당없음"],
    "timing": ["상시", "오픈", "명절", "공휴일·연휴", "급여일", "방학", "시험·수능", "졸업·입학", "기념일", "스포츠경기", "지역축제", "날씨", "연말송년회", "비수기", "사회이슈", "기타"],
    "method": ["혜택형", "현장연출형", "체험·참여형", "온라인형", "동네매체형", "제휴형", "단골·관계형", "사회공헌형"],
    "target": ["전체", "신규", "단골", "단체·회식", "가족", "커플", "직장인", "학생", "어르신", "외국인", "배달·포장", "인근주민·상인", "특정직군", "특정조건"],
    "cost_structure": ["원가형", "인건비형", "광고비형", "무비용", "공급처지원", "혼합"],
    "exposure": ["매장안", "매장앞", "동네", "지역", "온라인", "배달앱", "전국"],
    "industry": ["요식업", "소매", "미용·뷰티", "병의원·약국", "학원·교육", "서비스업", "공통"],
    "district": ["주택가", "오피스", "대학가", "학원가", "번화가·유흥", "역세권", "관광지", "로드사이드", "지식산업센터", "배달전문", "전국·온라인", "미상"],
    "scale": ["개인매장", "소규모프랜차이즈", "대형프랜차이즈", "대기업·유통", "지자체·공공", "미상"],
    "cost_ratio_level": ["낮음", "중간", "높음", "해당없음", "미상"],
    "cost_recovery": ["신규유입", "추가주문", "재방문", "가격에포함", "공급처지원", "광고효과", "재고소진", "해당없음"],
    "goals": ["신규손님", "재방문", "객단가", "회전율", "비피크채우기", "비수기채우기", "리뷰수", "SNS노출", "단체예약", "포장배달", "재고소진", "신메뉴알리기", "인지도", "지역관계", "위기회복"],
    "source_types": ["뉴스", "업계매체", "사장님노하우", "공공자료", "프랜차이즈공지", "처분사례", "법령·고시", "블로그·카페", "해외자료", "학술·보고서"],
    "era": ["1980년대", "1990년대", "2000년대", "2010년대", "2020년대"],
}
# common synonyms -> canonical
SYN = {
    "nature": {"오픈 행사": "오픈행사", "홍보형": "홍보형행사", "홍보형 행사": "홍보형행사", "상시 서비스": "상시서비스", "가격 구조형": "가격구조형",
               "리뉴얼": "리뉴얼·신메뉴", "신메뉴": "리뉴얼·신메뉴", "리뉴얼·신메뉴출시": "리뉴얼·신메뉴", "리뉴얼/신메뉴": "리뉴얼·신메뉴", "위기 회복": "위기회복",
               "양도·폐업": "양도·폐업정리", "폐업정리": "양도·폐업정리", "양도/폐업정리": "양도·폐업정리"},
    "stage": {"오픈 전": "오픈전", "그랜드 오픈": "그랜드오픈", "오픈 N일": "오픈N일", "정착기(1~3개월)": "정착기", "폐업": "폐업정리", "양도·폐업정리": "폐업정리", "해당 없음": "해당없음", "리뉴얼·신메뉴": "리뉴얼"},
    "timing": {"공휴일": "공휴일·연휴", "연휴": "공휴일·연휴", "수능": "시험·수능", "시험": "시험·수능", "졸업": "졸업·입학", "입학": "졸업·입학", "스포츠": "스포츠경기",
               "축제": "지역축제", "송년회": "연말송년회", "연말": "연말송년회", "사회 이슈": "사회이슈", "생일": "기념일"},
    "method": {"현장 연출형": "현장연출형", "체험형": "체험·참여형", "참여형": "체험·참여형", "체험·참여": "체험·참여형", "동네 매체형": "동네매체형", "단골형": "단골·관계형", "관계형": "단골·관계형",
               "단골·관계": "단골·관계형", "사회 공헌형": "사회공헌형", "혜택": "혜택형"},
    "target": {"단체": "단체·회식", "회식": "단체·회식", "배달": "배달·포장", "포장": "배달·포장", "인근주민": "인근주민·상인", "주변상인": "인근주민·상인", "인근 주민": "인근주민·상인", "특정 직군": "특정직군", "특정 조건": "특정조건", "신규손님": "신규"},
    "cost_structure": {"원가": "원가형", "인건비": "인건비형", "광고비": "광고비형", "무비용형": "무비용", "비용없음": "무비용", "공급처 지원": "공급처지원"},
    "exposure": {"매장 안": "매장안", "매장내": "매장안", "매장 앞": "매장앞", "매장앞·거리": "매장앞", "온라인·전국": "온라인|전국", "배달 앱": "배달앱"},
    "industry": {"외식업": "요식업", "음식점": "요식업", "병의원": "병의원·약국", "약국": "병의원·약국", "학원": "학원·교육", "교육": "학원·교육", "미용": "미용·뷰티", "뷰티": "미용·뷰티", "서비스": "서비스업"},
    "district": {"주거": "주택가", "주거지": "주택가", "직장인": "오피스", "오피스가": "오피스", "유흥가": "번화가·유흥", "번화가": "번화가·유흥", "온라인": "전국·온라인", "전국": "전국·온라인", "알수없음": "미상", "미상/전국": "미상"},
    "scale": {"개인": "개인매장", "개인 매장": "개인매장", "프랜차이즈": "소규모프랜차이즈", "대형 프랜차이즈": "대형프랜차이즈", "대기업": "대기업·유통", "공공": "지자체·공공", "지자체": "지자체·공공", "중소프랜차이즈": "소규모프랜차이즈", "중소 프랜차이즈": "소규모프랜차이즈"},
    "cost_ratio_level": {"없음": "해당없음", "해당 없음": "해당없음", "낮음~중간": "낮음|중간", "중간~높음": "중간|높음", "알수없음": "미상"},
    "cost_recovery": {"신규 유입": "신규유입", "추가 주문": "추가주문", "재 방문": "재방문", "가격에 포함": "가격에포함", "가격포함": "가격에포함", "공급처 지원": "공급처지원", "광고 효과": "광고효과", "재고 소진": "재고소진", "해당 없음": "해당없음"},
    "goals": {"신규 손님": "신규손님", "신규유입": "신규손님", "재방문율": "재방문", "객단가 올리기": "객단가", "리뷰 수": "리뷰수", "리뷰": "리뷰수", "SNS 노출": "SNS노출", "단체 예약": "단체예약", "포장·배달": "포장배달", "포장배달 늘리기": "포장배달", "재고 소진": "재고소진", "신메뉴 알리기": "신메뉴알리기", "지역 관계": "지역관계", "위기 회복": "위기회복", "비피크 채우기": "비피크채우기", "비수기 채우기": "비수기채우기"},
    "source_types": {"기사": "뉴스", "언론": "뉴스", "업계 매체": "업계매체", "사장님 노하우": "사장님노하우", "노하우": "사장님노하우", "공공 자료": "공공자료", "정부자료": "공공자료", "프랜차이즈 공지": "프랜차이즈공지", "공식": "프랜차이즈공지", "보도자료": "뉴스", "처분 사례": "처분사례", "법령": "법령·고시", "고시": "법령·고시", "블로그": "블로그·카페", "카페": "블로그·카페", "커뮤니티": "블로그·카페", "해외": "해외자료", "논문": "학술·보고서", "보고서": "학술·보고서"},
    "era": {"1990s": "1990년대", "2000s": "2000년대", "2010s": "2010년대", "2020s": "2020년대", "현재": "2020년대"},
}


OFFICIAL = re.compile(r"대법원\s*\d{4}|선고\s*\d{2,4}[가-힣]+\d+|법제처\s*(?:법령해석\s*)?\d{2}-\d{4}|헌법재판소|\[공식 판단|\[공식 자료|법령해석 ?회신|회신 ?\d{6}")
AGENCY = re.compile(r"보도자료|Q&A|질의응답|보도참고자료|가이드라인")
def evidence_level(legal_risk, todo, extra=""):
    t = str(legal_risk) + " " + str(extra); todo = str(todo).strip()
    if todo == "해외 법": return "해외 법(국내 기준만 확인)"
    if todo == "법령 원문 없음": return "원문 없음(대체 근거)"
    if todo == "사실관계 불명": return "사실 확인 필요"
    if todo == "지자체 조례": return "조례 예시만 확인"
    if todo == "적용 해석":
        return "조문 해석만(공식 해석 원문 없음)" + ("·참고 판례 있음" if OFFICIAL.search(t) else "") + ("·부처 자료 있음" if AGENCY.search(t) else "")
    if OFFICIAL.search(t): return "공식 해석·판례 확인"
    if AGENCY.search(t): return "부처 공식 자료 확인"
    if re.search(r"제\d+조", t): return "법령 원문 확인"
    fq = sorted(set(re.findall(r"F0\d\d", t)))
    if fq: return "FAQ 근거 따름(" + "·".join(fq[:4]) + ")"
    if "해외" in t: return "해외 법(국내 기준만 확인)"
    return "법 쟁점 적음"

def csv_safe(df):
    """엑셀 수식 실행 막기: =,+,-,@,탭,CR 로 시작하는 문자열 칸 앞에 ' 를 붙인다(CSV에만, JSONL 원본은 그대로)."""
    d = df.copy()
    for c in d.columns:
        if d[c].dtype == object or str(d[c].dtype) in ("str", "string"):
            d[c] = d[c].map(lambda v: ("'" + v) if isinstance(v, str) and v[:1] in ("=", "+", "-", "@", "\t", "\r") and v != "" else v)
    return d

def split_multi(v):
    if v is None: return []
    s = str(v).strip()
    if not s: return []
    parts = re.split(r"\s*[|,/，、]\s*", s)
    return [p.strip() for p in parts if p.strip()]

def normalize_enum(field, v):
    vals = split_multi(v)
    out, bad = [], []
    for p in vals:
        q = SYN.get(field, {}).get(p, p)
        for qq in q.split("|"):
            if qq in ENUMS[field]:
                if qq not in out: out.append(qq)
            else:
                bad.append(qq)
    return "|".join(out), bad

def to_int(v):
    try:
        f = float(str(v).strip()); i = int(round(f))
        return str(min(5, max(1, i)))
    except Exception:
        return ""

def load_jsonl(path):
    rows, bad = [], 0
    with open(path, encoding="utf-8") as f:
        for ln, line in enumerate(f, 1):
            line = line.strip()
            if not line: continue
            try:
                obj = json.loads(line)
                if isinstance(obj, dict): rows.append(obj)
                else: bad += 1
            except Exception as e:
                bad += 1
    return rows, bad

def main():
    today = datetime.date.today().isoformat()
    idmap_path = f"{OUT}/id_map.json"
    idmap = json.load(open(idmap_path, encoding="utf-8")) if os.path.exists(idmap_path) else {}
    next_id = max([v for v in idmap.values()] + [0]) + 1

    all_rows, bad_lines, invalid = [], {}, collections.Counter()
    invalid_examples = collections.defaultdict(set)
    files = sorted(glob.glob(f"{RAW}/*.jsonl"))
    for fp in files:
        fn = os.path.basename(fp)
        if fn.endswith("_faq.jsonl") or "수정기록" in fn: continue
        rows, bad = load_jsonl(fp)
        bad_lines[fn] = bad
        for r in rows:
            r = {k: ("" if v is None else v) for k, v in r.items()}
            r["src_file"] = fn
            r["orig_id"] = str(r.get("id", "")).strip()
            all_rows.append(r)

    # normalize
    seen_orig = set()
    recs = []
    for r in all_rows:
        rec = {k: "" for k in CASE_KEYS}
        for k in CASE_KEYS:
            if k in r:
                v = r[k]
                if isinstance(v, (list, tuple)): v = "|".join(str(x) for x in v)
                rec[k] = str(v).strip()
        for f in ENUMS:
            if f in ("kind",):
                continue
            if f == "goals" and str(rec.get(f, "")).strip().startswith("해당없음"):
                rec[f] = "해당없음(가게 목표 없음)"; continue  # 처분·정책 사례: 사용자 결정(회차9)
            if f == "scale" and str(rec.get(f, "")).startswith("기타"):
                rec["notes"] = (rec["notes"] + f" [규모 원래값: {rec[f]}]").strip(); rec[f] = "미상"
            val, bad = normalize_enum(f, rec.get(f, ""))
            if bad:
                invalid[f] += len(bad)
                for b in bad: invalid_examples[f].add(b)
                # keep unknown values in notes for traceability
                rec["notes"] = (rec["notes"] + f" [미표준값 {f}: {', '.join(bad)}]").strip()
            rec[f] = val
        k = rec["kind"].strip()
        rec["kind"] = "응용" if k.startswith("응") else "실제"
        for f in ("perceived_value", "distinctiveness", "shareability", "difficulty"):
            rec[f] = to_int(rec[f])
        if not rec["verified_date"]: rec["verified_date"] = today
        # 원문확인: 실제는 기본 '검색요약만', 응용은 '해당없음(응용)'
        vs = rec.get("verify_status", "").strip()
        if rec["kind"] == "응용": rec["verify_status"] = "해당없음(응용)"
        elif vs == "검색요약만" or vs not in ("확인함", "막힘", "원문 불일치"): rec["verify_status"] = "막힘" if vs == "검색요약만" else (vs if vs in ("확인함", "막힘", "원문 불일치") else "막힘")
        rec["_merged_into"] = str(r.get("merged_into", "")).strip()
        key = f'{rec["src_file"]}::{rec["orig_id"]}'
        if key in seen_orig:
            # duplicate orig id inside one file -> suffix
            n = 2
            while f"{key}#{n}" in seen_orig: n += 1
            key = f"{key}#{n}"
            rec["orig_id"] = rec["orig_id"] + f"#{n}"
        seen_orig.add(key)
        recs.append(rec)

    # assign ids (stable)
    for rec in recs:
        key = f'{rec["src_file"]}::{rec["orig_id"]}'
        if key not in idmap:
            idmap[key] = next_id; next_id += 1
        rec["id"] = idmap[key]
    json.dump(idmap, open(idmap_path, "w", encoding="utf-8"), ensure_ascii=False, indent=0)

    # remap base_ids (orig prefixed ids -> final ids)
    orig_to_final = {}
    for rec in recs:
        orig_to_final[rec["orig_id"]] = rec["id"]
    unresolved_base = []
    for rec in recs:
        if rec["kind"] == "응용":
            parts = split_multi(rec["base_ids"])
            mapped = []
            for p in parts:
                if p.isdigit(): mapped.append(p)
                elif p in orig_to_final: mapped.append(str(orig_to_final[p]))
                else: unresolved_base.append((rec["id"], p))
            rec["base_ids"] = "|".join(mapped)

    # 중복 합치기: merged_into 가 있는 사례는 본 DB에서 빼서 합쳐진사례.csv 로 보존(번호는 id_map에 그대로)
    def resolve(x):
        x = str(x).strip()
        return int(x) if x.isdigit() else orig_to_final.get(x)
    absorbed = [r for r in recs if r["_merged_into"]]
    main_recs = [r for r in recs if not r["_merged_into"]]
    by_final = {r["id"]: r for r in main_recs}
    bad_merge = []
    for r in absorbed:
        tgt = resolve(r["_merged_into"])
        if tgt not in by_final: bad_merge.append((r["id"], r["_merged_into"])); continue
        r["notes"] = (r["notes"] + f" [합쳐짐→{tgt}]").strip()
        t = by_final[tgt]
        ids = [x for x in t["merged_from"].split("|") if x]
        if str(r["id"]) not in ids: ids.append(str(r["id"]))
        t["merged_from"] = "|".join(ids)
    if bad_merge: print("합칠 대상 없음:", bad_merge)
    csv_safe(pd.DataFrame(absorbed, columns=CASE_KEYS + ["_merged_into"]).sort_values("id")).to_csv(
        f"{OUT}/합쳐진사례.csv", index=False, encoding="utf-8-sig",
        header=[h for _, h in CASE_COLS] + ["합쳐진곳(원래번호)"], quoting=csv.QUOTE_ALL)
    recs = main_recs
    # 수정 기록
    logs = []
    for fp in sorted(glob.glob(f"{RAW}/*수정기록*.jsonl")):
        rows, bad = load_jsonl(fp); logs += rows
    LOGK = ["date", "case", "field", "before", "after", "reason", "source_url"]
    LOGH = ["날짜", "사례(수집ID 또는 번호)", "칸", "고치기전", "고친뒤", "이유", "근거주소"]
    for l in logs:
        c = str(l.get("case", "")); l["case"] = f"{orig_to_final.get(c, c)} ({c})" if c in orig_to_final else c
    csv_safe(pd.DataFrame(logs, columns=LOGK)).to_csv(f"{OUT}/수정기록.csv", index=False, encoding="utf-8-sig", header=LOGH, quoting=csv.QUOTE_ALL)

    # 안전운영조건: 법 칸의 '안전한 운영:' 문구를 뽑아 따로 둠(raw에 적지 않는 파생 칸). 법확인필요사유가 남은 사례는 생성 시 이 조건을 행사안에 붙여야 함
    for r in recs:
        segs = re.findall(r"안전한 운영\s*[:：]\s*([^\]]+?)(?=\]|\s*\[|$)", r["legal_risk"])
        segs = [x.strip(" /.;") for x in segs if x.strip()]
        r["safe_ops"] = " ／ ".join(dict.fromkeys(segs))
    # FAQ 쪽 공식 해석 원문 없음 여부(사례 근거수준에 함께 표시)
    faq_noorig = set()
    for fp in glob.glob(f"{RAW}/FAQ*_faq.jsonl"):
        for ln in open(fp, encoding="utf-8"):
            if not ln.strip(): continue
            try: fr = json.loads(ln)
            except Exception: continue
            nt = str(fr.get("notes", ""))
            if re.search(r"\[확인 필요 사유:[^\]]*(적용 해석|원문)", nt) or str(fr.get("verdict", "")) == "확인 필요":
                faq_noorig.add(str(fr.get("faq_id", "")).strip().upper())
    for r in recs:
        r["evidence_level"] = evidence_level(r["legal_risk"], r["legal_todo"])
        fx = sorted(set(f.strip().upper() for f in split_multi(r["faq_ids"]) if f.strip().upper() in faq_noorig))
        r["faq_evidence"] = ("관련 FAQ " + "·".join(fx[:4]) + (" 등" if len(fx) > 4 else "") + " 공식 해석 원문 없음") if fx else ""
    # 유사 사례 묶음(spec/유사묶음.json, scripts/similar.py가 만듦): 묶음 번호와 대표 사례 번호
    sg_path = f"{SPEC}/유사묶음.json"
    if os.path.exists(sg_path):
        rid = {r["id"]: r for r in recs}
        for g in json.load(open(sg_path, encoding="utf-8"))["묶음"]:
            for m in g["members"]:
                if m in rid:
                    rid[m]["similar_group"] = f'{g["group"]}({len(g["members"])}건)'
                    rid[m]["group_rep"] = "대표" if m == g["rep"] else str(g["rep"])
    # 판 11: 행사방식 칸(기본 행사 방식 키, spec/사례_방식.json — scripts/anon11.py가 보조 판단 결과로 만듦)
    pm_path = f"{SPEC}/사례_방식.json"
    if os.path.exists(pm_path):
        pm = json.load(open(pm_path, encoding="utf-8"))["사례"]
        for r in recs: r["promo_method"] = "|".join(pm.get(str(r["id"]), []))
    df = pd.DataFrame(recs, columns=CASE_KEYS).sort_values("id")
    csv_safe(df).to_csv(f"{OUT}/사례DB.csv", index=False, encoding="utf-8-sig",
              header=[h for _, h in CASE_COLS], quoting=csv.QUOTE_ALL)
    df.to_json(f"{OUT}/사례DB.jsonl", orient="records", lines=True, force_ascii=False)

    # ---------- FAQ ----------
    faq_rows = []
    for fp in sorted(glob.glob(f"{RAW}/*_faq.jsonl")):
        rows, bad = load_jsonl(fp)
        bad_lines[os.path.basename(fp)] = bad
        for r in rows:
            rec = {k: "" for k in FAQ_KEYS}
            for k in FAQ_KEYS:
                if k in r:
                    v = r[k]
                    if isinstance(v, (list, tuple)): v = "|".join(str(x) for x in v)
                    rec[k] = str(v if v is not None else "").strip()
            if not rec["verified_date"]: rec["verified_date"] = today
            faq_rows.append(rec)
    # merge duplicate faq_ids: keep the longest reason
    byid = {}
    for r in faq_rows:
        fid = r["faq_id"].strip().upper()
        r["faq_id"] = fid
        if fid not in byid or len(r["reason"]) > len(byid[fid]["reason"]):
            byid[fid] = r
    # link case ids
    faq_cases = collections.defaultdict(list)
    for rec in recs:
        for fid in split_multi(rec["faq_ids"]):
            faq_cases[fid.strip().upper()].append(str(rec["id"]))
    for fid, r in byid.items():
        r["case_ids"] = "|".join(faq_cases.get(fid, []))
    for fid, r in byid.items():
        nt = str(r.get("notes", "")); v = str(r.get("verdict", ""))
        m = re.search(r"\[확인 필요 사유:\s*([^\]]+)\]", nt)
        todo = ""
        if m:
            reason = m.group(1)
            todo = "적용 해석" if "적용 해석" in reason else "법령 원문 없음" if "원문" in reason else "지자체 조례" if "조례" in reason else "사실관계 불명" if "사실" in reason else "적용 해석"
        elif re.search(r"공식 해석 (?:원문 )?(?:없음|미확인)|해석 원문 미확인|원문 미확인", nt) or v == "확인 필요":
            todo = "적용 해석"
        r["evidence_level"] = evidence_level(" ".join(str(r.get(k, "")) for k in ("reason", "precedents", "laws")), todo, nt)
    fdf = pd.DataFrame(sorted(byid.values(), key=lambda x: x["faq_id"]), columns=FAQ_KEYS)
    csv_safe(fdf).to_csv(f"{OUT}/FAQ.csv", index=False, encoding="utf-8-sig", header=[h for _, h in FAQ_COLS], quoting=csv.QUOTE_ALL)

    # ---------- stats ----------
    L = []
    L.append(f"# 병합 통계 ({today})\n")
    L.append(f"- 총 사례: {len(df)} (실제 {int((df.kind=='실제').sum())}, 응용 {int((df.kind=='응용').sum())})")
    L.append(f"- FAQ: {len(fdf)}  진행여부별: " + ", ".join(f"{k} {v}" for k, v in fdf['verdict'].value_counts().items()))
    L.append(f"- 깨진 줄(파싱 실패): " + ", ".join(f"{k}:{v}" for k, v in bad_lines.items() if v) if any(bad_lines.values()) else "- 깨진 줄 없음")
    L.append(f"- 수집 파일별 건수: " + ", ".join(f"{k}:{v}" for k, v in df['src_file'].value_counts().items()))
    vc = df[df.kind == "실제"]["verify_status"].value_counts()
    nreal = int((df.kind == "실제").sum()) or 1
    L.append("- 원문확인(실제 사례): " + ", ".join(f"{k} {v}건({v*100/nreal:.0f}%)" for k, v in vc.items()))
    L.append(f"- 합쳐진 사례(본 DB에서 빠지고 합쳐진사례.csv에 보존): {len(absorbed)}건")
    L.append(f"- 수정 기록: {len(logs)}건 (merged/수정기록.csv)")
    # 한국/해외 구분(실제)
    rr = df[df.kind == "실제"]
    kr = rr[rr.country.str.contains("한국")]
    L.append(f"- 실제 사례 국가: 한국 {len(kr)}건({len(kr)*100/max(len(rr),1):.0f}%), 해외 {len(rr)-len(kr)}건")
    L.append(f"- 참고제외 표시: {int((df.ref_exclude.astype(str).str.strip()!='').sum())}건")
    if unresolved_base: L.append(f"- 바탕사례 미해결 참조: {unresolved_base[:20]}")
    if invalid:
        L.append("- 값 목록 밖 값(비고에 보존): " + "; ".join(f"{k}:{v} 예) {', '.join(list(invalid_examples[k])[:6])}" for k, v in invalid.items()))

    def multi_counts(col):
        c = collections.Counter()
        for v in df[col]:
            for p in split_multi(v): c[p] += 1
        return c
    for col, title in [("industry", "업종"), ("nature", "성격"), ("method", "방식"), ("timing", "시점"), ("stage", "단계"), ("era", "시대"), ("country", "국가"), ("scale", "가게규모"), ("source_types", "출처유형"), ("verify_status", "원문확인")]:
        c = multi_counts(col)
        L.append(f"\n## {title}별 건수\n" + ", ".join(f"{k} {v}" for k, v in sorted(c.items(), key=lambda x: -x[1])))

    # sub_industry
    c = multi_counts("sub_industry")
    L.append("\n## 세부업종별 건수\n" + ", ".join(f"{k} {v}" for k, v in sorted(c.items(), key=lambda x: -x[1])[:60]))

    # industry x nature x method matrix (real cases only)
    real = df[df.kind == "실제"]
    cube = collections.Counter()
    for _, r in real.iterrows():
        for i in split_multi(r["industry"]) or ["(없음)"]:
            for n in split_multi(r["nature"]) or ["(없음)"]:
                for m in split_multi(r["method"]) or ["(없음)"]:
                    cube[(i, n, m)] += 1
    L.append("\n## 업종 × 성격 × 방식 (실제 사례) — 비어 있는 조합")
    empties = []
    for i in ENUMS["industry"]:
        if i == "공통": continue
        for n in ENUMS["nature"]:
            for m in ENUMS["method"]:
                if cube[(i, n, m)] == 0: empties.append(f"{i}×{n}×{m}")
    L.append(f"- 전체 조합 {6*len(ENUMS['nature'])*len(ENUMS['method'])}개 중 비어 있음 {len(empties)}개")
    # Show matrix industry x nature and industry x method
    L.append("\n### 업종 × 성격 (실제)")
    hdr = "| 업종 | " + " | ".join(ENUMS["nature"]) + " |"
    L.append(hdr); L.append("|" + "---|" * (len(ENUMS["nature"]) + 1))
    for i in ENUMS["industry"]:
        row = []
        for n in ENUMS["nature"]:
            row.append(str(sum(v for (ii, nn, mm), v in cube.items() if ii == i and nn == n)))
        L.append(f"| {i} | " + " | ".join(row) + " |")
    L.append("\n### 업종 × 방식 (실제)")
    hdr = "| 업종 | " + " | ".join(ENUMS["method"]) + " |"
    L.append(hdr); L.append("|" + "---|" * (len(ENUMS["method"]) + 1))
    for i in ENUMS["industry"]:
        row = []
        for m in ENUMS["method"]:
            row.append(str(sum(v for (ii, nn, mm), v in cube.items() if ii == i and mm == m)))
        L.append(f"| {i} | " + " | ".join(row) + " |")
    L.append("\n### 성격 × 방식 (실제, 요식업)")
    hdr = "| 성격 | " + " | ".join(ENUMS["method"]) + " |"
    L.append(hdr); L.append("|" + "---|" * (len(ENUMS["method"]) + 1))
    for n in ENUMS["nature"]:
        row = [str(cube[("요식업", n, m)]) for m in ENUMS["method"]]
        L.append(f"| {n} | " + " | ".join(row) + " |")
    L.append("\n### 비어 있는 조합 목록(업종×성격×방식)")
    L.append(", ".join(empties))

    # 채우기 우선순위
    L.append("\n## 채우기 우선순위 (무엇을 채우면 가장 많이 풀리나)")
    grp = collections.Counter(); grp2 = collections.Counter()
    for e in empties:
        i, n, m = e.split("×"); grp[(i, n)] += 1; grp2[(i, m)] += 1
    L.append("- 빈 조합(실제 기준)을 업종×성격으로 묶으면: " + " · ".join(f"{i}×{n} {v}개" for (i, n), v in grp.most_common(10)))
    L.append("- 업종×방식으로 묶으면: " + " · ".join(f"{i}×{m} {v}개" for (i, m), v in grp2.most_common(10)))
    W = {"staging": 3, "condition": 3, "benefit": 3, "duration": 2, "unit_cost": 2, "resources": 2, "case_qna": 2, "faq_ids": 1, "source_dates": 1, "known_result": 0}
    pr = []
    for k, w in W.items():
        if k not in df.columns: continue
        nb = int((df[k].astype(str).str.strip() == "").sum())
        if k == "known_result": nb = 0  # 원문에 있을 때만 적는 칸이라 채우기 대상 아님
        pr.append((nb * w, k, nb, w))
    L.append("- 빈 칸 채우기 순위(빈칸 수 × 생성 사용 가중치): " + " · ".join(f"{dict(CASE_COLS)[k]} {nb}칸(가중 {w})" for sc, k, nb, w in sorted(pr, reverse=True) if nb))
    L.append("  (알려진결과는 원문에 있을 때만 적는 칸이라 순위에서 제외)")

    # empties per column
    L.append("\n## 칸별 빈 칸 비율 (전체 사례)")
    emp = []
    for k, h in CASE_COLS:
        if k in ("base_ids", "faq_new", "notes", "src_file", "orig_id", "verify_note", "merged_from", "similar_group", "group_rep", "safe_ops", "evidence_level", "faq_evidence"): continue
        ratio = float((df[k].astype(str).str.strip() == "").mean()) if len(df) else 0
        emp.append((ratio, h))
    for ratio, h in sorted(emp, reverse=True):
        L.append(f"- {h}: 빈칸 {ratio*100:.0f}%")

    # 성격·방식·업종별 한국/해외(실제)
    L.append("\n## 유형별 한국/해외 (실제 사례)")
    for col, title in [("nature", "성격"), ("method", "방식"), ("industry", "업종")]:
        ck, co = collections.Counter(), collections.Counter()
        for _, r in rr.iterrows():
            for p in split_multi(r[col]):
                (ck if "한국" in str(r["country"]) else co)[p] += 1
        L.append(f"- {title}: " + " · ".join(f"{k} 한국{ck[k]}/해외{co[k]}" for k in sorted(set(ck)|set(co), key=lambda k: -(ck[k]+co[k]))))
    gp = df[df.notes.astype(str).str.contains(r"\[대체 사례:")]
    if len(gp):
        L.append("\n## 실제 사례 없는 빈 곳 (대체 사례로 채움, 사용자 결정)")
        for g, sub in gp.groupby(gp.notes.astype(str).str.extract(r"\[대체 사례: '([^']+)'")[0]):
            L.append(f"- {g}: 대체 {len(sub)}건 ({', '.join(sub.orig_id)})")
    L.append("\n## 법 칸 '확인 필요' 사유별 (전체)")
    lt = df[df.legal_todo.astype(str).str.strip() != ""]
    L.append(f"- 법확인필요사유가 적힌 사례: {len(lt)}건 / 사유: " + ", ".join(f"{k} {v}" for k, v in lt.legal_todo.astype(str).value_counts().items()))
    so = df[(df.legal_todo.astype(str).str.strip() != "")]
    L.append(f"- 사유가 남은 사례 중 안전운영조건이 있는 사례: {int((so.safe_ops.astype(str).str.strip()!='').sum())}건 / 없는 사례: {int((so.safe_ops.astype(str).str.strip()=='').sum())}건 (사유별 없는 수: " + ", ".join(f"{k} {v}" for k, v in so[so.safe_ops.astype(str).str.strip()==''].legal_todo.value_counts().items()) + ")")
    nr = df[(df.legal_todo.astype(str).str.strip() == "") & df.legal_risk.astype(str).str.contains("확인 필요")]
    L.append(f"- 법 칸에 '확인 필요' 글자가 있는데 사유가 비어 있는 사례: {len(nr)}건 " + str(nr.orig_id.tolist()[:20]))
    L.append("\n## 생성용 칸 채움 상태 (전체)")
    lim = df.limit.astype(str).str.strip()
    L.append(f"- 수량·1인한도: 빈칸 {int((lim=='').sum())}, 원문에 한도 언급 없음 {int(lim.str.startswith('원문에 한도 언급 없음').sum())}, 제안 {int(lim.str.startswith('제안').sum())}, 해당없음 {int(lim.str.startswith('해당없음').sum())}, 원문 확인 불가 {int(lim.str.startswith('원문 확인 불가').sum())}, 구체 값 {int(((lim!='') & ~lim.str.startswith(('원문에 한도','제안','해당없음','원문 확인 불가'))).sum())}")
    for k in ["kpi", "upsell_path"]:
        v = df[k].astype(str).str.strip()
        L.append(f"- {dict(CASE_COLS)[k]}: 빈칸 {int((v=='').sum())}, 없음(이유) {int(v.str.startswith('없음').sum())}")
    L.append("\n## 위험 칸 채움 상태 (전체)")
    for k in ["legal_risk", "business_risk", "ops_risk", "reputation_risk"]:
        v = df[k].astype(str).str.strip()
        L.append(f"- {dict(CASE_COLS)[k]}: 빈칸 {int((v=='').sum())}, 없음(이유) {int(v.str.startswith('없음').sum())}, 확인 필요 포함 {int(v.str.contains('확인 필요').sum())}")

    # dup candidates
    L.append("\n## 중복 후보 (이름 유사도 ≥ 0.75 또는 같은 첫 출처 URL)")
    names = list(zip(df["id"], df["name"], df["source_urls"]))
    first_url = collections.defaultdict(list)
    for i, n, u in names:
        us = [x.strip() for x in str(u).split("|") if x.strip()]
        if us: first_url[us[0]].append((i, n))
    dups = []
    for u, lst in first_url.items():
        if len(lst) > 1: dups.append(("URL", u[:60], [f"{i}:{n[:25]}" for i, n in lst]))
    nm = [(i, n) for i, n, _ in names]
    for a in range(len(nm)):
        for b in range(a + 1, len(nm)):
            sm = difflib.SequenceMatcher(None, nm[a][1], nm[b][1])
            if sm.real_quick_ratio() >= 0.75 and sm.quick_ratio() >= 0.75 and sm.ratio() >= 0.75:
                dups.append(("NAME", "", [f"{nm[a][0]}:{nm[a][1][:25]}", f"{nm[b][0]}:{nm[b][1][:25]}"]))
    rv_path = f"{SPEC}/중복검토.json"
    reviewed = [set(g) for g in json.load(open(rv_path, encoding="utf-8"))["중복아님"]] if os.path.exists(rv_path) else []
    def is_rev(lst):
        ids = {int(x.split(":")[0]) for x in lst}
        return any(ids <= g for g in reviewed)
    new_d = [d for d in dups if not is_rev(d[2])]
    L.append(f"- 후보 {len(dups)}건 중 검토 끝남(중복 아님, spec/중복검토.json) {len(dups)-len(new_d)}건, 새로 검토할 것 {len(new_d)}건")
    for t, u, lst in new_d:
        L.append(f"  - [{t}] {u} {lst}")

    # integrity checks
    L.append("\n## 무결성 점검")
    url_re = re.compile(r"^https?://[^\s|]+$")
    no_src = [str(r["id"]) for _, r in df.iterrows() if r["kind"] == "실제" and not str(r["source_urls"]).strip()]
    bad_url = []
    for _, r in df.iterrows():
        for u in [x.strip() for x in str(r["source_urls"]).split("|") if x.strip()]:
            if not url_re.match(u) or "example.com" in u: bad_url.append((str(r["id"]), u[:60]))
    app_res = [str(r["id"]) for _, r in df.iterrows() if r["kind"] == "응용" and str(r["known_result"]).strip()]
    app_nobase = [str(r["id"]) for _, r in df.iterrows() if r["kind"] == "응용" and not str(r["base_ids"]).strip()]
    no_q = [str(r["id"]) for _, r in df.iterrows() if not str(r["faq_ids"]).strip() and not str(r["case_qna"]).strip()]
    L.append(f"- 출처 없는 실제 사례: {len(no_src)}건 {no_src[:20]}")
    L.append(f"- 형식 이상 URL: {len(bad_url)}건 {bad_url[:10]}")
    L.append(f"- 응용인데 알려진결과가 있는 사례: {len(app_res)}건 {app_res[:20]}")
    L.append(f"- 응용인데 바탕사례 번호 없는 사례: {len(app_nobase)}건 {app_nobase[:20]}")
    L.append(f"- FAQ번호도 사례별질문도 없는 사례: {len(no_q)}건 {no_q[:20]}")

    # faq_new proposals
    props = [p for p in df["faq_new"] if str(p).strip()]
    L.append(f"\n## 새 질문 제안 (faq_new) {len(props)}건")
    for p in props[:80]: L.append(f"- {str(p)[:160]}")

    # blocked sources from logs
    L.append("\n## 로그에 적힌 막힌 원천·메모")
    for lp in sorted(glob.glob(f"{RAW}/*_log.md")):
        txt = open(lp, encoding="utf-8", errors="ignore").read()
        m = re.findall(r"(?im)^.*(막힌|차단|blocked|접근 불가|불가능|ENOTFOUND|403).*$", txt)
        L.append(f"- {os.path.basename(lp)}: " + (" / ".join(x.strip()[:120] for x in m[:8]) if m else "(특이사항 없음)"))

    open(f"{OUT}/통계.md", "w", encoding="utf-8").write("\n".join(L))
    print("\n".join(L[:12]))
    print(f"... full stats at {OUT}/통계.md")

if __name__ == "__main__":
    main()
