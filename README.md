# House Designer — React + Three.js

A starter implementation of the supplied UI. It includes:
- Dark three-column design workspace.
- Three.js viewport with orbit, zoom and pan.
- Demo house so the viewport is not empty on first launch.
- GLB/GLTF upload using `GLTFLoader`.
- Click-to-select meshes and transform gizmo (move/rotate/scale).
- Position, rotation and scale fields.
- Basic material-colour application.
- GLB export using `GLTFExporter`.

## Requirements
- Node.js 20.19+ or 22.12+
- VS Code

## Run it
1. Extract this folder.
2. Open the folder in VS Code.
3. Open Terminal > New Terminal.
4. Run:

```bash
npm install
npm run dev
```

5. Open the local URL printed by Vite (normally http://localhost:5173).

## Upload a model
Click **New / Upload GLB** and select a `.glb` or `.gltf` file. The viewer uses Three.js `GLTFLoader`.

## Important current limitations
This is a front-end starter, not a complete BIM editor:
- Walls, rooms, doors, windows, stairs and furniture buttons currently select a tool mode and show a status message. They do not yet create structural geometry.
- The 2D button changes the camera to a top-down view; it is not a full 2D floor-plan editor.
- The floor selector is currently UI-only.
- Save, undo history, object visibility/locking, physically based material libraries, and photorealistic rendering are not implemented yet.
- The material picker changes the selected mesh's base colour. It does not load texture maps.
- GLB export exports the current model group.

## Suggested next milestones
1. Add a scene/object hierarchy and multi-object selection.
2. Implement wall drawing with snap/grid and numeric dimensions.
3. Add doors/windows as parametric objects and boolean/opening logic.
4. Add a real floor-plan editor and synchronize 2D/3D geometry.
5. Add texture maps, PBR material properties, environment lighting and shadows.
6. Add save/load projects through a backend.
7. Add undo/redo command history.
