import { readFile, mkdir, writeFile, copyFile } from "node:fs/promises";
import { createHash } from "node:crypto";
import path from "node:path";
import { fileURLToPath } from "node:url";
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const manifest = JSON.parse(
  await readFile(path.join(root, "asset-manifest.json"), "utf8"),
);
const sha = (b) => createHash("sha256").update(b).digest("hex");
for (const item of manifest.assets) {
  const dest = path.join(root, item.path);
  let current;
  try {
    current = await readFile(dest);
  } catch {}
  if (current && sha(current) === item.sha256) {
    console.log("verified", item.path);
    continue;
  }
  const res = await fetch(item.url, { signal: AbortSignal.timeout(90000) });
  if (!res.ok) throw new Error(`${item.url}: HTTP ${res.status}`);
  const body = Buffer.from(await res.arrayBuffer());
  if (sha(body) !== item.sha256)
    throw new Error(
      `Checksum changed for ${item.path}; inspect upstream before updating asset-manifest.json.`,
    );
  await mkdir(path.dirname(dest), { recursive: true });
  await writeFile(dest, body);
  console.log("downloaded", item.path);
}
const draco = path.join(root, "public/draco");
await mkdir(draco, { recursive: true });
for (const f of [
  "draco_decoder.js",
  "draco_wasm_wrapper.js",
  "draco_decoder.wasm",
])
  await copyFile(
    path.join(root, "node_modules/three/examples/jsm/libs/draco/gltf", f),
    path.join(draco, f),
  );
console.log(
  "Assets ready. Files are local-only; see THIRD_PARTY.md before redistribution.",
);
