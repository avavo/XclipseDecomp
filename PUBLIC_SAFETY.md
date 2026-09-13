# Public-safety statement — can this repo go public later?

Short answer: **yes, in its current state, after the 2026-09-13 cleanup.**

## Why it is public-safe now

- **No vendor binaries.** No `.so`, no kernel snapshot, no `.zip/.tzst/.pdf`.
  Enforced by `.gitignore` (`*.so`, `*.zip`, `*.tzst`, `*.pdf`,
  `SM-S926B-opensource/`, `build-*/`).
- **No raw proprietary dumps.** The two verbose dumps (`local-bc-strings.txt`
  ~1 MB, `local-string-hits.txt` ~1.9 MB, containing large PAL settings JSON
  blobs) were **deleted** from the bundle. What remains is factual and small:
  - `IMG_FMT-list-local.txt` — 260 format-enum names (facts, not code).
  - `local-dynsym.txt` — 344 dynamic symbol names (linker interface facts).
  - Counts and short quoted identifiers in `BCN_BC1-BC7.md` / `EXTERNAL_REPO_AUDIT.md`.
- **No device secrets.** Logs are sanitized summaries (model/platform/family IDs,
  firmware versions, hashes). No serials, IMEIs, credentials, memory contents.
  Verified: `logs/SM-S721B-build-properties.txt`,
  `logs/SM-S721B-firmware-and-gpu.txt`, `logs/SM-S721B-hashes.txt`,
  `logs/SM-S926B-2026-09-06-bringup-RESULTS.md`.
- **External repo.** Only short factual quotes with attribution (symbol counts,
  string counts, presence/absence of identifiers). No code copied from
  `WearyConcern1165/xclipse-vulkan-decompiled`; the audit links to it instead.
- **License.** Own docs/scripts under MIT (`LICENSE`). Proprietary blobs are
  referenced by hash/path only, never redistributed.

## Before flipping to Public, run this checklist

```powershell
Set-Location C:\Users\alvaro\Documents\xclipse940-privado
git status --short
git log --oneline -5
git ls-files | Select-String '\.so$|\.zip$|\.tzst$|\.pdf$|opensource'
# expected: no output (only .md/.txt/.py/.gitignore/LICENSE)
git ls-files | ForEach-Object { (Get-Item $_).Length } | Measure-Object -Sum
# small total (~50 KB); anything in MB needs review
```

Then on GitHub: repo Settings → General → Danger Zone → Change visibility → Public.
No history rewrite is needed: this repo was born public-safe (binaries were never
committed here — they only ever lived in `../radv/vendor/`, a different repo).

## What would make it UNSAFE (do not add)

- `vendor/vulkan.samsung.so`, `libdrm_sgpu.so`, `vulkan.radv_eden.so`.
- `vendor/SM-S926B-opensource/` or any `*.zip` kernel snapshot.
- Full `strings` dumps or `readelf -a` pastes of the proprietary `.so`.
- Device serials, `dumpstate`, `bugreport`, keystore, tokens, `local.properties`.
