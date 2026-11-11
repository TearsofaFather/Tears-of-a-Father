# Tears of a Father: PC render kit
Branch `render-kit` only (the website deploys from `main`; nothing here touches it).
- `setup.ps1`: one-time setup and the comparison test.
- `run.py queue`: renders `queue.txt` earliest first and uploads each chapter's mp3 + timing file to `out/` on this branch. Safe to stop (Ctrl+C) and restart; finished chapters are skipped.
- Voice code, speaker files, pronunciation cache: identical to the cloud pipeline as of Nov 9, 2026. Model: Kokoro v1.0 ONNX (checksums in setup.ps1).
- Chapters 8, 23 and 36 (the ones with music) use their own scripts in `work/` and the mono masters in `music/`.
- Cleanup, encoding and publishing happen on the cloud side after each upload.
