import json, re, urllib.request, urllib.parse
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0 Safari/537.36"
def get(u, t=45):
    r = urllib.request.Request(u, headers={"User-Agent": UA})
    with urllib.request.urlopen(r, timeout=t) as h:
        return h.read().decode("utf-8", "ignore")
seed = json.load(open("fastapi_backend/app/data/moboreels_catalog.json"))
missing = {r["source_id"] for r in seed if not r.get("cover_url")}
cover = {}
pages = ["/", "/dramas", "/search?keyword=daddy", "/search?keyword=married", "/search?keyword=reborn", "/search?keyword=alpha"]
for p in pages:
    try:
        h = get("https://www.moboreels.com" + p)
    except Exception:
        continue
    for m in re.finditer(r'href="/drama/([a-z0-9\-]{6,90})"[^>]*>\s*<img src="([^"]+)"', h):
        slug, src = m.group(1), m.group(2)
        if slug in missing and slug not in cover:
            cover[slug] = src.split("?")[0]
res = {"covered": len(cover), "missing_total": len(missing), "covers": cover}

slug = sorted(missing)[0]
eh = get("https://www.moboreels.com/episode/" + slug + "-01")
raw = eh.encode().decode("unicode_escape", "ignore")
urls = re.findall(r'https://[^"\\ ]+?\.mp4[^"\\ ]*', raw)
res["episode"] = {"slug": slug, "bytes": len(eh), "mp4_found": len(urls), "url_head": urls[0][:180] if urls else None}
if urls:
    try:
        req = urllib.request.Request(urls[0], headers={"User-Agent": UA, "Range": "bytes=0-1023"})
        with urllib.request.urlopen(req, timeout=45) as h:
            head = h.read(64)
            res["episode"]["download"] = {"status": h.status, "content_type": h.headers.get("content-type"), "first_bytes": head[:16].hex()}
    except Exception as e:
        res["episode"]["download"] = repr(e)[:160]
open("covers2.json", "w").write(json.dumps(res, ensure_ascii=False, indent=1))
print(json.dumps({k: res[k] for k in ["covered", "missing_total", "episode"]}, ensure_ascii=False)[:1200])
