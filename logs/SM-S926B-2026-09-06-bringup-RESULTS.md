# Bring-up no SM-S926B — 2026-09-06

Execução via ADB como `uid=2000(shell)`, SELinux `Enforcing`, sem root.
SM-S926B (`e2s`), Android 16, build `S926BXXSHDZH3`, kernel `6.1.157-android14-11`.
Este aparelho é distinto do SM-S721B das capturas antigas.

DRM: `amdgpu 3.42.0`; driver de plataforma: `sgpu`. Device `0x73a0`, chip
`0x02600200`, família `147`, 12 CUs, wave DRM 32. VA inicial `0x8000000`, limite
`0x800000000000`, alinhamento/página GART 4096.

## Resultados

| Teste | Resultado | Evidência |
| --- | --- | --- |
| Consulta de identidade/VA | PASS | [query-v2.log](query-v2.log) |
| Teste C de perfil no Android | PASS | [profile.log](profile.log) |
| BO nativo 64 KiB, CPU write/read, VA map/unmap, cleanup | PASS | [native-final.log](native-final.log) |
| Memória nativa repetida | 10/10 PASS | [native-repeat10.log](native-repeat10.log) |
| PRIME direto, system-uncached, 64 KiB | PASS | [prime-system-uncached.log](prime-system-uncached.log) |
| PRIME direto, system, 64 KiB | PASS | [prime-system.log](prime-system.log) |
| libdrm corrigida, system-uncached, 64 KiB | PASS | [vendor-system-uncached.log](vendor-system-uncached.log) |
| libdrm corrigida, system, 64 KiB | PASS | [vendor-system.log](vendor-system.log) |
| libdrm corrigida, tamanho antigo 4 KiB | PASS | [vendor-4k.log](vendor-4k.log) |
| Importação libdrm repetida | 10/10 PASS | [vendor-repeat10.log](vendor-repeat10.log) |
| BO importado system-uncached: VA map/unmap | PASS | [imported-va-uncached.log](imported-va-uncached.log) |
| BO importado system: VA map/unmap | PASS | [imported-va-system.log](imported-va-system.log) |
| Contexto, syncobjs e sync_file CPU | PASS | [context-sync-file.log](context-sync-file.log) |

As repetições abrem/fecham sessões separadas. Cleanup retorna sucesso; isso não
é uma medição sistemática de vazamentos internos do kernel.

## Correções confirmadas

- A libdrm do telefone tem o mesmo SHA-256 do artefato auditado:
  `8CE6C7735DED02D05D2F19998BC64EFCE65F20A42F38773845DA342DA8021373`.
  O tipo DMA-BUF corrigido de `1` para `2` agora importa com sucesso, inclusive
  4 KiB. O defeito estático do probe antigo tem uma correção validada em runtime.
- `DRM_VERSION` retorna `amdgpu`, mas sysfs identifica a plataforma como `sgpu`.
  A primeira versão rejeitou esse nome: [query.log](query.log) preserva a falha.
  O código aceita ambos e exige device/família conhecidos antes de alocar/importar.
- Os nós dos heaps comuns são abertos com `O_RDONLY`; o ioctl de alocação cria
  o DMA-BUF com `O_RDWR`. Isso é suportado por `dma_heap_ioctl_allocate` no kernel
  fornecido e funcionou como shell. Não foram alterados permissões ou SELinux.
- `amdgpu_device_initialize` retorna `0` com errno residual `2`: é sucesso.
  O retorno da função determina o resultado; errno é preservado para diagnóstico.
- Os buffers testados não exigiram heap protegido ou metadata de imagem.
  Isso não resolve os requisitos de gralloc/DCC.

## Alcance da sincronização

GFX 10.0 reportou rings `0xf`, COMPUTE 10.0 rings `0x7`, ambos com alinhamento
de IB 32/32. DMA reportou zero rings. O contexto recém-criado teve `hangs=0` e
`reset_status=0` e foi liberado com sucesso.

Passaram: criação de dois syncobjs, sinalização pela CPU, espera imediata,
exportação de sync_file, importação no segundo objeto, espera e destruição.
Após reset do primeiro objeto, a espera imediata retornou `ETIME` (62), esperado.

**Não foi submetido IB/PM4 nem executado shader.** Isso não testa fence produzida
por GPU, timeline Vulkan, WSI ou coerência CPU/GPU. Não se comprovou ausência
global de faults/resets, apenas o estado consultado desse contexto novo.

## Proveniência

Cada log possui JSON com comando, horários UTC, código de saída ADB e hash do log.
[identity.log](identity.log) e [final-provenance.log](final-provenance.log) registram
identidade, SELinux e hashes. [build-v2.json](build-v2.json) corresponde aos testes
iniciais/repetições; [build-v3.json](build-v3.json), à importação+VA e contexto/sync.
O campo `deviceTestsRun=false` dos manifests descreve o momento do cross-build;
as execuções posteriores são documentadas aqui e nos JSON de cada comando.

Os executáveis finais estão em `/data/local/tmp/radv-bringup-20260906-03/`.
As pastas de teste `radv-bringup-20260906-01`, `-02` e `-03` foram mantidas para
reprodução. A primeira contém o probe que rejeitava o nome DRM. Nenhuma biblioteca
vendor ou binário antigo foi modificado.

Próximo marco: CS mínimo com fence GPU, depois compute com saída conhecida.
Faltam determinar/implementar IB/preamble, residência/BO list e recuperação para
essa execução; syncobj sinalizado por CPU não substitui esse marco.
