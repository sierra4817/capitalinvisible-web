# -*- coding: utf-8 -*-
import json, re, subprocess

with open('capitulos_data.js', encoding='utf-8') as f:
    content = f.read()
m = re.search(r"const\s+CAPITULOS\s*=\s*(\[.*\])", content, flags=re.DOTALL)
capitulos = json.loads(m.group(1))

lines = [";FFMETADATA1", "title=La Mente Millonaria es Invisible",
         "artist=Albert Sierra", "album=La Mente Millonaria es Invisible"]
start_ms = 0
for c in capitulos:
    dur = float(subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", c["audio"]]).decode().strip())
    dur_ms = round(dur * 1000)
    end_ms = start_ms + dur_ms
    lines += ["[CHAPTER]", "TIMEBASE=1/1000", f"START={start_ms}", f"END={end_ms}", f"title={c['titulo']}"]
    print(f"{c['id']:60s} {start_ms:>10d} -> {end_ms:>10d}")
    start_ms = end_ms

with open("chapters_metadata.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(lines) + "\n")

print(f"\nTotal duracion: {start_ms/1000/60:.1f} min")
