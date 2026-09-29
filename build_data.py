#!/usr/bin/env python3
"""Build data/ for Learn a Word from a Kaikki.org (Wiktextract) English-language JSONL file.

Usage:  python build_data.py kaikki.org-dictionary-English.jsonl [--min-langs 10] [--max-words 0]
Accepts .jsonl or .jsonl.gz. Writes data/meta.json and data/w/<n>.json (one small file per word).

Word data: Wiktionary contributors, via Kaikki.org (Wiktextract), CC BY-SA 4.0.
"""
import argparse, gzip, json, random, re, shutil
from collections import defaultdict
from pathlib import Path

POS = {"noun", "verb", "adj", "adv"}
WORD = re.compile(r"^[a-z]+$")  # single lowercase words only: no names, no phrases


def build(entry):
    # Wiktionary groups translations by sense ("fruit", "computer company"...).
    # Keep the sense with the most languages so the course teaches one meaning.
    groups, roms, names = defaultdict(dict), defaultdict(dict), {}
    for t in entry.get("translations", []):
        code, form = t.get("code"), (t.get("word") or "").strip()
        if not code or not form or code == "en":
            continue
        names[code] = t.get("lang") or code  # Wiktionary's name, used when the browser doesn't know the code
        key = (t.get("sense") or "").strip().lower()
        forms = groups[key].setdefault(code, [])
        if form not in forms and len(forms) < 3:
            forms.append(form)
        if t.get("roman") and code not in roms[key]:
            roms[key][code] = t["roman"].strip()
    if not groups:
        return None
    key = max(groups, key=lambda k: len(groups[k]))
    glosses = [g for s in entry.get("senses", []) for g in s.get("glosses", [])]
    definition = next((g for g in glosses if key and key in g.lower()),
                      key or (glosses[0] if glosses else ""))
    return {"w": entry["word"], "def": {"en": definition}, "tr": groups[key],
            "rom": {c: r for c, r in roms[key].items() if c in groups[key]},
            "ln": {c: names[c] for c in groups[key]}}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("source")
    ap.add_argument("--min-langs", type=int, default=10, help="skip words with fewer translations")
    ap.add_argument("--max-words", type=int, default=0, help="random subset size (0 = keep all)")
    a = ap.parse_args()

    best = {}
    with (gzip.open if a.source.endswith(".gz") else open)(a.source, "rt", encoding="utf-8") as f:
        for n, line in enumerate(f, 1):
            if '"translations"' not in line:  # cheap pre-filter, skips most lines
                continue
            e = json.loads(line)
            w = e.get("word", "")
            if e.get("lang_code") != "en" or e.get("pos") not in POS or not WORD.match(w):
                continue
            r = build(e)
            if r and len(r["tr"]) >= a.min_langs and (w not in best or len(r["tr"]) > len(best[w]["tr"])):
                best[w] = r
            if n % 200000 == 0:
                print(f"{n} lines read, {len(best)} words kept")

    words = sorted(best)
    random.Random(1).shuffle(words)
    if a.max_words:
        words = words[:a.max_words]
    out = Path("data")
    shutil.rmtree(out / "w", ignore_errors=True)
    (out / "w").mkdir(parents=True)
    for i, w in enumerate(words):
        (out / "w" / f"{i}.json").write_text(
            json.dumps(best[w], ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    (out / "meta.json").write_text(json.dumps({"count": len(words)}))
    print(f"Done: {len(words)} words written to data/")


if __name__ == "__main__":
    main()
