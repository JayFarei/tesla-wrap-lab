# Asset provenance and licence boundaries

## Code

Project-authored viewer, scripts, documentation and skill instructions are MIT-licensed. Three.js is an npm dependency with its own MIT licence; its Draco decoder includes upstream notices. Dependencies are installed rather than vendored into Git.

## Vehicle meshes and templates

The five GLBs come from `https://teslawrapgallery.com/tesla_3d_models/v2/`. They are render meshes, not engineering CAD. Public download availability is not a redistribution licence. Redistribution rights are unverified, so GLBs are excluded from Git and release ZIPs; the setup command fetches them locally. The model registry describes meshes and template families, not a guarantee of exact trim/year/wheel fidelity.

Templates come from Tesla's `teslamotors/custom-wraps` repository at commit `86c7d31454caf0f20af6f6af105f577643f13bce`. They are also fetched during setup, not relicensed under this repository's MIT licence. `asset-manifest.json` records URLs and SHA-256 digests. No source or asset is fetched by executing third-party page scripts.

The unrelated `core-hacked/tesla-custom-wraps-gallery` repository was inspected during prototyping but is neither a dependency nor included here. Its licence is not used to claim rights over the live visualizer's models.

A local Vite production build copies downloaded public assets into `dist`. That directory is ignored and not a public release artifact. Review asset rights separately before hosting a complete viewer publicly.

## Generated example artwork

The included example illustrations and wrap textures were generated with imagegen and fitted by project scripts. They are demonstration fan artwork inspired by fictional houses, a magical train, and earlier vehicle designs. They are excluded from the software licence. You may use and adapt the project's own contributions to these examples for personal experimentation; this does not grant rights to third-party characters, marks or designs or establish commercial clearance. No affiliation or endorsement is implied.

Generated illustrations are not evidence of physical vehicle changes or in-car acceptance. Some examples reproduce brand-like motifs; users should choose original themes for uses requiring clear third-party rights.

## User reference files

Original user-supplied photographs, old generated scratch files, local review logs and unrelated reference checkouts remain outside the release file list. Public screenshots show only this viewer and its included examples.
