"""Weather Query Agent - Working Multi-Agent Version"""

import re
from typing import Dict

import gradio as gr

# Weather data
WEATHER = {
    "New York": {"temp_f": 72, "temp_c": 22, "condition": "Partly Cloudy", "humidity": 65, "wind": "8 mph NW"},
    "Los Angeles": {"temp_f": 85, "temp_c": 29, "condition": "Sunny", "humidity": 45, "wind": "6 mph W"},
    "Chicago": {"temp_f": 68, "temp_c": 20, "condition": "Cloudy", "humidity": 72, "wind": "12 mph NE"},
    "Miami": {"temp_f": 88, "temp_c": 31, "condition": "Thunderstorms", "humidity": 78, "wind": "9 mph SE"},
    "Seattle": {"temp_f": 62, "temp_c": 17, "condition": "Drizzle", "humidity": 85, "wind": "10 mph S"},
    "San Francisco": {"temp_f": 65, "temp_c": 18, "condition": "Fog", "humidity": 75, "wind": "10 mph W"},
    "London": {"temp_f": 58, "temp_c": 14, "condition": "Light Rain", "humidity": 80, "wind": "16 mph SW"},
    "Tokyo": {"temp_f": 77, "temp_c": 25, "condition": "Clear", "humidity": 60, "wind": "6 mph E"}
}

class QueryParser:
    """Agent 1: Parse natural language queries"""
    def __init__(self):
        self.cities = {k.lower(): k for k in WEATHER.keys()}
        self.cities.update({"nyc": "New York", "ny": "New York", "la": "Los Angeles", "sf": "San Francisco"})
    
    def parse(self, query: str) -> Dict:
        q = query.lower()
        city = next((v for k, v in self.cities.items() if k in q), None)
        units = "celsius" if "celsius" in q or "°c" in q else "fahrenheit"
        return {"city": city, "units": units}

class DataRetriever:
    """Agent 2: Retrieve weather data"""
    def retrieve(self, parsed: Dict) -> Dict:
        city = parsed["city"]
        if not city or city not in WEATHER:
            return {"error": f"City not found. Available: {', '.join(list(WEATHER.keys())[:3])}..."}
        return WEATHER[city]

class ResponseGenerator:
    """Agent 3: Generate natural language responses"""
    def generate(self, data: Dict, parsed: Dict) -> str:
        if "error" in data:
            return f"⚠️ {data['error']}"
        
        city = parsed["city"]
        temp = data["temp_c"] if parsed["units"] == "celsius" else data["temp_f"]
        unit = "°C" if parsed["units"] == "celsius" else "°F"
        
        condition_lower = data["condition"].lower()
        if "sun" in condition_lower or "clear" in condition_lower:
            emoji = "☀️"
        elif "cloud" in condition_lower:
            emoji = "☁️"
        elif "rain" in condition_lower or "drizzle" in condition_lower:
            emoji = "🌧️"
        elif "storm" in condition_lower:
            emoji = "⛈️"
        elif "fog" in condition_lower:
            emoji = "🌫️"
        else:
            emoji = "🌡️"
        
        return f"""{emoji} **Weather in {city}**

• **Condition:** {data["condition"]}
• **Temperature:** {temp}{unit}
• **Humidity:** {data["humidity"]}%
• **Wind:** {data["wind"]}

*Multi-agent system: QueryParser → DataRetriever → ResponseGenerator*"""

class Orchestrator:
    """Coordinates all agents"""
    def __init__(self):
        self.parser = QueryParser()
        self.retriever = DataRetriever()
        self.generator = ResponseGenerator()
    
    def ask(self, query: str) -> str:
        if not query.strip():
            return "Please enter a weather question."
        parsed = self.parser.parse(query)
        data = self.retriever.retrieve(parsed)
        return self.generator.generate(data, parsed)

# Initialize
orchestrator = Orchestrator()

# Create UI using Blocks instead of ChatInterface to avoid schema bugs
with gr.Blocks(title="Weather Query Agent") as demo:
    gr.Markdown("# 🌤️ Weather Query Agent")
    gr.Markdown("Multi-agent system for natural language weather queries. Ask about: New York, LA, Chicago, Miami, Seattle, SF, London, Tokyo")
    
    with gr.Row():
        with gr.Column():
            query_input = gr.Textbox(
                label="Your Weather Question",
                placeholder="What's the weather in New York?",
                lines=2
            )
            submit_btn = gr.Button("Get Weather", variant="primary")
    
    with gr.Row():
        output = gr.Markdown(label="Response")
    
    # Examples
    gr.Examples(
        examples=[
            ["What's the weather in New York?"],
            ["How hot is it in Los Angeles?"],
            ["Temperature in Tokyo in celsius"],
            ["Is it rainy in Seattle?"]
        ],
        inputs=query_input
    )
    
    submit_btn.click(fn=orchestrator.ask, inputs=query_input, outputs=output)
    query_input.submit(fn=orchestrator.ask, inputs=query_input, outputs=output)

demo.launch(server_name="0.0.0.0", server_port=7860)
app = demo.app
