import re, urllib.request, json
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0 Safari/537.36"
def get(u, t=40):
    req = urllib.request.Request(u, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=t) as r:
        return r.status, r.read().decode("utf-8", "ignore")
out = []
targets = [
  "https://www.moboreels.com/robots.txt",
  "https://www.moboreels.com/sitemap.xml",
  "https://www.moboreels.com/dramas",
  "https://www.moboreels.com/dramas/romance",
  "https://www.moboreels.com/search?keyword=love",
]
for u in targets:
    try:
        st, body = get(u)
        cards = len(re.findall(r"home-list-item-img", body))
        drama = len(set(re.findall(r"/drama/[a-z0-9\-]{6,80}", body)))
        out.append("%s -> %s bytes=%d cards=%d uniq_drama=%d" % (u, st, len(body), cards, drama))
        if "sitemap" in u or "robots" in u:
            out.append("   head: " + body[:300].replace("\n", " "))
    except Exception as e:
        out.append("%s -> ERR %r" % (u, e))
open("result2.md", "w").write("\n".join(out))
print("\n".join(out))
