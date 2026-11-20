import json, re, urllib.request

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0 Safari/537.36"
BASE = "https://www.moboreels.com"
SLUG = "the-hockey-stars-contract-cruise-fiancee-193718322"
INDEXES = list(range(1, 21))

def get(u, t=40):
    r = urllib.request.Request(u, headers={"User-Agent": UA, "Referer": BASE + "/"})
    with urllib.request.urlopen(r, timeout=t) as h:
        return h.read().decode("utf-8", "ignore")

MEDIA_HOSTS = ("overseas-video.cdreader.com", "cdn6video.cdreader.com", "cdn2video.cdreader.com",
               "video-cdn2.cdreader.com", "video-cdn3.cdreader.com", "cdnvideo.cdreader.com")

def media_of(html):
    text = html.replace(chr(92) + "u002F", "/").replace(chr(92) + "/", "/")
    urls = re.findall(r"https://[^\"\'\s\)<>,]{20,600}", text)
    cands = [u for u in urls if any(h in u for h in MEDIA_HOSTS)]
    cands.sort(key=lambda u: (0 if ".mp4" in u else 1 if ("?t=" in u or "sign=" in u) else 2, -len(u)))
    return cands[0] if cands else None

out = {"slug": SLUG, "resolved": {}, "page_bytes": {}}
for idx in INDEXES:
    url = "%s/episode/%s-%02d" % (BASE, SLUG, idx)
    try:
        html = get(url)
        m = media_of(html)
        out["page_bytes"][str(idx)] = len(html)
        if m:
            out["resolved"][str(idx)] = m
        print(idx, len(html), "media" if m else "no-media", flush=True)
    except Exception as e:
        print(idx, "ERR", type(e).__name__, flush=True)

open("media_urls.json", "w").write(json.dumps(out, ensure_ascii=False, indent=1))
print("resolved", len(out["resolved"]), "/", len(INDEXES), flush=True)
