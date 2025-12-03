from pydantic import BaseModel, Field
from langchain_core.tools import tool
import requests
from os import getenv
from dotenv import load_dotenv

load_dotenv()

API_KEY = getenv("OPEN_WEATHER_API_KEY")

# --------- Schema Definition ----------- #
class WeatherInputSchema(BaseModel):
    city: str = Field(..., description="City name")

class WeatherOutputSchema(BaseModel):
    temperature: float = Field(..., description="Temperature")
    condition: str = Field(..., description="Weather condition")
    humidity: int = Field(..., description="Humidity")

# --------- Tool Definition ----------- #
@tool(args_schema=WeatherInputSchema)
def get_weather(city: str) -> WeatherOutputSchema:
    """Get weather information for a city."""
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&appid={API_KEY}"

    response = requests.get(url)
    if response.status_code != 200:
        return f"Error: Unable to fetch weather data. Status code: {response.status_code}, Message: {response.text}"
        
    data = response.json()
    return WeatherOutputSchema(
        temperature=data["main"]["temp"],
        condition=data["weather"][0]["description"],
        humidity=data["main"]["humidity"]
    )

