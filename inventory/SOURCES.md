# Where everything came from (original `radv` repo)

## Copied into this bundle (small, safe)

- `docs/01-hardware-overview.md` <- `radv/docs/01-hardware-overview.md`
- `docs/03-device-tree-and-platform.md` <- `radv/docs/03-device-tree-and-platform.md`
- `docs/17-textures-and-images.md` <- `radv/docs/17-textures-and-images.md`
- `docs/LOCAL_FINDINGS.md` <- `radv/radv-xclipse940/docs/LOCAL_FINDINGS.md` (EN translation of the original)
- `logs/SM-S926B-2026-09-06-bringup-RESULTS.md` <- `radv/data/devices/SM-S926B/2026-09-06-bringup/RESULTS.md`
- `logs/SM-S721B-*` <- `radv/data/devices/SM-S721B/{build-properties,firmware-and-gpu,hashes}.txt`

## NOT copied (large / sensitive / redundant) — fetch from the original when needed

- `radv/data/devices/SM-S926B/*` (100+ RESULTS folders 2026-09-07 to 12, ~8,954 files under
  `data+docs+evidence+reports+source-analysis`): full CS/fence/readback history,
  NIR, emitter, A/B. Keep in the original repo; this bundle is only the Xclipse 940 index.
- `radv/vendor/vulkan.samsung.so` (44,423,944), `libdrm_sgpu.so`, `vulkan.radv_eden.so`:
  proprietary blobs. Only lists/hashes here (`driver-analysis/*`, `LOCAL_FINDINGS.md`).
  To revalidate: `python driver-analysis/reproduce_bcn.py ..\radv\vendor\vulkan.samsung.so`.
- `radv/vendor/SM-S926B-opensource/` (~2.5 GB, ~108k files): Samsung kernel snapshot.
  Reference only; see `radv/vendor/README.md` + `radv/source-analysis/*`.
- `radv/evidence/device-captures/`, `radv/reports/`, `radv/archive/`: raw captures and
  historical snapshots. Consult the original.
- `C:\Users\alvaro\Documents\xclipse\*.zip` (`SM-S926B_16_Opensource.zip`, `Xclipse940.zip`,
  RDNA ISA PDFs, `*.tzst`): support material outside git. Not duplicated here.

## External audit — artifacts used

- Clone of `https://github.com/WearyConcern1165/xclipse-vulkan-decompiled` at
  `%TEMP%\opencode\xclipse-decompiled` (32 files). Checked:
  `extracted_data/{all_dynamic_symbols,all_strings_raw,exported_functions,samsung_strings,
  amd_pal_strings,all_source_files,assert_messages,vk_strings,decomp_vkCreateInstance}.txt`,
  `features/vk_formats.h`, `vk_icd/vk_device.c`, `vk_icd/vk_instance.c`, `pal/pal_device.h`,
  `sgpu/sgpu_kernel.h`. Conclusion in `driver-analysis/EXTERNAL_REPO_AUDIT.md`.
