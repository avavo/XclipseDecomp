# Audit: WearyConcern1165/xclipse-vulkan-decompiled — what is true?

Audited 2026-09-13 via clone + local `vendor/vulkan.samsung.so` (SM-S926B, 44,423,944 bytes).
The external repo analyzes a different build (they cite 44,514,072 bytes, ~90 KB larger) and does NOT ship
the binary — only `extracted_data/*.txt` + hand-written `.h/.c` "reconstructions". Verdict per claim:

## TRUE (confirmed here or in their own artifacts)

- **AMD base**: XGL (`drivers/xgl/icd/api/vk_device.cpp` etc.), PAL (`Pal::*`, `palSysUtil.h`,
  `palPipelineAbiProcessorImpl.h`), SC (`SCEmitterGFX10/103/40/401/402/403/404`, `SCTargetInfo*`,
  `AMDGPU.*`, `AMDVLK_ENABLE_DEVELOPING_EXT`, `AMD Vulkan Driver`). All confirmed locally.
- **Real Samsung HAL**: `Samsung::Vulkan::OpenDevice/CloseDevice`, `vulkan.samsung.so`,
  `SGR` (`sgr_intf_*`, 27 dynsym symbols), `SBWC` (`libsbwchelper.so`, `SBWCHelper::*`),
  `amdgpu_*` fork (`amdgpu_bo_list_destroy_raw`, `amdgpu_cs_ctx_create3`, etc.).
- **`0xdb48` allocation in `vkCreateInstance`**: `mov w1, 0xdb48` exists in
  their `decomp_vkCreateInstance.txt` (1 hit). Plausible for their build.
  (In the local SM-S926B build the `01 69 9B 52` pattern gives 0 hits — size differs per build.
  Do not generalize.)
- **60+ extensions / Vulkan 1.3 / RDNA2-GFX10**: local binary has 398 `VK_*` strings
  (incl. `VK_AMD_*`, `VK_EXT_*`, `VK_KHR_*`, `VK_ANDROID_*`). "60+" is actually
  conservative. Their exact list in `vk_icd/vk_device.c` is hand-curated, but the order
  of magnitude is right.
- **BC1–7 names exist**: `VK_FORMAT_BC*` (16) + `Bc*` (14) in both builds. BC1–3 with
  `IMG_FMT`, BC4–7 without `IMG_FMT` (see `BCN_BC1-BC7.md`). The "BC4–7 unsupported"
  phenomenon is real at the static level; they do not prove the exact mechanism (below).

## FALSE or UNSUBSTANTIATED (with proof)

1. **"830+ dynamic symbols" — FALSE.** Their own `extracted_data/all_dynamic_symbols.txt`
   is a `readelf` dump saying `contains 345 entries` (348 lines with header).
   Local: 345 entries, 344 non-empty. The number 830 appears in no artifact.
2. **"~39,000 strings" — FALSE.** Their `all_strings_raw.txt` is 2,715,442 bytes with
   **197,676 lines**, not 39k. Local (`strings >= 4` method): 308,023 strings.
3. **"221-format table" via assert `FormatPropertiesTable::GetFormatFlags: invalid
   formatId (formatId:221)` — NO EVIDENCE.** 0 hits for `FormatPropertiesTable`,
   `GetFormatFlags`, `formatId`, `invalid formatId` in the local binary **and** 0 hits in
   every file of their repo except their own `features/vk_formats.h`, which invents
   the quote. `221` appears 2x in their dump in unrelated contexts. Without a table
   dump, "221 entries" and "flags zeroed for 139–146" are unproven assertions.
4. **"Magic 0x01cdc0de" — NO EVIDENCE.** 0 hits in the local binary (LE/BE bytes), 0 hits
   in their `decomp_vkCreateInstance.txt`. `0xdb48` has 1 hit; the magic has none.
   Their `vk_instance.c` presents `0x01cdc0de`, offsets `0xd810/0xd850/0xd890/0xd8b8`
   and a `SgpuInstance` struct as "from disassembly", but the txt only supports `0xdb48`/`0xd810`.
5. **"95% AMD + 5% Samsung" / "exact 60+ device extensions" / `GfxIpLevel 0x2801–0x2805`
   ("940 = 0x2803", "405 = future") — INVENTED NUMBERS.** No LoC measurement,
   no `GfxIpLevel` dump, no `GFX405` in the local build (only 40–404 + `MGFX1–4`).
   They may be reasonable inferences, but are presented as extraction.
6. **`sgpu_query_soc_info` as "present" — ONLY IN THEIR BUILD.** 1 hit in their dump,
   **0 hits** in the local SM-S926B `.so` (which has `sgpu_query_dump_bpmd{,_to_fd}`,
   `sgpu_query_gpu_page_faults`, `sgpu_query_ifpo_disable`, `sgpu_instance_data_destroy`).
   Not universal; citing it as a stable SGPU interface is misleading.
7. **"Decompiled source" — ACTUALLY STUBS.** `hal/android_hal.c`, `vk_icd/*.c`,
   `pal/*.h`, `shader_compiler/*.h` are hand-written headers/code using 1–2 real strings
   as pretext ("Source paths (from binary)") + the rest inferred from public AMDVLK.
   No CFG, no Hex-Rays/Ghidra pseudocode, no diff against GPUOpen-Drivers. The only
   genuine disassembly artifact is `decomp_vkCreateInstance.txt` (raw disassembler output
   with ANSI, 323 KB) — and even it lacks the cited magic.
8. **"Disabled via software table, re-enable with a layer" — OVERSIMPLIFICATION.**
   The real static finding is stronger and more nuanced: `IMG_FMT_BC4/5/6/7` **do not exist**
   as PAL strings (only BC1–3), while `VK_FORMAT_BC4–7` + `Bc4–7` do. That suggests a
   missing/incomplete backend, not a simple `capabilities=0` in a 221-entry table.
   A layer intercepting `vkGetPhysicalDeviceFormatProperties` can mask the query,
   but it does not create sampling/decompression backend if none exists — and they never
   tested on-device (no CTS, `vulkaninfo`, or trace evidence).

## What to use / what to drop from that repo

- USE as a strings index and look-here map (XGL/PAL/SC, SGR/SBWC, `amdgpu_*`,
  `SCEmitterGFX40x`, 17 instance extensions as a working hypothesis).
- DO NOT CITE the numbers 830+, 39k, 221, `0x01cdc0de`, `0x2801–2805`, "95/5%" without revalidating.
- DO NOT treat `features/vk_formats.h` as a dump — it is a didactic header, not extraction.
- For BCn, prefer `BCN_BC1-BC7.md` + `reproduce_bcn.py` in this bundle (run on your
  build) + on-device runtime test on the S926B (`textureCompressionBC` + `FormatProperties` per format).

## Reproduction (what was run)

- Clone: `git clone https://github.com/WearyConcern1165/xclipse-vulkan-decompiled.git`
- Counts in their dump: `all_dynamic_symbols.txt` 348 lines / 345 entries;
  `all_strings_raw.txt` 197,676 lines; `FormatPropertiesTable` 0; `sgpu_query_soc_info` 1.
- In the local `.so`: `VK_FORMAT_BC*` 16, `Bc*` 14, `IMG_FMT_BC1-3` 6, `IMG_FMT_BC4-7` 0,
  `textureCompressionBC` 0, `.dynsym` 345, `mov w1,0xdb48` 0, magic 0.
