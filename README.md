# 🌤️ Multi-Agent Weather App

A multi-agent AI app built on Databricks Apps that fetches real-time weather using the Model Context Protocol (MCP) and Open-Meteo API

## Architecture

```text
User Query
    ↓
QueryParser Agent        — extracts city name and preferred temperature unit
    ↓
DataRetriever Agent      — MCP client that calls weather_mcp_server.py
    ↓
weather_mcp_server.py    — MCP server → Open-Meteo Geocoding + Forecast APIs
    ↓
ResponseGenerator Agent  — formats the result into natural language
    ↓
Gradio UI
```

## Files

| File | Purpose | Notes |
|---|---|---|
| `app.py` | Gradio UI + agent orchestration + MCP client | Main entrypoint |
| `weather_mcp_server.py` | MCP server wrapping Open-Meteo API | Spawned as subprocess |
| `app.yaml` | Databricks Apps entrypoint config | Points to app.py |
| `requirements.txt` | Python dependencies | gradio, mcp, httpx |
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

The MCP server (`weather_mcp_server.py`) is spawned as a local subprocess by `app.py` using stdio transport. Both processes run inside the same Databricks Apps container, so no separate server deployment is needed. Do not change the transport to SSE or HTTP.

## Data Source

- Geocoding: https://geocoding-api.open-meteo.com/v1/search — converts city name to lat/lon
- Forecast: https://api.open-meteo.com/v1/forecast — returns current temperature, wind speed, weather code, and humidity

Both endpoints are free, require no API key, and have no rate limit for reasonable usage.
