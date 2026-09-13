# Provenance of every file in this repo

Upstream sources:

- Bring-up notes, device results and hardware docs:
  [avavo/RadvXclipse](https://github.com/avavo/RadvXclipse)
  (`docs/`, `radv-xclipse940/docs/`, `data/devices/`).
- Audited driver build: `vulkan.samsung.so` (44,423,944 bytes, ELF AArch64,
  pulled from an SM-S926B). Only derived facts (name lists, counts, hashes)
  are committed here — never the binary.
- External claims checked against:
  [WearyConcern1165/xclipse-vulkan-decompiled](https://github.com/WearyConcern1165/xclipse-vulkan-decompiled)
  (`extracted_data/*.txt`, `features/vk_formats.h`, `vk_icd/*`, `pal/*`,
  `sgpu/*`). No code was copied from it; the audit links to it.

## File map

- `docs/01-hardware-overview.md` ← upstream `docs/01-hardware-overview.md`
- `docs/03-device-tree-and-platform.md` ← upstream `docs/03-device-tree-and-platform.md`
- `docs/17-textures-and-images.md` ← upstream `docs/17-textures-and-images.md`
- `docs/LOCAL_FINDINGS.md` ← English translation of upstream
  `radv-xclipse940/docs/LOCAL_FINDINGS.md` (DMA-BUF `handle_type` bug, ELF hashes)
- `logs/SM-S926B-2026-09-06-bringup-RESULTS.md` ← English translation of upstream
  `data/devices/SM-S926B/2026-09-06-bringup/RESULTS.md`
- `logs/SM-S721B-*` ← sanitized identity/firmware/hash summaries from upstream
  `data/devices/SM-S721B/`
- `driver-analysis/BCN_BC1-BC7.md`, `EXTERNAL_REPO_AUDIT.md`, `reproduce_bcn.py` —
  written for this repo from the static analysis described inside them
- `driver-analysis/IMG_FMT-list-local.txt` — 260 `IMG_FMT_*` names extracted from
  the audited build
- `driver-analysis/local-dynsym.txt` — 344 `.dynsym` names from the audited build

## Deliberately not included

- Vendor binaries (`vulkan.samsung.so`, `libdrm_sgpu.so`) and the Samsung kernel
  snapshot: proprietary, referenced by hash only.
- Raw verbose string dumps: reproducible at any time with `reproduce_bcn.py`
  against your own device copy.
- Full on-device result history (100+ run folders upstream): summarized by the
  representative `logs/` files above.
