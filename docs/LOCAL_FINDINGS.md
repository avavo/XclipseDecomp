# Achados locais e correções — 2026-09-06

Atualização: [execução no SM-S926B](../../data/devices/SM-S926B/2026-09-06-bringup/RESULTS.md)
confirmou importação corrigida, memória nativa, VA de BO importado e sync_file
sinalizado por CPU. O texto abaixo preserva a análise anterior ao teste.

Análise dos arquivos fornecidos, sem execução nova no telefone. Os endereços abaixo
são endereços virtuais ELF, não offsets de arquivo. Os binários originais foram preservados.

## Causa demonstrável do `amdgpu_bo_import = -1` no probe fornecido

`../../radv_xclipse_s24_package/bin/test_standalone` resolve `amdgpu_bo_import`
(string em `0xc3d`, ponteiro salvo em `0x50c4`) e faz a chamada:

```text
0x5348  ldr x8, [x26, #0x808]   ; função amdgpu_bo_import
0x5350  add x3, sp, #0x8        ; saída
0x5354  ldr w2, [sp, #0x18]     ; FD do DMA-BUF
0x5358  mov w1, #1              ; tipo incorreto
0x5360  blr x8
```

Na `../../libdrm_sgpu.so` fornecida:

```text
0x10868  mov w23, w1
0x10878  cmp w23, #2
0x1087c  b.ne 0x10928
0x1088c  bl drmPrimeFDToHandle
...
0x10928  mov w26, #-1
0x10934  cmp w23, #1
0x10938  b.eq 0x10a24
...
0x10a2c  mov w0, w26
```

O tipo `1` é rejeitado antes de PRIME. O tipo `2` seleciona o caminho DMA-BUF.
Portanto, **a falha deste par de binários não demonstra que o exporter, heap,
metadata ou alinhamento foram rejeitados pelo kernel**. Não se pode estender essa
conclusão a todas as execuções históricas sem identificar os hashes usados nelas.

Há outro detalhe de ABI: em `0x10b38`, `stp x25, x8, [x20]` escreve dois campos
de 64 bits, handle e tamanho. O probe antigo fornece uma região de saída de 8 bytes
em `sp+8`; o segundo campo sobrepõe os 8 bytes seguintes usados pela alocação DMA.
O substituto usa uma estrutura de 16 bytes com verificação de tamanho/offset.

O fluxo antigo também termina em `0x548c` zerando o código de saída mesmo após
falha de importação e imprime uma mensagem de sucesso. O novo probe considera
falhas de importação, validação e cleanup no resultado final.

`sgpu-import-probe` reconstrói o teste a partir de fonte, com tipo `2`, saída de
16 bytes, `errno` capturado imediatamente e liberação dos recursos. Não modifica
o binário antigo nem a biblioteca Samsung. O tamanho padrão é 64 KiB; `--size 4096`
permite reproduzir o tamanho do teste antigo com o tipo corrigido.

Isso corrige um defeito estático confirmado. **Importação bem-sucedida no aparelho
ainda precisa ser demonstrada**: tipo `2` também passa por PRIME, `lseek` e código
interno da biblioteca. `sgpu-memory-probe --heap ...` isola PRIME diretamente, sem
depender do namespace que carrega a biblioteca vendor.

## Memória: evidência além do resumo antigo

`../../probe_SM-S721B.txt:32` registra `GEM_CREATE`, `mmap+touch`, `VA_MAP`,
`VA_UNMAP` e `GEM_CLOSE` com sucesso. O mesmo log informa duas consultas falhas
(`DRM_VERSION`/EFAULT e `SGPU_KMD_VERSION`/EINVAL); não é um teste inteiramente verde.
Ele comprova uma sequência CPU/VM registrada, não acesso GPU, caches ou submissão.

O novo código usa diretamente o `sgpu_drm.h` da árvore Samsung fornecida:

`../../SM-S926B/SM-S926B_16_Opensource/Kernel/kernel/include/uapi/drm/sgpu_drm.h`

Na mesma árvore, `drivers/gpu/drm/samsung/gpu/sgpu/amdgpu_kms.c:1352` registra
`AMDGPU_GEM_CREATE`, e `amdgpu_gem.c` implementa criação GTT e map/unmap.
O kernel exige GTT na alocação; o probe pede GTT com acesso CPU, sem secure ou metadata.
Os requests são gerados pelos macros do header, não copiados de uma versão desktop.

A origem SM-S926B não garante correspondência exata com o kernel do SM-S721B.
Os hashes do header e do build ficam registrados; nova validação no aparelho é necessária.

O teste nativo usa um novo FD/VM e um único BO de 64 KiB, endereço derivado de
DEV_INFO com validação de alinhamento, intervalo e overflow. Valida o nome DRM
`sgpu` e, antes de alocar, família `147` e device `0x73a0`. Não é um alocador de
VA para múltiplos BOs nem um winsys RADV completo. Map bem-sucedido não comprova
que a GPU leu/escreveu as páginas. Não existe teste de coerência GPU neste probe.

## Identidade e wavefront

| Campo | Captura bruta | Uso no código |
| --- | --- | --- |
| Vulkan vendor | `vkjson-1.txt`: 5197 = `0x144d` | Identificação da captura stock |
| Vulkan device | `vkjson-1.txt:4287`: 39846400 = `0x02600200` | Corrige o antigo `0x02600000` |
| DRM device/família | `probe_SM-S721B.txt`: `0x73a0` / `147` | Seleção DRM separada |
| Wavefront stock | `vkjson-1.txt:32`: 64 | Campo estático Vulkan |
| Wavefront DRM | `probe_SM-S721B.txt:6`: 32 | Campo separado, observado |

Nenhum desses valores, sozinho, escolhe um alvo ACO nem comprova compatibilidade ISA.
Os testes comparam a seleção Vulkan do código diretamente com o JSON fornecido.

## Artefatos exatos auditados

| Arquivo | SHA-256 |
| --- | --- |
| `libdrm_sgpu.so` | `8CE6C7735DED02D05D2F19998BC64EFCE65F20A42F38773845DA342DA8021373` |
| `radv_xclipse_s24_package/bin/test_standalone` | `259925A6975D8E280466901A97EB0FE32AFFA19758C24F73C08E6FD4DFBC9C6E` |
| `probe_SM-S721B.txt` | `1ECA1098B609B158DE7EEDD0229E88251DB30F8BDA104BFD3B4DD1D9DED5972A` |
| `vkjson-1.txt` | `91DA1E4CE7712F113A08A39FE8B235E0AA2FD38D19DD0C35C3FAD170DA6894B3` |

`tests/test_legacy_import.py` verifica hashes, arquitetura ELF e instruções
relevantes. Não executa nem emula código vendor.

## Limite deste avanço

Agora há código compilável para repetir memória nativa e isolar importação direta
e via libdrm. Ainda faltam execução desses novos binários no aparelho, CS/fence,
compute com readback GPU e integração à árvore fonte exata Mesa/RADV. As bibliotecas
RADV empacotadas não substituem essa árvore fonte nem comprovam resultados no Eden.

Após a execução no SM-S926B, memória, importação, VA de BO importado, contexto e
sync_file CPU passaram. O contrato UAPI para a próxima etapa está em
[CS_BRINGUP.md](CS_BRINGUP.md); nenhum submit foi feito nesta sessão.
