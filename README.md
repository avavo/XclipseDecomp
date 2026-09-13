# Xclipse 940 / Exynos 2400 — Arquivo privado

Bundle curado em 2026-09-13 a partir de `C:\Users\alvaro\Documents\radv` (origin `avavo/RadvXclipse`)
+ análise estática de `vendor/vulkan.samsung.so` (SM-S926B, 44.423.944 bytes)
+ auditoria de https://github.com/WearyConcern1165/xclipse-vulkan-decompiled

> PRIVADO. Contém referência a blobs proprietários Samsung (`vulkan.samsung.so`,
> `libdrm_sgpu.so`, snapshot kernel). NÃO tornar público sem remover/relicenciar.
> Ver `../radv/vendor/README.md` e `../radv/source-analysis/license-inventory.md`.

## O que tem aqui

```text
README.md                        este arquivo
docs/                            cópias curadas do repo local
  01-hardware-overview.md        SM-S721B r12s, erd9945/s5e9945, 0x73a0, fam 147, GFX/COMPUTE 10.0, 12 CUs, wave32
  03-device-tree-and-platform.md DT /sgpu@22200000
  17-textures-and-images.md      doc base de texturas do repo local
  LOCAL_FINDINGS.md              bug handle-type 1 vs 2, hashes ELF, limites
logs/                            capturas hashes + 1 RESULTS
  SM-S926B-2026-09-06-bringup-RESULTS.md
  SM-S721B-build-properties.txt / firmware-and-gpu.txt / hashes.txt
driver-analysis/
  BCN_BC1-BC7.md                 resposta: BC1-7 faltam? incompletos?
  EXTERNAL_REPO_AUDIT.md         o repo WearyConcern1165 é verdade?
  reproduce_bcn.py               re-executa a análise de strings/ELF localmente
  IMG_FMT-list-local.txt         260 IMG_FMT_* extraídos do .so local
  local-dynsym.txt               344 símbolos .dynsym locais
  local-bc-strings.txt / local-string-hits.txt  dumps brutos (verbosos)
inventory/
  SOURCES.md                     onde está cada coisa no repo original + o que NÃO foi copiado
```

## Xclipse 940 / Exynos 2400 em 30 segundos (só o confirmado no seu repo)

- Alvo lab: SM-S721B (`r12s`), plataforma `erd9945`, hw `s5e9945`; SGPU em
  `/dev/dri/renderD128` (`samsung-sgpu,samsung-sgpu`, `/sgpu@22200000`), display separado
  em `renderD129`. GFX 1×10.0 rings `0xf`, COMPUTE 1×10.0 rings `0x7`, DMA 0.
  Família `147 (MGFX)`, device `0x73a0`, chip `0x02600200` (EVT0 no fonte = `0x02600100`,
  manter separado). 12 CUs, wave32 (DRM) vs 64 (campo estático Vulkan). Fonte:
  `docs/01-hardware-overview.md` copiado aqui.
- SM-S926B (S24+, Exynos 2400 / Xclipse 940): GEM/VA/import/sync CPU validados 2026-09-06;
  CS/fence/readback, shader via submit próprio e NIR restrito validados 2026-09-07→12
  (ver `PORT_STATUS.md` e `data/devices/SM-S926B/*` no repo original — NÃO copiados
  integralmente aqui, ver `inventory/SOURCES.md`).
- Driver: `/vendor/lib64/hw/vulkan.samsung.so` (local 44.423.944 bytes), `libdrm_sgpu.so`
  (`8CE6C773…`), ICD carregado em SurfaceFlinger, Termux só vê llvmpipe. Bug clássico:
  `test_standalone` passa `handle_type=1` onde a lib exige `2` p/ DMA-BUF.

## Criar o repo privado no GitHub (sem `gh`, 3 min)

`gh` não está instalado nesta máquina, então o push não foi feito automaticamente.
O diretório atual já é um bundle pronto — basta:

1. No GitHub web: New repository → nome sugerido `xclipse940-privado` → **Private** →
   **NÃO** marcar add README/license (já existem arquivos). Create.
2. No PowerShell, dentro desta pasta:

```powershell
git init
git add .
git commit -m "Arquivo privado Xclipse 940/Exynos 2400 + analise BCn + auditoria externa (2026-09-13)"
git branch -M main
git remote add origin https://github.com/<seu-user>/xclipse940-privado.git
git push -u origin main
```

3. Opcional (recomendado): ative push protection / secret scanning nas settings do repo.
4. NÃO adicione `vendor/*.so` nem `SM-S926B-opensource/` (~2,5 GB) sem pensar em LFS/custo.
   Este bundle traz só hashes/listas; use `inventory/SOURCES.md` p/ copiar os blobs
   localmente se precisar (continuam privados).

## Revalidar a análise BCn

```powershell
python .\driver-analysis\reproduce_bcn.py ..\radv\vendor\vulkan.samsung.so
```

Saída esperada (build SM-S926B local): 16 `VK_FORMAT_BC*`, 14 `Bc*`, 6 `IMG_FMT_BC1-3`,
0 `IMG_FMT_BC4-7`, 0 `textureCompressionBC`, 0 `FormatPropertiesTable`.
Detalhes em `driver-analysis/BCN_BC1-BC7.md`.
