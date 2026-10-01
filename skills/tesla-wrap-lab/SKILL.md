---
name: tesla-wrap-lab
description: Create, fit, preview and refine custom Tesla Model Y Paint Shop wrap PNGs using image generation and a local 3D viewer, then explain installation in the Tesla app or by USB. Supports original Model Y, 2025+ Standard, Premium, Performance and Model Y L.
---

# Tesla Wrap Lab

Deliver a model-specific PNG, an actual mapped preview, and installation steps. This changes the car's digital Paint Shop appearance, not physical vinyl or vehicle geometry.

## Locate and start the studio

Run `python3 <this-skill>/scripts/bootstrap.py --setup`. It resolves a linked checkout, `TESLA_WRAP_LAB_DIR`, or clones the public repository into this skill's `.runtime/`. It installs local dependencies and downloads checksum-pinned templates/meshes. Use the returned checkout and Python paths; never assume the user's working directory is the viewer.

Start `npm run dev -- --port 5178` in that checkout and verify the returned local URL. If the port is occupied, use the actual URL Vite reports. Read the checkout's `AGENTS.md` and `docs/PIPELINE.md` before producing a new design. For existing examples, select the model/design in the viewer and validate the exported file; generation is unnecessary.

## Resolve the exact model

Use known conversation context. Otherwise ask for the body generation and trim before generating model-dependent artwork. `Long Range` is not `Model Y L`; a registration year alone may not identify a transition-year body. Run `<python> scripts/wrap.py models` for supported ids. 2025+ Standard, Premium and Performance each have their own template. Keep exports and metadata bound to one model. Never apply the original Model Y PNG to every newer body or relabel it as compatible.

## Generate → fit → inspect → refine

1. Translate the user's theme into a coherent palette and motifs. Use the built-in imagegen tool when available. A car concept is optional, but detailed raster artwork must come from imagegen; do not replace it with crude canvas sketches. If imagegen is unavailable, explain that limitation and offer an existing example or user-supplied artwork. Do not silently use a paid API fallback.
2. For a rich full-body design, capture neutral views of the actual selected mesh first. Use them to plan how artwork follows handles, mirrors, seams, wheel arches and painted roof rails; leave glass alone. Use `docs/FEATURE-AWARE.md` for surface-to-UV probing. Prefer a coherent multi-view concept followed by a decomposed atlas over repeating one crest in approximate boxes. Generate feature-sensitive ornaments separately when exact placement matters.
3. Inspect the exact local template `public/templates/<model>.png` before sending it to imagegen. Generate either a full flat atlas with exact island layout, or reusable detailed decal tiles. Preserve generated sources and prompts in `artifacts/<design>/<model>/`. For tiles, use per-model placement boxes in `public/models.json` and the example composer as a starting point; use code for cutting, sizing, orientation and masking, not inventing replacement illustrations.
4. Export/register with `<python> scripts/wrap.py export --model <id> --source <flat-atlas.png> --name <Design_v1.png> --base <hex> --id <design-id> --title <title>`. This sizes/masks/quantizes and validates; it does NOT infer semantic fit or rotate graphics intelligently. Choose a new version filename/id for iterations. Existing files require explicit `--replace`.
5. Open `?model=<id>&wrap=<design-id>` in the local viewer. Inspect front, rear, both sides and top. Save real viewer screenshots using its camera presets and Save view or the available browser tooling. Read `references/visual-review.md` for the specific failure modes. Prefer `npm run review -- --model <id> --wrap <design-id> --out artifacts/<design>/<model>/review-v1` for five-angle evidence and hashes; see PIPELINE.md for browser setup. Verify `window.studioState.ready` and the intended model and export; UI rendering is not in-car proof.
6. Feed the generated artwork, actual viewer screenshots and exact template back to imagegen with precise corrections (panel location, scale, orientation, seam margins). Do at least one screenshot-guided correction pass for a new design unless the user explicitly wants a first draft only or inspection establishes that no meaningful correction is needed. Re-fit and inspect the corrected PNG. Stop after three imagegen correction passes and report remaining issues rather than claiming perfect fit or spending indefinitely.
7. Run `<python> scripts/wrap.py validate-catalog` and validate the selected PNG. When using the capture command, run `<python> scripts/wrap.py validate-review <capture.json>` to reject stale screenshots. Save the prompt, filenames, template/model id, screenshots, what changed and remaining limitations in a review note. Report the local viewer link, PNG path, dimensions/bytes, and concise Tesla install instructions from `references/tesla-install.md`.

The viewer is matte by default, but PNGs cannot control Tesla's roughness, lighting or materials. Wraps cannot add geometry, change the silhouette, replace glass, or recolour wheels. Keep screenshot/concept claims separate from the actual atlas and in-car appearance. Do not mark a design in-car verified without user evidence.

## Scope and handoff

Keep requested changes inside the chosen checkout and its artifacts. Installation of this skill or creation of a wrap is not authorization to publish a repository, submit a gallery design, format a USB drive or modify a vehicle. Give installation instructions by default; perform a user-requested file copy only to a verified destination. Third-party vehicle meshes/templates are setup downloads with separate provenance; the repository's code licence does not grant rights to redistribute those assets.
