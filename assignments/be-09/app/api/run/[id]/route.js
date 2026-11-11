import { loadRun } from '../../../../lib/store';
export async function GET(_request, { params }) {
  const { id } = await params;
  const run = await loadRun(id);
  return run ? Response.json(run) : Response.json({ error: 'Run not found' }, { status: 404 });
}
