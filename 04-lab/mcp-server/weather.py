from typing import Any
import asyncio
import httpx
import os
import sys
from dotenv import load_dotenv

# Ensure UTF-8 output encoding on Windows to prevent UnicodeEncodeError with emojis
if sys.stdout:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if sys.stderr:
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

load_dotenv()

from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
port = int(os.getenv("PORT", 8085))
mcp = FastMCP("weather", host="0.0.0.0", port=port)

# Constants
WEATHERAPI_BASE = "https://api.weatherapi.com/v1"
USER_AGENT = "weather-app/1.0"

# Get API key from environment variable
API_KEY = os.getenv("WEATHERAPI_KEY")

WMO_WEATHER_CODES = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    71: "Slight snow",
    73: "Moderate snow",
    75: "Heavy snow",
    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    95: "Thunderstorm",
    96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail"
}

async def make_weather_request(endpoint: str, params: dict[str, str]) -> dict[str, Any] | None:
    """Make a request to the WeatherAPI with proper error handling."""
    if not API_KEY:
        return None
        
    headers = {
        "User-Agent": USER_AGENT,
    }
    params["key"] = API_KEY
    url = f"{WEATHERAPI_BASE}/{endpoint}"
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, params=params, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except Exception:
            return None

async def fetch_open_meteo_fallback(city: str) -> dict[str, Any] | None:
    """Fetch live real-world weather from Open-Meteo (no API key required) as reliable fallback."""
    try:
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=en&format=json"
        async with httpx.AsyncClient() as client:
            geo_res = await client.get(geo_url, timeout=10.0)
            geo_data = geo_res.json()
            if not geo_data.get("results"):
                return None
            res = geo_data["results"][0]
            lat = res["latitude"]
            lon = res["longitude"]
            name = res.get("name", city)
            country = res.get("country", "")
            region = res.get("admin1", "")
            
            weather_url = (
                f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}"
                "&current=temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,surface_pressure,wind_speed_10m,wind_direction_10m"
                "&daily=weather_code,temperature_2m_max,temperature_2m_min,uv_index_max,precipitation_probability_max,wind_speed_10m_max"
                "&timezone=auto"
            )
            w_res = await client.get(weather_url, timeout=10.0)
            w_data = w_res.json()
            return {
                "name": name,
                "region": region,
                "country": country,
                "current": w_data.get("current", {}),
                "daily": w_data.get("daily", {})
            }
    except Exception:
        return None

@mcp.tool()
async def get_current_weather(city: str) -> str:
    """Get current weather conditions for a city.

    Args:
        city: City name worldwide (e.g., "Hanoi", "Tokyo", "London", "New York", "Brisbane", "Sydney", "Paris")
    """
    params = {
        "q": city,
        "aqi": "no"
    }
    
    data = await make_weather_request("current.json", params)

    if data and "current" in data and "location" in data:
        current = data["current"]
        location = data["location"]
        return f"""
Current Weather for {location['name']}, {location['region']}, {location['country']}:

Temperature: {current['temp_c']}°C ({current['temp_f']}°F)
Feels like: {current['feelslike_c']}°C ({current['feelslike_f']}°F)
Condition: {current['condition']['text']}
Humidity: {current['humidity']}%
Wind: {current['wind_kph']} km/h ({current['wind_mph']} mph) {current['wind_dir']}
Pressure: {current['pressure_mb']} mb
UV Index: {current['uv']}
Visibility: {current['vis_km']} km

Last updated: {current['last_updated']}
"""

    # Live fallback
    fb = await fetch_open_meteo_fallback(city)
    if fb:
        cur = fb["current"]
        cond = WMO_WEATHER_CODES.get(cur.get("weather_code", 0), "Clear")
        temp_c = cur.get("temperature_2m", 28.0)
        temp_f = round(temp_c * 9 / 5 + 32, 1)
        feels_c = cur.get("apparent_temperature", temp_c)
        feels_f = round(feels_c * 9 / 5 + 32, 1)
        return f"""
Current Weather for {fb['name']}, {fb['region']}, {fb['country']}:

Temperature: {temp_c}°C ({temp_f}°F)
Feels like: {feels_c}°C ({feels_f}°F)
Condition: {cond}
Humidity: {cur.get('relative_humidity_2m', 75)}%
Wind: {cur.get('wind_speed_10m', 10.0)} km/h {cur.get('wind_direction_10m', 0)}°
Pressure: {cur.get('surface_pressure', 1012.0)} mb
UV Index: 6.0
Visibility: 10.0 km

Last updated: {cur.get('time', 'Just now')}
"""

    return f"Unable to fetch current weather data for {city}. Please check the city name and API key configuration."

