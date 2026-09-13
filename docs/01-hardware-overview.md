# Hardware Overview

**Status:** confirmed for the supplied SM-S721B capture, with revision-specific details kept separate.

The current laboratory target is a Samsung SM-S721B (`r12s`) using platform `erd9945` and hardware `s5e9945`. The SGPU render node is `/dev/dri/renderD128`, attached to the platform device `/sgpu@22200000` and the kernel driver `sgpu`. The display path is separate: `/dev/dri/renderD129` is attached to `exynos-drm`.

| Field | Observed value | Evidence label |
| --- | --- | --- |
| Model | `SM-S721B` | Confirmed from device log |
| Device codename | `r12s` | Confirmed from device log |
| Platform | `erd9945` | Confirmed from device log |
| Hardware property | `s5e9945` | Confirmed from device log |
| GPU family | `147 (MGFX)` | Confirmed from SGPU probe |
| Device ID | `0x000073a0` | Confirmed from SGPU probe |
| Chip revision | `0x02600200` | Confirmed from SGPU probe |
| SGPU node | `/dev/dri/renderD128` | Confirmed from device log |
| SGPU compatible | `samsung-sgpu,samsung-sgpu` | Confirmed from uevent/DT |
| GFX IP | one instance, version `10.0` | Confirmed for this capture |
| COMPUTE IP | one instance, version `10.0` | Confirmed for this capture |
| DMA IP | zero instances reported | Confirmed for this capture |
| Wave front size | `32` | Confirmed for this capture |
| Active CUs | `12` | Confirmed for this capture |

The device log also reports `ro.hardware.vulkan=samsung` and `ro.hwui.use_vulkan=true`. These properties establish the intended Android graphics configuration, not that a Termux process can load the Samsung ICD.

## Revision boundary

The source release includes an `s5e9945-sgpu_evt0.dtsi` file with `chip_revision = <0x02600100>`, while the observed device reports `0x02600200`. This difference is a reason to keep EVT0 source values separate from the observed sample until the exact build and Device Tree composition are correlated.

## What this does not prove

The hardware summary does not prove shader ISA compatibility with AMDGPU, RADV, or Turnip. The AMDGPU-like family and identifiers appear in the kernel/UAPI layer, but user-space compiler and driver compatibility remain open questions.

## References

[1]: https://quickshare.samsungcloud.com/cN3RdfqvjU6y "Quick Share archive supplied for Xclipse Open Project analysis"
[2]: https://registry.khronos.org/vulkan/specs/1.3-extensions/html/ "Vulkan API specification"
