# BE-09: AI Decision Flow

A Next.js workflow editor using React Flow, Inngest and an OpenAI-compatible model. Add and edit decision nodes, select YES or NO for a new connection, and run the first node against a test input. Each visited node executes in its own durable Inngest step; the model must return only YES or NO. The editor supports browser-local save/load, JSON import/export and an execution log.

```sh
npm ci
# Supply LLM_API_KEY through a secret manager. Optional: LLM_BASE_URL, LLM_MODEL.
INNGEST_DEV=1 npm run dev
# In another terminal:
npx inngest-cli@latest dev -u http://localhost:3000/api/inngest
```

Open `http://localhost:3000`. The default provider is Groq's OpenAI-compatible endpoint with `openai/gpt-oss-20b`. Do not put an API key in browser code or Git. Runs are stored on local disk under `data/runs` and are not suitable for multi-instance hosting; the application is a local learning demo and has no authentication. Add auth, tenant isolation, durable shared storage and spending controls before exposing it to other users.

The production build and browser interactions (add node, edit prompt, save) were checked locally. Inngest receives run events. Real model traversal remains pending provider credentials; do not represent it as verified until an actual run completes.

Next.js's PostCSS dependency is overridden to a patched 8.5 release, and the `gcp-metadata` dependency uses a patched gaxios 7 release; the production build was checked again. As of 2026-11-11, `npm audit --omit=dev` still reports two high-severity vulnerable dependency entries, Inngest and its Zod dependency. This demo should remain local until the remaining advisories are resolved and the application is tested again.
