import json, re, urllib.request

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/144.0 Safari/537.36"
MOVIE = "https://www.reelshort.com/movie/what-you-re-in-my-body-695b2e2a1d7ae5789607eeaa"
BOOK = MOVIE.rstrip("/").split("-")[-1]
MAX_EP = 20

def get(u, t=45):
    r = urllib.request.Request(u, headers={"User-Agent": UA, "Referer": "https://www.reelshort.com/"})
    with urllib.request.urlopen(r, timeout=t) as h:
        return h.read().decode("utf-8", "ignore")

page = get(MOVIE)
m = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', page, re.S)
data = json.loads(m.group(1))
info = data["props"]["pageProps"]["data"]
chapters = sorted(
    ({"num": int(c["serial_number"]), "id": c["chapter_id"]} for c in info["online_base"]),
    key=lambda c: c["num"],
)
out = {"book": BOOK, "title": info.get("book_title"), "total": len(chapters), "resolved": {}}
for ch in chapters[:MAX_EP]:
    try:
        html = get("https://www.reelshort.com/en/embed/%s-%s" % (BOOK, ch["id"]))
        urls = re.findall(r"https://[^\"\'\s]{20,300}-video-hd\.m3u8", html) or \
               re.findall(r"https://[^\"\'\s]{20,300}\.m3u8", html)
        if urls:
            out["resolved"][str(ch["num"])] = urls[0]
        print(ch["num"], "ok" if urls else "no-url", flush=True)
    except Exception as e:
        print(ch["num"], "ERR", type(e).__name__, flush=True)
open("rs_urls.json", "w").write(json.dumps(out, ensure_ascii=False, indent=1))
print("resolved", len(out["resolved"]), "/", min(MAX_EP, len(chapters)), flush=True)
