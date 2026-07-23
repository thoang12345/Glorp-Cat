from Functions.tool import Tool
import requests

WEATHER_CODES = {
            0: "Clear sky",
            1: "Mainly clear",
            2: "Partly cloudy",
            3: "Overcast",
            45: "Fog",
        }

class WeatherTool(Tool):
    def __init__(self):
            super().__init__(
                "get_weather",
                "Returns the current weather for a specified city."
            )

    def schema(self):
        return {
            "type": "function",
            "function": {
                "name": "get_weather",
                "description": "Get the current weather for a city.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "City, town, or other location."
                        }
                    },
                    "required": ["location"]
                }
            }
        }

    def _geocode(self, location) -> dict:
        GEOCODE_URL = "https://geocoding-api.open-meteo.com/v1/search"

        # Try progressively simpler searches if necessary
        search_attempts = [
            location,
            location.replace(",", ""),
            location.split(",")[0].strip()
        ]

        for candidate in search_attempts:

            location_params = {
                "name": candidate,
                "count": 5,          # Get multiple matches for disambiguation
                "language": "en"
            }

            location_response = requests.get(
                url=GEOCODE_URL,
                params=location_params,
                timeout=5
            )

            location_response.raise_for_status()

            location_data = location_response.json()

            if "results" not in location_data or not location_data["results"]:
                continue

            # If the original query specified a state, try to match it.
            if "," in location:
                requested_state = location.split(",", 1)[1].strip().lower()

                for result in location_data["results"]:
                    if result.get("admin1", "").lower() == requested_state:
                        return {
                            "name": result["name"],
                            "country": result["country"],
                            "latitude": result["latitude"],
                            "longitude": result["longitude"],
                            "timezone": result["timezone"]
                        }

            # Otherwise just return the first result
            result = location_data["results"][0]

            return {
                "name": result["name"],
                "country": result["country"],
                "latitude": result["latitude"],
                "longitude": result["longitude"],
                "timezone": result["timezone"]
            }

        raise ValueError(f"Could not find location '{location}'.")

    def _weather(self, location):
        WEATHER_URL = "https://api.open-meteo.com/v1/forecast"
        

        weather_params = {
            "latitude": location["latitude"],
            "longitude": location["longitude"],
            "current": [
                "temperature_2m",
                "apparent_temperature",
                "wind_speed_10m",
                "weather_code"
            ]
        }

        weather_response = requests.get(WEATHER_URL, params=weather_params, timeout=5)
        weather_response.raise_for_status()
        weather_data = weather_response.json()

        if "current" not in weather_data:
            raise ValueError("Could not retrieve weather data.")

        current = weather_data["current"]
        condition = WEATHER_CODES.get(
            current["weather_code"],
            "Unknown"
        )

        return {
            "location" : location["name"],
            "country" : location["country"],
            "temperature": current["temperature_2m"],
            "feels_like": current["apparent_temperature"],
            "condition" : condition,
            "wind_speed": current["wind_speed_10m"],
            "weather_code": current["weather_code"]
        }
        

    async def execute(self, location):
            location = self._geocode(location)
            return self._weather(location)