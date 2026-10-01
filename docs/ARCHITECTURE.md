# Architecture

`src/viewer.js` owns Three.js resources, model replacement, camera framing and the wrap material. It binds the texture to glTF TEXCOORD_1 (Three.js channel 1) on Paint/Paint2 materials only. Other materials retain their own textures; rough/fade paint is approximated dark. Glass, lights and wheels remain geometry/material data from the downloaded model. The renderer is intentionally approximate and matte.

`src/main.js` owns model/design selection, the local PNG picker, UI state and downloads. Asynchronous model/texture changes use sequence guards so stale fetches cannot replace a newer choice. Changing models invalidates the old downloadable blob and only lists catalogue entries for the selected template. A custom upload is explicitly model-unverified; bytes are preserved on download. `src/files.js` validates PNG signatures, dimensions and bytes and sanitizes download filenames.

`public/models.json` enumerates the five official Model Y template families and the available mesh files. The placement boxes are conservative artist-defined regions for example decals, not CAD-derived universal surface boundaries. Template source URLs and hashes are in `asset-manifest.json`. `npm run setup:assets` verifies existing files or fetches matching bytes; a changed upstream hash stops setup rather than silently substituting geometry.

`public/catalog.json` binds design ids to model-specific PNGs. Every export has a JSON sidecar with exact model, source/template/output hashes and separate visual/in-car statuses. The generic export command resizes a source atlas to 1024px, cuts it to the model mask, leaves base-colour gutter padding, quantizes to 256 colours and validates. It does not infer panel identities, retarget an arbitrary source atlas between bodies or prove seams align.

The Hogwarts house examples use generated emblem tiles, composed independently into each model's measured hood/door boxes. Hogwarts Express retains the richer original-body atlas; the four newer-body editions use the owl artwork in separately fitted simpler layouts. They are not claimed to be identical full-body designs. Earlier F1/Alpine studies remain original-body-only.

`window.studioState` is a read-only-by-convention diagnostic snapshot for browser verification: model, wrap, wrapMeshes, width, bytes and uvChannel. Read it after model/texture loads; use rendered screenshots as visual evidence. Model selection can be deep-linked with `?model=modely-l&wrap=ravenclaw`.
