# XclipseDecomp — Xclipse 940 / Exynos 2400 driver notes & BCn analysis

Static-analysis notes on Samsung's proprietary Vulkan driver (`vulkan.samsung.so`)
for the Xclipse 940 GPU (Exynos 2400): whether BC1–BC7 texture compression is
present, missing, or incomplete, plus hardware and bring-up notes from on-device
probes.

No proprietary binaries are shipped here (MIT-licensed notes and scripts only).

## Findings up front

**Hardware (from on-device probes, SM-S721B / SM-S926B).**
SGPU on `/dev/dri/renderD128` (`samsung-sgpu`, `/sgpu@22200000`), display on a
separate node. Family `147 (MGFX)`, device `0x73a0`, GFX 1×10.0, COMPUTE 1×10.0,
12 CUs, DRM wavefront 32. Details in `docs/01-hardware-overview.md`.

**BCn support (static analysis of one SM-S926B driver build, 44,423,944 bytes).**
No BC format is fully missing as a name — all 16 `VK_FORMAT_BC*` (Vulkan enum
131–146) and all 14 internal `Bc*` identifiers are present. But the PAL backend
only exposes image formats for BC1–BC3:

| Formats | Vulkan names | PAL `IMG_FMT_*` | Status |
|---|---|---|---|
| BC1 (131–134), BC2 (135–136), BC3 (137–138) | present | `BC1/2/3_UNORM/SRGB` present | complete |
| BC4 (139–140), BC5 (141–142), BC6H (143–144), BC7 (145–146) | present | absent (0 hits) | **incomplete** |

`textureCompressionBC` is also absent as a string, and ETC2/ASTC have full
mappings on both levels — the gap is specific to BC4–7. Static analysis cannot
prove the runtime behavior; confirming requires `vkGetPhysicalDeviceFeatures`
plus per-format `vkGetPhysicalDeviceFormatProperties` on-device. Full evidence
in `driver-analysis/BCN_BC1-BC7.md`.

**Driver stack.** The binary confirms an AMD-based stack (XGL ICD paths, PAL
symbols, shader-compiler `SCEmitterGFX40*` targets) with Samsung integration
(Vulkan HAL open/close, SGR/gralloc interface, SBWC helper, amdgpu-derived
kernel interface). 345 `.dynsym` entries, 398 `VK_*` strings.

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

## Reproduce

Pull the driver from your own device and run the script against that copy:

```sh
adb pull /vendor/lib64/hw/vulkan.samsung.so
python driver-analysis/reproduce_bcn.py vulkan.samsung.so
```

Expected output for the audited build: 16 `VK_FORMAT_BC*`, 14 `Bc*`,
6 `IMG_FMT_BC1-3`, 0 `IMG_FMT_BC4-7`, 0 `textureCompressionBC`,
0 `FormatPropertiesTable`, `.dynsym` 345 entries.

## Provenance & license

Derived from on-device bring-up notes and results plus independent static
analysis of a device-pulled driver copy. See `inventory/SOURCES.md`.

Own documentation and scripts are MIT-licensed (`LICENSE`). Samsung binaries,
kernel snapshots and device dumps are referenced by hash only and are not
redistributed here.
