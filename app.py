"""Weather Query Agent - Working Multi-Agent Version"""

import asyncio
import json
from pathlib import Path
import sys

import gradio as gr
import nest_asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.serving import ChatMessage, ChatMessageRole


nest_asyncio.apply()

WEATHER_TOOL = {
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "Get current weather for any city worldwide using Open-Meteo API",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "The city name to get weather for, e.g. 'San Jose' or 'Tokyo'",
                }
            },
            "required": ["city"],
        },
    },
}


class MCPWeatherClient:
    async def call_async(self, city: str) -> dict:
        server_path = Path(__file__).with_name("weather_mcp_server.py")
        server_params = StdioServerParameters(
            command=sys.executable,
            args=[str(server_path)],
        )
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool("get_weather", {"city": city})
                content = getattr(result, "content", None)
                if content and hasattr(content[0], "text"):
                    return json.loads(content[0].text)
                return {"error": "No result from MCP server"}

    def call(self, city: str) -> dict:
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self.call_async(city))


class AgentOrchestrator:
    def __init__(self):
        self.client = WorkspaceClient()
        self.mcp_client = MCPWeatherClient()
        self.model = "databricks-meta-llama-3-3-70b-instruct"
        self.system_prompt = """You are a helpful weather assistant.
You have access to a get_weather tool that fetches real-time weather data for any city worldwide.
When a user asks about weather, always use the tool to get current data before responding.
After getting the weather data, provide a friendly, conversational response that includes:
- Current conditions and temperature
- Practical advice (what to wear, whether to carry an umbrella, etc.)
- Any notable weather warnings if conditions are severe
Always use the tool — never make up weather data."""

    def ask(self, query: str) -> str:
        if not query.strip():
            return "Please enter a weather question."

        messages = [
            ChatMessage(role=ChatMessageRole.SYSTEM, content=self.system_prompt),
            ChatMessage(role=ChatMessageRole.USER, content=query),
        ]

        # Agentic loop: keep going until the LLM stops calling tools.
        for _ in range(5):
            response = self.client.serving_endpoints.query(
                name=self.model,
                messages=messages,
                tools=[WEATHER_TOOL],
                tool_choice="auto",
                max_tokens=1024,
            )

            message = response.choices[0].message

            if not message.tool_calls:
                return message.content

            messages.append(message)

            for tool_call in message.tool_calls:
                if tool_call.function.name == "get_weather":
                    args = json.loads(tool_call.function.arguments)
                    city = args.get("city", "").split(",")[0].strip()
                    weather_data = self.mcp_client.call(city)

                    messages.append(
                        ChatMessage(
                            role=ChatMessageRole.TOOL,
                            content=json.dumps(weather_data),
                            tool_call_id=tool_call.id,
                        )
                    )

        return "Sorry, I was unable to complete the weather lookup. Please try again."

# Initialize
orchestrator = AgentOrchestrator()

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

demo.launch()
