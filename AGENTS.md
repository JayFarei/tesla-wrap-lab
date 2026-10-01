# Tesla Wrap Lab

Read README.md for setup, docs/PIPELINE.md for generation and docs/ARCHITECTURE.md before changing the viewer. The installable skill is skills/tesla-wrap-lab/SKILL.md.

- Every PNG belongs to an exact model id in public/models.json. Original Long Range is not Model Y L. Do not reuse one model's atlas on another body or relabel compatibility.
- Use built-in imagegen for new raster artwork. Use code for reproducible cutting, fitting, masking, quantizing and validation. Preserve generated sources and prompts; never replace detailed artwork with a crude procedural redraw without the user's instruction.
- Inspect the actual mapped model and feed real screenshots into imagegen for meaningful corrections. Keep file validation, local rendering, human/agent visual review and in-car evidence separate.
- Catalogue assets live under public/wraps/<model-id>/ and have model-bound JSON sidecars. Validate with `.venv/bin/python scripts/wrap.py validate-catalog` (Windows: .venv/Scripts/python.exe). Register new generated work with scripts/wrap.py; use versioned names rather than silently overwriting it.
- Third-party GLBs, templates and Draco files are setup downloads, excluded from Git and release archives. Do not relicense or publish them as project-owned. See THIRD_PARTY.md.
- Keep viewer runtime local-only and dependency assets local. No analytics, uploads, credentials or external calls in the page. Model downloads happen only during setup.
- Run npm test, Python exporter tests, validate:examples, npm run build and relevant browser checks for changes. Browser checks must use actual rendered WebGL, not just a green DOM. Preserve useful review screenshots in docs/screenshots or examples/reviews; do not commit tool logs or machine paths.
- Do not publish community-gallery content, write to USB, or mutate a vehicle unless explicitly requested. Install instructions are the normal handoff.
