"""LocationResolverAgent resolves location, activity, and date from a query."""

from agents.base_agent import BaseAgent
from schemas.agent_contracts import LocationContext


SYSTEM_PROMPT = """You are a location and intent resolver for a weather assistant.
Given a user query, extract:
- city: the primary city name (just the city, no state or country)
- region: state or region if mentioned (e.g. "California"), null if not
- country: country if mentioned, null if not
- activity: the activity type if mentioned (e.g. "hiking", "travel", "running", "general"), default "general"
- date_description: date reference if mentioned (e.g. "this Saturday", "today", "next week"), null if not

Return ONLY a JSON object with these exact keys. No explanation, no markdown fences.
Example: {"city": "Fremont", "region": "California", "country": null, "activity": "hiking", "date_description": "this Saturday"}
If no city is mentioned, set city to null."""


class LocationResolverAgent(BaseAgent):
    def run(self, user_query: str) -> LocationContext:
        try:
            data = self._call_llm_json(SYSTEM_PROMPT, user_query)
            return LocationContext(
                city=data.get("city") or "",
                region=data.get("region"),
                country=data.get("country"),
                activity=data.get("activity", "general"),
                date_description=data.get("date_description"),
                raw_input=user_query,
            )
        except Exception:
            return LocationContext(city="", raw_input=user_query)
