from __future__ import annotations

import json
import re
import time
import urllib.parse
from pathlib import Path

import requests

UA = "RUDN-GMU-educational-platform/0.7 (Wikidata media probe; contact: omnistat@yandex.ru)"
S = requests.Session(); S.headers.update({"User-Agent": UA})
API = "https://www.wikidata.org/w/api.php"
COMMONS_API = "https://commons.wikimedia.org/w/api.php"

INSTITUTIONS = [
"Государственная Дума Федерального Собрания Российской Федерации",
"Верховный Суд Российской Федерации",
"Правительство Москвы",
"Министерство иностранных дел Российской Федерации",
"Верховный Суд Республики Татарстан",
"Екатеринбургская городская Дума",
"Правительство Российской Федерации",
"Свердловский областной суд",
"Мэрия города Новосибирска",
"Законодательное Собрание Омской области",
"Министерство финансов Российской Федерации",
"Московский городской суд",
"Городская Дума города Нижнего Новгорода",
"Федеральная налоговая служба",
"Департамент финансов Курганской области",
"Правительство Челябинской области",
"Конституционный Суд Российской Федерации",
"Администрация города Екатеринбурга",
"Совет Федерации Федерального Собрания Российской Федерации",
"Кабинет Министров Республики Татарстан",
"Министерство внутренних дел Российской Федерации",
"Управление МВД России по Тюменской области",
"Московская городская Дума",
"Новосибирский областной суд",
"Министерство здравоохранения Российской Федерации",
"Администрация города Краснодара",
"Аппарат Государственной Думы Федерального Собрания Российской Федерации",
"Правительство Пермского края",
"Министерство науки и высшего образования Российской Федерации",
"Челябинская городская Дума",
"Судебный департамент при Верховном Суде Российской Федерации",
"Федеральная антимонопольная служба",
"Межрегиональное управление Федеральной антимонопольной службы по Ярославской области и Костромской области",
"Федеральное казначейство",
"Краснодарский краевой суд",
"Федеральная служба государственной статистики",
"Министерство промышленности и торговли Донецкой Народной Республики",
"Законодательное Собрание Санкт-Петербурга",
"Аппарат Уполномоченного по правам ребёнка в Свердловской области",
"Межрайонная инспекция Федеральной налоговой службы по Воронежской области",
"Аппарат Законодательного собрания Ростовской области",
"Управление социальной политики по городу Асбесту",
"Управление МВД России по городу Тольятти",
"Администрация городского округа Первоуральск",
"Аппарат Совета Депутатов городского округа Троицк",
"Избирательная комиссия городского округа Самара",
"Управление Россельхознадзора по Брянской области",
"Контрольно-счетная палата Иркутской области",
"Администрация федеральной территории Сириус",
"Администрация Президента Российской Федерации",
]

ALIASES = {
5: ["Верховный суд Татарстана"],
6: ["Екатеринбургская городская дума", "Городская дума Екатеринбурга"],
8: ["Свердловский областной суд"],
9: ["Мэрия Новосибирска", "Администрация Новосибирска"],
10: ["Законодательное собрание Омской области"],
13: ["Городская дума Нижнего Новгорода"],
15: ["Департамент финансов Курганской области"],
18: ["Администрация Екатеринбурга"],
20: ["Кабинет министров Татарстана", "Правительство Татарстана"],
22: ["УМВД России по Тюменской области"],
24: ["Новосибирский областной суд"],
26: ["Администрация Краснодара"],
28: ["Правительство Пермского края"],
30: ["Челябинская городская дума"],
31: ["Судебный департамент при Верховном Суде РФ"],
32: ["ФАС России"],
34: ["Федеральное казначейство России"],
36: ["Росстат"],
38: ["Законодательное собрание Санкт-Петербурга"],
43: ["УМВД России по Тольятти"],
44: ["Администрация Первоуральска"],
45: ["Совет депутатов Троицка Москва"],
47: ["Россельхознадзор"],
48: ["Контрольно-счетная палата Иркутской области"],
49: ["Администрация Сириуса"],
50: ["Администрация президента России"],
}

