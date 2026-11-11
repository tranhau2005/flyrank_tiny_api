import { inngest } from '../../../lib/inngest';
import { saveRun } from '../../../lib/store';
import { validateGraph } from '../../../lib/graph';
export async function POST(request) {
  try {
    const { graph, input } = await request.json();
    validateGraph(graph);
    if (typeof input !== 'string' || !input.trim() || input.length > 4000) return Response.json({ error: 'Enter an input of 1–4,000 characters' }, { status: 400 });
    const id = crypto.randomUUID();
    await saveRun(id, { id, status: 'pending', log: [] });
    try { await inngest.send({ id, name: 'flow/requested', data: { id, graph, input } }); }
    catch { await saveRun(id, { id, status: 'failed', log: [], error: 'Could not send the event to Inngest' }); return Response.json({ error: 'Could not connect to Inngest' }, { status: 503 }); }
    return Response.json({ id }, { status: 202 });
  } catch (error) { return Response.json({ error: error.message || 'Invalid request' }, { status: 400 }); }
}
