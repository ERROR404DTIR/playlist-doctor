#!/usr/bin/env python3
"""Playlist Doctor — audit and repair local M3U/M3U8 playlists."""
import argparse, json, os, sys
from pathlib import Path
def parse(path, root=None):
    p=Path(path).resolve(); base=Path(root).resolve() if root else p.parent
    lines=p.read_text(encoding="utf-8-sig",errors="replace").splitlines()
    entries=[]; pending=""
    for no,line in enumerate(lines,1):
        line=line.strip()
        if not line: continue
        if line.startswith("#EXTINF:"): pending=line
        elif line.startswith("#"): continue
        else:
            if "://" in line or line.startswith("file:"):
                target=None; kind="remote"
            else:
                raw=Path(line)
                target=(base/raw).resolve() if not raw.is_absolute() else raw.resolve()
                kind="local"
            entries.append({"line":no,"path":line,"title":pending.split(",",1)[1].strip() if "," in pending else "","extinf":pending,"kind":kind,"exists":target.exists() if target else None,"resolved":str(target) if target else None})
            pending=""
    return entries
def main():
    p=argparse.ArgumentParser(description="Find broken, missing and duplicate M3U/M3U8 entries")
    s=p.add_subparsers(dest="cmd",required=True)
    for cmd in ("audit","repair"):
        q=s.add_parser(cmd); q.add_argument("playlist"); q.add_argument("--root",help="resolve relative paths against this media folder")
        if cmd=="audit": q.add_argument("--json")
        else: q.add_argument("--output",required=True,help="write repaired playlist here")
    a=p.parse_args(); src=Path(a.playlist); entries=parse(src,a.root)
    seen={}; missing=[]; duplicates=[]
    for e in entries:
        key=e["resolved"] if e["kind"]=="local" else e["path"].casefold()
        if key in seen: duplicates.append((e["line"],seen[key]))
        else: seen[key]=e["line"]
        if e["kind"]=="local" and not e["exists"]: missing.append(e)
    if a.cmd=="audit":
        print(f"Playlist: {src}\\nEntries: {len(entries)} | Missing: {len(missing)} | Duplicates: {len(duplicates)}")
        for e in missing: print(f"[MISSING] line {e['line']}: {e['path']}")
        for line,first in duplicates: print(f"[DUPLICATE] line {line} repeats line {first}")
        if a.json: Path(a.json).write_text(json.dumps(entries,indent=2,ensure_ascii=False),encoding="utf-8")
        return 1 if missing else 0
    out=[]; used=set()
    for e in entries:
        key=e["resolved"] if e["kind"]=="local" else e["path"].casefold()
        if key in used: continue
        used.add(key)
        if e["extinf"]: out.append(e["extinf"])
        if e["kind"]=="local" and e["exists"]:
            try: line=os.path.relpath(e["resolved"],Path(a.output).resolve().parent).replace(os.sep,"/")
            except ValueError: line=e["resolved"]
        else: line=e["path"]
        out.append(line)
    Path(a.output).write_text("#EXTM3U\\n"+"\\n".join(out)+"\\n",encoding="utf-8")
    print(f"Wrote {a.output}: {len(entries)} input entries, {len(used)} retained, {len(missing)} missing paths left unchanged.")
    return 0
if __name__=="__main__": sys.exit(main())
