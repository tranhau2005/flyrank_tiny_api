import { mkdir, readFile, rename, writeFile } from 'node:fs/promises';
import path from 'node:path';
const directory = path.join(process.cwd(), 'data', 'runs');
export async function saveRun(id, data) {
  if (!/^[0-9a-f-]{36}$/.test(id)) throw new Error('Invalid run ID');
  await mkdir(directory, { recursive: true });
  const target = path.join(directory, `${id}.json`);
  const temporary = `${target}.${crypto.randomUUID()}.tmp`;
  await writeFile(temporary, JSON.stringify(data));
  await rename(temporary, target);
}
export async function loadRun(id) {
  if (!/^[0-9a-f-]{36}$/.test(id)) return null;
  try { return JSON.parse(await readFile(path.join(directory, `${id}.json`), 'utf8')); }
  catch (error) { if (error.code === 'ENOENT') return null; throw error; }
}
