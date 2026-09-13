# XclipseDecomp — Xclipse 940 / Exynos 2400 driver notes

On-device facts and static analysis on Samsung's Xclipse 940 GPU (Exynos 2400)
and its proprietary Vulkan driver: hardware identity, bring-up results, a
DMA-BUF import bug with its fix, and a BC1–BC7 texture-compression audit.

No proprietary binaries are shipped here (MIT-licensed notes and scripts only).

## Hardware

From on-device probes (SM-S721B / SM-S926B):

- SoC hints: platform `erd9945`, hardware `s5e9945`, Android 16, kernel
  `6.1.157-android14-11`, AArch64
- GPU: family `147 (MGFX)`, device `0x73a0`, chip revision `0x02600200`
  (the EVT0 source tree says `0x02600100` — kept separate until correlated)
- SGPU render node `/dev/dri/renderD128` (`samsung-sgpu`, `/sgpu@22200000`);
  display on a separate node
- GFX 1×10.0 (rings `0xf`), COMPUTE 1×10.0 (rings `0x7`), DMA 0 rings;
  12 active CUs, DRM wavefront 32 (the static Vulkan field says 64)
- Firmware seen on the probe: SGPU `2.23.0`, RTL `0x4ea15`

Details: `docs/01-hardware-overview.md`, `docs/03-device-tree-and-platform.md`,
`logs/SM-S721B-firmware-and-gpu.txt`, `logs/SM-S721B-build-properties.txt`.

## Bring-up results (SM-S926B, via ADB, no root, SELinux Enforcing)

Validated 2026-09-06 (`logs/SM-S926B-2026-09-06-bringup-RESULTS.md`):

- Native 64 KiB BO: GEM create, CPU write/read, VA map/unmap, cleanup — 10/10
- DMA-BUF PRIME import, direct and via libdrm, on `system` / `system-uncached`
  heaps, 64 KiB and 4 KiB — 10/10, plus VA map/unmap of imported BOs
- Fresh context: syncobj create, CPU signal/wait, sync_file export/import,
  timeout-after-reset semantics

Explicitly out of scope of these probes: GPU command submission, GPU-produced
fences, shader execution with GPU readback, and any Vulkan ICD integration.

## Import bug and fix

The supplied `test_standalone` probe called `amdgpu_bo_import` with type `1`,
which the shipped `libdrm_sgpu` rejects before PRIME (`-1`); type `2` selects
the DMA-BUF path. The old probe also undersized the output struct (8 bytes
instead of 16) and zeroed its exit code even on failure. A from-source
replacement probe with type `2`, a 16-byte result struct and immediate `errno`
capture imports successfully on-device. Full disassembly-level analysis with
hashes: `docs/LOCAL_FINDINGS.md`.

## Driver stack (static)

One SM-S926B driver build (`vulkan.samsung.so`, 44,423,944 bytes, ELF AArch64):

- AMD-based stack: XGL ICD source paths, PAL symbols, shader-compiler
  `SCEmitterGFX40/401/402/403/404` targets (`MGFX1–4`, no `GFX405`)
- Samsung integration: Vulkan HAL open/close, SGR/gralloc interface (27 dynsym
  symbols), SBWC helper, amdgpu-derived kernel interface
  (`amdgpu_bo_list_destroy_raw`, `amdgpu_cs_ctx_create3`, …)
- 345 `.dynsym` entries, 398 `VK_*` strings; `sgpu_instance_data_destroy`
  present, `sgpu_query_soc_info` absent in this build

## BCn texture compression

Short version: no BC format is missing as a name (all 16 `VK_FORMAT_BC*`,
131–146, plus all 14 internal `Bc*`), but the PAL backend only carries image
formats for BC1–BC3 — `IMG_FMT_BC4/5/6/7` are absent, so BC4, BC5, BC6H and BC7
are **incomplete** in this build. ETC2/ASTC map fully on both levels. The
`textureCompressionBC` string is absent too, but so are all sibling feature
names — this binary simply doesn't embed them, so runtime support can only be
settled on-device (`vkGetPhysicalDeviceFeatures` + per-format
`vkGetPhysicalDeviceFormatProperties`). Full evidence:
`driver-analysis/BCN_BC1-BC7.md`.

## Layout

```text
docs/                  hardware / platform / texture notes, import-bug analysis
logs/                  sanitized device identity, firmware and bring-up results
driver-analysis/
  BCN_BC1-BC7.md         full BCn evidence and what it does (not) prove
  reproduce_bcn.py       re-runs the strings/ELF checks on any driver copy
  IMG_FMT-list-local.txt 260 PAL IMG_FMT_* names from the audited build
  local-dynsym.txt       344 .dynsym symbol names from the audited build
inventory/
  SOURCES.md             provenance of every file in this repo
```

## Reproduce the static checks

Pull the driver from your own device and run the script against that copy:

```sh
adb pull /vendor/lib64/hw/vulkan.samsung.so
python driver-analysis/reproduce_bcn.py vulkan.samsung.so
```

Expected output for the audited build: 16 `VK_FORMAT_BC*`, 14 `Bc*`,
6 `IMG_FMT_BC1-3`, 0 `IMG_FMT_BC4-7`, `.dynsym` 345 entries.

## Provenance & license

Derived from on-device bring-up notes and results plus independent static
analysis of a device-pulled driver copy. See `inventory/SOURCES.md`.

Own documentation and scripts are MIT-licensed (`LICENSE`). Samsung binaries,
kernel snapshots and device dumps are referenced by hash only and are not
redistributed here.
