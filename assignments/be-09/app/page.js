'use client';
import { useCallback, useEffect, useState } from 'react';
import { ReactFlow, Background, Controls, MiniMap, addEdge, useEdgesState, useNodesState } from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { Button } from '../components/ui/button';

const initialNodes = [
  { id:'start', position:{x:50,y:120}, data:{label:'Is this a support request?'} },
  { id:'support', position:{x:390,y:20}, data:{label:'Does this require urgent help?'} },
  { id:'sales', position:{x:390,y:250}, data:{label:'Is the sender asking about pricing?'} },
];
const initialEdges = [
  { id:'e1', source:'start', target:'support', label:'YES' },
  { id:'e2', source:'start', target:'sales', label:'NO' },
];

export default function Page() {
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);
  const [selected, setSelected] = useState('start');
  const [branch, setBranch] = useState('YES');
  const [input, setInput] = useState('I cannot log in to my account.');
  const [run, setRun] = useState(null);
  const [notice, setNotice] = useState('');
  const [busy, setBusy] = useState(false);
  const node = nodes.find(n => n.id === selected);
  const connect = useCallback(connection => setEdges(items => {
    if (items.some(e => e.source === connection.source && e.label === branch)) { setNotice(`This node already has a ${branch} branch.`); return items; }
    return addEdge({ ...connection, label: branch, animated: false }, items);
  }), [branch, setEdges]);
  useEffect(() => {
    if (!run?.id || !['pending','running'].includes(run.status)) return;
    const timer = setInterval(async () => {
      try { const response = await fetch(`/api/run/${run.id}`, { cache:'no-store' }); const next = await response.json(); if (!response.ok) throw new Error(next.error); setRun(next); }
      catch { setNotice('Could not refresh the run status.'); }
    }, 1200);
    return () => clearInterval(timer);
  }, [run?.id, run?.status]);
  function addNode() {
    const id = crypto.randomUUID();
    setNodes(items => [...items, { id, position:{ x: 80 + (items.length % 3) * 230, y: 80 + (items.length % 4) * 100 }, data:{ label:'Write a yes/no question' } }]);
    setSelected(id);
  }
  function save() { localStorage.setItem('decision-flow', JSON.stringify({nodes,edges})); setNotice('Workflow saved in this browser.'); }
  function load() {
    try { const value = JSON.parse(localStorage.getItem('decision-flow')); if (!value?.nodes || !value?.edges) throw new Error(); setNodes(value.nodes); setEdges(value.edges); setSelected(value.nodes[0]?.id); setNotice('Saved workflow loaded.'); }
    catch { setNotice('No valid saved workflow was found.'); }
  }
  function exportJson() {
    const blob = new Blob([JSON.stringify({nodes,edges},null,2)], {type:'application/json'});
    const url = URL.createObjectURL(blob); const link = document.createElement('a'); link.href=url; link.download='decision-flow.json'; link.click(); URL.revokeObjectURL(url);
  }
  function importJson(event) {
    const file=event.target.files?.[0]; if (!file) return;
    const reader=new FileReader(); reader.onload=() => { try { const value=JSON.parse(reader.result); if (!Array.isArray(value.nodes)||!Array.isArray(value.edges)) throw new Error(); setNodes(value.nodes); setEdges(value.edges); setSelected(value.nodes[0]?.id); setNotice('Workflow imported.'); } catch { setNotice('The file is not a valid workflow.'); } }; reader.readAsText(file); event.target.value='';
  }
  async function execute() {
    setBusy(true); setNotice(''); setRun(null);
    try { const response=await fetch('/api/run',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({graph:{nodes,edges},input})}); const result=await response.json(); if(!response.ok) throw new Error(result.error); setRun({id:result.id,status:'pending',log:[]}); }
    catch(error) { setNotice(error.message || 'Could not start workflow.'); }
    finally { setBusy(false); }
  }
  return <main className="shell">
    <header className="header"><div><p className="eyebrow">FLYRANK · BACKEND ENGINEERING</p><h1>Decision Flow</h1><p className="subhead">Build a path. Ask one question at a time.</p></div><div className="header-actions"><Button onClick={save}>Save</Button><Button onClick={load}>Load</Button><Button onClick={exportJson}>Export JSON</Button><label className="button button-secondary file-button">Import JSON<input type="file" accept="application/json" onChange={importJson}/></label></div></header>
    <section className="workspace" aria-label="Workflow editor">
      <div className="canvas-panel"><div className="panel-heading"><div><strong>Workflow canvas</strong><span>Connect a node to build a branch</span></div><Button onClick={addNode}>+ Add node</Button></div>
        <div className="branch-bar"><label htmlFor="branch">New connection</label><select id="branch" value={branch} onChange={e=>setBranch(e.target.value)}><option>YES</option><option>NO</option></select><span>Drag from a node’s handle to another node.</span></div>
        <div className="canvas"><ReactFlow nodes={nodes} edges={edges} onNodesChange={onNodesChange} onEdgesChange={onEdgesChange} onConnect={connect} onNodeClick={(_,n)=>setSelected(n.id)} fitView><Background gap={20} size={1}/><Controls/><MiniMap pannable zoomable/></ReactFlow></div>
      </div>
      <aside className="inspector"><div className="panel-heading"><div><strong>Inspector</strong><span>Edit the selected decision</span></div></div>
        {node ? <div className="section"><label htmlFor="prompt">Decision question</label><textarea id="prompt" value={node.data.label} onChange={e=>setNodes(items=>items.map(n=>n.id===node.id?{...n,data:{...n.data,label:e.target.value}}:n))}/><small>Phrase it so the model can answer YES or NO.</small></div> : <div className="section muted">Select a node to edit its question.</div>}
        <div className="section"><label htmlFor="input">Test input</label><textarea id="input" value={input} onChange={e=>setInput(e.target.value)} maxLength={4000}/><Button variant="primary" onClick={execute} disabled={busy || !input.trim()}>{busy?'Starting…':'Run workflow'}</Button></div>
        <div className="section"><div className="run-title"><strong>Execution</strong><span className="status">{run?.status || 'Not started'}</span></div>{run?.log?.length ? <ol className="log">{run.log.map(item=><li key={item.nodeId}><span>{item.prompt}</span><b>{item.answer}</b></li>)}</ol> : <p className="muted">Run the workflow to see the path taken.</p>}{run?.error && <p className="error" role="alert">{run.error}</p>}</div>
      </aside>
    </section>{notice && <p className="notice" role="status">{notice}</p>}
  </main>;
}
