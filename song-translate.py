# Simple Song Select / CCLI text file translator
# Uses DeepL translation API
# Detects song sections and adds translation below each lyric line
# Stable live-use version

import deepl
import os
import argparse
import re


# -----------------------------
# Arguments
# -----------------------------
parser = argparse.ArgumentParser()
parser.add_argument('--infile', dest='infile', type=str, help='Input file')
parser.add_argument('--outfile', dest='outfile', type=str, help='Output file')
parser.add_argument('--lang', dest='lang', type=str, help='Language code (e.g. ZH-HANS, ES, FR)')
parser.add_argument('--api', dest='apikey', type=str, help='DeepL API key')
args = parser.parse_args()


# -----------------------------
# Performance helpers
# -----------------------------
translation_cache = {}
recent_lyrics = []


print("This program takes a CCLI song file")
print("and integrates translated text below each lyric line")
print("using the DeepL translator")
print("")


# -----------------------------
# API key
# -----------------------------
if args.apikey is None:
    args.apikey = "51a696aa-01af-41fa-9418-0f75d1694bd3:fx"


# -----------------------------
# Validation
# -----------------------------
if args.infile is None:
    print("Input file not specified.")
    exit()


# -----------------------------
# Language
# -----------------------------
if args.lang is None:
    args.lang = "ZH-HANS"
    print("Using default language:", args.lang)
else:
    print("Language:", args.lang)


# -----------------------------
# Paths
# -----------------------------
patha = args.infile
pathb = args.outfile

if args.outfile is None:
    pathb = (
        os.path.splitext(patha)[0]
        + "_"
        + args.lang
        + os.path.splitext(patha)[1]
    )
    print("Default file name:", os.path.basename(pathb))
else:
    print("Output file name:", os.path.basename(pathb))


# -----------------------------
# Section detection
# -----------------------------
def is_section_heading(text):
    text = text.strip().lower()

    patterns = [
        r"^verse(?:\s+\d+)?$",
        r"^chorus(?:\s+\d+)?$",
        r"^bridge(?:\s+\d+)?$",
        r"^pre[- ]?chorus$",
        r"^post[- ]?chorus$",
        r"^intro$",
        r"^outro$",
        r"^ending$",
        r"^tag$",
        r"^instrumental$",
        r"^interlude$",
        r"^refrain$",
        r"^leader(?:\s+only)?$",
        r"^spoken$",
    ]

    return any(re.match(p, text) for p in patterns)


# -----------------------------
# File checks
# -----------------------------
if not os.path.isfile(patha):
    print("Input file not found")
    exit()

if os.path.isfile(pathb):
    print("Output file already exists. Delete it first.")
    exit()


# -----------------------------
# DeepL init
# -----------------------------
translator = deepl.Translator(args.apikey)

print("Begin processing:", os.path.basename(patha))
print("")


# -----------------------------
# Read file
# -----------------------------
with open(args.infile, 'r', encoding='utf8') as f:
    lines = f.readlines()


# -----------------------------
# Clean blank lines (safe pass-through)
# -----------------------------
cleaned_lines = []

for i, line in enumerate(lines):
    if line.strip():
        cleaned_lines.append(line)
        continue

    # keep blank line only if next non-empty is a section heading
    for j in range(i + 1, len(lines)):
        if lines[j].strip():
            if is_section_heading(lines[j].strip()):
                cleaned_lines.append(line)
            break


# -----------------------------
# Processing
# -----------------------------
song_title_found = False
in_footer = False
footer_started = False

with open(pathb, 'w', encoding='utf8') as out:

    for line in cleaned_lines:

        stripped = line.strip()


        # -------------------------
        # Footer detection (STRICT)
        # -------------------------
        if stripped.startswith("CCLI") or stripped.startswith("©"):
            in_footer = True


        if in_footer:
            if not footer_started:
                out.write("\n")
                footer_started = True

            out.write(stripped + "\n")
            print(stripped)
            continue


        # -------------------------
        # Song title
        # -------------------------
        if not song_title_found and stripped:
            song_title_found = True

            song_title = stripped
            if not song_title.endswith(f" - {args.lang}"):
                song_title = f"{song_title} - {args.lang}"

            out.write(song_title + "\n")
            print("Song title -", song_title)
            continue


        # -------------------------
        # Blank lines
        # -------------------------
        if stripped == "":
            out.write("\n")
            continue


        # -------------------------
        # Section headings
        # -------------------------
        if is_section_heading(stripped):
            out.write(stripped + "\n")
            print(stripped)
            continue


        # -------------------------
        # Artist line protection (pre-footer metadata)
        # -------------------------
        if (
            not song_title_found
            or ("," in stripped and len(stripped.split()) <= 12)
        ):
            # likely artist line
            if "," in stripped:
                out.write("\n")
                out.write(stripped + "\n")
                print(stripped)
                continue


        # -------------------------
        # Duplicate lyric skip
        # -------------------------
        if stripped in recent_lyrics:
            out.write(stripped + "\n")
            print("(dup skip)", stripped)
            continue

        recent_lyrics.append(stripped)
        if len(recent_lyrics) > 50:
            recent_lyrics.pop(0)


        # -------------------------
        # Translation (cached)
        # -------------------------
        try:

            if stripped in translation_cache:
                translated = translation_cache[stripped]
            else:
                result = translator.translate_text(
                    stripped,
                    target_lang=args.lang
                )
                translated = result.text
                translation_cache[stripped] = translated

            out.write(stripped + "\n")
            out.write(translated + "\n")

            print(stripped)
            print(translated)

        except Exception as e:
            print("Translation error:", e)
            out.write(stripped + "\n")


print("")
print("Finished.")