def norm(s: str) -> str:
    return re.sub(r"[^a-zа-яё0-9]+", " ", s.lower()).strip()

def search(q: str):
    r=S.get(API,params={"action":"wbsearchentities","search":q,"language":"ru","uselang":"ru","type":"item","limit":10,"format":"json","origin":"*"},timeout=60); r.raise_for_status()
    return r.json().get("search",[])

def entity(qid: str):
    r=S.get(API,params={"action":"wbgetentities","ids":qid,"props":"labels|descriptions|aliases|claims|sitelinks","languages":"ru|en","sitefilter":"ruwiki|enwiki|commonswiki","format":"json","origin":"*"},timeout=60); r.raise_for_status()
    return r.json()["entities"].get(qid,{})

def claim_files(ent: dict):
    out={}
    for prop in ("P18","P154","P94","P41"):
        vals=[]
        for c in (ent.get("claims") or {}).get(prop,[]):
            try:
                v=c["mainsnak"]["datavalue"]["value"]
                if isinstance(v,str): vals.append(v)
            except Exception: pass
        out[prop]=vals
    return out

def commons_info(filename: str):
    title="File:"+filename
    r=S.get(COMMONS_API,params={"action":"query","titles":title,"prop":"imageinfo","iiprop":"url|mime|size|extmetadata","iiurlwidth":1800,"format":"json","formatversion":2,"origin":"*"},timeout=60); r.raise_for_status()
    pages=r.json().get("query",{}).get("pages",[])
    if not pages: return None
    p=pages[0]; ii=(p.get("imageinfo") or [{}])[0]; meta=ii.get("extmetadata") or {}
    def cv(k):
        x=(meta.get(k) or {}).get("value") or ""
        return re.sub(r"<[^>]+>"," ",x)
    return {"title":p.get("title"),"url":ii.get("thumburl") or ii.get("url"),"original_url":ii.get("url"),"mime":ii.get("mime"),"width":ii.get("width"),"height":ii.get("height"),"description_url":ii.get("descriptionurl"),"license":cv("LicenseShortName") or cv("UsageTerms"),"author":cv("Artist"),"description":cv("ImageDescription")}

def score_result(title: str, item: dict):
    n=norm(title); label=norm(item.get("label") or ""); desc=norm(item.get("description") or "")
    score=0
    if n==label: score+=100
    for tok in set(n.split()):
        if len(tok)>3 and tok in label: score+=5
        if len(tok)>3 and tok in desc: score+=1
    if any(x in desc for x in ("орган", "суд", "правитель", "министер", "дума", "служб", "администрац")): score+=5
    return score

def main():
    out=[]
    media={}
    for idx,title in enumerate(INSTITUTIONS,1):
        queries=[title]+ALIASES.get(idx,[])
        by={}
        for q in queries:
            try:
                for item in search(q): by[item["id"]]=item
            except Exception as e: print("search",idx,q,e,flush=True)
            time.sleep(.15)
        ranked=sorted(by.values(),key=lambda x:score_result(title,x),reverse=True)
        candidates=[]
        for item in ranked[:5]:
            try:
                ent=entity(item["id"]); files=claim_files(ent)
            except Exception as e:
                files={}; ent={}
            candidates.append({"qid":item["id"],"label":item.get("label"),"description":item.get("description"),"score":score_result(title,item),"files":files,"sitelinks":ent.get("sitelinks",{})})
            for values in files.values():
                for f in values:
                    if f not in media:
                        try: media[f]=commons_info(f)
                        except Exception as e: media[f]={"error":str(e)}
                        time.sleep(.12)
        out.append({"number":idx,"title":title,"candidates":candidates})
        print(idx,title,[(c['qid'],c['label'],c['score'],c['files']) for c in candidates[:2]],flush=True)
    Path("_quiz50/wikidata_probe.json").write_text(json.dumps({"institutions":out,"media":media},ensure_ascii=False,indent=2),encoding="utf-8")

if __name__=="__main__": main()
