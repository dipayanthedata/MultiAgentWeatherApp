"""Weather Query Agent - Working Multi-Agent Version"""

import ast
import asyncio
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict

import gradio as gr
import nest_asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


nest_asyncio.apply()

class QueryParser:
    """Agent 1: Parse natural language queries"""
    def __init__(self):
        pass
    
    def parse(self, query: str) -> Dict:
        q = query.lower()
        city = self._extract_city(query)
        units = "celsius" if "celsius" in q or "°c" in q else "fahrenheit"
        return {"city": city, "units": units}

    def _extract_city(self, query: str) -> str | None:
        patterns = [
            r"(?:weather|temperature|temp|forecast|hot|cold|rainy|raining|snowing)\s+(?:in|at|for)\s+(.+)",
            r"(?:in|at|for)\s+([A-Za-z .'-]+)",
        ]
        for pattern in patterns:
            match = re.search(pattern, query, flags=re.IGNORECASE)
            if match:
                city = match.group(1)
                city = re.sub(r"\b(in )?(celsius|fahrenheit|degrees?|today|now|please)\b", "", city, flags=re.IGNORECASE)
                city = city.strip(" ?.!,")
                return city.title() if city else None
        return None

class DataRetriever:
    """Agent 2: Retrieve weather data"""
    async def retrieve_async(self, parsed: Dict) -> Dict:
        city = parsed["city"]
        if not city:
            return {"error": "City not found. Please include a city name in your question."}

        server_path = Path(__file__).with_name("weather_mcp_server.py")
        server_params = StdioServerParameters(
            command=sys.executable,
            args=[str(server_path)],
        )

        try:
            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    result = await session.call_tool("get_weather", {"city": city})
        except Exception as exc:
            return {"error": f"MCP weather lookup failed: {exc}"}

        data = self._parse_tool_result(result)
        if "error" not in data and data.get("city"):
            parsed["city"] = data["city"]
        return data

    def retrieve(self, parsed: Dict) -> Dict:
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self.retrieve_async(parsed))

    def _parse_tool_result(self, result) -> Dict:
        structured_content = getattr(result, "structuredContent", None)
        if structured_content is None:
            structured_content = getattr(result, "structured_content", None)
        if isinstance(structured_content, dict):
            return structured_content

        content = getattr(result, "content", None)
        if isinstance(content, list) and content:
            first = content[0]
            if isinstance(first, dict):
                return first

            text = getattr(first, "text", None)
            if isinstance(text, str):
                try:
                    return json.loads(text)
                except json.JSONDecodeError:
                    try:
                        parsed = ast.literal_eval(text)
                    except (SyntaxError, ValueError):
                        return {"error": text}
                    if isinstance(parsed, dict):
                        return parsed

        if isinstance(result, dict):
            return result

        return {"error": "Unexpected MCP tool response."}

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
    gr.Markdown("Multi-agent system for natural language weather queries. Ask about any city worldwide — powered by Open-Meteo")
    
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

demo.launch(server_name="0.0.0.0", server_port=8080)
