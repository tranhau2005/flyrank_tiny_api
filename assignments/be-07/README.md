# BE-07: Structured AI triage

This extends the SQLite task API with `POST /triage`, a single classification of support text. See `JOB-CARD.md` and `prompts/triage-v1.md`. Results are validated against closed enums and confidence bounds; malformed output is sent for one repair and then rejected without returning raw model text. The client uses a 30-second timeout and bounded retries on timeouts, 429 and server errors. Logs include model, prompt version, duration, usage and repair count, never the message or API key.

```sh
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
# Supply LLM_API_KEY using your secret manager; optionally set LLM_BASE_URL and LLM_MODEL.
uvicorn app.main:app --port 8000
curl -s http://localhost:8000/triage -H 'Content-Type: application/json' -d '{"message":"I was charged twice"}'
```

`LLM_ENABLED=false` returns a deterministic low-confidence fallback without a provider call. `LLM_STUB=1` is a clearly identified development mode. Set `LLM_INPUT_USD_PER_MILLION` and `LLM_OUTPUT_USD_PER_MILLION` to provider rates to log an estimated cost; otherwise the cost is unknown, not zero. The endpoint's validation and fallback have been tested locally. A live model evaluation of the eight hand-labelled cases, actual cost and real output remain pending API credentials.

The client uses its own retry policy (up to three attempts per model call); 429 `Retry-After` is honored. Run `python evals/run.py` against a running server to measure the eight labelled examples. Failed model outputs and input are stored locally in `logs/quarantine.jsonl` for inspection; the directory is ignored by Git and should be handled as sensitive data. Do not run this on private messages without an appropriate retention policy.

## Live evaluation, 2026-11-09

With `triage-v1` and Groq `openai/gpt-oss-20b`, seven of the first eight cases returned valid answers and all seven matched their expected category. The eighth case, a prompt-injection example, received HTTP 400 from the provider on a separate diagnostic retry. That counts as a failed request: 7/8 produced a correct classification, and the remaining case produced no model answer. One observed successful call used 317 input and 108 output tokens; at the then-published illustrative rates of $0.075 and $0.30 per million tokens respectively, the estimate is $0.000056175, or about $0.56 for 10,000 similar calls. Actual billing depends on the provider and plan. A previous attempt using `llama-3.3-70b-versatile` returned 404 and produced no valid score.
