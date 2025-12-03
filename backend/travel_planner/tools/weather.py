from pydantic import BaseModel, Field
from langchain_core.tools import tool
import requests
from os import getenv
from dotenv import load_dotenv
from functools import lru_cache
from datetime import datetime
from travel_planner.utils.decorators import retry_on_error

load_dotenv()

API_KEY = getenv("OPEN_WEATHER_API_KEY")

# --------- Schema Definition ----------- #
class WeatherInputSchema(BaseModel):
    city: str = Field(..., description="City name")

class WeatherOutputSchema(BaseModel):
    temperature: float = Field(..., description="Temperature")
    condition: str = Field(..., description="Weather condition")
    humidity: int = Field(..., description="Humidity")

# --------- Helper Function with Caching ----------- #
@retry_on_error(max_attempts=2, delay=1.0)
@lru_cache(maxsize=128)
def _fetch_weather_cached(city: str, hour_key: str):
    """
    Internal cached function to fetch weather data.
    
    WHY: Cache based on city + hour_key to get ~1 hour cache duration.
    Weather doesn't change frequently, so caching reduces API costs.
    Retry decorator handles transient API failures.
    """
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&appid={API_KEY}"
    
    try:
        # WHY: 10 second timeout prevents hanging on slow APIs
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Raises HTTPError for bad status codes
        return response.json()
        
    except requests.exceptions.HTTPError as e:
        # WHY: Provide friendly error messages, not stack traces
        if e.response.status_code == 404:
            raise ValueError(f"City '{city}' not found. Please check the spelling.")
        elif e.response.status_code == 401:
            raise ValueError("Weather API key is invalid or missing.")
        else:
            raise ValueError(f"Weather service error: {e.response.status_code}")
            
    except requests.exceptions.Timeout:
        raise ValueError(f"Weather service timeout for '{city}'. Please try again.")
        
    except requests.exceptions.RequestException as e:
        raise ValueError(f"Could not connect to weather service: {str(e)}")

# --------- Tool Definition ----------- #
@tool(args_schema=WeatherInputSchema)
def get_weather(city: str) -> WeatherOutputSchema:
    """Get weather information for a city."""
    try:
        # WHY: Hour-based cache key gives us ~1 hour cache duration
        hour_key = datetime.utcnow().strftime("%Y%m%d%H")
        data = _fetch_weather_cached(city, hour_key)
        
        return WeatherOutputSchema(
            temperature=data["main"]["temp"],
            condition=data["weather"][0]["description"],
            humidity=data["main"]["humidity"]
        )
        
    except ValueError as e:
        # WHY: Return friendly error message that LLM can communicate to user
        return str(e)
    except Exception as e:
        return f"Unexpected error getting weather: {str(e)}"

