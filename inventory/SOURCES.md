# Provenance of every file in this repo

Sources: on-device bring-up notes and results (SM-S721B / SM-S926B) and
independent static analysis of a device-pulled `vulkan.samsung.so` copy
(44,423,944 bytes, ELF AArch64). Only derived facts (name lists, counts,
hashes) are committed here — never the binary.

## File map

- `docs/01-hardware-overview.md` — SoC/GPU identity, DT node, IP blocks
- `docs/03-device-tree-and-platform.md` — device-tree and platform mapping
- `docs/17-textures-and-images.md` — texture/image pipeline notes
- `docs/LOCAL_FINDINGS.md` — DMA-BUF `handle_type` bug analysis, ELF hashes
  (English translation of the original note)
- `logs/SM-S926B-2026-09-06-bringup-RESULTS.md` — bring-up results
  (English translation of the original report)
- `logs/SM-S721B-*` — sanitized identity/firmware/hash summaries
- `driver-analysis/BCN_BC1-BC7.md`, `reproduce_bcn.py` — written for this repo
  from the static analysis described inside them
- `driver-analysis/IMG_FMT-list-local.txt` — 260 `IMG_FMT_*` names extracted from
  the audited build
- `driver-analysis/local-dynsym.txt` — 344 `.dynsym` names from the audited build

## Deliberately not included

- Vendor binaries (`vulkan.samsung.so`, `libdrm_sgpu.so`) and the Samsung kernel
  snapshot: proprietary, referenced by hash only.
- Raw verbose string dumps: reproducible at any time with `reproduce_bcn.py`
  against your own device copy.
- Full on-device result history: summarized by the representative `logs/` files
  above.
