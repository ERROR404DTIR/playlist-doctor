# Playlist Doctor

<p align="center"><img src="assets/banner.svg" alt="Playlist Doctor animated banner" width="100%"></p>

**Fix the playlist, not your music folder.** Playlist Doctor audits M3U/M3U8 files locally, finds missing tracks and duplicate references, and can write a cleaned playlist.

## Features
- M3U and M3U8 parsing, including EXTINF titles
- Missing local-file detection
- Duplicate path detection
- Optional alternate media root for moved libraries
- Repair output with portable relative paths
- Remote stream URLs are preserved, not downloaded or contacted

## Run

Python 3.9+; no dependencies:

```bash
python app.py audit ./mix.m3u
python app.py audit ./mix.m3u --root /media/Music --json report.json
python app.py repair ./mix.m3u --root /media/Music --output ./mix-fixed.m3u
```

Repair never deletes or moves audio files. It writes a new playlist and leaves missing entries visible so you can review them.