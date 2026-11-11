export function validateGraph(graph) {
  if (!graph || !Array.isArray(graph.nodes) || !Array.isArray(graph.edges) || graph.nodes.length < 1 || graph.nodes.length > 30 || graph.edges.length > 60) throw new Error('Use 1–30 nodes and at most 60 edges');
  const ids = new Set();
  for (const n of graph.nodes) {
    if (typeof n.id !== 'string' || n.id.length > 100 || ids.has(n.id) || typeof n.data?.label !== 'string' || !n.data.label.trim() || n.data.label.length > 1000) throw new Error('Every node needs a unique ID and a prompt');
    ids.add(n.id);
  }
  const branches = new Set();
  for (const e of graph.edges) {
    if (!ids.has(e.source) || !ids.has(e.target) || !['YES','NO'].includes(e.label)) throw new Error('Each connection needs a valid source, target and YES or NO label');
    const key = `${e.source}:${e.label}`;
    if (branches.has(key)) throw new Error('A node may have only one edge for each answer');
    branches.add(key);
  }
  return graph;
}
