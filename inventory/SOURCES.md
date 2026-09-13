# De onde veio cada coisa (repo original `radv`)

## Copiado para este bundle (pequeno, seguro)

- `docs/01-hardware-overview.md` <- `radv/docs/01-hardware-overview.md`
- `docs/03-device-tree-and-platform.md` <- `radv/docs/03-device-tree-and-platform.md`
- `docs/17-textures-and-images.md` <- `radv/docs/17-textures-and-images.md`
- `docs/LOCAL_FINDINGS.md` <- `radv/radv-xclipse940/docs/LOCAL_FINDINGS.md`
- `logs/SM-S926B-2026-09-06-bringup-RESULTS.md` <- `radv/data/devices/SM-S926B/2026-09-06-bringup/RESULTS.md`
- `logs/SM-S721B-*` <- `radv/data/devices/SM-S721B/{build-properties,firmware-and-gpu,hashes}.txt`

## NÃO copiado (grande / sensível / redundante) — buscar no original quando precisar

- `radv/data/devices/SM-S926B/*` (100+ pastas RESULTS 2026-09-07→12, ~8.954 arquivos em
  `data+docs+evidence+reports+source-analysis`): histórico completo de CS/fence/readback,
  NIR, emitter, A/B. Manter no repo original; este bundle é só o índice do Xclipse 940.
- `radv/vendor/vulkan.samsung.so` (44.423.944), `libdrm_sgpu.so`, `vulkan.radv_eden.so`:
  blobs proprietários. Aqui vão só listas/hashes (`driver-analysis/*`, `LOCAL_FINDINGS.md`).
  Para revalidar: `python driver-analysis/reproduce_bcn.py ..\radv\vendor\vulkan.samsung.so`.
- `radv/vendor/SM-S926B-opensource/` (~2,5 GB, ~108k arquivos): snapshot kernel Samsung.
  Referência apenas; ver `radv/vendor/README.md` + `radv/source-analysis/*`.
- `radv/evidence/device-captures/`, `radv/reports/`, `radv/archive/`: capturas brutas e
  snapshots históricos. Consultar no original.
- `C:\Users\alvaro\Documents\xclipse\*.zip` (`SM-S926B_16_Opensource.zip`, `Xclipse940.zip`,
  RDNA ISA PDFs, `*.tzst`): material de apoio fora do git. Não duplicado aqui.

## Auditoria externa — artefatos usados

- Clone de `https://github.com/WearyConcern1165/xclipse-vulkan-decompiled` em
  `%TEMP%\opencode\xclipse-decompiled` (32 arquivos). Checados:
  `extracted_data/{all_dynamic_symbols,all_strings_raw,exported_functions,samsung_strings,
  amd_pal_strings,all_source_files,assert_messages,vk_strings,decomp_vkCreateInstance}.txt`,
  `features/vk_formats.h`, `vk_icd/vk_device.c`, `vk_icd/vk_instance.c`, `pal/pal_device.h`,
  `sgpu/sgpu_kernel.h`. Conclusão em `driver-analysis/EXTERNAL_REPO_AUDIT.md`.
