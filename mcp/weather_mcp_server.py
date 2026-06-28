"""MCP weather server backed by the Open-Meteo API."""

from typing import Any

import httpx
from mcp.server.fastmcp import FastMCP


mcp = FastMCP("weather-server")


def _condition_from_weathercode(code: int) -> str:
    if code == 0:
        return "Clear"
    if 1 <= code <= 3:
        return "Partly Cloudy"
    if 45 <= code <= 48:
        return "Fog"
    if 51 <= code <= 67:
        return "Rain"
    if 71 <= code <= 77:
        return "Snow"
    if 80 <= code <= 82:
        return "Showers"
    if 95 <= code <= 99:
        return "Thunderstorms"
    return "Cloudy"


@mcp.tool()
async def get_weather(city: str) -> dict[str, Any]:
    """Return current weather for a city using Open-Meteo."""
    if not city or not city.strip():
        return {"error": "City is required."}

    # Strip ", State" or ", Country" suffix if user passed "City, Region" format.
    city = city.split(",")[0].strip()

    async with httpx.AsyncClient(timeout=20.0) as client:
        geocode_response = await client.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={"name": city, "count": 1},
        )
        geocode_response.raise_for_status()
        geocode_data = geocode_response.json()

        results = geocode_data.get("results") or []
        if not results:
            return {"error": f"City not found: {city}"}

        place = results[0]
        latitude = place["latitude"]
        longitude = place["longitude"]

        forecast_response = await client.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": latitude,
                "longitude": longitude,
                "current_weather": "true",
                "hourly": "relativehumidity_2m",
                "forecast_days": 1,
            },
        )
        forecast_response.raise_for_status()
        forecast_data = forecast_response.json()

    current_weather = forecast_data.get("current_weather") or {}
    hourly = forecast_data.get("hourly") or {}
    humidity_values = hourly.get("relativehumidity_2m") or []

    temp_c = current_weather.get("temperature")
    windspeed = current_weather.get("windspeed")
    weathercode = int(current_weather.get("weathercode", -1))

    if temp_c is None or windspeed is None:
        return {"error": f"Weather data unavailable for {city}"}

    display_city = place.get("name", city)
    country = place.get("country")
    if country:
        display_city = f"{display_city}, {country}"

    return {
        "city": display_city,
        "temp_c": round(float(temp_c)),
        "temp_f": round(float(temp_c) * 9 / 5 + 32),
        "condition": _condition_from_weathercode(weathercode),
        "humidity": humidity_values[0] if humidity_values else "N/A",
        "wind": f"{windspeed} km/h",
    }


if __name__ == "__main__":
    mcp.run()
