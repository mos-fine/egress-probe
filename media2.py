import json, re, urllib.request
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0 Safari/537.36"
def get(u, t=45, extra=None):
    h = {"User-Agent": UA}
    if extra: h.update(extra)
    r = urllib.request.Request(u, headers=h)
    with urllib.request.urlopen(r, timeout=t) as resp:
        return resp.status, resp.headers.get("content-type"), resp.read()
out = {}
html = get("https://www.moboreels.com/episode/broke-his-heart-to-keep-it-beating-194304322-01")[2].decode("utf-8", "ignore")
raw = html.encode().decode("unicode_escape", "ignore")
urls = re.findall(r'https://[^"\\ ]+?\.mp4[^"\\ ]*', raw)
out["url"] = urls[0] if urls else None
if urls:
    for name, extra in [("none", None), ("referer", {"Referer": "https://www.moboreels.com/", "Origin": "https://www.moboreels.com"})]:
        try:
            st, ct, body = get(urls[0], extra=extra)
            out[name] = {"status": st, "ctype": ct, "bytes": len(body), "magic": body[:12].hex()}
        except Exception as e:
            out[name] = repr(e)[:120]
open("media2.json", "w").write(json.dumps(out, ensure_ascii=False, indent=1))
print(json.dumps(out, ensure_ascii=False)[:900])
