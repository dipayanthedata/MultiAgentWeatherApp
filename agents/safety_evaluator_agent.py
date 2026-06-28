"""SafetyEvaluatorAgent evaluates weather safety for the intended activity."""

from agents.base_agent import BaseAgent
from schemas.agent_contracts import LocationContext, SafetyContext, WeatherContext


SYSTEM_PROMPT = """You are a safety evaluator for outdoor and travel activities.
Given weather conditions and an intended activity, assess the safety risk.
Return ONLY a JSON object with these keys:
{
  "risk_level": "low" | "moderate" | "high" | "extreme",
  "risk_reasons": ["reason1", "reason2"],
  "proceed_recommended": true | false
}
Risk factors include: extreme heat (>38°C), thunderstorms, heavy rain, high wind (>50 km/h),
fog, snow, ice. Consider the activity type when evaluating risk.
No explanation, no markdown fences."""


class SafetyEvaluatorAgent(BaseAgent):
    def run(self, location: LocationContext, weather: WeatherContext) -> SafetyContext:
        if weather.error:
            return SafetyContext(
                risk_level="unknown",
                risk_reasons=["Weather data unavailable"],
                proceed_recommended=False,
            )

        user_msg = f"""
Activity: {location.activity or 'general'}
City: {weather.city_display}
Temperature: {weather.temp_c}°C / {weather.temp_f}°F
Condition: {weather.condition}
Humidity: {weather.humidity}%
Wind: {weather.wind}
Date: {location.date_description or 'today'}
"""
        try:
            data = self._call_llm_json(SYSTEM_PROMPT, user_msg)
            return SafetyContext(
                risk_level=data.get("risk_level", "low"),
                risk_reasons=data.get("risk_reasons", []),
                proceed_recommended=data.get("proceed_recommended", True),
            )
        except Exception:
            return SafetyContext(
                risk_level="low",
                risk_reasons=[],
                proceed_recommended=True,
            )
