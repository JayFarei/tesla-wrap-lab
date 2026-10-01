import test from "node:test";
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { createHash } from "node:crypto";
import { safeFilename } from "../src/files.js";
const models = JSON.parse(
  await readFile(new URL("../public/models.json", import.meta.url)),
);
const catalog = JSON.parse(
  await readFile(new URL("../public/catalog.json", import.meta.url)),
);
test("all five Model Y families have separate pinned templates and meshes", async () => {
  const manifest = JSON.parse(
    await readFile(new URL("../asset-manifest.json", import.meta.url)),
  );
  assert.equal(new Set(models.map((m) => m.id)).size, 5);
  assert.equal(new Set(models.map((m) => m.mesh)).size, 5);
  for (const m of models) {
    assert.ok(
      manifest.assets.some((a) => a.path === `public/templates/${m.id}.png`),
    );
    assert.ok(
      manifest.assets.some((a) => a.path === `public/models/${m.mesh}`),
    );
  }
});
test("Hogwarts Express and four houses have valid PNGs for every model", async () => {
  for (const id of [
    "hogwarts",
    "gryffindor",
    "slytherin",
    "ravenclaw",
    "hufflepuff",
  ]) {
    const wrap = catalog.find((w) => w.id === id);
    assert.ok(wrap);
    for (const m of models) {
      const item = wrap.models[m.id];
      assert.ok(item, `${id}/${m.id}`);
      assert.ok(item.file.startsWith(`/wraps/${m.id}/`));
      const bytes = await readFile(
        new URL("../public" + item.file, import.meta.url),
      );
      assert.ok(bytes.length <= 1000000);
      assert.equal(bytes.subarray(0, 8).toString("hex"), "89504e470d0a1a0a");
      assert.equal(bytes.readUInt32BE(16), 1024);
      assert.equal(bytes.readUInt32BE(20), 1024);
      const meta = JSON.parse(
        await readFile(
          new URL(
            "../public" + item.file.replace(/\.png$/, ".json"),
            import.meta.url,
          ),
        ),
      );
      assert.equal(meta.model, m.id);
      assert.equal(
        meta.sha256,
        createHash("sha256").update(bytes).digest("hex"),
      );
      assert.equal(meta.inCarVerified, false);
    }
  }
});
test("download names cannot contain paths and obey the conservative length limit", () => {
  for (const value of ["../../my🚗wrap.png", "x".repeat(100) + ".png", ""]) {
    const name = safeFilename(value);
    assert.match(name, /^[A-Za-z0-9_ -]{1,26}\.png$/);
    assert.ok(name.length <= 30);
  }
});