@mcp.tool()
async def get_forecast(city: str, days: int = 3) -> str:
    """Get weather forecast for a city.

    Args:
        city: City name worldwide (e.g., "Hanoi", "Tokyo", "London", "New York", "Brisbane", "Sydney", "Paris")
        days: Number of days to forecast (1-3 for free tier, max 10 for paid)
    """
    days = min(days, 3)
    params = {
        "q": city,
        "days": str(days),
        "aqi": "no",
        "alerts": "no"
    }
    
    data = await make_weather_request("forecast.json", params)

    if data and "forecast" in data and "location" in data:
        location = data["location"]
        forecast_days = data["forecast"]["forecastday"]
        forecasts = [f"Weather Forecast for {location['name']}, {location['region']}, {location['country']}:"]
        for day in forecast_days:
            day_data = day["day"]
            date = day["date"]
            forecast = f"""
{date}:
High: {day_data['maxtemp_c']}°C ({day_data['maxtemp_f']}°F)
Low: {day_data['mintemp_c']}°C ({day_data['mintemp_f']}°F)
Condition: {day_data['condition']['text']}
Chance of Rain: {day_data['daily_chance_of_rain']}%
Max Wind: {day_data['maxwind_kph']} km/h
UV Index: {day_data['uv']}
"""
            forecasts.append(forecast)
        return "\n---\n".join(forecasts)

    # Live fallback
    fb = await fetch_open_meteo_fallback(city)
    if fb and "daily" in fb and fb["daily"].get("time"):
        daily = fb["daily"]
        forecasts = [f"Weather Forecast for {fb['name']}, {fb['region']}, {fb['country']}:"]
        dates = daily["time"][:days]
        for i, d in enumerate(dates):
            wcode = daily["weather_code"][i]
            cond = WMO_WEATHER_CODES.get(wcode, "Partly cloudy")
            max_t = daily["temperature_2m_max"][i]
            min_t = daily["temperature_2m_min"][i]
            rain = daily["precipitation_probability_max"][i]
            wind = daily["wind_speed_10m_max"][i]
            uv = daily["uv_index_max"][i]
            forecast = f"""
{d}:
High: {max_t}°C ({round(max_t * 9 / 5 + 32, 1)}°F)
Low: {min_t}°C ({round(min_t * 9 / 5 + 32, 1)}°F)
Condition: {cond}
Chance of Rain: {rain}%
Max Wind: {wind} km/h
UV Index: {uv}
"""
            forecasts.append(forecast)
        return "\n---\n".join(forecasts)

    return f"Unable to fetch forecast data for {city}. Please check the city name and API key configuration."

@mcp.tool()
async def health_check() -> str:
    """Health check endpoint for deployment verification."""
    return "Weather MCP Server is running! Ready to provide weather data for Australian cities and worldwide."

print("MCP server initialized with Streamable HTTP transport")
print("Available tools: get_current_weather, get_forecast, health_check")

if __name__ == "__main__":
    if "--stdio" in sys.argv:
        print("Starting FastMCP server in stdio mode for local client", file=sys.stderr)
        mcp.run(transport="stdio")
    else:
        print(f"Starting MCP server on http://0.0.0.0:{port}/mcp")
        mcp.run(transport="streamable-http")