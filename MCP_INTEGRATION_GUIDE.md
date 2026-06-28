# MCP Weather Integration Guide

## Architecture

The app now retrieves real weather data through a local MCP server instead
of a hardcoded Python dictionary.

Request flow:

```text
QueryParser
  -> DataRetriever (MCP client)
  -> weather_mcp_server.py (MCP server)
  -> Open-Meteo API
  -> ResponseGenerator
```

`app.py` starts the MCP server as a local subprocess using MCP stdio
transport. This is intentional for Databricks Apps: both `app.py` and
`weather_mcp_server.py` run in the same container, so no separate server,
port, SSE endpoint, or HTTP transport is needed for MCP communication.

## Open-Meteo

Open-Meteo is free to use for this scenario and does not require an API key.

The MCP server uses two endpoints:

1. Geocoding:

```text
https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1
```

This converts a city name into latitude and longitude.

2. Forecast:

```text
https://api.open-meteo.com/v1/forecast
```

Parameters:

```text
latitude={latitude}
longitude={longitude}
current_weather=true
hourly=relativehumidity_2m
forecast_days=1
```

This returns current weather fields such as Celsius temperature, windspeed,
WMO weather code, and hourly relative humidity.

## MCP Tool

The MCP server is named `weather-server` and exposes one tool:

```text
get_weather(city: str)
```

The tool returns:

```python
{
    "city": "City, Country",
    "temp_c": 22,
    "temp_f": 72,
    "condition": "Partly Cloudy",
    "humidity": 65,
    "wind": "12.3 km/h",
}
```

If the city cannot be found, the tool returns:

```python
{"error": "City not found: <city>"}
```

## Weather Code Mapping

WMO weather codes are mapped to user-facing conditions:

| Code | Condition |
|---|---|
| `0` | Clear |
| `1-3` | Partly Cloudy |
| `45-48` | Fog |
| `51-67` | Rain |
| `71-77` | Snow |
| `80-82` | Showers |
| `95-99` | Thunderstorms |
| anything else | Cloudy |

## Deployment Notes

No separate deployment is required for the MCP server. Databricks Apps runs
`python app.py`, and `app.py` launches `weather_mcp_server.py` as a local
subprocess whenever the data retriever calls the MCP tool.
