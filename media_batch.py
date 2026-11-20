import json, re, time, urllib.request

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0 Safari/537.36"
BASE = "https://www.moboreels.com"
SLUG = "the-hockey-stars-contract-cruise-fiancee-193718322"
INDEXES = list(range(1, 21))
MEDIA_HOSTS = ("overseas-video.cdreader.com", "cdn6video.cdreader.com", "cdn2video.cdreader.com",
               "video-cdn2.cdreader.com", "video-cdn3.cdreader.com", "cdnvideo.cdreader.com")

def get(u, t=60):
    r = urllib.request.Request(u, headers={"User-Agent": UA, "Referer": BASE + "/"})
    with urllib.request.urlopen(r, timeout=t) as h:
        return h.read()

def media_of(html):
    text = html.replace(chr(92) + "u002F", "/").replace(chr(92) + "/", "/")
    urls = re.findall(r"https://[^\"\'\s\)<>,]{20,600}", text)
    c = [u for u in urls if any(h in u for h in MEDIA_HOSTS)]
    c.sort(key=lambda u: (0 if ".mp4" in u else 1, -len(u)))
    return c[0] if c else None

out = {"rows": [], "ok": 0, "fail": 0, "bytes": 0}
t0 = time.time()
for idx in INDEXES:
    t = time.time()
    try:
        html = get("%s/episode/%s-%02d" % (BASE, SLUG, idx)).decode("utf-8", "ignore")
        url = media_of(html)
        if not url:
            raise RuntimeError("no media url")
        blob = get(url, t=180)
        magic = blob[:12]
        ok = magic[4:8] == b"ftyp"
        out["rows"].append({"ep": idx, "bytes": len(blob), "ftyp": ok, "secs": round(time.time() - t, 1)})
        out["ok"] += 1 if ok else 0
        out["fail"] += 0 if ok else 1
        out["bytes"] += len(blob)
        print("ep%02d %9d B ftyp=%s %5.1fs" % (idx, len(blob), ok, time.time() - t), flush=True)
    except Exception as e:
        out["fail"] += 1
        out["rows"].append({"ep": idx, "error": type(e).__name__})
        print("ep%02d ERR %s" % (idx, type(e).__name__), flush=True)
wall = time.time() - t0
out["wall"] = round(wall, 1)
open("media_batch.json", "w").write(json.dumps(out, ensure_ascii=False, indent=1))
print("SUMMARY ok=%d fail=%d bytes=%d wall=%.1fs avg=%.2fs/ep speed=%.2fMB/s" % (
      out["ok"], out["fail"], out["bytes"], wall, wall / len(INDEXES), out["bytes"] / 1048576 / wall), flush=True)
