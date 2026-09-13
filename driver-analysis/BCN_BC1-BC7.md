# BCn in the Xclipse driver (local SM-S926B) — BC1, BC2, BC3, BC4, BC5, BC6H, BC7

Question: does the driver have BCn 1,2,3,4,5,6 and 7? Is any missing? Any incomplete?

Method (static, reproducible): `python driver-analysis/reproduce_bcn.py <vulkan.samsung.so>`.
Audited target: `radv/vendor/vulkan.samsung.so`, 44,423,944 bytes, ELF AArch64.
This is NOT proof of runtime behavior — the final verdict requires
`vkGetPhysicalDeviceFeatures` (`textureCompressionBC`) +
`vkGetPhysicalDeviceFormatProperties[2]` on the device.

## Short answer

- **No BC is fully missing as a name**: all 16 `VK_FORMAT_BC*` (131–146) and all 14
  internal `Bc*` exist in the binary.
- **BC1, BC2, BC3 — complete at the static level**: `VK_FORMAT_*` + `Bc*_Unorm/Srgb` +
  `IMG_FMT_BC1/2/3_{UNORM,SRGB}` present.
- **BC4, BC5, BC6H, BC7 — REPORTED by default, but PAL-side INCOMPLETE**:
  `VK_FORMAT_BC4_{UNORM,SNORM}`, `BC5_{UNORM,SNORM}`, `BC6H_{UFLOAT,SFLOAT}`,
  `BC7_{UNORM,SRGB}` + `Bc4/5/6/7_*` exist, and the driver carries an explicit
  opt-out switch, `ForceEtcAstcEnable` (default `false`), whose description
  states it *"forces reporting support of ASTC/ETC2 texture reads and disables
  BC4-7"*, warning it is only for IFH (simulation) mode on gfx10 hardware. A
  switch that disables BC4–7, off by default, confirms they are reported when
  off. At the same time, the PAL side is demonstrably incomplete: there are
  **no `IMG_FMT_BC4/5/6/7` names at all** (0 hits in raw bytes; total `IMG_FMT`
  = 260 entries, only `BC1/2/3` named, plus 100+ `RESERVED_*` slots of unknown
  mapping). So apps are told BC4–7 exist, but the internal PAL format enum has
  no named entries for them and the exact internal mapping path is undetermined
  statically. Zero hits for `FormatPropertiesTable`, `GetFormatFlags`,
  `formatId`.
- On `textureCompressionBC` specifically: it is absent in every form checked
  (exact, case-insensitive, fragments, UTF-16LE) — but so are its siblings
  `textureCompressionETC2` / `textureCompressionASTC_LDR` and other
  `VkPhysicalDeviceFeatures` member names (`samplerAnisotropy`,
  `shaderStorageImageMultisample`). The only `robustBufferAccess` hits are
  shader-compiler option keys, not the features struct. So this binary does not
  embed feature-member names at all, and **nothing about runtime BC support can
  be concluded from the missing string** — only an on-device
  `vkGetPhysicalDeviceFeatures` query decides that.
- In other words: the Vulkan frontend reports BC4–7 (opt-out defaults to off),
  but the PAL side stays incomplete — no named `IMG_FMT_BC4–7` entries, unknown
  `RESERVED_*` mapping, undetermined internal path. Reported yet incomplete.

## Table (local static)

| Format | VK_FORMAT_* | Internal Bc* | IMG_FMT_* (PAL) | Static verdict |
|---|---|---|---|---|
| BC1 RGB UNORM/SRGB, RGBA UNORM/SRGB (131–134) | 4/4 | Bc1_Unorm/Srgb | BC1_UNORM/SRGB | complete |
| BC2 UNORM/SRGB (135–136) | 2/2 | Bc2_Unorm/Srgb | BC2_UNORM/SRGB | complete |
| BC3 UNORM/SRGB (137–138) | 2/2 | Bc3_Unorm/Srgb | BC3_UNORM/SRGB | complete |
| BC4 UNORM/SNORM (139–140) | 2/2 | Bc4_Unorm/Snorm | — (0) | **reported; PAL incomplete** |
| BC5 UNORM/SNORM (141–142) | 2/2 | Bc5_Unorm/Snorm | — (0) | **reported; PAL incomplete** |
| BC6H UFLOAT/SFLOAT (143–144) | 2/2 | Bc6_Ufloat/Sfloat | — (0) | **reported; PAL incomplete** |
| BC7 UNORM/SRGB (145–146) | 2/2 | Bc7_Unorm/Srgb | — (0) | **reported; PAL incomplete** |

