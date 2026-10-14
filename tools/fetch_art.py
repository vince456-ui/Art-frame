#!/usr/bin/env python3
"""Fetch public domain paintings from the Met Museum API and prepare them for the art frame.

Output (in --out):
    art/0001.jpg    800x480 baseline JPEG, art letterboxed into the top 800x440, bottom 40 px black (caption strip)
    art/0001.json   {"title", "artist", "date", "met_id", "url"}
    art/index.json  ordered list of entries
    time.txt        placeholder showing the format for setting the RTC (edit before copying)

Usage:
    python fetch_art.py --count 365 --out out
"""
import argparse
import io
import json
import random
import sys
import time
import unicodedata
from pathlib import Path

import requests
from PIL import Image

API = "https://collectionapi.metmuseum.org/public/collection/v1"
SCREEN_W, SCREEN_H = 800, 480
CAPTION_H = 40
ART_H = SCREEN_H - CAPTION_H

# Met department ids: 11 = European Paintings, 21 = Modern and Contemporary Art,
# 1 = American Decorative Arts (skip), 9 = Drawings and Prints (skip).
DEFAULT_DEPARTMENTS = [11]


def to_ascii(text: str) -> str:
    """Embedded fonts rarely have accents, so strip them."""
    for src, dst in (("’", "'"), ("‘", "'"), ("“", '"'), ("”", '"'),
                     ("–", "-"), ("—", "-"), ("æ", "ae"), ("œ", "oe")):
        text = text.replace(src, dst)
    norm = unicodedata.normalize("NFKD", text)
    return "".join(c for c in norm if not unicodedata.combining(c)).encode("ascii", "ignore").decode()


def get(session: requests.Session, url: str, **params):
    for attempt in range(4):
        try:
            r = session.get(url, params=params, timeout=30)
            if r.status_code == 200:
                return r
            if r.status_code in (403, 429, 503):
                time.sleep(2 * (attempt + 1))
                continue
            return None
        except requests.RequestException:
            time.sleep(2 * (attempt + 1))
    return None


def search_ids(session, departments, query):
    ids = set()
    for dep in departments:
        r = get(session, f"{API}/search", isPublicDomain="true", hasImages="true",
                departmentId=dep, q=query)
        if r is not None:
            ids.update(r.json().get("objectIDs") or [])
    return sorted(ids)


def letterbox(img: Image.Image) -> Image.Image:
    img = img.convert("RGB")
    img.thumbnail((SCREEN_W, ART_H), Image.LANCZOS)
    canvas = Image.new("RGB", (SCREEN_W, SCREEN_H), (0, 0, 0))
    x = (SCREEN_W - img.width) // 2
    y = (ART_H - img.height) // 2
    canvas.paste(img, (x, y))
    return canvas


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--count", type=int, default=365, help="number of artworks to keep")
    ap.add_argument("--out", default="out")
    ap.add_argument("--departments", type=int, nargs="+", default=DEFAULT_DEPARTMENTS)
    ap.add_argument("--query", default="painting")
    ap.add_argument("--min-ratio", type=float, default=1.2, help="min width/height of source image")
    ap.add_argument("--max-ratio", type=float, default=2.0, help="max width/height of source image")
    ap.add_argument("--seed", type=int, default=42, help="shuffle seed, same seed gives same order")
    ap.add_argument("--quality", type=int, default=88)
    ap.add_argument("--keep-accents", action="store_true", help="do not transliterate text to ASCII")
    args = ap.parse_args()

    out = Path(args.out)
    art = out / "art"
    art.mkdir(parents=True, exist_ok=True)

    session = requests.Session()
    session.headers["User-Agent"] = "art-frame-fetcher/0.1"

    print("Searching the Met collection...")
    ids = search_ids(session, args.departments, args.query)
    if not ids:
        sys.exit("No results. Check the network or the query.")
    random.Random(args.seed).shuffle(ids)
    print(f"{len(ids)} candidates")

    entries = []
    n = 0
    for oid in ids:
        if n >= args.count:
            break
        r = get(session, f"{API}/objects/{oid}")
        time.sleep(0.05)  # stay far below the 80 req/s limit
        if r is None:
            continue
        o = r.json()
        if not o.get("isPublicDomain") or not o.get("primaryImage"):
            continue

        ir = get(session, o["primaryImage"])
        if ir is None:
            continue
        try:
            src = Image.open(io.BytesIO(ir.content))
            src.load()
        except Exception:
            continue

        ratio = src.width / src.height
        if not (args.min_ratio <= ratio <= args.max_ratio):
            continue

        n += 1
        name = f"{n:04d}"
        letterbox(src).save(art / f"{name}.jpg", "JPEG", quality=args.quality,
                            progressive=False, optimize=False, subsampling=0)

        title = o.get("title") or "Untitled"
        artist = o.get("artistDisplayName") or "Unknown artist"
        date = o.get("objectDate") or ""
        if not args.keep_accents:
            title, artist, date = to_ascii(title), to_ascii(artist), to_ascii(date)
        meta = {"title": title, "artist": artist, "date": date,
                "met_id": oid, "url": o.get("objectURL", "")}
        (art / f"{name}.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
        entries.append({"file": f"{name}.jpg", "meta": f"{name}.json"})
        print(f"[{n}/{args.count}] {artist} - {title}")

    (art / "index.json").write_text(json.dumps({"count": len(entries), "entries": entries}, indent=2),
                                    encoding="utf-8")
    (out / "time.txt").write_text("2026-01-01 00:00\n", encoding="utf-8")
    print(f"Done: {len(entries)} images in {art}")
    if len(entries) < args.count:
        print("Fewer than requested. Widen --min-ratio/--max-ratio or add --departments.")


if __name__ == "__main__":
    main()
