# Auditoria: WearyConcern1165/xclipse-vulkan-decompiled — o que é verdade?

Auditado em 2026-09-13 via clone + `vendor/vulkan.samsung.so` local (SM-S926B, 44.423.944 bytes).
O repo externo analisa outro build (eles citam 44.514.072 bytes, ~90 KB maior) e NÃO entrega
o binário — só `extracted_data/*.txt` + `.h/.c` “reconstruídos”. Veredito por claim:

## VERDADEIRO (confirmado aqui ou nos próprios artefatos deles)

- **Base AMD**: XGL (`drivers/xgl/icd/api/vk_device.cpp` etc.), PAL (`Pal::*`, `palSysUtil.h`,
  `palPipelineAbiProcessorImpl.h`), SC (`SCEmitterGFX10/103/40/401/402/403/404`, `SCTargetInfo*`,
  `AMDGPU.*`, `AMDVLK_ENABLE_DEVELOPING_EXT`, `AMD Vulkan Driver`). Local confirma todos.
- **HAL Samsung real**: `Samsung::Vulkan::OpenDevice/CloseDevice`, `vulkan.samsung.so`,
  `SGR` (`sgr_intf_*`, 27 símbolos dynsym), `SBWC` (`libsbwchelper.so`, `SBWCHelper::*`),
  `amdgpu_*` fork (`amdgpu_bo_list_destroy_raw`, `amdgpu_cs_ctx_create3`, etc.).
- **Alocação 0xdb48 em `vkCreateInstance`**: `mov w1, 0xdb48` existe no
  `decomp_vkCreateInstance.txt` deles (1 hit). É plausível p/ o build deles.
  (No build local SM-S926B o padrão `01 69 9B 52` dá 0 hits — tamanho difere por build.
  Não generalize.)
- **60+ extensões / Vulkan 1.3 / RDNA2-GFX10**: local tem 398 strings `VK_*`
  (incl. `VK_AMD_*`, `VK_EXT_*`, `VK_KHR_*`, `VK_ANDROID_*`). O número “60+” é até
  conservador. A lista exata em `vk_icd/vk_device.c` deles é curada à mão, mas a ordem
  de grandeza está certa.
- **Nomes BC1–7 existem**: `VK_FORMAT_BC*` (16) + `Bc*` (14) nos dois builds. BC1–3 com
  `IMG_FMT`, BC4–7 sem `IMG_FMT` (ver `BCN_BC1-BC7.md`). O fenômeno “BC4–7 sem suporte”
  é real no nível estático; o mecanismo exato eles não provam (ver abaixo).

## FALSO ou NÃO SUBSTANCIADO (com prova)

1. **“830+ símbolos dinâmicos” — FALSO.** O próprio `extracted_data/all_dynamic_symbols.txt`
   deles é um `readelf` que diz `contains 345 entries` (348 linhas c/ cabeçalho).
   Local: 345 entradas, 344 não vazias. O número 830 não aparece em nenhum artefato.
2. **“~39.000 strings” — FALSO.** `all_strings_raw.txt` deles tem 2.715.442 bytes e
   **197.676 linhas**, não 39k. Local (método `strings ≥4`): 308.023 strings.
3. **“Tabela de 221 formatos” via assert `FormatPropertiesTable::GetFormatFlags: invalid
   formatId (formatId:221)` — SEM EVIDÊNCIA.** 0 hits para `FormatPropertiesTable`,
   `GetFormatFlags`, `formatId`, `invalid formatId` no binário local **e** 0 hits em
   todos os arquivos do repo deles exceto o próprio `features/vk_formats.h` que inventa
   a citação. `221` aparece 2× no dump deles em contextos não relacionados. Sem dump da
   tabela, “221 entradas” e “flags zeradas p/ 139–146” são afirmação sem prova.
