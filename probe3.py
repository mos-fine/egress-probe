import re, urllib.request
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0 Safari/537.36"
def get(u, t=40):
    req = urllib.request.Request(u, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=t) as r:
        return r.read().decode("utf-8", "ignore")
out = []
def slugs(h):
    return set(re.findall(r"/drama/([a-z0-9][a-z0-9\-]{5,80})", h))
home = get("https://www.moboreels.com/")
out.append("home cards=%d slugs=%d" % (len(re.findall("home-list-item-img", home)), len(slugs(home))))
srcs = re.findall(r"src=.\/_(nuxt)/[a-z0-9]+\.js.", home)
script_paths = re.findall(r'src="(/_nuxt/[a-z0-9]+\.js)"', home)[:10]
out.append("scripts: %d" % len(script_paths))
apis = set()
for s in script_paths:
    try:
        js = get("https://www.moboreels.com" + s)
        for m in re.findall(r"\"(/(?:video|api)/[a-zA-Z0-9/_.-]{2,60})\"", js):
            apis.add(m)
    except Exception as e:
        out.append("  js %s failed %r" % (s, e))
out.append("api strings: %d" % len(apis))
for a in sorted(apis)[:40]:
    out.append("  " + a)
out.append("")
out.append("## paging tests")
for u in [
  "https://www.moboreels.com/search?keyword=love&page=2",
  "https://www.moboreels.com/dramas?page=2",
  "https://www.moboreels.com/dramas/romance?page=2",
  "https://www.moboreels.com/dramas/romance/2",
  "https://www.moboreels.com/dramas/all",
]:
    try:
        h = get(u)
        out.append("%s -> bytes=%d slugs=%d" % (u.split("moboreels.com")[1], len(h), len(slugs(h))))
    except Exception as e:
        out.append("%s -> ERR %r" % (u.split("moboreels.com")[1], e))
open("result3.md", "w").write("\n".join(out))
print("\n".join(out))
