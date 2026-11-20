#!/usr/bin/env python3
"""海外短剧种子目录抓取（用 GitHub Actions 的海外出口跑，零成本）。

只依赖标准库。流程：
1) 抓 https://www.moboreels.com/ 首页 + /dramas + 首页里的分类页，收集 /drama/<slug> 链接；
2) 对种子里还没有的 slug，抓详情页 SSR，解析集数 / 免费集边界 / 简介 / 封面；
3) 合并写回 fastapi_backend/app/data/moboreels_catalog.json（保留已有 title_zh）。

用法：
    python3 scripts/enrich_overseas_seed.py            # 增量，最多 150 部新剧
    MAX_NEW=400 python3 scripts/enrich_overseas_seed.py
"""

from __future__ import annotations

import json
import os
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.request import Request, urlopen

BASE = "https://www.moboreels.com"
SEED = Path(__file__).resolve().parents[1] / "fastapi_backend/app/data/moboreels_catalog.json"
UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/144.0 Safari/537.36"
)
MAX_NEW = int(os.environ.get("MAX_NEW", "150"))
#: 搜索页在海外出口是 SSR 的，用来把目录从「首页+分类」扩到几百部
SEARCH_TERMS = [
    "love", "revenge", "ceo", "werewolf", "marriage", "rebirth", "billionaire",
    "contract", "alpha", "vampire", "divorce", "pregnant", "secret", "mafia",
    "system", "cultivation", "romance", "family", "hate", "reborn",
]
WORKERS = int(os.environ.get("WORKERS", "6"))
TIMEOUT = 30


def fetch(url: str, timeout: int = TIMEOUT) -> str:
    req = Request(url, headers={"User-Agent": UA, "Accept-Language": "en"})
    with urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", "ignore")


def slugs_from(html: str) -> set[str]:
    return set(re.findall(r"/drama/([a-z0-9][a-z0-9\-]{5,80})", html))


def category_pages(html: str) -> set[str]:
    return {"/dramas/" + c for c in set(re.findall(r'href="(/dramas/[a-z0-9\-]{2,30})"', html))}


def parse_detail(html: str, slug: str) -> dict:
    data: dict = {"source_id": slug}
    title = re.search(r'<meta property="og:title" content="([^"]+)"', html)
    if title:
        data["title"] = title.group(1).replace(" - MoboReels", "").strip()
    cover = re.search(r'<meta property="og:image" content="([^"]+)"', html)
    if cover:
        data["cover_url"] = cover.group(1).split("?")[0]
    intro = re.search(r'<meta property="og:description" content="([^"]+)"', html)
    if intro:
        data["intro"] = intro.group(1).strip()[:1000]

    counts = [int(n) for n in re.findall(r"(\d{1,4})\s*Episodes", html)]
    counts = [c for c in counts if 0 < c <= 1000]
    if counts:
        data["episode_total"] = max(set(counts), key=counts.count)
        data["episode_count"] = f"全 {data['episode_total']} 集"

    # __NUXT__ 里 payEpisFrom 是压缩引用，退一步用页面文案里的 free 区间
    free = re.search(r"(\d{1,4})\s*Episodes?\s*Free|Free Episodes?:\s*(\d{1,4})", html, re.I)
    if free:
        val = free.group(1) or free.group(2)
        try:
            data["free_until"] = int(val)
        except (TypeError, ValueError):
            pass
    return data


def main() -> int:
    seed = json.loads(SEED.read_text("utf-8")) if SEED.exists() else []
    known = {row["source_id"] for row in seed}
    print(f"seed={len(seed)} known_slugs={len(known)}", flush=True)

    urls: set[str] = set()
    try:
        home = fetch(BASE + "/")
        urls |= slugs_from(home)
        listing_pages = {"/dramas"} | category_pages(home)
    except Exception as exc:  # noqa: BLE001
        print("home failed:", exc, flush=True)
        listing_pages = {"/dramas"}

    for path in sorted(listing_pages)[:40]:
        try:
            urls |= slugs_from(fetch(BASE + path))
            print(f"  {path}: cumulative {len(urls)}", flush=True)
        except Exception as exc:  # noqa: BLE001
            print(f"  {path} failed: {exc}", flush=True)

    if os.environ.get("USE_SEARCH", "1") == "1":
        for term in SEARCH_TERMS:
            try:
                urls |= slugs_from(fetch(f"{BASE}/search?keyword={term}"))
            except Exception as exc:  # noqa: BLE001
                print(f"  search {term} failed: {exc}", flush=True)
        print(f"after search terms: {len(urls)} slugs", flush=True)

    fresh = sorted(urls - known)[:MAX_NEW]
    print(f"new slugs to fetch: {len(fresh)}", flush=True)

    added: list[dict] = []
    errors = 0

    def work(slug: str) -> dict | None:
        try:
            return parse_detail(fetch(f"{BASE}/drama/{slug}"), slug)
        except Exception:  # noqa: BLE001
            return None

    t0 = time.time()
    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        for idx, item in enumerate(pool.map(work, fresh), 1):
            if not item:
                errors += 1
                continue
            item.setdefault("source", "MoboReels")
            item.setdefault("source_url", f"{BASE}/drama/{item['source_id']}")
            item.setdefault("title", item["source_id"])
            item["title_zh"] = None
            item["category"] = None
            item["downloadable"] = True
            added.append(item)
            if idx % 20 == 0:
                print(f"  parsed {idx}/{len(fresh)} ok={len(added)} err={errors}", flush=True)

    merged = seed + added
    for row in merged:
        if not row.get("source_url"):
            row["source_url"] = f"{BASE}/drama/{row['source_id']}"
    SEED.write_text(json.dumps(merged, ensure_ascii=False, indent=1), "utf-8")
    with_counts = sum(1 for r in merged if r.get("episode_total"))
    print(
        f"DONE total={len(merged)} added={len(added)} errors={errors} "
        f"with_episode_total={with_counts} elapsed={time.time() - t0:.0f}s",
        flush=True,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
