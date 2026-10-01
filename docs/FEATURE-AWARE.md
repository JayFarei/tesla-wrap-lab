# Design around real vehicle features

Use a richer design brief when the user wants a full-body transformation. Repeating an emblem in approximate panel boxes is a decal study, not a body-aware composition. The [Ravenclaw experiment](../public/studies/ravenclaw/README.md) preserves a concrete comparison, sources, failures and refinements.

## Geometry before decoration

Confirm the exact model, load its mesh and capture neutral front/rear/left/right/top views. A temporary square solid-colour PNG uploaded through the viewer makes a neutral reference without changing geometry. Record the real handles, mirrors, seams, wheel arches, hood shape and painted rails. Glass, lights, wheels and other unpaintable surfaces are constraints. Tell imagegen which reference is geometry, which is style and which is the output template.

Use the neutral views to generate a coherent multi-view concept. Look for opportunities such as feathers following a shoulder crease, small ornament surrounding a flush handle, mirror-cap accents and lines following a painted roof rail. A concept image is not evidence that the wrap fits.

## Measure correspondence rather than guessing boxes

After `window.studioState.ready` is true, `window.studioProbe(x, y)` accepts normalized coordinates within the **canvas**, not the browser page. For a point measured in a canvas screenshot, divide its x/y by that screenshot's width/height. The viewer raycasts the actual loaded mesh and returns `{mesh, paintable, pixel}`. `pixel` is the actual second-UV position on a 1024px texture, with top-left image origin; it is null for unpaintable surfaces. Background or invalid coordinates return null.

```js
// Example browser-tool evaluation; use coordinates from your current screenshot.
const hit = window.studioProbe(0.56, 0.55);
```

Take several samples around a feature and verify them visually. A raycast establishes surface correspondence, not semantic identity: it does not know that a surface is a door handle. Camera, viewport, model and rotation must match the screenshot used to select a point. Never transplant these coordinates between model families. Retain the model id, template checksum, screen dimensions, sampled coordinates and intended feature names.

Build a labeled guide from the exact local template for imagegen, showing orientation, masks and measured feature positions. Labels belong to the guide, not the exported artwork. The two atlas side columns may face opposite directions; “left in the image” does not necessarily mean the car's left side. The narrow painted rails are not the roof glass.

## Split creative and precise work

Ask imagegen to decompose the concept onto the exact UV template. Preserve broad continuous forms and a useful amount of negative space; avoid thin high-contrast borders at every panel edge. Then export and inspect all views. Do not expect a prompt with numeric coordinates to produce pixel-perfect placement.

If the generator keeps moving a feature-sensitive motif, ask it to provide the continuous base artwork without that motif. Extract or generate the motif separately, then place those generated pixels using measured mesh anchors. Code may cut, alpha-mask, scale, rotate and place artwork; it should not silently replace detailed generated imagery with procedural icons. Keep the source layer and placement recipe so corrections are reproducible.

The Ravenclaw hybrid demonstrates this: imagegen removed the four inaccurate handle surrounds, and `scripts/compose-ravenclaw-study.py` placed an extracted generated ornament at measured positions. That improved alignment in the actual viewer. It did not automatically fix all panel seams.

## Compare mapped outputs

Use identical model, camera, light and viewport settings. Preserve the old version and compare actual exports, not an AI car rendering against a local mesh. Check broad composition, handle/mirror relationships, both side orientations, hood/hatch positioning, seam continuity and small-scale readability. Report objective quantities such as PNG dimensions, file size and measured landmark offsets separately from subjective aesthetic judgments.

A one-sample design comparison is exploratory; a candidate with extra correction passes has a different effort budget. State that instead of presenting it as a universal benchmark. Stop when remaining problems are known and the user can inspect the actual result; never turn “captures generated” into “fit approved.”

Finish with `validate-catalog`, a fresh five-angle capture and `validate-review`, plus a note about residual seams and the absence of in-car evidence. Use the exported PNG and mapped screenshots in the handoff; show source art and concepts separately.
