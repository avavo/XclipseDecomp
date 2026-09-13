# Textures and Images

**Status:** planned investigation; no result is claimed until an evidence record is linked.

## Purpose

Document formats, tiling, swizzles, layouts, compression, views, and synchronization requirements.

## Current boundary

The project plan identifies this area as necessary for an independent Xclipse driver, but the supplied plan is not itself proof that the area has been implemented or experimentally validated. This chapter must distinguish source-backed facts, direct observations, probable interpretations, hypotheses, and discarded approaches.

## Evidence table

| Question | Evidence required | Current state | Confidence |
| --- | --- | --- | --- |
| What is known? | Raw artifact, source path, or reproducible output. | Initial plan only. | Hypothesis until an artifact is attached. |
| What is executable? | A test that reaches the target layer and validates a result. | Not demonstrated by the plan. | Not established. |
| What can be reused? | License and provenance review. | Pending archive inventory. | Not established. |

## Method

Start with read-only observations and source inventory. Preserve raw outputs without cosmetic edits. Add an interpretation report beside each raw artifact. If a harness initializes a test but does not submit and validate work on the target GPU, record it as an initializer or probe rather than an execution test.

## Open questions

The chapter remains open until the relevant source paths, device revision, firmware context, safety boundary, and reproducible validation procedure are documented.

## References

[1]: https://registry.khronos.org/vulkan/specs/1.3-extensions/html/ "Vulkan API specification"
[2]: https://source.android.com/docs/core/architecture/vndk/linker-namespace "Android linker namespaces"
