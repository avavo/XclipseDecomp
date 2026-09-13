# Xclipse 940 / Exynos 2400 — Private archive (public-safe)

Curated bundle built 2026-09-13 from `C:\Users\alvaro\Documents\radv` (origin `avavo/RadvXclipse`)
+ static analysis of `vendor/vulkan.samsung.so` (SM-S926B, 44,423,944 bytes)
+ audit of https://github.com/WearyConcern1165/xclipse-vulkan-decompiled

> This repo is currently **private by choice, not by necessity**.
> It contains NO vendor binaries and NO raw proprietary dumps, so it CAN go
> public later as-is. See `PUBLIC_SAFETY.md` + pre-flip checklist before changing
> visibility. License: MIT for own docs/scripts (`LICENSE`); Samsung blobs are
> referenced by hash/path only, never redistributed.

## Contents

```text
README.md                        this file
PUBLIC_SAFETY.md                 why this repo can go public + pre-flip checklist
LICENSE                          MIT (own docs/scripts only)
docs/                            curated copies from the local repo
  01-hardware-overview.md        SM-S721B r12s, erd9945/s5e9945, 0x73a0, fam 147, GFX/COMPUTE 10.0, 12 CUs, wave32
  03-device-tree-and-platform.md DT /sgpu@22200000
  17-textures-and-images.md      base texture doc from the local repo
  LOCAL_FINDINGS.md              handle-type 1 vs 2 bug, ELF hashes, limits (EN translation)
logs/                            sanitized captures + 1 RESULTS (EN)
  SM-S926B-2026-09-06-bringup-RESULTS.md
  SM-S721B-build-properties.txt / firmware-and-gpu.txt / hashes.txt
driver-analysis/
  BCN_BC1-BC7.md                 answer: are BC1-7 missing? incomplete?
  EXTERNAL_REPO_AUDIT.md         is the WearyConcern1165 repo true?
  reproduce_bcn.py               re-runs the local strings/ELF analysis
  IMG_FMT-list-local.txt         260 IMG_FMT_* extracted from the local .so
  local-dynsym.txt               344 local .dynsym symbols
inventory/
  SOURCES.md                     where everything lives in the original repo + what was NOT copied
```

Note: the two verbose raw dumps (`local-bc-strings.txt`, `local-string-hits.txt`)
were intentionally deleted — they carried large PAL JSON blobs. Reproduce them any
time with `reproduce_bcn.py` against your private copy of the `.so`.

## Xclipse 940 / Exynos 2400 in 30 seconds (only what your repo confirms)

- Lab target: SM-S721B (`r12s`), platform `erd9945`, hw `s5e9945`; SGPU on
  `/dev/dri/renderD128` (`samsung-sgpu,samsung-sgpu`, `/sgpu@22200000`), separate display
  on `renderD129`. GFX 1x10.0 rings `0xf`, COMPUTE 1x10.0 rings `0x7`, DMA 0.
  Family `147 (MGFX)`, device `0x73a0`, chip `0x02600200` (EVT0 in source = `0x02600100`,
  keep separate). 12 CUs, wave32 (DRM) vs 64 (static Vulkan field). Source:
  `docs/01-hardware-overview.md` copied here.
- SM-S926B (S24+, Exynos 2400 / Xclipse 940): native GEM/VA/import/CPU sync validated 2026-09-06;
  CS/fence/readback, self-submitted shader and restricted NIR validated 2026-09-07 to 12
  (see `PORT_STATUS.md` and `data/devices/SM-S926B/*` in the original repo — NOT fully
  copied here, see `inventory/SOURCES.md`).
- Driver: `/vendor/lib64/hw/vulkan.samsung.so` (local 44,423,944 bytes), `libdrm_sgpu.so`
  (`8CE6C773…`), ICD loaded in SurfaceFlinger, Termux only sees llvmpipe. Classic bug:
  `test_standalone` passes `handle_type=1` where the lib requires `2` for DMA-BUF.

## Publishing to GitHub (why you don't see it yet)

This bundle exists only on your disk (`git remote -v` is empty) — nothing was ever
pushed, which is why it is not on github.com. To create it:

1. On GitHub web: New repository → name `xclipse940-privado` → **Private** →
   do **NOT** check add README/license (files already exist). Create.
2. In PowerShell, inside this folder:

```powershell
git branch -M main
git remote add origin https://github.com/<your-user>/xclipse940-privado.git
git push -u origin main
```

3. Later, to go public: re-run the checklist in `PUBLIC_SAFETY.md`, then GitHub
   Settings → General → Danger Zone → Change visibility → Public. No history
   rewrite needed.

## Revalidating the BCn analysis

```powershell
python .\driver-analysis\reproduce_bcn.py ..\radv\vendor\vulkan.samsung.so
```

Expected output (local SM-S926B build): 16 `VK_FORMAT_BC*`, 14 `Bc*`, 6 `IMG_FMT_BC1-3`,
0 `IMG_FMT_BC4-7`, 0 `textureCompressionBC`, 0 `FormatPropertiesTable`.
Details in `driver-analysis/BCN_BC1-BC7.md`.
