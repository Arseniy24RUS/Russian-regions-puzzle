from __future__ import annotations

import html
import io
import json
import re
import time
import urllib.parse
from pathlib import Path

import cairosvg
import requests
from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "out"
PHOTOS = OUT / "photos"
SYMBOLS = OUT / "symbols"
API = "https://commons.wikimedia.org/w/api.php"
UA = "RUDN-GMU-educational-platform/0.7 (media audit; contact: omnistat@yandex.ru)"
SESSION = requests.Session()
SESSION.headers.update({"User-Agent": UA})
ALLOWED = ("cc", "public domain", "pd", "gfdl", "copyrighted free use", "free art")
BAD_LICENSE = ("fair use", "non-free", "copyrighted", "all rights reserved")
PHOTO_BAD = ("logo", "emblem", "coat of arms", "flag", "map", "diagram", "seal", "badge", "icon", "portrait", "stamp", "герб", "флаг", "эмблем", "логотип", "карта", "схема", "портрет")
PHOTO_GOOD = ("building", "headquarters", "city hall", "court", "palace", "house", "administration", "government", "office", "здание", "дворец", "суд", "администрац", "правительств", "дума")
SYMBOL_GOOD = ("logo", "emblem", "coat of arms", "seal", "badge", "symbol", "герб", "эмблем", "логотип", "символ")
SYMBOL_BAD = ("building", "street", "headquarters", "city hall", "court building", "здание", "улица", "дворец")


