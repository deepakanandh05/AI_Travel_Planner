# geo_search_tool.py
import os
import requests
from typing import List
from pydantic import BaseModel, Field
from langchain_core.tools import tool
from dotenv import load_dotenv
from functools import lru_cache
from travel_planner.utils.decorators import retry_on_error

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


# ------------------ HELPER FUNCTIONS ------------------ #
@retry_on_error(max_attempts=2, delay=1.0)
@lru_cache(maxsize=256)
def get_coordinates(place: str):
    """
    Geocode a place name to get coordinates.
    
    WHY: Cached to avoid repeated geocoding of same location.
    Retry decorator handles transient API failures.
    """
    url = f"https://api.geoapify.com/v1/geocode/search?text={place}&apiKey={API_KEY}"
    
    try:
        # WHY: 10 second timeout prevents hanging
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        
        data = res.json()
        if data.get("features"):
            props = data["features"][0]["properties"]
            return props.get("lat"), props.get("lon")
        else:
            # WHY: Return None for invalid locations, don't retry (not transient)
            return None, None
            
    except requests.exceptions.Timeout:
        raise ValueError(f"Geocoding timeout for '{place}'. Please try again.")
        
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            raise ValueError("Places API key is invalid or missing.")
        else:
            raise ValueError(f"Geocoding service error: {e.response.status_code}")
            
    except requests.exceptions.RequestException as e:
        raise ValueError(f"Could not connect to geocoding service: {str(e)}")


@retry_on_error(max_attempts=2, delay=1.0)
def search_geoapify(place: str, categories: str, limit: int) -> List[PlaceResult]:
    """
    Internal function to call Geoapify API.
    
    WHY: Centralized API calling with error handling.
    Retry decorator handles transient failures.
    """
    try:
        lat, lon = get_coordinates(place)
        if not lat or not lon:
            # WHY: Friendly error message for invalid location
            return []

        # Search within a 20km radius (20000 meters)
        url = (
            f"{BASE_URL}?categories={categories}"
            f"&filter=circle:{lon},{lat},20000"
            f"&limit={limit}"
            f"&apiKey={API_KEY}"
        )

        # WHY: 10 second timeout prevents hanging
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        
        data = res.json()
        features = data.get("features", [])

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
        
    except ValueError:
        # WHY: Re-raise ValueError from get_coordinates (user-friendly errors)
        raise
        
    except requests.exceptions.Timeout:
        raise ValueError(f"Places search timeout for '{place}'. Please try again.")
        
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            raise ValueError("Places API key is invalid or missing.")
        else:
            raise ValueError(f"Places service error: {e.response.status_code}")
            
    except requests.exceptions.RequestException as e:
        raise ValueError(f"Could not connect to places service: {str(e)}")


# --------------------- TOOLS --------------------- #

@tool(args_schema=PlaceSearchInput)
def search_attractions(place: str, limit: int = 10) -> PlaceSearchOutput:
    """Search top attractions at a place."""
    try:
        results = search_geoapify(place, "tourism.sights", limit)
        if not results:
            return f"No attractions found for '{place}'. Please check the location name."
        return PlaceSearchOutput(results=results)
    except ValueError as e:
        return str(e)
    except Exception as e:
        return f"Unexpected error searching attractions: {str(e)}"


@tool(args_schema=PlaceSearchInput)
def search_restaurants(place: str, limit: int = 10) -> PlaceSearchOutput:
    """Search restaurants at a place."""
    try:
        results = search_geoapify(place, "catering.restaurant", limit)
        if not results:
            return f"No restaurants found for '{place}'. Please check the location name."
        return PlaceSearchOutput(results=results)
    except ValueError as e:
        return str(e)
    except Exception as e:
        return f"Unexpected error searching restaurants: {str(e)}"


@tool(args_schema=PlaceSearchInput)
def search_hotels(place: str, limit: int = 10) -> PlaceSearchOutput:
    """Search hotels at a place."""
    try:
        results = search_geoapify(place, "accommodation", limit)
        if not results:
            return f"No hotels found for '{place}'. Please check the location name."
        return PlaceSearchOutput(results=results)
    except ValueError as e:
        return str(e)
    except Exception as e:
        return f"Unexpected error searching hotels: {str(e)}"


@tool(args_schema=PlaceSearchInput)
def search_activities(place: str, limit: int = 10) -> PlaceSearchOutput:
    """Search activities or things to do at a place."""
    try:
        results = search_geoapify(place, "entertainment,leisure", limit)
        if not results:
            return f"No activities found for '{place}'. Please check the location name."
        return PlaceSearchOutput(results=results)
    except ValueError as e:
        return str(e)
    except Exception as e:
        return f"Unexpected error searching activities: {str(e)}"


