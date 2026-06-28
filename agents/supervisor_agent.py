"""SupervisorAgent coordinates all agents and manages the pipeline."""

from agents.activity_advisor_agent import ActivityAdvisorAgent
from agents.location_resolver_agent import LocationResolverAgent
from agents.response_composer_agent import ResponseComposerAgent
from agents.safety_evaluator_agent import SafetyEvaluatorAgent
from agents.weather_data_agent import WeatherDataAgent


class SupervisorAgent:
    """Coordinates the fixed multi-agent weather pipeline."""

    def __init__(self):
        self.location_agent = LocationResolverAgent()
        self.weather_agent = WeatherDataAgent()
        self.safety_agent = SafetyEvaluatorAgent()
        self.activity_agent = ActivityAdvisorAgent()
        self.response_agent = ResponseComposerAgent()

    def run(self, user_query: str) -> str:
        if not user_query.strip():
            return "Please enter a weather question."

        location = self.location_agent.run(user_query)
        if not location.city:
            return "⚠️ I couldn't find a city in your question. Please include a city name."

        weather = self.weather_agent.run(location)
        safety = self.safety_agent.run(location, weather)
        activity = self.activity_agent.run(location, weather, safety)

        return self.response_agent.run(
            user_query,
            location,
            weather,
            safety,
            activity,
        )
