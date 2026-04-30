"""Shared LLM client for structured JSON responses."""

from __future__ import annotations

import json
from urllib import error, request

from config.settings import settings


class LLMError(RuntimeError):
    """Raised when LLM request/response handling fails."""


class LLMClient:
    def __init__(self) -> None:
        self.provider = settings.llm_provider.lower()
        self.model = settings.llm_model
        self.max_tokens = int(settings.llm_max_tokens)
        self.api_key = settings.anthropic_api_key

    def complete_json(
        self,
        *,
        task_name: str,
        system_prompt: str,
        user_prompt: str,
    ) -> dict:
        if self.provider != "anthropic":
            raise LLMError(
                f"Unsupported LLM provider '{self.provider}'. "
                "Use LLM_PROVIDER=anthropic for this runtime."
            )
        return self._anthropic_json(system_prompt=system_prompt, user_prompt=user_prompt)

    def _anthropic_json(self, *, system_prompt: str, user_prompt: str) -> dict:
        if not self.api_key or self.api_key == "sk-ant-...":
            raise LLMError("ANTHROPIC_API_KEY is missing or placeholder.")

        last_model_error: LLMError | None = None
        for candidate_model in self._candidate_models():
            try:
                return self._anthropic_json_with_model(
                    model=candidate_model,
                    system_prompt=system_prompt,
                    user_prompt=user_prompt,
                )
            except LLMError as exc:
                text = str(exc).lower()
                if "http 404" in text and "model" in text:
                    last_model_error = exc
                    continue
                raise

        if last_model_error:
            raise last_model_error
        raise LLMError("Anthropic request failed: no usable model candidate.")

    def _anthropic_json_with_model(self, *, model: str, system_prompt: str, user_prompt: str) -> dict:
        payload = {
            "model": model,
            "max_tokens": self.max_tokens,
            "temperature": 0.1,
            "system": system_prompt,
            "messages": [{"role": "user", "content": user_prompt}],
        }
        data = json.dumps(payload).encode("utf-8")
        req = request.Request(
            url="https://api.anthropic.com/v1/messages",
            method="POST",
            data=data,
            headers={
                "Content-Type": "application/json",
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
            },
        )

        try:
            with request.urlopen(req, timeout=40) as response:
                body = response.read().decode("utf-8")
        except error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            detail = self._anthropic_error_message(body) or str(exc)
            hint = self._anthropic_remediation_hint(detail, exc.code)
            raise LLMError(
                f"Anthropic request failed (HTTP {exc.code}): {detail}. What to do: {hint}"
            ) from exc
        except (error.URLError, TimeoutError) as exc:
            raise LLMError(
                "Anthropic request failed due to network/timeout. "
                "What to do: verify internet access, proxy/firewall settings, and retry."
            ) from exc

        try:
            parsed = json.loads(body)
            content = parsed.get("content", [])
            text_parts = [entry.get("text", "") for entry in content if isinstance(entry, dict)]
            text = "\n".join(part for part in text_parts if part).strip()
            return self._extract_json_object(text)
        except Exception as exc:
            raise LLMError(f"Failed to parse LLM JSON response: {exc}") from exc

    def _candidate_models(self) -> list[str]:
        candidates = [
            self.model,
            "claude-sonnet-4-6",
            "claude-opus-4-7",
            "claude-haiku-4-5-20251001",
        ]
        deduped: list[str] = []
        for model in candidates:
            if model and model not in deduped:
                deduped.append(model)
        return deduped

    @staticmethod
    def _extract_json_object(text: str) -> dict:
        text = text.strip()
        try:
            obj = json.loads(text)
            if isinstance(obj, dict):
                return obj
        except Exception:
            pass

        start = text.find("{")
        end = text.rfind("}")
        if start == -1 or end == -1 or end <= start:
            raise LLMError("LLM output did not include a valid JSON object.")
        candidate = text[start : end + 1]
        obj = json.loads(candidate)
        if not isinstance(obj, dict):
            raise LLMError("LLM output JSON was not an object.")
        return obj

    @staticmethod
    def _anthropic_error_message(body: str) -> str:
        try:
            parsed = json.loads(body)
            if isinstance(parsed, dict):
                error_obj = parsed.get("error")
                if isinstance(error_obj, dict):
                    message = error_obj.get("message")
                    if isinstance(message, str) and message.strip():
                        return message.strip()
        except Exception:
            pass
        return body.strip()

    @staticmethod
    def _anthropic_remediation_hint(detail: str, status_code: int) -> str:
        text = (detail or "").lower()
        if "credit balance is too low" in text or "plans & billing" in text:
            return "add Anthropic API credits (Plans & Billing), then rerun."
        if "invalid x-api-key" in text or "authentication" in text or status_code == 401:
            return "set a valid ANTHROPIC_API_KEY and rerun."
        if "model" in text and ("not found" in text or "access" in text):
            return (
                "set an accessible LLM_MODEL (e.g., claude-sonnet-4-6) for your account and rerun."
            )
        if status_code == 429:
            return "wait for rate limit reset or lower request rate, then retry."
        return "confirm ANTHROPIC_API_KEY/LLM_MODEL and account access, then rerun."
