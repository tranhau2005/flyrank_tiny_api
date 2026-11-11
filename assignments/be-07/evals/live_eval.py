"""Run eight synthetic evaluation messages through the real configured provider."""
import asyncio
import json
import logging
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from app.triage import TriageInput, triage

async def main():
    logging.basicConfig(level=logging.INFO)
    logging.getLogger('httpx').setLevel(logging.WARNING)
    os.environ.setdefault('LLM_INPUT_USD_PER_MILLION', '0.075')
    os.environ.setdefault('LLM_OUTPUT_USD_PER_MILLION', '0.30')
    os.environ['LLM_ENABLED'] = 'true'
    os.environ['LLM_STUB'] = '0'
    cases = json.loads((Path(__file__).parent / 'cases.json').read_text())
    if len(sys.argv) > 1:
        index = int(sys.argv[1])
        cases = [cases[index - 1]]
    passed = 0
    completed = 0
    for i, case in enumerate(cases, 1):
        try:
            result = await triage(TriageInput(message=case['message']))
            ok = result.category == case['category']
            completed += 1
            passed += int(ok)
            print(f'{i}: {"PASS" if ok else "FAIL"} expected={case["category"]} actual={result.category}', flush=True)
        except Exception as exc:
            print(f'{i}: ERROR {type(exc).__name__} status={getattr(exc, "status_code", "unknown")}', flush=True)
    print(f'Completed {completed}/{len(cases)}; matches {passed}/{completed}' if completed else f'Completed 0/{len(cases)}; no valid score', flush=True)
    if completed != len(cases):
        raise SystemExit(1)

if __name__ == '__main__':
    asyncio.run(main())
