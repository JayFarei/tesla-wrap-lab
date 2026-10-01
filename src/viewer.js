import * as THREE from "three";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";
import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";
import { DRACOLoader } from "three/addons/loaders/DRACOLoader.js";
import { RoomEnvironment } from "three/addons/environments/RoomEnvironment.js";

/** Owns scene resources and the second-UV paint contract; no gallery or file policy. */
export function createViewer(container) {
  const renderer = new THREE.WebGLRenderer({
    antialias: true,
    preserveDrawingBuffer: true,
  });
  renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.05;
  container.appendChild(renderer.domElement);
  const scene = new THREE.Scene();
  scene.background = new THREE.Color("#e9ece6");
  const pmrem = new THREE.PMREMGenerator(renderer),
    room = new RoomEnvironment(),
    env = pmrem.fromScene(room, 0.04);
  scene.environment = env.texture;
  room.dispose();
  pmrem.dispose();
  scene.add(new THREE.HemisphereLight(0xffffff, 0x6b7861, 2));
  const light = new THREE.DirectionalLight(0xffffff, 2);
  light.position.set(4, 8, 5);
  scene.add(light);
  const camera = new THREE.PerspectiveCamera(35, 1, 0.01, 1000);
  const controls = new OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;
  controls.maxPolarAngle = Math.PI * 0.49;
  controls.autoRotateSpeed = 0.7;
  const paint = new THREE.MeshStandardMaterial({
    color: 0xffffff,
    metalness: 0,
    roughness: 1,
    envMapIntensity: 0.12,
  });
  const decoder = new DRACOLoader();
  decoder.setDecoderPath("/draco/");
  const loader = new GLTFLoader();
  loader.setDRACOLoader(decoder);
  let root,
    home,
    texture,
    loadSequence = 0,
    wrapCount = 0,
    wire = false;
  function disposeModel(model) {
    const materials = new Set(),
      textures = new Set();
    model.traverse((o) => {
      if (!o.isMesh) return;
      o.geometry.dispose();
      for (const m of Array.isArray(o.material) ? o.material : [o.material])
        if (m !== paint) {
          materials.add(m);
          for (const value of Object.values(m))
            if (value?.isTexture) textures.add(value);
        }
    });
    textures.forEach((t) => t.dispose());
    materials.forEach((m) => m.dispose());
  }
  function view(name = "front") {
    if (!home) return;
    const distance = home.distance * Math.max(1, 1.1 / camera.aspect);
    const positions = {
      front: [distance, distance * 0.55, -distance],
      rear: [distance, distance * 0.55, distance],
      left: [distance * 1.4, distance * 0.35, 0],
      right: [-distance * 1.4, distance * 0.35, 0],
      top: [0.001, distance * 1.6, 0.001],
    };
    camera.position.set(...(positions[name] || positions.front));
    controls.target.copy(home.target);
    controls.update();
  }
  function resize() {
    const { width, height } = container.getBoundingClientRect();
    if (!width || !height) return;
    const old = camera.aspect;
    camera.aspect = width / height;
    camera.updateProjectionMatrix();
    renderer.setSize(width, height);
    if (home && Math.abs(old - camera.aspect) > 0.05) view();
  }
  new ResizeObserver(resize).observe(container);
  resize();
  async function loadModel(config) {
    const seq = ++loadSequence;
    const gltf = await loader.loadAsync(`/models/${config.mesh}`);
    if (seq !== loadSequence) {
      disposeModel(gltf.scene);
      return false;
    }
    if (root) {
      scene.remove(root);
      disposeModel(root);
    }
    root = gltf.scene;
    wrapCount = 0;
    root.traverse((o) => {
      if (!o.isMesh) return;
      const name = o.material.name;
      if (/^Plate(NA|EU)$/.test(name)) {
        o.visible = false;
        return;
      }
      if (["Paint", "Paint2"].includes(name) && o.geometry.attributes.uv1) {
        o.material.dispose();
        o.material = paint;
        wrapCount++;
      } else if (["PaintRough", "PaintFade"].includes(name)) {
        o.material.dispose();
        o.material = new THREE.MeshStandardMaterial({
          color: "#353d37",
          roughness: 0.9,
        });
      } else if (name === "Exterior") {
        o.material.color.multiplyScalar(0.28);
        o.material.envMapIntensity = 0.5;
      }
      o.material.wireframe = wire;
    });
    if (!wrapCount)
      throw new Error(
        `Model ${config.id} has no paint meshes with TEXCOORD_1.`,
      );
    const box = new THREE.Box3().setFromObject(root),
      size = box.getSize(new THREE.Vector3()),
      center = box.getCenter(new THREE.Vector3());
    root.position.sub(center);
    root.position.y += size.y / 2;
    scene.add(root);
    const d = Math.max(size.x, size.z);
    home = {
      distance: d * 1.05,
      target: new THREE.Vector3(0, size.y * 0.48, 0),
    };
    controls.minDistance = d * 0.6;
    controls.maxDistance = d * 6;
    camera.far = d * 30;
    camera.updateProjectionMatrix();
    view();
    return true;
  }
  function setTexture(image) {
    texture?.dispose();
    texture = new THREE.Texture(image);
    texture.flipY = false;
    texture.channel = 1;
    texture.colorSpace = THREE.SRGBColorSpace;
    texture.needsUpdate = true;
    paint.map = texture;
    paint.needsUpdate = true;
  }
  function setWireframe(value) {
    wire = value;
    root?.traverse((o) => {
      if (o.isMesh) o.material.wireframe = value;
    });
  }
  // Normalized canvas coordinates -> the mesh's actual second UV set.
  // Non-paintable surfaces are reported, never silently sampled through glass.
  function surfaceAt(x, y) {
    if (
      !root ||
      !Number.isFinite(x) ||
      !Number.isFinite(y) ||
      x < 0 ||
      x > 1 ||
      y < 0 ||
      y > 1
    )
      return null;
    const ray = new THREE.Raycaster();
    ray.setFromCamera(new THREE.Vector2(x * 2 - 1, 1 - y * 2), camera);
    const hit = ray.intersectObject(root, true).find((h) => h.object.visible);
    if (!hit) return null;
    const paintable = hit.object.material === paint;
    return {
      mesh: hit.object.name,
      paintable,
      pixel: paintable && hit.uv1 ? [hit.uv1.x * 1024, hit.uv1.y * 1024] : null,
    };
  }
  renderer.setAnimationLoop(() => {
    controls.update();
    renderer.render(scene, camera);
  });
  return {
    loadModel,
    setTexture,
    view,
    setWireframe,
    surfaceAt,
    setRotate: (value) => {
      controls.autoRotate = value;
    },
    clearTexture: () => {
      texture?.dispose();
      texture = null;
      paint.map = null;
      paint.needsUpdate = true;
    },
    get wrapCount() {
      return wrapCount;
    },
    screenshot: () => renderer.domElement.toDataURL("image/png"),
  };
}