4. **“Magic 0x01cdc0de” — SEM EVIDÊNCIA.** 0 hits no binário local (bytes LE/BE), 0 hits
   no `decomp_vkCreateInstance.txt` deles. `0xdb48` tem 1 hit; o magic não tem nenhum.
   `vk_instance.c` deles apresenta `0x01cdc0de`, offsets `0xd810/0xd850/0xd890/0xd8b8`
   e struct `SgpuInstance` como “da desmontagem”, mas o txt só sustenta `0xdb48`/`0xd810`.
5. **“95% AMD + 5% Samsung” / “60+ device extensions exatas” / `GfxIpLevel 0x2801–0x2805`
   (“940 = 0x2803”, “405 = futuro”) — NÚMEROS INVENTADOS.** Nenhuma medição de LoC,
   nenhum dump de `GfxIpLevel`, nenhum `GFX405` no build local (só 40–404 + `MGFX1–4`).
   Podem ser inferências razoáveis, mas são apresentadas como extração.
6. **`sgpu_query_soc_info` como “presente” — SÓ NO BUILD DELES.** 1 hit no dump deles,
   **0 hits** no `.so` SM-S926B local (que tem `sgpu_query_dump_bpmd{,_to_fd}`,
   `sgpu_query_gpu_page_faults`, `sgpu_query_ifpo_disable`, `sgpu_instance_data_destroy`).
   Não é universal; citar como interface estável do SGPU é enganoso.
7. **“Decompiled source” — NA VERDADE STUBS.** `hal/android_hal.c`, `vk_icd/*.c`,
   `pal/*.h`, `shader_compiler/*.h` são headers/código escritos à mão com 1–2 strings
   reais como pretexto (“Source paths (from binary)”) + resto inferido de AMDVLK público.
   Não há CFG, pseudocódigo Hex-Rays/Ghidra, nem diff contra GPUOpen-Drivers. O único
   artefato real de desmontagem é `decomp_vkCreateInstance.txt` (saída crua de
   desassemblador com ANSI, 323 KB) — e nem ele contém o magic citado.
8. **“Desligado por tabela de software, reative com layer” — OVERSIMPLIFICAÇÃO.**
   O dado estático real é mais forte e mais nuançado: `IMG_FMT_BC4/5/6/7` **não existem**
   como strings PAL (só BC1–3), enquanto `VK_FORMAT_BC4–7` + `Bc4–7` existem. Isso sugere
   backend incompleto/ausente, não um simples `capabilities=0` numa tabela de 221.
   O “layer que intercepta `vkGetPhysicalDeviceFormatProperties`” pode mascarar a query,
   mas não cria backend de amostragem/decompressão se ele não existir — e eles nunca
   testaram no aparelho (sem evidência de CTS, `vulkaninfo`, ou trace).

## O que usar / o que descartar desse repo

- USE como índice de strings e mapa de onde olhar (XGL/PAL/SC, SGR/SBWC, `amdgpu_*`,
  `SCEmitterGFX40x`, 17 extensões de instância como hipótese de trabalho).
- NÃO CITE os números 830+, 39k, 221, `0x01cdc0de`, `0x2801–2805`, “95/5%” sem revalidar.
- NÃO trate `features/vk_formats.h` como dump — é um header didático, não extração.
- Para BCn, prefira `BCN_BC1-BC7.md` + `reproduce_bcn.py` deste bundle (rodados no seu
  build) + teste runtime no S926B (`textureCompressionBC` + `FormatProperties` por formato).

## Reprodução (o que foi rodado)

- Clone: `git clone https://github.com/WearyConcern1165/xclipse-vulkan-decompiled.git`
- Contagens no dump deles: `all_dynamic_symbols.txt` 348 linhas / 345 entradas;
  `all_strings_raw.txt` 197.676 linhas; `FormatPropertiesTable` 0; `sgpu_query_soc_info` 1.
- No `.so` local: `VK_FORMAT_BC*` 16, `Bc*` 14, `IMG_FMT_BC1-3` 6, `IMG_FMT_BC4-7` 0,
  `textureCompressionBC` 0, `.dynsym` 345, `mov w1,0xdb48` 0, magic 0.
