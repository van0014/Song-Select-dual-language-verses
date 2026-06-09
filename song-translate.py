# Simple Song Select / CCLI text file translator
# Uses DeepL translation API
# Detects song sections and adds translation below each verse
# By Daniel van Rijthoven

import deepl, os, argparse

# -----------------------------
# Arguments
# -----------------------------
parser = argparse.ArgumentParser()
parser.add_argument('--infile', dest='infile', type=str, help='Input file')
parser.add_argument('--outfile', dest='outfile', type=str, help='Output file')
parser.add_argument('--lang', dest='lang', type=str, help='Language code')
parser.add_argument('--api', dest='apikey', type=str, help='DeepL API key')
args = parser.parse_args()

# -----------------------------
# Input / Output paths
# -----------------------------
patha = args.infile
pathb = args.outfile

# -----------------------------
# Counters (NEW)
# -----------------------------
line_count = 0
translated_count = 0
space = 0
conseq = 0
title = 0
fatal = 0

print("This program takes a CCLI song file")
print("and integrates translated text below each line")
print("using the DeepL translator")
print("")

def write_line(f, text):
    f.write(text.strip() + "\n")
    
# -----------------------------
# API key
# -----------------------------
if args.apikey is None:
    args.apikey = "DeepL API key"

# -----------------------------
# File validation
# -----------------------------
if args.infile is None:
    print("File not found. Exiting")
    fatal += 1

if fatal >= 1:
    print("Program ended.")
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
# Output file handling
# -----------------------------
if args.outfile is None:
    froot, fext = os.path.splitext(patha)
    pathb = os.path.dirname(patha) + "/" + os.path.splitext(os.path.basename(patha))[0] + "_" + args.lang + fext
    args.outfile = pathb
    print("Default file name:", os.path.splitext(os.path.basename(patha))[0] + "_" + args.lang)
else:
    print("Output file name:", os.path.splitext(os.path.basename(pathb))[0] + fext)

# -----------------------------
# File existence check
# -----------------------------
if os.path.isfile(patha) and not os.path.isfile(pathb):

    auth_key = args.apikey
    translator = deepl.Translator(auth_key)

    print("\nBegin processing file:", os.path.splitext(os.path.basename(patha))[0])
    print("")

    with open(args.infile, 'r', encoding='utf8') as firstfile, open(args.outfile, 'w', encoding='utf8') as secondfile:

        for line in firstfile:

            line_count += 1
            raw = line.rstrip("\n")
            stripped = raw.strip()

            print(f"[{line_count}] Processing: {stripped if stripped else '<blank>'}")

            # -----------------------------
            # End conditions (footer)
            # -----------------------------
            if "©" in line:
                print("\n🚫 Copyright detected — stopping processing\n")
                break

            if "CCLI" in line:
                print("\n🚫 CCLI detected — stopping processing\n")
                break

            # -----------------------------
            # Blank lines
            # -----------------------------
            if len(line) <= 1:
                space += 1
                conseq = 0
                print("")
                secondfile.write(line)
                continue
            else:
                space = 0
                conseq += 1

                if title == 0:
                    title = 1
                    print(f"\n🎵 SONG TITLE: {stripped}\n")

            # -----------------------------
            # Section detection (approx)
            # -----------------------------
            if title >= 2 and conseq == 1:
                print(f"\n📌 SECTION: {stripped}\n")

            # -----------------------------
            # Translation block
            # -----------------------------
            if title >= 1 and conseq >= 2:

                try:
                    result = translator.translate_text(line, target_lang=args.lang)
                    translated_text = result.text

                    write_line(secondfile, stripped)
                    write_line(secondfile, translated_text)

                    print(f"🎤 EN: {stripped}")
                    print(f"🌐 TR: {translated_text}")

                    translated_count += 1

                except Exception as e:
                    print("⚠️ Translation error:", e)
                    secondfile.write(line)

            else:
                secondfile.write(line)

            # -----------------------------
            # Progress update
            # -----------------------------
            if translated_count > 0 and translated_count % 10 == 0:
                print(f"\n⏳ Progress: {translated_count} lines translated...\n")

else:
    if not os.path.isfile(patha):
        print("Input file not found")
    else:
        print("Output file already exists. Delete it first.")

# -----------------------------
# Summary
# -----------------------------
print("\n====================")
print("✔ DONE")
print(f"Lines processed: {line_count}")
print(f"Translated lines: {translated_count}")
print("====================\n")
