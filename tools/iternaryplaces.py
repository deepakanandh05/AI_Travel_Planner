# geo_search_tool.py
import os
import requests
from typing import List
from pydantic import BaseModel, Field
from langchain_core.tools import tool
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GEOAPIFY_API_KEY")

BASE_URL = "https://api.geoapify.com/v2/places"


# --------------------- SCHEMAS --------------------- #
class PlaceSearchInput(BaseModel):
    place: str = Field(..., description="City or location to search places for")
    limit: int = Field(10, description="Number of results to return")


class PlaceResult(BaseModel):
    name: str
    category: str
    address: str


class PlaceSearchOutput(BaseModel):
    results: List[PlaceResult]


# ------------------ HELPER FUNCTION ------------------ #
def search_geoapify(place: str, categories: str, limit: int) -> List[PlaceResult]:
    """Internal function to call Geoapify API."""

    url = (
        f"{BASE_URL}?text={place}"
        f"&categories={categories}"
        f"&limit={limit}"
        f"&apiKey={API_KEY}"
    )

    res = requests.get(url).json()
    features = res.get("features", [])

    results = []
    for f in features:
        props = f.get("properties", {})
        results.append(
            PlaceResult(
                name=props.get("name", "Unknown"),
                category=props.get("categories", ["unknown"])[0],
                address=props.get("formatted", "No address available"),
            )
        )
    return results


# --------------------- TOOLS --------------------- #

@tool(args_schema=PlaceSearchInput)
def search_attractions(place: str, limit: int = 10) -> PlaceSearchOutput:
    """Search top attractions at a place."""
    results = search_geoapify(place, "tourism.sights", limit)
    return PlaceSearchOutput(results=results)


@tool(args_schema=PlaceSearchInput)
def search_restaurants(place: str, limit: int = 10) -> PlaceSearchOutput:
    """Search restaurants at a place."""
    results = search_geoapify(place, "catering.restaurant", limit)
    return PlaceSearchOutput(results=results)


@tool(args_schema=PlaceSearchInput)
def search_hotels(place: str, limit: int = 10) -> PlaceSearchOutput:
    """Search hotels at a place."""
    results = search_geoapify(place, "accommodation.hotel", limit)
    return PlaceSearchOutput(results=results)


@tool(args_schema=PlaceSearchInput)
def search_activities(place: str, limit: int = 10) -> PlaceSearchOutput:
    """Search activities or things to do at a place."""
    results = search_geoapify(place, "entertainment,leisure", limit)
    return PlaceSearchOutput(results=results)


