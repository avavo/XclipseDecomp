# Bring-up on SM-S926B — 2026-09-06
# (EN translation of radv/data/devices/SM-S926B/2026-09-06-bringup/RESULTS.md)

Run via ADB as `uid=2000(shell)`, SELinux `Enforcing`, no root.
SM-S926B (`e2s`), Android 16, build `S926BXXSHDZH3`, kernel `6.1.157-android14-11`.
This device is distinct from the SM-S721B of the old captures.

DRM: `amdgpu 3.42.0`; platform driver: `sgpu`. Device `0x73a0`, chip
`0x02600200`, family `147`, 12 CUs, DRM wave 32. Initial VA `0x8000000`, limit
`0x800000000000`, GART alignment/page 4096.

## Results

| Test | Result | Evidence (original repo, not copied here) |
| --- | --- | --- |
| Identity/VA query | PASS | query-v2.log |
| C profile test on Android | PASS | profile.log |
| Native 64 KiB BO, CPU write/read, VA map/unmap, cleanup | PASS | native-final.log |
| Repeated native memory | 10/10 PASS | native-repeat10.log |
| Direct PRIME, system-uncached, 64 KiB | PASS | prime-system-uncached.log |
| Direct PRIME, system, 64 KiB | PASS | prime-system.log |
| Fixed libdrm, system-uncached, 64 KiB | PASS | vendor-system-uncached.log |
| Fixed libdrm, system, 64 KiB | PASS | vendor-system.log |
| Fixed libdrm, old 4 KiB size | PASS | vendor-4k.log |
| Repeated libdrm import | 10/10 PASS | vendor-repeat10.log |
| Imported BO system-uncached: VA map/unmap | PASS | imported-va-uncached.log |
| Imported BO system: VA map/unmap | PASS | imported-va-system.log |
| Context, syncobjs and CPU sync_file | PASS | context-sync-file.log |

Repeats open/close separate sessions. Cleanup returns success; this is not a
systematic measurement of in-kernel leaks.

## Confirmed fixes

- The phone's libdrm matches the audited artifact SHA-256:
  `8CE6C7735DED02D05D2F19998BC64EFCE65F20A42F38773845DA342DA8021373`.
  The fixed DMA-BUF type `1` → `2` now imports successfully, including 4 KiB.
  The old probe's static defect has a runtime-validated fix.
- `DRM_VERSION` returns `amdgpu`, but sysfs identifies the platform as `sgpu`.
  The first version rejected that name (failure preserved in query.log).
  The code accepts both and requires known device/family before allocating/importing.
- Common heap nodes are opened `O_RDONLY`; the alloc ioctl creates the DMA-BUF
  `O_RDWR`. Supported by `dma_heap_ioctl_allocate` in the supplied kernel and
  worked as shell. No permission or SELinux changes.
- `amdgpu_device_initialize` returns `0` with residual errno `2`: success.
  The function return decides the result; errno is kept for diagnostics.
- Tested buffers needed no protected heap or image metadata.
  This does not resolve gralloc/DCC requirements.

## Sync scope

GFX 10.0 reported rings `0xf`, COMPUTE 10.0 rings `0x7`, both with IB alignment
32/32. DMA reported zero rings. The fresh context showed `hangs=0` and
`reset_status=0` and was released successfully.

Passed: two syncobj creations, CPU signalling, immediate wait, sync_file export,
import into the second object, wait and destroy. After resetting the first object,
the immediate wait returned `ETIME` (62), as expected.

**No IB/PM4 was submitted and no shader executed.** This does not test GPU-produced
fences, Vulkan timelines, WSI or CPU/GPU coherency. No global absence of
faults/resets was proven, only the queried state of that fresh context.

## Provenance

Each log has JSON with command, UTC times, ADB exit code and log hash.
identity.log and final-provenance.log record identity, SELinux and hashes.
build-v2.json matches the initial tests/repeats; build-v3.json matches import+VA
and context/sync. The manifests' `deviceTestsRun=false` describes the cross-build
moment; later runs are documented in the per-command JSON.

Final binaries were at `/data/local/tmp/radv-bringup-20260906-03/`.
Test folders `radv-bringup-20260906-01`, `-02`, `-03` were kept for reproduction.
The first holds the probe that rejected the DRM name. No vendor library or old
binary was modified.

Next milestone: minimal CS with GPU fence, then compute with known output.
IB/preamble, residency/BO-list and recovery were still open for that run;
CPU-signalled syncobj does not replace that milestone.
