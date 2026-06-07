import deepl
import os
import argparse
import re

# -----------------------------
# Args
# -----------------------------
parser = argparse.ArgumentParser()
parser.add_argument('--infile', type=str)
parser.add_argument('--outfile', type=str)
parser.add_argument('--lang', type=str)
parser.add_argument('--api', type=str)
args = parser.parse_args()

if not args.infile:
    exit("No input file")

if not args.lang:
    args.lang = "ZH-HANS"

if not args.api:
    args.api = "51a696aa-01af-41fa-9418-0f75d1694bd3:fx"

translator = deepl.Translator(args.api)

patha = args.infile
pathb = args.outfile

if not pathb:
    pathb = os.path.splitext(patha)[0] + "_" + args.lang + os.path.splitext(patha)[1]

if os.path.isfile(pathb):
    exit("Output already exists")

# -----------------------------
# Strict metadata filter
# -----------------------------
def is_metadata(line):
    t = line.strip()

    if not t:
        return False

    # CCLI / copyright / SongSelect
    if (
        t.startswith("CCLI") or
        t.startswith("©") or
        "songselect" in t.lower() or
        "ccli.com" in t.lower()
    ):
        return True

    # Song number lines
    if re.match(r"^CCLI Song #\d+", t, re.I):
        return True

    # Artist line heuristic (comma-separated names, no verbs)
    if (
        "," in t and
        len(t.split()) <= 12 and
        not re.search(r"\b(i|you|we|he|she|make|love|praise|lord)\b", t.lower())
    ):
        return True

    # Copyright/publisher lines
    if re.search(r"\b\d{4}\b.*(music|publishing|rights|reserved)", t.lower()):
        return True

    return False


# -----------------------------
# Section detection
# -----------------------------
def is_section(line):
    t = line.strip().lower()
    patterns = [
        r"^verse(?:\s+\d+)?$",
        r"^chorus(?:\s+\d+)?$",
        r"^bridge(?:\s+\d+)?$",
        r"^pre[- ]?chorus$",
        r"^post[- ]?chorus$",
        r"^intro$",
        r"^outro$",
        r"^tag$",
        r"^refrain$",
    ]
    return any(re.match(p, t) for p in patterns)


# -----------------------------
# Read file
# -----------------------------
with open(patha, "r", encoding="utf8") as f:
    lines = [l.rstrip("\n") for l in f.readlines()]

output = []
cache = {}

song_title_written = False

# -----------------------------
# Process
# -----------------------------
for line in lines:
    s = line.strip()

    # metadata → skip entirely
    if is_metadata(s):
        continue

    # blank
    if not s:
        output.append("")
        continue

    # title (first real line)
    if not song_title_written:
        output.append(s + " - " + args.lang)
        song_title_written = True
        continue

    # section headings
    if is_section(s):
        output.append(s)
        continue

    # lyric line
    if s in cache:
        translation = cache[s]
    else:
        try:
            result = translator.translate_text(s, target_lang=args.lang)
            translation = result.text
            cache[s] = translation
        except Exception:
            translation = "[translation error]"

    output.append(s)
    output.append(translation)

# -----------------------------
# Write output
# -----------------------------
with open(pathb, "w", encoding="utf8") as f:
    for o in output:
        f.write(o + "\n")

print("Finished:", os.path.basename(pathb))
