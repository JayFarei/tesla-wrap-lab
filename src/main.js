import { createViewer } from "./viewer.js";
import { decodeWrap, download } from "./files.js";
const $ = (id) => document.getElementById(id);
const status = (text) => {
  $("status").textContent = text;
};
let viewer,
  models,
  catalog,
  currentModel,
  currentWrap,
  currentBlob,
  operation = 0;
const query = new URLSearchParams(location.search);
function fail(error) {
  window.studioState = { ready: false, error: error.message };
  status(error.message);
  $("status").classList.add("error");
  $("download").disabled = true;
}
function record() {
  window.studioState = {
    ready: true,
    model: currentModel.id,
    wrap: currentWrap?.id || "custom",
    wrapMeshes: viewer.wrapCount,
    width: viewerImage?.width,
    bytes: currentBlob?.size,
    uvChannel: 1,
  };
}
let viewerImage;
function fillGallery() {
  $("designs").replaceChildren();
  for (const item of catalog.filter((w) => w.models[currentModel.id])) {
    const b = document.createElement("button");
    b.className = "design";
    b.dataset.wrap = item.id;
    b.innerHTML = "<span></span><small></small>";
    b.querySelector("span").textContent = item.name;
    b.querySelector("small").textContent = item.category;
    b.style.setProperty("--swatch", item.color || "#78958b");
    b.onclick = () => selectWrap(item);
    $("designs").appendChild(b);
  }
}
async function selectWrap(item) {
  const seq = ++operation;
  window.studioState = { ready: false };
  currentBlob = null;
  $("download").disabled = true;
  status(`Loading ${item.name}…`);
  const model = currentModel;
  try {
    const res = await fetch(item.models[model.id].file);
    if (!res.ok) throw new Error(`Wrap unavailable: HTTP ${res.status}`);
    const blob = await res.blob(),
      image = await decodeWrap(blob);
    if (seq !== operation) return;
    viewer.setTexture(image);
    viewerImage = image;
    currentBlob = blob;
    currentWrap = item;
    $("designname").textContent = item.name;
    $("description").textContent = item.description;
    $("evidence").textContent = item.models[model.id].status;
    $("fileinfo").textContent =
      `${image.width} × ${image.height} · ${Math.ceil(blob.size / 1024)} KB · ${model.short}`;
    document.querySelectorAll("[data-wrap]").forEach((b) => {
      const active = b.dataset.wrap === item.id;
      b.classList.toggle("active", active);
      b.setAttribute("aria-pressed", String(active));
    });
    $("texture").src = item.models[model.id].file;
    $("download").disabled = false;
    $("status").classList.remove("error");
    status(`${model.short} · ${viewer.wrapCount} mapped paint meshes`);
    history.replaceState(null, "", `?model=${model.id}&wrap=${item.id}`);
    record();
  } catch (e) {
    if (seq === operation) fail(e);
  }
}
async function selectModel(id) {
  const seq = ++operation;
  window.studioState = { ready: false };
  currentModel = models.find((m) => m.id === id) || models[0];
  currentBlob = null;
  viewer.clearTexture();
  $("download").disabled = true;
  $("upload").disabled = true;
  $("model").value = currentModel.id;
  $("modelnote").textContent = currentModel.notes;
  $("template").href = `/templates/${currentModel.id}.png`;
  fillGallery();
  document.querySelectorAll("[data-wrap]").forEach((b) => (b.disabled = true));
  status(`Loading ${currentModel.label}…`);
  try {
    await viewer.loadModel(currentModel);
    if (seq !== operation) return;
    $("upload").disabled = false;
    document
      .querySelectorAll("[data-wrap]")
      .forEach((b) => (b.disabled = false));
    const initial =
      catalog.find(
        (w) =>
          w.id === (currentWrap?.id || query.get("wrap")) &&
          w.models[currentModel.id],
      ) || catalog.find((w) => w.models[currentModel.id]);
    if (initial) await selectWrap(initial);
    else status("Model ready. Load a PNG made for this exact model.");
  } catch (e) {
    if (seq === operation)
      fail(new Error(`${e.message} Run npm run setup:assets, then reload.`));
  }
}
$("download").onclick = () => {
  if (currentBlob)
    download(
      currentBlob,
      currentWrap?.models[currentModel.id].filename || "Custom_Wrap.png",
    );
};
$("model").onchange = (e) => selectModel(e.target.value);
$("upload").onchange = async (e) => {
  const file = e.target.files[0];
  if (!file) return;
  const seq = ++operation;
  window.studioState = { ready: false };
  currentBlob = null;
  $("download").disabled = true;
  try {
    const image = await decodeWrap(file);
    if (seq !== operation) return;
    viewer.setTexture(image);
    viewerImage = image;
    currentBlob = file;
    currentWrap = null;
    $("designname").textContent = file.name;
    $("description").textContent =
      "Your local PNG. Confirm it was created with the selected model’s template.";
    $("evidence").textContent =
      "Custom file: alignment and in-car appearance unverified.";
    $("fileinfo").textContent =
      `${image.width} × ${image.height} · ${Math.ceil(file.size / 1024)} KB`;
    $("download").disabled = false;
    $("status").classList.remove("error");
    status("Custom PNG loaded locally");
    document.querySelectorAll("[data-wrap]").forEach((b) => {
      b.classList.remove("active");
      b.setAttribute("aria-pressed", "false");
    });
    const reader = new FileReader();
    reader.onload = () => {
      if (seq === operation) $("texture").src = reader.result;
    };
    reader.readAsDataURL(file);
    history.replaceState(null, "", `?model=${currentModel.id}`);
    record();
  } catch (e) {
    if (seq === operation) fail(e);
  }
};
document
  .querySelectorAll("[data-camera]")
  .forEach((b) => (b.onclick = () => viewer?.view(b.dataset.camera)));
for (const [id, fn] of [
  ["rotate", "setRotate"],
  ["wire", "setWireframe"],
])
  $(id).onclick = () => {
    const on = $(id).getAttribute("aria-pressed") !== "true";
    $(id).setAttribute("aria-pressed", String(on));
    $(id).classList.toggle("active", on);
    viewer?.[fn](on);
  };
document.querySelectorAll("[data-view]").forEach(
  (b) =>
    (b.onclick = () => {
      $("stage").className = b.dataset.view;
      document.querySelectorAll("[data-view]").forEach((x) => {
        x.classList.toggle("active", x === b);
        x.setAttribute("aria-pressed", String(x === b));
      });
    }),
);
$("capture").onclick = () => {
  if (!viewer) return;
  const a = document.createElement("a");
  a.href = viewer.screenshot();
  a.download = `${currentModel.id}-${currentWrap?.id || "custom"}-preview.png`;
  a.click();
};
async function start() {
  try {
    [models, catalog] = await Promise.all(
      ["/models.json", "/catalog.json"].map(async (url) => {
        const r = await fetch(url);
        if (!r.ok) throw new Error(`Missing ${url}`);
        return r.json();
      }),
    );
    for (const m of models) {
      const o = document.createElement("option");
      o.value = m.id;
      o.textContent = m.label;
      $("model").appendChild(o);
    }
    viewer = createViewer($("viewer"));
    window.studioCapture = () => window.studioState?.ready ? viewer.screenshot() : null;
    window.studioProbe = (x, y) =>
      window.studioState?.ready ? viewer.surfaceAt(x, y) : null;
    await selectModel(query.get("model") || models[0].id);
  } catch (e) {
    fail(e);
  }
}
start();
