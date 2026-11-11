"""Run the hand-labelled cases against a running API."""
import json
import sys
from pathlib import Path
import httpx

cases = json.loads((Path(__file__).parent / 'cases.json').read_text())
base = sys.argv[1] if len(sys.argv) > 1 else 'http://127.0.0.1:8000'
passed = 0
for number, case in enumerate(cases, 1):
    try:
        response = httpx.post(base + '/triage', json={'message': case['message']}, timeout=120)
        response.raise_for_status()
        actual = response.json()['category']
        ok = actual == case['category']
        passed += int(ok)
        print(f"{number}: {'PASS' if ok else 'FAIL'} expected={case['category']} actual={actual}")
    except (httpx.HTTPError, KeyError) as exc:
        print(f'{number}: ERROR {type(exc).__name__}')
print(f'{passed}/{len(cases)} ({100*passed/len(cases):.1f}%)')
