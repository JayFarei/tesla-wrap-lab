# Inspect the mapped result

Use screenshots of the actual viewer, not a generated car concept, as evidence for the next imagegen pass. Keep both the source atlas and screenshots so the generator can relate an observed defect to its pixels.

Check the correct model id and wrap id before every capture. Capture front three-quarter, rear three-quarter, left, right and top; at least one mobile viewport checks the viewer layout. `Save view` captures the canvas. Browser screenshots can include the interface and evidence labels. For automation, use `window.studioState` to wait for both model and wrap and a positive `wrapMeshes` count; wait for two animation frames after changing camera before capture.

Look for sideways or mirrored emblems, details crossing a panel seam, paint leaking into a gutter, black edges caused by atlas misalignment, a roof-rail motif mistaken for a roof-glass graphic, duplicated lights or handles, dark grilles erased by background removal, and details too small to survive 1024px export. Check both sides: mirroring a panel can reverse text or heraldry.

Feed imagegen specific corrections: “move this emblem 15 percent inward on the left front door island,” “reduce the grille height,” “rotate these slats in the atlas so they appear horizontal on the car,” “leave a 12px quiet margin,” or “keep the tyre's black tread; only remove exterior gutters.” Avoid asking it to simply improve the whole design without naming what failed.

Do not rotate whole irregular islands just to fix a logo: that can put a wheel-arch cutout in a door. Cut the motif instead, or regenerate the island. The export helper applies a mask; it does not solve this semantic correspondence. Inspect again after every such edit.

A verified PNG signature, size and model metadata establish file compatibility only. A rendered local mesh establishes preview fit only. Neither establishes acceptance in Tesla Paint Shop. Record residual seam and lighting uncertainty plainly.
