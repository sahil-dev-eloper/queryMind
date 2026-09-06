import json
import time

import httpx

from app.ai.models import QueryAnalysis, SQLGenerationResult
from app.ai.prompts.query_analysis import build_query_analysis_prompt
from app.ai.prompts.sql_generation import build_sql_generation_prompt
from app.ai.provider import AIProvider, AIProviderError
from app.core.config import settings


class OpenAIProvider(AIProvider):
    endpoint = "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions"

    async def _complete(self, prompt: str) -> dict:
        import asyncio
        import logging
        log = logging.getLogger(__name__)
        started = time.perf_counter()
        max_retries = 5
        try:
            async with httpx.AsyncClient(timeout=120) as client:
                for attempt in range(max_retries + 1):
                    response = await client.post(self.endpoint, headers={"Authorization": f"Bearer {settings.ai_api_key}"}, json={"model": settings.ai_model, "temperature": 0, "response_format": {"type": "json_object"}, "messages": [{"role": "user", "content": prompt}]})
                    if response.status_code in (429, 503) and attempt < max_retries:
                        wait = min(5 * (2 ** attempt), 60)
                        log.warning("AI API returned %s, retrying in %ss (attempt %s/%s)", response.status_code, wait, attempt + 1, max_retries)
                        await asyncio.sleep(wait)
                        continue
                    if response.status_code != 200:
                        log.error("AI API error %s: %s", response.status_code, response.text[:500])
                    response.raise_for_status()
                    break
                content = response.json()["choices"][0]["message"]["content"]
                return {"payload": json.loads(content), "latency_ms": int((time.perf_counter() - started) * 1000)}
        except (httpx.HTTPError, KeyError, ValueError, json.JSONDecodeError) as exc:
            raise AIProviderError("The AI provider returned an invalid response.") from exc

    async def analyze_query(self, query: str, schema: dict, dialect: str) -> QueryAnalysis:
        result = await self._complete(build_query_analysis_prompt(query, schema, dialect))
        return QueryAnalysis.model_validate(result["payload"])

    async def generate_sql(self, query: str, analysis: QueryAnalysis, schema: dict, dialect: str) -> SQLGenerationResult:
        result = await self._complete(build_sql_generation_prompt(query, analysis.model_dump(), schema, dialect))
        return SQLGenerationResult.model_validate(result["payload"])
