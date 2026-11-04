#!/usr/bin/env python3
"""사용자가 준 문자샘플 자료(preview/문자샘플_원본.json)에서 행사 공지에 쓸 문구만 고른다. build_preview.py가 불러 씀.
- 시작 인사말(월·계절), 끝 인사말: 넣기 가능
- 업종·행사 문자: 다른 가게 이름이 들어 있어 보기용(참고)으로만
- 빼는 것: 술이 나오는 문구, 최초·최저가·원조, 건강 효과(몸에 좋은·다이어트 등), 노키즈·환불 불가·복권, 선거·유흥·주점·안마 분류, 너무 긴 글"""
import json,re,os
B=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIQ=re.compile(r"(?<![가-힣])(술|소주|맥주|생맥|막걸리|하이볼|와인|사케|샴페인|주류|양주|위스키|칵테일)")
BAD=re.compile(r"국내 ?최초|최저가|업계 ?1위|원조|최고의 맛|몸에 ?좋|건강에 ?좋|다이어트|면역|해독|디톡스|살 ?빠|숙취|노키즈|환불 ?불가|복권|로또|대출|투자|수익 ?보장")
# 거래처·편지 말투를 손님에게 보내는 말로 고쳐 쓴다(거르지 않음). 순서대로 적용
ADAPT=[("OOO사장님 곁에 제가 있기를 소망하면서","고객님 곁에 늘 가까운 가게로 있기를 소망하면서"),
 ("OOO님의 고견과 하명을 기다리며, 가정과 직장에","고객님의 말씀에 늘 귀 기울이며, 가정과 일터에"),
 ("앞으로도 계속적인 지원을 부탁 드리오며","앞으로도 자주 들러 주시길 부탁드리며"),
 ("추진하시는 사업들이 나날이 발전하시고","하시는 일마다 나날이 좋은 일 가득하시고"),
 ("하시는 사업이 늘 순풍을 만난 배처럼 끝없이 발전하시기를","하시는 일마다 늘 순풍을 만난 배처럼 잘 풀리시기를"),
 ("OOO가 감사하는","저희 가게가 감사하는"),
 ("앞으로 OOO 가족의 일원으로서 함께 나아가며 다음과 같은 목표를 달성하기 위해 최선을 다하겠습니다.","앞으로도 고객님과 함께하며 더 좋은 가게가 되도록 최선을 다하겠습니다."),
 ("저희 OOO는 여러분과 함께 더욱 성장하고 발전해 나갈 것입니다.","저희 가게는 고객님과 함께 더 좋은 가게로 자라 가겠습니다."),
 ("저희 OOO가족이 되신 것을","저희 가게 단골이 되어 주신 것을"),
 ("하시는 사업 위에 좋은 성과","하시는 일마다 좋은 일"),("OOO님의 하시는 일마다","고객님께서 하시는 일마다"),("OOO님의 사업이","고객님께서 하시는 일이"),("하시는 사업","하시는 일"),
 ("번창하","잘 되"),("좋은 성과 있으시기를","좋은 일 있으시기를"),("좋은 성과만","좋은 일만"),("많은 성과 거두시고","좋은 일 많으시고"),
 ("좋은 소식을 기다립니다","다시 찾아 주시길 기다립니다"),("사장님의 건강은","고객님의 건강은"),("OO년 새해","새해")]
def adapt(t):
    o=t
    for a,b in ADAPT: t=t.replace(a,b)
    t=t.replace("고객님의 하시는","고객님께서 하시는")
    return t,(o if t!=o else "")
SKIPC={"A7","B23","B27","B34","B33","B11","B10","U9","U7","B3","B19","B8"}
IND={"요식업":["B21","B22"],"미용·뷰티":["B15"],"소매":["B14","B28","B31","B26"],"학원·교육":["B6"],"병의원·약국":["B18"],"서비스업":["B12","B37","B16","B20","B24"]}
LIT=re.compile(r"삭막|사색|애상|그윽|만안|존체|비나이다|지필|호젓|예감|여미게|소망하|기원하|……|시리도록|무심케|아랫목|원단\(|묵은 때|일기|독서의 계절|추억을 떠올")
def fit(t):
    f=0
    if len(t)>60: f-=1
    if len(t)>90: f-=1
    f-=len(LIT.findall(t))
    if len(re.findall(r"[.!?]",t))>2: f-=1
    return f
def load():
    p=f"{B}/preview/문자샘플_원본.json"
    if not os.path.exists(p): return None
    j=json.load(open(p,encoding="utf-8")); q=j["q"]; out={"start":[],"end":[],"ex":{},"skip":0,"total":len(q)}
    for x in q:
        t=x["t"].strip(); c=set(x["c"])
        if c&SKIPC or LIQ.search(t) or BAD.search(t): out["skip"]+=1; continue
        orig=""
        if x["fm"] in ("시작 인사말","끝 인사말"): t,orig=adapt(t)
        if x["fm"]=="시작 인사말" and len(t)<=80:
            m=re.search(r"\((\d{1,2})월\)",x["h"]); mons=[int(m.group(1))] if m else []
            if not mons:
                for k,ms in (("H1",[3,4,5]),("H2",[6,7,8]),("H3",[9,10,11]),("H4",[12,1,2])):
                    if k in c: mons=ms
            if mons: out["start"].append([t,mons,orig,fit(t)])
        elif x["fm"]=="끝 인사말" and len(t)<=70:
            mons=[]
            for w,ms in (("새해",[12,1]),("연말",[12]),("설",[1,2]),("추석",[9,10]),("크리스마스",[12]),("봄",[3,4,5]),("여름",[6,7,8]),("휴가",[7,8]),("가을",[9,10,11]),("단풍",[10,11]),("겨울",[12,1,2]),("추위",[11,12,1,2]),("더위",[6,7,8])):
                if w in t: mons+=ms
            out["end"].append([t,mons,orig,fit(t)])
        elif x["fm"]=="본문 문자" and len(t)<=260 and ("A2" in c or any(k in c for v in IND.values() for k in v)):
            for ind,ks in IND.items():
                if any(k in c for k in ks): out["ex"].setdefault(ind,[]).append([x["h"],t])
    return out
if __name__=="__main__":
    o=load(); print("고쳐 쓴 인사말",sum(1 for x in o["start"]+o["end"] if x[2]),"전체",o["total"],"뺀 것",o["skip"],"시작",len(o["start"]),"끝",len(o["end"]),{k:len(v) for k,v in o["ex"].items()})
