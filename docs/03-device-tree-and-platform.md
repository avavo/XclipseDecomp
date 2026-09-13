# Device Tree and Platform

**Status:** source-backed and cross-checked against the supplied device capture.

The Samsung source release defines the SGPU node for s5e9945 in `kernel/arch/arm64/boot/dts/exynos/s5e9945-sgpu_common.dtsi`. The node is `sgpu@22200000` with compatible string `samsung-sgpu,samsung-sgpu`. The observed uevent exposes the same compatible string and full name `/sgpu@22200000`.

| Property | Source-backed value | Meaning or follow-up |
| --- | --- | --- |
| Node | `sgpu@22200000` | Platform GPU node and address base. |
| Compatible | `samsung-sgpu,samsung-sgpu` | Matches `sgpu_kms_driver` in `amdgpu_drv.c`. |
| Register regions | `gpu`, `doorbell`, `debug`, `pwrctl`, `sysreg`, `htu` | Six MMIO regions are declared; access must remain source- and safety-reviewed. |
| Interrupts | `SGPU`, `GPU-AFM` | GPU and adaptive-frequency-management interrupt sources. |
| Chip flag | `CHIP_VANGOGH_LITE` | The driver maps this flag to device ID `0x73A0`. |
| GL2 ACEM instances | `4` | Consumed during driver initialization. |
| Power | `pd_g3dcore` | GPU power-domain dependency. |
| Coherency | `dma-coherent` | Source declaration; memory behavior still requires runtime validation. |
| AFM | PMIC source `2`, offset `0x20` | Power safety and frequency limiting path. |

`amdgpu_drv.c` reads `chip_revision` from the Device Tree unless a force parameter overrides it. It also reads the GL2 ACEM instance count and optionally the DVFS calibration ID. The Samsung driver registers a platform driver named `sgpu`, not only a conventional PCI driver.

## Revision-specific data

The EVT0 include adds `chip_revision = <0x02600100>` and DVFS/IFPO parameters. The observed sample reports `0x02600200`. This repository therefore treats Device Tree values as revision-scoped evidence, not universal Xclipse constants.

## Platform-to-GPU path

The observed path is: `/sys/firmware/devicetree/base/sgpu@22200000` → platform device `22200000.sgpu` → driver `/sys/bus/platform/drivers/sgpu` → DRM nodes `card0` and `renderD128`. The display controller is a separate `exynos-drm` path on `card1` and `renderD129`.

## References

[1]: https://quickshare.samsungcloud.com/cN3RdfqvjU6y "Quick Share archive supplied for Xclipse Open Project analysis"
[2]: https://docs.kernel.org/devicetree/usage-model.html "Linux DeviceTree usage model"
