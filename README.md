# 🌤️ Multi-Agent Weather App

A multi-agent AI app built on Databricks Apps that fetches real-time weather using the Model Context Protocol (MCP) and Open-Meteo API

## Architecture

```text
User Query
    ↓
SupervisorAgent            — coordinates the pipeline
    ├── LocationResolverAgent   — extracts city, activity, date from query
    ├── WeatherDataAgent        — decides what to fetch; calls MCP tool layer
    │       ↓
    │   MCPWeatherClient → mcp/weather_mcp_server.py → Open-Meteo API
    ├── SafetyEvaluatorAgent    — assesses risk for the activity
    ├── ActivityAdvisorAgent    — produces go/delay/avoid recommendation
    └── ResponseComposerAgent   — writes the final natural language answer
    ↓
Gradio UI on Databricks Apps
```

## Files

| File | Purpose | Notes |
|---|---|---|
| `app.py` | Gradio UI only | Main entrypoint |
| `agents/` | Six-agent pipeline coordinated by `SupervisorAgent` | LLM reasoning and response composition |
| `agents/base_agent.py` | Shared Databricks Foundation Model API helper | Uses `WorkspaceClient()` |
| `schemas/` | Typed dataclass contracts between agents | Location, weather, safety, activity |
| `mcp/weather_mcp_client.py` | MCP stdio client used by `WeatherDataAgent` | Spawns local MCP server |
| `mcp/weather_mcp_server.py` | MCP server wrapping Open-Meteo API | Spawned as subprocess |
| `app.yaml` | Databricks Apps entrypoint config | Points to `app.py` |
| `requirements.txt` | Python dependencies | `gradio`, `mcp`, `httpx`, `nest_asyncio`, `databricks-sdk` |
| `MCP_INTEGRATION_GUIDE.md` | MCP architecture detail | Transport: stdio |
| `README.md` | This file | — |

## Supported Cities

Any city worldwide is supported via Open-Meteo Geocoding — not limited to a hardcoded list.

Example queries:

```text
What's the weather in Mumbai?
Temperature in Berlin in celsius
Is it raining in São Paulo?
```

## Local Setup

Step 1:

```bash
pip install -r requirements.txt
```

Step 2:

```bash
python app.py
```

Step 3: Open `http://localhost:7860` in your browser.

No API key or environment variable needed — Open-Meteo is free and open.

## Deploying to Databricks Apps

1. Upload all files to a Databricks Workspace folder or Repo
2. Go to Compute → Apps → Create App
3. Point the source to the folder containing `app.yaml`
4. Click Deploy — Databricks reads `requirements.txt` and installs dependencies automatically
5. Once status shows Running, click the assigned URL

Requires Databricks Premium plan or above with Apps enabled.

## MCP Transport

The MCP server (`mcp/weather_mcp_server.py`) is spawned as a local subprocess by `mcp/weather_mcp_client.py` using stdio transport. Both processes run inside the same Databricks Apps container, so no separate server deployment is needed. Do not change the transport to SSE or HTTP.

## Data Source

- Geocoding: https://geocoding-api.open-meteo.com/v1/search — converts city name to lat/lon
- Forecast: https://api.open-meteo.com/v1/forecast — returns current temperature, wind speed, weather code, and humidity

Both endpoints are free, require no API key, and have no rate limit for reasonable usage.
