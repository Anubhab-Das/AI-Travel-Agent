import os
from typing import Optional
from pydantic import BaseModel, Field
from langchain_core.tools import tool
from serpapi import GoogleSearch  # Use GoogleSearch from the serpapi package

class HotelsInput(BaseModel):
    q: str = Field(description='City or location for the hotel search')
    check_in_date: str = Field(description='Check-in date YYYY-MM-DD')
    check_out_date: str = Field(description='Check-out date YYYY-MM-DD')
    adults: Optional[int] = Field(1, description='Number of adults. Default 1.')
    children: Optional[int] = Field(0, description='Number of children. Default 0.')
    rooms: Optional[int] = Field(1, description='Number of rooms. Default 1.')
    hotel_class: Optional[str] = Field(None, description='Filter by hotel class, e.g. 3,4,5')

class HotelsInputSchema(BaseModel):
    params: HotelsInput

@tool(args_schema=HotelsInputSchema)
def hotels_finder(params: HotelsInput):
    """Find hotels using the Google Hotels engine via SerpAPI."""

    query_params = {
        "api_key": os.environ.get("SERPAPI_API_KEY"),
        "engine": "google_hotels",
        "hl": "en",
        "gl": "us",
        "q": params.q,
        "check_in_date": params.check_in_date,
        "check_out_date": params.check_out_date,
        "currency": "USD",
        "adults": params.adults,
        "children": params.children,
        "rooms": params.rooms,
        "hotel_class": params.hotel_class
    }

    print("\n🔥 DEBUG: Calling SerpAPI with params:", query_params)
    
    try:
        search = GoogleSearch(query_params)  # Create a GoogleSearch instance
        results = search.get_dict().get("properties", [])[:5]
        print("\n✅ DEBUG: SerpAPI Response:", results)
        return results
    except Exception as e:
        print("\n❌ DEBUG: SerpAPI Error:", str(e))
        return {"error": str(e)}
