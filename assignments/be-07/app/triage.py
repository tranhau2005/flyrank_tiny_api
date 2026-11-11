"""Structured, bounded AI support triage using an OpenAI-compatible API."""
import asyncio
import json
import logging
import os
import random
import re
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
import time
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Literal
import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, ConfigDict, Field, ValidationError

router = APIRouter(tags=["AI triage"])
log = logging.getLogger("triage")
PROMPT = Path(__file__).resolve().parent.parent / "prompts" / "triage-v1.md"


class TriageInput(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    message: str = Field(min_length=1, max_length=4000)


class TriageResult(BaseModel):
    model_config = ConfigDict(extra="forbid")
    category: Literal["billing", "bug", "feature", "other"]
    urgency: Literal["low", "medium", "high"]
    suggested_team: Literal["billing", "engineering", "product", "support"]
    confidence: float = Field(ge=0, le=1, allow_inf_nan=False)


async def model_call(messages):
    key = os.getenv("LLM_API_KEY")
    if not key:
        raise HTTPException(503, "AI provider is not configured")
    base = os.getenv("LLM_BASE_URL", "https://api.groq.com/openai/v1").rstrip("/")
    model = os.getenv("LLM_MODEL", "openai/gpt-oss-20b")
    async with httpx.AsyncClient(timeout=30) as client:
        for attempt in range(3):
            try:
                response = await client.post(base + "/chat/completions", headers={"Authorization": f"Bearer {key}"}, json={"model": model, "temperature": 0, "max_completion_tokens": 1024, "messages": messages, "response_format": {"type": "json_object"}})
                if response.status_code == 429 or response.status_code >= 500:
                    if attempt < 2:
                        delay = (2 ** attempt) + random.uniform(0, 0.2)
                        if response.status_code == 429 and response.headers.get("retry-after"):
                            value = response.headers["retry-after"]
                            try:
                                delay = max(0, float(value))
                            except ValueError:
                                try:
                                    delay = max(0, (parsedate_to_datetime(value) - datetime.now(timezone.utc)).total_seconds())
                                except (TypeError, ValueError):
                                    pass
                        if delay > 30:
                            raise HTTPException(503, "AI provider rate limit; retry later", headers={"Retry-After": str(int(delay))})
                        await asyncio.sleep(delay)
                        continue
                    raise HTTPException(503, "AI provider temporarily unavailable")
                response.raise_for_status()
                return response.json()
            except httpx.TimeoutException as exc:
                if attempt == 2:
                    raise HTTPException(504, "AI provider timed out") from exc
                await asyncio.sleep((2 ** attempt) + random.uniform(0, 0.2))
            except httpx.HTTPStatusError as exc:
                log.warning("AI provider rejected request status=%s", exc.response.status_code)
                raise HTTPException(502, "AI provider rejected the request") from exc
            except httpx.RequestError as exc:
                raise HTTPException(503, "AI provider unavailable") from exc
    raise HTTPException(503, "AI provider unavailable")


@router.post("/triage", response_model=TriageResult)
async def triage(payload: TriageInput):
    if os.getenv("LLM_ENABLED", "true").lower() == "false":
        return TriageResult(category="other", urgency="low", suggested_team="support", confidence=0.0)
    if os.getenv("LLM_STUB", "0") == "1":
        return TriageResult(category="other", urgency="low", suggested_team="support", confidence=0.1)
    messages = [{"role": "system", "content": PROMPT.read_text(encoding="utf-8")}, {"role": "user", "content": json.dumps({"message": payload.message}, ensure_ascii=False)}]
    started = time.monotonic()
    tokens_in = tokens_out = 0
    for repair in range(2):
        response = await model_call(messages)
        usage = response.get("usage") or {}
        tokens_in += usage.get("prompt_tokens", 0) or 0
        tokens_out += usage.get("completion_tokens", 0) or 0
        raw = ""
        try:
            raw = response["choices"][0]["message"]["content"]
            if not isinstance(raw, str):
                raise ValueError("Model output is not text")
            cleaned = re.sub(r"^\s*```(?:json)?\s*|\s*```\s*$", "", raw.strip(), flags=re.IGNORECASE)
            if not cleaned.startswith("{") and "{" in cleaned:
                cleaned = cleaned[cleaned.index("{"):]
            obj, _ = json.JSONDecoder().raw_decode(cleaned)
            result = TriageResult.model_validate(obj)
            try:
                in_rate = Decimal(os.environ["LLM_INPUT_USD_PER_MILLION"])
                out_rate = Decimal(os.environ["LLM_OUTPUT_USD_PER_MILLION"])
                cost = str((in_rate * tokens_in + out_rate * tokens_out) / Decimal(1_000_000))
            except (KeyError, InvalidOperation):
                cost = None
            log.info("triage prompt=triage-v1 model=%s input_tokens=%s output_tokens=%s duration_ms=%s repairs=%s estimated_usd=%s", os.getenv("LLM_MODEL", "openai/gpt-oss-20b"), tokens_in, tokens_out, round((time.monotonic()-started)*1000), repair, cost)
            return result
        except (ValidationError, ValueError, KeyError, IndexError, TypeError) as exc:
            raw_value = locals().get("raw", "")
            if not isinstance(raw_value, str):
                raw_value = ""
            if repair:
                directory = Path(__file__).resolve().parent.parent / "logs"
                directory.mkdir(exist_ok=True)
                record = {"prompt_version": "triage-v1", "input": payload.message, "output": raw_value, "error": str(exc)}
                fd = os.open(directory / "quarantine.jsonl", os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600)
                with os.fdopen(fd, "a", encoding="utf-8") as output:
                    output.write(json.dumps(record, ensure_ascii=False) + "\n")
                log.warning("triage output quarantined prompt=triage-v1 repairs=1 error_type=%s", type(exc).__name__)
                raise HTTPException(422, "Unable to produce a valid classification") from exc
            details = exc.errors(include_input=False) if isinstance(exc, ValidationError) else str(exc)
            messages.append({"role": "assistant", "content": raw_value})
            messages.append({"role": "user", "content": f"The previous answer was rejected: {details}. Return only corrected JSON matching the schema."})
    raise HTTPException(422, "Unable to produce a valid classification")
