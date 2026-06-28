"""ResponseComposerAgent composes the final natural language response."""

from agents.base_agent import BaseAgent
from schemas.agent_contracts import (
    ActivityContext,
    LocationContext,
    SafetyContext,
    WeatherContext,
)


SYSTEM_PROMPT = """You are a friendly weather assistant writing the final response
to a user's weather question. You have been given structured data from other agents.
Write a clear, conversational, helpful response that:
- Directly answers the user's question
- Mentions current weather conditions and temperature
- Includes the safety assessment if relevant
- Gives the activity recommendation with reasoning
- Lists practical gear or preparation suggestions
- Uses a warm, helpful tone
Keep the response concise — 3 to 5 sentences or short bullet points. No JSON."""


class ResponseComposerAgent(BaseAgent):
    def run(
        self,
        user_query: str,
        location: LocationContext,
        weather: WeatherContext,
        safety: SafetyContext,
        activity: ActivityContext,
    ) -> str:
        if weather.error:
            return f"⚠️ I couldn't retrieve weather data: {weather.error}"

        gear_str = (
            ", ".join(activity.gear_suggestions)
            if activity.gear_suggestions
            else "standard gear"
        )

        user_msg = f"""
User question: {user_query}

Weather in {weather.city_display}:
- Condition: {weather.condition}
- Temperature: {weather.temp_c}°C / {weather.temp_f}°F
- Humidity: {weather.humidity}%
- Wind: {weather.wind}

Safety: {safety.risk_level} risk — {', '.join(safety.risk_reasons) if safety.risk_reasons else 'no major concerns'}
Activity recommendation: {activity.recommendation.upper()}
Best time: {activity.best_time_window or 'anytime today'}
Gear: {gear_str}
Reasoning: {activity.reasoning}
"""
        try:
            return self._call_llm(SYSTEM_PROMPT, user_msg, max_tokens=512)
        except Exception as e:
            return f"⚠️ Could not compose response: {e}"
