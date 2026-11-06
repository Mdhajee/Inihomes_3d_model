import React, { forwardRef, useEffect, useImperativeHandle, useRef } from 'react';
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { TransformControls } from 'three/addons/controls/TransformControls.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { GLTFExporter } from 'three/addons/exporters/GLTFExporter.js';

const ThreeViewport = forwardRef(function ThreeViewport({ onSelectionChange, onStatus }, ref) {
  const hostRef = useRef(null);
  const engineRef = useRef(null);

  useImperativeHandle(ref, () => ({
    loadFile(file) {
      const engine = engineRef.current;
      if (!engine) return;
      const url = URL.createObjectURL(file);
      const loader = new GLTFLoader();
      loader.load(url, (gltf) => {
        engine.clearModel();
        engine.modelGroup.add(gltf.scene);
        engine.currentModel = gltf.scene;
        centerModel(gltf.scene);
        URL.revokeObjectURL(url);
        onStatus?.(`Loaded ${file.name}`);
        onSelectionChange?.(null);
      }, undefined, (error) => {
        console.error(error);
        URL.revokeObjectURL(url);
        onStatus?.('Could not load this GLB/GLTF file.');
      });
    },
    setMode(mode) {
      const e = engineRef.current;
      if (!e) return;
      if (mode === '2D') {
        e.camera.position.set(0, 18, 0.001);
        e.camera.up.set(0, 0, -1);
        e.camera.lookAt(0, 0, 0);
      } else {
        e.camera.up.set(0, 1, 0);
        e.camera.position.set(10, 9, 12);
        e.camera.lookAt(0, 0, 0);
      }
      e.controls.update();
    },
    setTool(tool) {
      const e = engineRef.current;
      if (!e) return;
      e.transform.setMode(tool === 'Move' ? 'translate' : tool === 'Rotate' ? 'rotate' : 'scale');
    },
    setTransform(values) {
      const e = engineRef.current;
      const o = e?.selected;
      if (!o) return;
      if (values.position) o.position.set(...values.position);
      if (values.rotation) o.rotation.set(...values.rotation.map(v => THREE.MathUtils.degToRad(v)));
      if (values.scale) o.scale.set(...values.scale);
    },
    applyMaterial(color) {
      const e = engineRef.current;
      if (!e?.selected) return;
      const target = e.selected;
      const apply = (obj) => {
        if (!obj.isMesh) return;
        const mats = Array.isArray(obj.material) ? obj.material : [obj.material];
        obj.material = mats.map(mat => {
          const clone = mat.clone();
          if (clone.color) clone.color.set(color);
          return clone;
        });
      };
      apply(target);
      target.traverse?.(apply);
      onStatus?.('Material updated');
    },
    exportGLB() {
      const e = engineRef.current;
      if (!e) return;
      const exporter = new GLTFExporter();
      exporter.parse(e.modelGroup, (result) => {
        const blob = new Blob([result], { type: 'model/gltf-binary' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'house-design.glb';
        a.click();
        URL.revokeObjectURL(url);
        onStatus?.('GLB exported');
      }, (error) => {
        console.error(error);
        onStatus?.('Export failed');
      }, { binary: true });
    },
    resetCamera() {
      const e = engineRef.current;
      if (!e) return;
      e.camera.up.set(0, 1, 0);
      e.camera.position.set(10, 9, 12);
      e.camera.lookAt(0, 0, 0);
      e.controls.update();
    }
  }), [onSelectionChange, onStatus]);

  useEffect(() => {
    const host = hostRef.current;
    if (!host) return;

    const scene = new THREE.Scene();
    scene.background = new THREE.Color('#061b12');

    const camera = new THREE.PerspectiveCamera(45, host.clientWidth / host.clientHeight, 0.1, 1000);
    camera.position.set(10, 9, 12);

    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.setSize(host.clientWidth, host.clientHeight);
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    renderer.outputColorSpace = THREE.SRGBColorSpace;
    host.appendChild(renderer.domElement);

    const controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.target.set(0, 0, 0);

    scene.add(new THREE.HemisphereLight(0xffffff, 0x314436, 2.1));
    const sun = new THREE.DirectionalLight(0xffffff, 2.5);
    sun.position.set(8, 14, 8);
    sun.castShadow = true;
    scene.add(sun);

    const grid = new THREE.GridHelper(24, 24, 0x1e7550, 0x17452f);
    grid.position.y = -0.02;
    scene.add(grid);

    const ground = new THREE.Mesh(
      new THREE.PlaneGeometry(24, 24),
      new THREE.MeshStandardMaterial({ color: '#0a281b', roughness: 0.95 })
    );
    ground.rotation.x = -Math.PI / 2;
    ground.position.y = -0.04;
    ground.receiveShadow = true;
    scene.add(ground);

    const modelGroup = new THREE.Group();
    modelGroup.name = 'House Model';
    scene.add(modelGroup);

    const transform = new TransformControls(camera, renderer.domElement);
    transform.addEventListener('dragging-changed', (event) => { controls.enabled = !event.value; });
    transform.addEventListener('objectChange', () => {
      const o = transform.object;
      if (o) onSelectionChange?.(getObjectInfo(o));
    });
    scene.add(transform.getHelper());

    const raycaster = new THREE.Raycaster();
    const pointer = new THREE.Vector2();
    let selected = null;

    const selectFromPointer = (event) => {
      if (transform.dragging) return;
      const rect = renderer.domElement.getBoundingClientRect();
      pointer.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
      pointer.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
      raycaster.setFromCamera(pointer, camera);
      const hits = raycaster.intersectObjects(modelGroup.children, true).filter(h => h.object.isMesh);
      if (!hits.length) {
        selected = null;
        transform.detach();
        onSelectionChange?.(null);
        return;
      }
      selected = hits[0].object;
      transform.attach(selected);
      onSelectionChange?.(getObjectInfo(selected));
    };
    renderer.domElement.addEventListener('pointerdown', selectFromPointer);

    function clearModel() {
      transform.detach();
      while (modelGroup.children.length) {
        const child = modelGroup.children[0];
        modelGroup.remove(child);
        child.traverse?.(obj => {
          obj.geometry?.dispose?.();
          if (Array.isArray(obj.material)) obj.material.forEach(m => m.dispose?.());
          else obj.material?.dispose?.();
        });
      }
      selected = null;
    }

    function addDemoHouse() {
      const wallMat = new THREE.MeshStandardMaterial({ color: '#e7e0d1', roughness: 0.85 });
      const roofMat = new THREE.MeshStandardMaterial({ color: '#f5f1e8', roughness: 0.8 });
      const glassMat = new THREE.MeshStandardMaterial({ color: '#75b9d5', roughness: 0.25, metalness: 0.1 });
      const doorMat = new THREE.MeshStandardMaterial({ color: '#74442c' });
      const box = (name, size, pos, mat) => {
        const mesh = new THREE.Mesh(new THREE.BoxGeometry(...size), mat);
        mesh.name = name;
        mesh.position.set(...pos);
        mesh.castShadow = true;
        mesh.receiveShadow = true;
        modelGroup.add(mesh);
        return mesh;
      };
      // Ground-floor mass and upper-floor mass; demo geometry only.
      box('Ground Floor', [6, 2.2, 4.5], [0, 1.1, 0], wallMat);
      box('Upper Floor', [3.7, 1.8, 3.3], [0.5, 3.1, -0.2], roofMat);
      box('Front Window', [1.5, 0.9, 0.08], [-1.45, 1.25, 2.29], glassMat);
      box('Side Window', [0.08, 0.9, 1.1], [3.02, 1.25, 0.3], glassMat);
      box('Front Door', [0.85, 1.75, 0.09], [1.7, 0.88, 2.3], doorMat);
      box('Upper Window 1', [0.9, 0.7, 0.08], [-0.35, 3.05, 1.47], glassMat);
      box('Upper Window 2', [0.9, 0.7, 0.08], [1.35, 3.05, 1.47], glassMat);
    }

    function centerModel(object) {
      const box = new THREE.Box3().setFromObject(object);
      const center = box.getCenter(new THREE.Vector3());
      object.position.sub(center);
      const newBox = new THREE.Box3().setFromObject(object);
      object.position.y -= newBox.min.y;
    }

    addDemoHouse();

    const resize = () => {
      const w = host.clientWidth;
      const h = host.clientHeight;
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
      renderer.setSize(w, h);
    };
    const observer = new ResizeObserver(resize);
    observer.observe(host);

    let frame;
    const animate = () => {
      frame = requestAnimationFrame(animate);
      controls.update();
      renderer.render(scene, camera);
    };
    animate();

    engineRef.current = { scene, camera, renderer, controls, transform, modelGroup, get selected() { return selected; }, set selected(v) { selected = v; }, clearModel, currentModel: null };

    return () => {
      cancelAnimationFrame(frame);
      observer.disconnect();
      renderer.domElement.removeEventListener('pointerdown', selectFromPointer);
      controls.dispose();
      transform.dispose();
      renderer.dispose();
      if (renderer.domElement.parentNode === host) host.removeChild(renderer.domElement);
      engineRef.current = null;
    };
  }, [onSelectionChange, onStatus]);

  return <div className="viewport-canvas" ref={hostRef} />;
});

function getObjectInfo(object) {
  const r = object.rotation;
  return {
    name: object.name || 'Object',
    position: [object.position.x, object.position.y, object.position.z].map(n => +n.toFixed(2)),
    rotation: [r.x, r.y, r.z].map(n => +THREE.MathUtils.radToDeg(n).toFixed(1)),
    scale: [object.scale.x, object.scale.y, object.scale.z].map(n => +n.toFixed(2))
  };
}

function centerModel(object) {
  const box = new THREE.Box3().setFromObject(object);
  const center = box.getCenter(new THREE.Vector3());
  object.position.sub(center);
  const updated = new THREE.Box3().setFromObject(object);
  object.position.y -= updated.min.y;
}

export default ThreeViewport;
