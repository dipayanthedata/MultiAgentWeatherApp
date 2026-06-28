"""Base class for all LLM agents in the pipeline."""

import json

from databricks.sdk import WorkspaceClient


class BaseAgent:
    MODEL = "databricks-meta-llama-3-3-70b-instruct"

    def __init__(self):
        self.client = WorkspaceClient()

    def _call_llm(
        self,
        system_prompt: str,
        user_message: str,
        max_tokens: int = 512,
    ) -> str:
        """Call the Foundation Model API and return the text response."""
        response = self.client.api_client.do(
            "POST",
            f"/serving-endpoints/{self.MODEL}/invocations",
            body={
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message},
                ],
                "max_tokens": max_tokens,
            },
        )
        return response["choices"][0]["message"]["content"].strip()

    def _call_llm_json(
        self,
        system_prompt: str,
        user_message: str,
        max_tokens: int = 512,
    ) -> dict:
        """Call the LLM and parse the response as JSON."""
        raw = self._call_llm(system_prompt, user_message, max_tokens)
        clean = raw.strip()
        if clean.startswith("```"):
            clean = clean.split("```")[1]
            if clean.startswith("json"):
                clean = clean[4:]
        return json.loads(clean.strip())