Context: ETC2 (6 `VK_FORMAT_ETC2_*` + 10 `IMG_FMT_ETC2_*`) and ASTC LDR (28
`VK_FORMAT_ASTC_*` + 28 `IMG_FMT_ASTC_*`) have complete mapping on both levels;
BC4–7 are reported via the `ForceEtcAstcEnable` opt-out evidence above, yet keep
an incomplete PAL enum (no named entries, unknown `RESERVED_*` mapping).

## What this does NOT prove

- Per-app overrides remain possible: driver settings blobs can flip behavior
  per application, so a runtime `vkGetPhysicalDeviceFeatures` check on the
  target app is still the gold standard. The baseline/default, however, is BC
  enabled per the `ForceEtcAstcEnable` default above.

## How to confirm on-device (pending)

```c
VkPhysicalDeviceFeatures f; vkGetPhysicalDeviceFeatures(phys, &f);
// f.textureCompressionBC == VK_TRUE?
for (VkFormat fmt = VK_FORMAT_BC1_RGB_UNORM_BLOCK; fmt <= VK_FORMAT_BC7_SRGB_BLOCK; fmt++)
  vkGetPhysicalDeviceFormatProperties(phys, fmt, &props);
// check props.optimalTilingFeatures & SAMPLED_IMAGE_BIT etc.
```

If `textureCompressionBC==VK_FALSE` and BC4–7 return 0, the block is real at
runtime (regardless of mechanism). If they return features, HW+driver support them.

## Disassembly: hunting the BC feature slot (AArch64, capstone)

Since the name never appears as a string, the `.text` segment was disassembled
for real (`STR Wt,[Xn,#88]` = struct offset of the BC flag inside a
`VkPhysicalDeviceFeatures`-shaped struct, plus `STP`/`STR Xt` variants), and
every site was checked for sibling-offset stores (80/84/92 = ETC2/ASTC/BC
neighbors) on the same base register:

- 496 `STR W,#88` sites, 0 `STP #88`, 0 `STR X,#88`. Offset 88 is common to many
  structs, so most sites are unrelated whole-struct copies (`ldrb` loops),
  zero-fills, or mixed u32/u8 structs.
- 22 sites sit in functions that also store to 80/84/92 on the same base. None
  is unambiguously the Vulkan features fill.
- Closest candidate, at `0x1455578`: 15 consecutive u32 stores to one base at
  offsets 64…120 with per-field loads — the same shape as features 16…30 —
  including the BC slot sourced from a runtime table:
  `ldr w8, [x24, #0xeb0]` → `[x19,#0x50]` (80),
  `ldr w8, [x24, #0xf0c]` → `[x19,#0x54]` (84),
  `ldr w8, [x23, #0x8e0]` → `[x19,#0x58]` (88).
  But the same function also writes byte fields (`0x84`, `0x8c`–`0x8e`,
  `0x92`–`0x93`) and far offsets (`0xc9c`), so it is a mixed internal struct,
  not `VkPhysicalDeviceFeatures` itself — and the #88 value comes from runtime
  data, so 0/1 cannot be read statically.

Bottom line of the code hunt alone: the name is absent as string/symbol, and no
code site settles the value statically — the slot is data-driven. Combined with
the `ForceEtcAstcEnable` default (`false` = BC4–7 stay reported), the static
picture is: supported by default, with a debug-only off switch.
Re-run the scan with `python driver-analysis/reproduce_bcn.py <driver> --disasm`
(requires the `capstone` package).

## Other local .so findings relevant to BCn

- GFX: `SCEmitterGFX40/401/402/403/404`, `SCTargetInfoGFX40/401/402/403`,
  `MGFX1:gfx4010` … `MGFX4:gfx4040`. **No `GFX405`** in this build.
- XGL/PAL confirmed: `drivers/xgl/icd/api/*.cpp`, `SCEmitter*`, `AMDVLK_ENABLE_DEVELOPING_EXT`,
  `AMD Vulkan Driver`, `Samsung::Vulkan::OpenDevice/CloseDevice`, `vulkan.samsung.so`.
- `sgpu_query_soc_info` = 0 hits in this build.
  `sgpu_instance_data_destroy`, `amdgpu_bo_list_destroy_raw`, `amdgpu_cs_ctx_create3` = 1 hit.
- `.dynsym` = 345 entries (344 non-empty). `VK_*` = 398 strings.
- `Xclipse` only in "Xclipse GPU Fault"; no "Xclipse 940/920", no `0x73A0`, no "Exynos 2400"
  (only residual `exynos9810`). SoC IDs come from probes/JSON, not the `.so`.
