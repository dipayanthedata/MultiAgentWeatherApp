"""WeatherDataAgent fetches real-time weather via the MCP tool layer."""

from agents.base_agent import BaseAgent
from mcp.weather_mcp_client import MCPWeatherClient
from schemas.agent_contracts import LocationContext, WeatherContext


SYSTEM_PROMPT = """You are a weather data agent. Given a location context,
decide the best city name to query for weather data.
Return ONLY a JSON object with one key: {"query_city": "<city name to query>"}
Use the most unambiguous form of the city name. Do not include state or country
unless needed to distinguish from another city with the same name.
No explanation, no markdown fences."""


class WeatherDataAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.mcp_client = MCPWeatherClient()

    def run(self, location: LocationContext) -> WeatherContext:
        if not location.city:
            return WeatherContext(
                city_display="Unknown",
                error="No city could be resolved from the query.",
            )

        try:
            data = self._call_llm_json(
                SYSTEM_PROMPT,
                f"City: {location.city}, Region: {location.region}, "
                f"Country: {location.country}",
            )
            query_city = data.get("query_city", location.city)
        except Exception:
            query_city = location.city

        result = self.mcp_client.call(query_city)

        if "error" in result:
            return WeatherContext(
                city_display=query_city,
                error=result["error"],
            )

        return WeatherContext(
            city_display=result.get("city", query_city),
            temp_c=result.get("temp_c", 0),
            temp_f=result.get("temp_f", 0),
            condition=result.get("condition", ""),
            humidity=result.get("humidity", 0),
            wind=result.get("wind", ""),
        )
