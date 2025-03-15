# tools/weather_finder.py

import os
import requests
from langchain_core.tools import tool

OPENWEATHER_API_KEY = os.environ.get("OPENWEATHER_API_KEY")

@tool("weather_finder")
def weather_finder(city: str, date_str: str = "") -> str:
    """
    Fetch real-time weather info for 'city' from OpenWeatherMap.
    date_str can be used for short forecast logic if you want to handle near-future dates.
    If the user requests a far-future date (e.g. 2025), real data won't exist.
    """

    if not city:
        return "No city provided."

    # Basic example: current weather
    # If you want to handle near-future forecast, you can adapt the endpoint:
    #   https://api.openweathermap.org/data/2.5/forecast
    # or 16-day forecast, etc. 
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city,
        "appid": OPENWEATHER_API_KEY,
        "units": "metric"
    }

    try:
        response = requests.get(url, params=params)
        data = response.json()
        if "main" in data:
            desc = data["weather"][0]["description"]
            temp = data["main"]["temp"]
            return f"Current weather in {city}: {desc}, {temp}°C."
        else:
            return f"Could not fetch weather for {city}. Response: {data}"
    except Exception as e:
        return f"Error calling weather API: {e}"
