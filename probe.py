import json, re, urllib.request

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0 Safari/537.36"
SLUG = "a-village-girl-tamed-the-citys-most-wanted-72945322"
out = []

def get(url, headers=None, timeout=40):
    req = urllib.request.Request(url, headers={"User-Agent": UA, **(headers or {})})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.status, r.read()

out.append("## detail page SSR")
try:
    st, body = get("https://www.moboreels.com/drama/" + SLUG)
    html = body.decode("utf-8", "ignore")
    out.append("status %s bytes %s" % (st, len(body)))
    out.append("episode links: %d" % len(re.findall(r"/episode/", html)))
    for kw in ["lastEpis", "allEpis", "payEpisFrom"]:
        found = re.findall(kw + r"[^,}]{0,24}", html)
        out.append(kw + ": " + str(found[:3]))
    m = re.findall(r"(\d{1,3})\s*(?:Episodes|episodes)", html)
    out.append("episodes-text: " + str(m[:5]))
except Exception as e:
    out.append("detail page failed: %r" % (e,))

out.append("")
out.append("## api variants")
variants = [
    "https://videoapi-hk.cdreader.com/video/h5/series/detail?seriesId=72945322",
    "https://videoapi-hk.cdreader.com/video/h5/series/detail?id=72945322",
    "https://videoapi-hk.cdreader.com/video/series/detail?seriesId=72945322",
    "https://videoapi-hk.cdreader.com/video/h5/series/72945322",
    "https://videoapi-hk.cdreader.com/video/h5/series/episodes?seriesId=72945322",
]
for u in variants:
    try:
        st, body = get(u, {"Referer": "https://www.moboreels.com/", "Origin": "https://www.moboreels.com"})
        out.append("%s -> %s %s bytes | %s" % (u.split("/video/")[-1], st, len(body), body[:120].decode("utf-8", "ignore")))
    except Exception as e:
        out.append("%s -> ERR %r" % (u.split("/video/")[-1], e))

open("result.md", "w").write("\n".join(out))
print("\n".join(out))
