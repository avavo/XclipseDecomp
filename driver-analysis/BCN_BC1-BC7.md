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
- **BC4, BC5, BC6H, BC7 — INCOMPLETE in the backend**: `VK_FORMAT_BC4_{UNORM,SNORM}`,
  `BC5_{UNORM,SNORM}`, `BC6H_{UFLOAT,SFLOAT}`, `BC7_{UNORM,SRGB}` + `Bc4/5/6/7_*`
  exist, but there is **no `IMG_FMT_BC4/5/6/7` at all** (0 hits in raw bytes).
  Total `IMG_FMT` = 260 entries, of which only `BC1/2/3` appear. Also **zero hits**
  for `textureCompressionBC`, `FormatPropertiesTable`, `GetFormatFlags`, `formatId`.
- In other words: the Vulkan frontend knows the BC4–7 names, but the internal PAL
  does not expose the corresponding image mapping in strings — consistent with
  "reported as unsupported / no backend", not with "a flag table zeroed out" (that
  table has never been dumped by anyone so far).

## Table (local static)

| Format | VK_FORMAT_* | Internal Bc* | IMG_FMT_* (PAL) | Static verdict |
|---|---|---|---|---|
| BC1 RGB UNORM/SRGB, RGBA UNORM/SRGB (131–134) | 4/4 | Bc1_Unorm/Srgb | BC1_UNORM/SRGB | complete |
| BC2 UNORM/SRGB (135–136) | 2/2 | Bc2_Unorm/Srgb | BC2_UNORM/SRGB | complete |
| BC3 UNORM/SRGB (137–138) | 2/2 | Bc3_Unorm/Srgb | BC3_UNORM/SRGB | complete |
| BC4 UNORM/SNORM (139–140) | 2/2 | Bc4_Unorm/Snorm | — (0) | **incomplete** |
| BC5 UNORM/SNORM (141–142) | 2/2 | Bc5_Unorm/Snorm | — (0) | **incomplete** |
| BC6H UFLOAT/SFLOAT (143–144) | 2/2 | Bc6_Ufloat/Sfloat | — (0) | **incomplete** |
| BC7 UNORM/SRGB (145–146) | 2/2 | Bc7_Unorm/Srgb | — (0) | **incomplete** |

Context: ETC2 (6 `VK_FORMAT_ETC2_*` + 10 `IMG_FMT_ETC2_*`) and ASTC LDR (28
`VK_FORMAT_ASTC_*` + 28 `IMG_FMT_ASTC_*`) have complete mapping on both levels —
the hole is specific to BC4–7.

## What this does NOT prove

- It does not prove deliberate blocking vs HW limitation: desktop RDNA2 supports BC4–7,
  and Xclipse is GFX10/MGFX (see below), but without a runtime test you cannot claim
  "HW supports it and Samsung turned it off with a flag".
- No format-count or capability-flag table was recovered: there is no table dump
  and no matching assert string in the binary, so no format-table total
  or per-format flag value can be verified statically.
- `RESERVED_*` in `IMG_FMT` (100+ entries) could theoretically map BC4–7 without
  strings — only a runtime table dump or reverse engineering of
  `vkGetPhysicalDeviceFormatProperties` settles it.

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
