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
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&appid={API_KEY}"

    response = requests.get(url).json()

    return WeatherOutputSchema(
        temperature=response["main"]["temp"],
        condition=response["weather"][0]["description"],
        humidity=response["main"]["humidity"]
    )