def clean_markup(value: str | None) -> str:
    value = html.unescape(value or "")
    value = re.sub(r"<[^>]+>", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def tokens(text: str) -> set[str]:
    return {x.lower() for x in re.findall(r"[A-Za-zА-Яа-яЁё0-9]+", text) if len(x) >= 4}


def license_allowed(meta: dict) -> bool:
    lic = " ".join(
        clean_markup((meta.get(key) or {}).get("value"))
        for key in ("LicenseShortName", "UsageTerms", "License")
    ).lower()
    if any(x in lic for x in BAD_LICENSE):
        return False
    return not lic or any(x in lic for x in ALLOWED)


def search(query: str, limit: int = 30) -> list[dict]:
    params = {
        "action": "query",
        "generator": "search",
        "gsrsearch": query,
        "gsrnamespace": 6,
        "gsrlimit": limit,
        "prop": "imageinfo",
        "iiprop": "url|extmetadata|mime|size",
        "iiurlwidth": 1600,
        "format": "json",
        "formatversion": 2,
        "origin": "*",
    }
    r = SESSION.get(API, params=params, timeout=60)
    r.raise_for_status()
    pages = (r.json().get("query") or {}).get("pages") or []
    out = []
    for page in pages:
        ii = (page.get("imageinfo") or [{}])[0]
        meta = ii.get("extmetadata") or {}
        if not license_allowed(meta):
            continue
        url = ii.get("thumburl") or ii.get("url")
        if not url:
            continue
        out.append(
            {
                "title": page.get("title", ""),
                "url": url,
                "original_url": ii.get("url") or url,
                "mime": ii.get("mime", ""),
                "width": int(ii.get("width") or 0),
                "height": int(ii.get("height") or 0),
                "description_url": ii.get("descriptionurl") or "https://commons.wikimedia.org/wiki/" + urllib.parse.quote((page.get("title") or "").replace(" ", "_")),
                "author": clean_markup((meta.get("Artist") or {}).get("value")),
                "credit": clean_markup((meta.get("Credit") or {}).get("value")),
                "license": clean_markup((meta.get("LicenseShortName") or {}).get("value")) or clean_markup((meta.get("UsageTerms") or {}).get("value")),
                "license_url": clean_markup((meta.get("LicenseUrl") or {}).get("value")),
                "description": clean_markup((meta.get("ImageDescription") or {}).get("value")),
            }
        )
    return out


def score(candidate: dict, queries: list[str], kind: str) -> float:
    title = candidate["title"].lower()
    desc = candidate.get("description", "").lower()
    hay = title + " " + desc
    query_tokens = set().union(*(tokens(q) for q in queries))
    value = sum(5 for token in query_tokens if token in hay)
    value += min(candidate.get("width", 0), 2000) / 500
    mime = candidate.get("mime", "").lower()
    if kind == "photo":
        value += sum(12 for w in PHOTO_GOOD if w in hay)
        value -= sum(45 for w in PHOTO_BAD if w in hay)
        if "svg" in mime or title.endswith(".svg"):
            value -= 100
        if candidate.get("width", 0) >= 1000 and candidate.get("height", 0) >= 500:
            value += 8
    else:
        value += sum(18 for w in SYMBOL_GOOD if w in hay)
        value -= sum(35 for w in SYMBOL_BAD if w in hay)
        if "svg" in mime or title.endswith(".svg"):
            value += 25
        if any(title.endswith(ext) for ext in (".svg", ".png")):
            value += 8
    return value


def collect_one(key: str, queries: list[str], kind: str) -> tuple[dict | None, list[dict]]:
    by_title: dict[str, dict] = {}
    expanded = []
    for query in queries:
        expanded.extend([query, f'intitle:"{query}"'])
    for query in expanded:
        try:
            for item in search(query):
                by_title[item["title"]] = item
        except Exception as exc:
            print("SEARCH ERROR", key, query, exc, flush=True)
        time.sleep(0.15)
    candidates = list(by_title.values())
    for item in candidates:
        item["score"] = round(score(item, queries, kind), 3)
    candidates.sort(key=lambda x: x["score"], reverse=True)
    return (candidates[0] if candidates else None), candidates[:10]


def load_image(candidate: dict) -> Image.Image:
    r = SESSION.get(candidate["url"], timeout=90)
    r.raise_for_status()
    data = r.content
    if candidate.get("mime") == "image/svg+xml" or candidate["title"].lower().endswith(".svg"):
        data = cairosvg.svg2png(bytestring=data, output_width=1200, output_height=1200)
    image = Image.open(io.BytesIO(data))
    image.load()
    return image.convert("RGBA")


def save_photo(candidate: dict, path: Path) -> None:
    image = load_image(candidate).convert("RGB")
    image = ImageOps.fit(image, (1600, 900), method=Image.Resampling.LANCZOS, centering=(0.5, 0.5))
    image.save(path, "WEBP", quality=84, method=6)


def save_symbol(candidate: dict, path: Path) -> None:
    image = load_image(candidate)
    bbox = image.getbbox()
    if bbox:
        image = image.crop(bbox)
    image.thumbnail((440, 440), Image.Resampling.LANCZOS)
    canvas = Image.new("RGBA", (512, 512), (255, 255, 255, 0))
    canvas.alpha_composite(image, ((512 - image.width) // 2, (512 - image.height) // 2))
    canvas.save(path, "PNG", optimize=True)


def font(size: int, bold: bool = False):
    paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
    ]
    for p in paths:
        if Path(p).exists():
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def wrap(draw, text, fnt, width):
    words = text.split()
    lines, line = [], ""
    for word in words:
        test = (line + " " + word).strip()
        if draw.textbbox((0, 0), test, font=fnt)[2] <= width:
            line = test
        else:
            if line:
                lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines


def contact_sheet(manifest: dict, photo_meta: dict, symbol_meta: dict):
    cards = []
    for inst in manifest["institutions"]:
        photo_path = PHOTOS / f'{inst["photo_group"]}.webp'
        symbol_path = SYMBOLS / f'{inst["symbol_group"]}.png'
        card = Image.new("RGB", (1200, 700), "white")
        draw = ImageDraw.Draw(card)
        if photo_path.exists():
            photo = Image.open(photo_path).convert("RGB")
            photo = ImageOps.fit(photo, (760, 430), Image.Resampling.LANCZOS)
            card.paste(photo, (0, 0))
        if symbol_path.exists():
            symbol = Image.open(symbol_path).convert("RGBA")
            symbol.thumbnail((280, 280), Image.Resampling.LANCZOS)
            card.paste(symbol, (850 + (280-symbol.width)//2, 65 + (280-symbol.height)//2), symbol)
        draw.rectangle((0, 430, 1200, 700), fill=(247, 250, 253))
        title = f'{inst["number"]}. {inst["title_ru"]}'
        y = 455
        for line in wrap(draw, title, font(31, True), 1140)[:3]:
            draw.text((30, y), line, font=font(31, True), fill=(15, 42, 75)); y += 40
        p = photo_meta.get(inst["photo_group"], {})
        s = symbol_meta.get(inst["symbol_group"], {})
        draw.text((30, 610), f'Фото: {p.get("title", "НЕТ")} | score {p.get("score", "-")}', font=font(18), fill=(80, 90, 105))
        draw.text((30, 642), f'Символ: {s.get("title", "НЕТ")} | score {s.get("score", "-")}', font=font(18), fill=(80, 90, 105))
        cards.append(card)
    cols = 2
    rows = (len(cards) + cols - 1) // cols
    sheet = Image.new("RGB", (cols*1200, rows*700), (225, 232, 240))
    for i, card in enumerate(cards):
        sheet.paste(card, ((i%cols)*1200, (i//cols)*700))
    sheet.save(OUT / "contact_sheet.jpg", quality=87, optimize=True)


def main():
    manifest = json.loads((ROOT / "media-search-manifest.json").read_text(encoding="utf-8"))
    PHOTOS.mkdir(parents=True, exist_ok=True)
    SYMBOLS.mkdir(parents=True, exist_ok=True)
    result = {"photos": {}, "symbols": {}, "candidates": {"photos": {}, "symbols": {}}}
    for kind, groups, directory in (("photo", manifest["photo_groups"], PHOTOS), ("symbol", manifest["symbol_groups"], SYMBOLS)):
        for index, (key, queries) in enumerate(groups.items(), 1):
            print(kind, index, len(groups), key, flush=True)
            selected, candidates = collect_one(key, queries, kind)
            result["candidates"]["photos" if kind == "photo" else "symbols"][key] = candidates
            if selected:
                try:
                    if kind == "photo":
                        save_photo(selected, directory / f"{key}.webp")
                        result["photos"][key] = selected
                    else:
                        save_symbol(selected, directory / f"{key}.png")
                        result["symbols"][key] = selected
                except Exception as exc:
                    print("DOWNLOAD ERROR", kind, key, exc, flush=True)
    (OUT / "commons_media_manifest.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    contact_sheet(manifest, result["photos"], result["symbols"])
    missing = {
        "photos": sorted(set(manifest["photo_groups"]) - set(result["photos"])),
        "symbols": sorted(set(manifest["symbol_groups"]) - set(result["symbols"])),
    }
    (OUT / "missing.json").write_text(json.dumps(missing, ensure_ascii=False, indent=2), encoding="utf-8")
    print("MISSING", missing, flush=True)


if __name__ == "__main__":
    main()
