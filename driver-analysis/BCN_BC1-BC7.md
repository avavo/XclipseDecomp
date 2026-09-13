# BCn no driver Xclipse (local SM-S926B) — BC1, BC2, BC3, BC4, BC5, BC6H, BC7

Pergunta: o driver tem BCn 1,2,3,4,5,6 e 7? Falta algum? Algum incompleto?

Método (estático, reproduzível): `python driver-analysis/reproduce_bcn.py <vulkan.samsung.so>`.
Alvo auditado: `radv/vendor/vulkan.samsung.so`, 44.423.944 bytes, ELF AArch64.
NÃO é prova de comportamento runtime — o veredito final exige
`vkGetPhysicalDeviceFeatures` (`textureCompressionBC`) +
`vkGetPhysicalDeviceFormatProperties[2]` no aparelho.

## Resposta curta

- **Nenhum BC some por completo como nome**: os 16 `VK_FORMAT_BC*` (131–146) e os 14
  `Bc*` internos existem no binário.
- **BC1, BC2, BC3 — completos no nível estático**: `VK_FORMAT_*` + `Bc*_Unorm/Srgb` +
  `IMG_FMT_BC1/2/3_{UNORM,SRGB}` presentes.
- **BC4, BC5, BC6H, BC7 — INCOMPLETOS no backend**: `VK_FORMAT_BC4_{UNORM,SNORM}`,
  `BC5_{UNORM,SNORM}`, `BC6H_{UFLOAT,SFLOAT}`, `BC7_{UNORM,SRGB}` + `Bc4/5/6/7_*`
  existem, mas **não há nenhum `IMG_FMT_BC4/5/6/7`** (0 hits em bytes brutos).
  `IMG_FMT` total = 260 entradas, das quais só `BC1/2/3` aparecem. Também **zero hits**
  para `textureCompressionBC`, `FormatPropertiesTable`, `GetFormatFlags`, `formatId`.
- Ou seja: o frontend Vulkan conhece os nomes BC4–7, mas o PAL interno não expõe o
  mapeamento de imagem correspondente nas strings — compatível com “anunciado como
  não suportado / sem backend”, não com “tabela de flags zerada” (essa tabela nunca
  foi despejada por ninguém até aqui).

## Tabela (estático local)

| Formato | VK_FORMAT_* | Bc* interno | IMG_FMT_* (PAL) | Veredito estático |
|---|---|---|---|---|
| BC1 RGB UNORM/SRGB, RGBA UNORM/SRGB (131–134) | 4/4 | Bc1_Unorm/Srgb | BC1_UNORM/SRGB | completo |
| BC2 UNORM/SRGB (135–136) | 2/2 | Bc2_Unorm/Srgb | BC2_UNORM/SRGB | completo |
| BC3 UNORM/SRGB (137–138) | 2/2 | Bc3_Unorm/Srgb | BC3_UNORM/SRGB | completo |
| BC4 UNORM/SNORM (139–140) | 2/2 | Bc4_Unorm/Snorm | — (0) | **incompleto** |
| BC5 UNORM/SNORM (141–142) | 2/2 | Bc5_Unorm/Snorm | — (0) | **incompleto** |
| BC6H UFLOAT/SFLOAT (143–144) | 2/2 | Bc6_Ufloat/Sfloat | — (0) | **incompleto** |
| BC7 UNORM/SRGB (145–146) | 2/2 | Bc7_Unorm/Srgb | — (0) | **incompleto** |

Contexto: ETC2 (6 `VK_FORMAT_ETC2_*` + 10 `IMG_FMT_ETC2_*`) e ASTC LDR (28
`VK_FORMAT_ASTC_*` + 28 `IMG_FMT_ASTC_*`) têm mapeamento completo nos dois níveis —
o buraco é específico de BC4–7.

## O que isso NÃO prova

- Não prova bloqueio deliberado vs limitação de HW: RDNA2 desktop suporta BC4–7, e o
  Xclipse é GFX10/MGFX (ver abaixo), mas sem teste runtime não dá p/ afirmar “HW
  suporta e Samsung desligou por flag”.
- Não prova os 221 formatos nem “capability flags = 0”: essas afirmações do repo
  externo não têm dump da tabela nem assert correspondente no binário (0 hits aqui e
  0 hits nos próprios `extracted_data` deles).
- `RESERVED_*` em `IMG_FMT` (100+ entradas) poderiam teoricamente mapear BC4–7 sem
  strings — só um dump runtime da tabela ou engenharia do `vkGetPhysicalDeviceFormatProperties`
  resolve.

## Como confirmar no aparelho (pendente)

```c
VkPhysicalDeviceFeatures f; vkGetPhysicalDeviceFeatures(phys, &f);
// f.textureCompressionBC == VK_TRUE?
for (VkFormat fmt = VK_FORMAT_BC1_RGB_UNORM_BLOCK; fmt <= VK_FORMAT_BC7_SRGB_BLOCK; fmt++)
  vkGetPhysicalDeviceFormatProperties(phys, fmt, &props);
// checar props.optimalTilingFeatures & SAMPLED_IMAGE_BIT etc.
```

Se `textureCompressionBC==VK_FALSE` e BC4–7 retornarem 0, o bloqueio é real no
runtime (independentemente do mecanismo). Se retornarem features, o HW+driver
suportam e o “disabled” externo está errado p/ este build.

## Outros achados do .so local relevantes a BCn

- GFX: `SCEmitterGFX40/401/402/403/404`, `SCTargetInfoGFX40/401/402/403`,
  `MGFX1:gfx4010` … `MGFX4:gfx4040`. **Sem `GFX405`** neste build.
- XGL/PAL confirmados: `drivers/xgl/icd/api/*.cpp`, `SCEmitter*`, `AMDVLK_ENABLE_DEVELOPING_EXT`,
  `AMD Vulkan Driver`, `Samsung::Vulkan::OpenDevice/CloseDevice`, `vulkan.samsung.so`.
- `sgpu_query_soc_info` = 0 hits aqui (existe 1 hit no dump externo — diferença de build).
  `sgpu_instance_data_destroy`, `amdgpu_bo_list_destroy_raw`, `amdgpu_cs_ctx_create3` = 1 hit.
- `.dynsym` = 345 entradas (344 não vazias), não 830+. `VK_*` = 398 strings (60+ extensões: OK).
- `Xclipse` só em “Xclipse GPU Fault”; sem “Xclipse 940/920”, sem `0x73A0`, sem “Exynos 2400”
  (só `exynos9810` residual). IDs de DaVinci vêm de probes/JSON, não do `.so`.
