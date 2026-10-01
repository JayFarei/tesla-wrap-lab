export const MAX_BYTES = 1000000;
export function safeFilename(name) {
  const stem =
    name
      .replace(/\.png$/i, "")
      .replace(/[^a-z0-9_ -]/gi, "_")
      .slice(0, 26) || "Wrap";
  return `${stem}.png`;
}
export async function decodeWrap(blob) {
  if (blob.size > MAX_BYTES) throw new Error("PNG exceeds Tesla’s 1 MB limit.");
  const head = new Uint8Array(await blob.slice(0, 8).arrayBuffer());
  if (![137, 80, 78, 71, 13, 10, 26, 10].every((v, i) => head[i] === v))
    throw new Error("Choose an actual PNG file.");
  const url = URL.createObjectURL(blob),
    img = new Image();
  try {
    img.src = url;
    await img.decode();
    if (img.width !== img.height || img.width < 512 || img.width > 1024)
      throw new Error("Use a square PNG from 512 to 1024 pixels.");
    return img;
  } finally {
    URL.revokeObjectURL(url);
  }
}
export function download(blob, filename) {
  const url = URL.createObjectURL(blob),
    a = document.createElement("a");
  a.href = url;
  a.download = safeFilename(filename);
  a.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}
