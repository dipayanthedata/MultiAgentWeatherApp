"""ActivityAdvisorAgent converts weather and safety into practical advice."""

from agents.base_agent import BaseAgent
from schemas.agent_contracts import (
    ActivityContext,
    LocationContext,
    SafetyContext,
    WeatherContext,
)


SYSTEM_PROMPT = """You are an activity advisor. Given weather data, safety evaluation,
and the user's intended activity, provide practical recommendations.
Return ONLY a JSON object with these keys:
{
  "recommendation": "go" | "delay" | "avoid",
  "best_time_window": "<time suggestion or null>",
  "gear_suggestions": ["item1", "item2"],
  "reasoning": "<one sentence explaining the recommendation>"
}
Be specific and practical. Gear suggestions should be relevant to the activity and weather.
No explanation, no markdown fences."""


class ActivityAdvisorAgent(BaseAgent):
    def run(
        self,
        location: LocationContext,
        weather: WeatherContext,
        safety: SafetyContext,
    ) -> ActivityContext:
        if weather.error:
            return ActivityContext(
                recommendation="avoid",
                reasoning="Weather data is unavailable.",
            )

        user_msg = f"""
Activity: {location.activity or 'general'}
Date: {location.date_description or 'today'}
Weather: {weather.condition}, {weather.temp_c}°C / {weather.temp_f}°F,
         humidity {weather.humidity}%, wind {weather.wind}
Safety risk: {safety.risk_level}
Safety reasons: {', '.join(safety.risk_reasons) if safety.risk_reasons else 'none'}
Proceed recommended: {safety.proceed_recommended}
"""
        try:
            data = self._call_llm_json(SYSTEM_PROMPT, user_msg)
            return ActivityContext(
                recommendation=data.get("recommendation", "go"),
                best_time_window=data.get("best_time_window"),
                gear_suggestions=data.get("gear_suggestions", []),
                reasoning=data.get("reasoning", ""),
            )
        except Exception:
            return ActivityContext(
                recommendation="go",
                reasoning="Could not evaluate activity advice.",
            )
