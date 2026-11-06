import React, { useRef, useState } from 'react';
import ThreeViewport from './ThreeViewport.jsx';

const tools = [
  ['Select', '↖', 'V'], ['Walls', '▤', 'W'], ['Rooms', '▦', 'R'],
  ['Doors', '▯', 'D'], ['Windows', '▣', 'N'], ['Stairs', '⌁', 'S'],
  ['Furniture', '▱', 'F'], ['Materials', '◉', 'M']
];

export default function App() {
  const viewportRef = useRef(null);
  const fileRef = useRef(null);
  const [activeTool, setActiveTool] = useState('Select');
  const [viewMode, setViewMode] = useState('3D');
  const [selected, setSelected] = useState(null);
  const [status, setStatus] = useState('Demo house loaded · Upload a GLB to begin');
  const [floor, setFloor] = useState('Ground Floor');
  const [material, setMaterial] = useState('#ded8c9');
  const [cameraMode, setCameraMode] = useState('Perspective');
  const [showGrid, setShowGrid] = useState(true);
  const [showMeasurements, setShowMeasurements] = useState(true);

  const chooseTool = (tool) => {
    setActiveTool(tool);
    if (['Select', 'Move', 'Rotate', 'Scale'].includes(tool)) viewportRef.current?.setTool(tool);
    else setStatus(`${tool} tool selected. Structural authoring is the next feature to implement.`);
  };

  const updateNumber = (key, index, value) => {
    if (!selected) return;
    const next = { ...selected, [key]: [...selected[key]] };
    next[key][index] = Number(value);
    setSelected(next);
    viewportRef.current?.setTransform({ [key]: next[key] });
  };

  const upload = (event) => {
    const file = event.target.files?.[0];
    if (file) viewportRef.current?.loadFile(file);
    event.target.value = '';
  };

  return (
    <div className="app-shell">
      <header className="topbar">
        <div className="brand">
          <div className="brand-icon">⬡</div>
          <div><strong>House Designer</strong><small>Untitled design</small></div>
        </div>
        <div className="top-actions">
          <button onClick={() => fileRef.current?.click()}>＋ <span>New / Upload GLB</span></button>
          <input ref={fileRef} type="file" accept=".glb,.gltf,model/gltf-binary,model/gltf+json" hidden onChange={upload} />
          <button onClick={() => setStatus('Project save is not connected yet.')}>▣ <span>Save</span></button>
          <i />
          <button onClick={() => viewportRef.current?.resetCamera()}>↶ <span>Undo view</span></button>
          <button onClick={() => viewportRef.current?.resetCamera()}>↷ <span>Redo view</span></button>
          <i />
          <div className="segmented">
            <button className={viewMode === '2D' ? 'chosen' : ''} onClick={() => { setViewMode('2D'); viewportRef.current?.setMode('2D'); }}>2D</button>
            <button className={viewMode === '3D' ? 'chosen' : ''} onClick={() => { setViewMode('3D'); viewportRef.current?.setMode('3D'); }}>3D</button>
          </div>
          <select className="floor-select" value={floor} onChange={e => setFloor(e.target.value)}>
            <option>Ground Floor</option><option>First Floor</option><option>Second Floor</option>
          </select>
        </div>
        <button className="export-btn" onClick={() => viewportRef.current?.exportGLB()}>↓ <span>Export GLB</span></button>
      </header>

      <main className="workspace">
        <aside className="left-panel panel">
          <h3>Design tools</h3>
          <p>Pick a tool, then click in the viewport.</p>
          <div className="tool-list">
            {tools.map(([name, icon, key]) => (
              <button key={name} className={`tool-button ${activeTool === name ? 'active' : ''}`} onClick={() => chooseTool(name)}>
                <span className="tool-icon">{icon}</span><span>{name}</span><kbd>{key}</kbd>
              </button>
            ))}
          </div>
          <div className="panel-divider" />
          <h3>Transform</h3>
          {['Move', 'Rotate', 'Scale'].map(t => <button key={t} className={`mini-tool ${activeTool === t ? 'active' : ''}`} onClick={() => chooseTool(t)}>{t}</button>)}
          <div className="upload-hint"><strong>Import model</strong><span>GLB / GLTF files supported</span><button onClick={() => fileRef.current?.click()}>Choose file</button></div>
        </aside>

        <section className="center-column">
          <div className="viewport-panel panel">
            <div className="viewport-heading"><span className="live-dot" /> {floor} · {cameraMode}</div>
            <div className="viewport-title"><strong>{viewMode} Viewport</strong><small>Interactive house visualization</small></div>
            <ThreeViewport ref={viewportRef} onSelectionChange={setSelected} onStatus={setStatus} />
            <div className="axis-widget"><span>Y</span><b>╱</b><i>╲</i><small>X&nbsp;&nbsp; Z</small></div>
            <div className="viewport-help"><span>Rotate · drag</span><span>Zoom · scroll</span><span>Pan · right-drag</span><span>Select · click</span></div>
          </div>
          <div className="bottom-controls panel">
            <div className="control-row">
              <span>Camera</span>
              {['Perspective', 'Top', 'Front', 'Side'].map(mode => <button key={mode} className={cameraMode === mode ? 'selected' : ''} onClick={() => { setCameraMode(mode); if (mode === 'Top') viewportRef.current?.setMode('2D'); else if (mode === 'Perspective') viewportRef.current?.setMode('3D'); }}>{mode}</button>)}
              <span className="spacer" />
              <span>View modes</span><button className="selected">Shaded</button><button onClick={() => setStatus('Wireframe view can be added next.')}>Wireframe</button>
              <label className="switch-label">Grid <input type="checkbox" checked={showGrid} onChange={e => setShowGrid(e.target.checked)} /></label>
            </div>
            <div className="control-row second-row"><span>Measurements</span><input type="checkbox" checked={showMeasurements} onChange={e => setShowMeasurements(e.target.checked)} /></div>
            <div className="status-line">{status}</div>
          </div>
        </section>

        <aside className="right-panel panel">
          <h3>Properties</h3>
          <p>{selected ? `${selected.name} · selected` : 'Select an object in the 3D viewport'}</p>
          <section className="property-section">
            <h4>Position</h4>
            <TripleFields labels={['X', 'Y', 'Z']} values={selected?.position || [0,0,0]} disabled={!selected} onChange={(i,v) => updateNumber('position',i,v)} />
          </section>
          <section className="property-section">
            <h4>Rotation (deg)</h4>
            <TripleFields labels={['X', 'Y', 'Z']} values={selected?.rotation || [0,0,0]} disabled={!selected} onChange={(i,v) => updateNumber('rotation',i,v)} />
          </section>
          <section className="property-section">
            <h4>Scale</h4>
            <TripleFields labels={['X', 'Y', 'Z']} values={selected?.scale || [1,1,1]} disabled={!selected} onChange={(i,v) => updateNumber('scale',i,v)} />
          </section>
          <section className="property-section">
            <h4>Floor</h4>
            <select className="property-select" value={floor} onChange={e => setFloor(e.target.value)}><option>Ground Floor</option><option>First Floor</option><option>Second Floor</option></select>
          </section>
          <section className="property-section">
            <h4>Materials</h4>
            <div className="swatches">
              {['#ded8c9','#9e4d3e','#858b96','#8b572e','#77b8d4'].map(c => <button key={c} style={{background:c}} className={material === c ? 'swatch selected-swatch' : 'swatch'} onClick={() => { setMaterial(c); viewportRef.current?.applyMaterial(c); }} />)}
            </div>
            <select className="property-select" onChange={e => { setMaterial(e.target.value); viewportRef.current?.applyMaterial(e.target.value); }} value={material}>
              <option value="#ded8c9">Plaster</option><option value="#9e4d3e">Terracotta</option><option value="#858b96">Concrete</option><option value="#8b572e">Wood</option><option value="#77b8d4">Glass blue</option>
            </select>
          </section>
          <section className="property-section object-settings">
            <h4>Object settings</h4>
            <label>Name<input value={selected?.name || ''} readOnly placeholder="No object selected" /></label>
            <Toggle label="Visible" defaultChecked />
            <Toggle label="Locked" />
            <Toggle label="Cast shadow" defaultChecked />
          </section>
        </aside>
      </main>
    </div>
  );
}

function TripleFields({ labels, values, disabled, onChange }) {
  return <div className="triple-fields">{labels.map((label, i) => <label key={label}>{label}<input type="number" step="0.1" disabled={disabled} value={values[i]} onChange={e => onChange(i,e.target.value)} /></label>)}</div>;
}
function Toggle({ label, defaultChecked = false }) {
  const [checked, setChecked] = useState(defaultChecked);
  return <label className="toggle-row">{label}<input type="checkbox" checked={checked} onChange={e => setChecked(e.target.checked)} /><span className="toggle-ui" /></label>;
}
