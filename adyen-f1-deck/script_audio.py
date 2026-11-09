"""Turn the pitch script into something to read or listen to on the move.

Writes a plain-text version (no Markdown) and an MP3 read aloud by an offline Piper voice.
Slide headings are spoken ("Slide 3. Competitive landscape."), "Remember" and "Ask Mark" lines are
kept with spoken labels, stage cues are read as "Note", and money and ranges are written out so the
voice reads them naturally.

Usage: python3 script_audio.py "Adyen x F1 - Pitch script.md" out_basename voice.onnx
"""
import re
import subprocess
import sys
import tempfile
import wave
from pathlib import Path

src, out_base, model = sys.argv[1], sys.argv[2], sys.argv[3]
md = open(src, encoding="utf-8").read()

UNITS = {"M": "million", "B": "billion", "bn": "billion", "tn": "trillion", "T": "trillion", "K": "thousand"}
CURR = {"$": "dollars", "€": "euros", "£": "pounds"}


def spoken(t):
    """Make a line easy for a voice to read."""
    t = t.replace("★", "").replace("×", "and").replace("·", ",").replace("→", "then")
    t = re.sub(r"\*\*(.+?)\*\*", r"\1", t)
    t = re.sub(r"(?<!\w)\*(.+?)\*(?!\w)", r"\1", t)
    t = t.replace("~", "about ")
    # €5–8M / €5–8 million  ->  5 to 8 million euros
    t = re.sub(r"([$€£])(\d[\d.,]*)[–-](\d[\d.,]*)\s(million|billion|trillion)",
               lambda m: f"{m.group(2)} to {m.group(3)} {m.group(4)} {CURR[m.group(1)]}", t)
    t = re.sub(r"([$€£])(\d[\d.,]*)[–-](\d[\d.,]*)\s?(M|B|bn|tn|T|K)\b",
               lambda m: f"{m.group(2)} to {m.group(3)} {UNITS[m.group(4)]} {CURR[m.group(1)]}", t)
    t = re.sub(r"([$€£])(\d[\d.,]*)\s?(M|B|bn|tn|T|K)\b\+?",
               lambda m: f"{m.group(2)} {UNITS[m.group(3)]} {CURR[m.group(1)]}", t)
    t = re.sub(r"([$€£])(\d[\d.,]*)\s(million|billion|trillion)",
               lambda m: f"{m.group(2)} {m.group(3)} {CURR[m.group(1)]}", t)
    t = re.sub(r"([$€£])(\d[\d.,]*)\+", lambda m: f"more than {m.group(2)} {CURR[m.group(1)]}", t)
    t = re.sub(r"([$€£])(\d[\d.,]*)", lambda m: f"{m.group(2)} {CURR[m.group(1)]}", t)
    t = re.sub(r"(\d{4})[–-](\d{4})", r"\1 to \2", t)
    t = re.sub(r"(\d+)[–-](\d+)", r"\1 to \2", t)
    t = t.replace("–", ", ").replace("—", ", ")
    t = re.sub(r"\s+", " ", t).strip()
    t = re.sub(r"\s+([.,;:])", r"\1", t)
    return t


def for_voice(t):
    """Spellings that help the voice pronounce names (audio only; the text version keeps the real spelling)."""
    return re.sub(r"\bAdyen", "Add-yen", t)


# split into blocks; build (kind, text) items
items = []
title = ""
for block in re.split(r"\n\s*\n", md.strip()):
    b = block.strip()
    if b.startswith("# "):
        title = b[2:].strip()
        items.append(("title", spoken(title)))
    elif b.startswith("## "):
        h = b[3:].strip()
        m = re.match(r"(\d+) · (.*)", h)
        items.append(("head", spoken(f"Slide {m.group(1)}. {m.group(2)}." if m else h + ".")))
    elif b == "---":
        items.append(("pause", ""))
    else:
        text = " ".join(l.strip() for l in b.splitlines())
        if text.startswith("**Remember:**"):
            items.append(("line", spoken("Remember. " + text[len("**Remember:**"):])))
        elif text.startswith("**Ask Mark:**"):
            items.append(("line", spoken("Question for Mark. " + text[len("**Ask Mark:**"):])))
        elif text.startswith("**Where it's from:**"):
            items.append(("line", spoken("Source. " + text[len("**Where it's from:**"):])))
        elif text.startswith("*") and not text.startswith("**"):
            items.append(("line", spoken("Note. " + text)))
        else:
            items.append(("line", spoken(text)))

# plain-text version
lines = []
for kind, text in items:
    if kind == "title":
        lines += [text.upper(), ""]
    elif kind == "head":
        lines += ["", "=" * 60, text, "=" * 60, ""]
    elif kind == "pause":
        lines += ["", "-" * 60, ""]
    else:
        lines += [text, ""]
Path(out_base + ".txt").write_text("\n".join(lines).strip() + "\n", encoding="utf-8")

# audio
from piper import PiperVoice  # noqa: E402
voice = PiperVoice.load(model)
rate = voice.config.sample_rate
gap = {"title": 1.2, "head": 1.0, "pause": 1.5, "line": 0.6}
with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
    wav_path = tmp.name
with wave.open(wav_path, "wb") as w:
    w.setnchannels(1)
    w.setsampwidth(2)
    w.setframerate(rate)
    for kind, text in items:
        if kind == "head":
            w.writeframes(b"\x00\x00" * int(rate * 0.8))
        if text:
            for chunk in voice.synthesize(for_voice(text)):
                w.writeframes(chunk.audio_int16_bytes)
        w.writeframes(b"\x00\x00" * int(rate * gap[kind]))
subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", wav_path, "-ac", "1", "-b:a", "64k", out_base + ".mp3"], check=True)
Path(wav_path).unlink()
print("wrote", out_base + ".txt", "and", out_base + ".mp3")
