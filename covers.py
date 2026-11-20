import json, re, urllib.request
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0 Safari/537.36"
def get(u, t=40):
    r = urllib.request.Request(u, headers={"User-Agent": UA})
    with urlopen(r, timeout=t) as h:
        return h.read().decode("utf-8", "ignore")
from urllib.request import urlopen
seed = json.load(open("fastapi_backend/app/data/moboreels_catalog.json"))
missing = [r["source_id"] for r in seed if not r.get("cover_url")]
out = {"covers": {}, "media": {}}
for slug in missing:
    try:
        h = get("https://www.moboreels.com/drama/" + slug)
        m = re.search(r'<meta property="og:image" content="([^"]+)"', h)
        if m:
            out["covers"][slug] = m.group(1).split("?")[0]
    except Exception as e:
        out["covers"][slug] = None
one = missing[0]
try:
    eh = get("https://www.moboreels.com/episode/" + one + "-01")
    out["media"]["episode_page_bytes"] = len(eh)
    out["media"]["mp4_urls"] = re.findall(r"https://[^\"\']+\.mp4[^\"\']*", eh)[:3]
    out["media"]["mediaUrl_hits"] = len(re.findall("mediaUrl", eh))
except Exception as e:
    out["media"]["error"] = repr(e)[:200]
open("covers.json", "w").write(json.dumps(out, ensure_ascii=False, indent=1))
print(json.dumps(out, ensure_ascii=False)[:1500])
