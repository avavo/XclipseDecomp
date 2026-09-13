# On-device Vulkan usage snapshot — 2026-09-12 (SM-S721B)

Source: per-app `dumpsys gpu` capture, 88 app blocks (sanitized: counts and
feature masks only, no app identifiers beyond well-known system packages).

- `vulkanVersion 4206592` (API 1.4.0), high `vkLoadingCount` with zero failures;
  `android.hardware.vulkan.compute` and level 1 present.
- `vulkanDeviceFeaturesEnabled` takes only two distinct values across all apps
  (`0x70f37fffbffffe` / `...fffff`, differing only in bit 0,
  `robustBufferAccess`). **Bit 22 (`textureCompressionBC`) is off in every
  app block.**
- Scope warning: this mask records what each app *enabled* at device creation,
  not what the driver *supports*. The observed apps (browsers, messengers,
  system UI) render through ANGLE/ETC2 paths and simply never request BC. This
  neither confirms nor contradicts the driver's default-on BC reporting (see
  `driver-analysis/BCN_BC1-BC7.md`); a direct `vkGetPhysicalDeviceFeatures`
  query is still the capability source of truth.
