import os
from typing import Optional
from pydantic import BaseModel, Field
from langchain_core.tools import tool
from serpapi import GoogleSearch  # Use GoogleSearch from the serpapi package

class FlightsInput(BaseModel):
    departure_airport: Optional[str] = Field(description="Departure airport code (IATA)")
    arrival_airport: Optional[str] = Field(description="Arrival airport code (IATA)")
    outbound_date: Optional[str] = Field(description="Outbound date YYYY-MM-DD")
    return_date: Optional[str] = Field(description="Return date YYYY-MM-DD")
    adults: Optional[int] = Field(1, description="Number of adults")
    children: Optional[int] = Field(0, description="Number of children")
    infants_in_seat: Optional[int] = Field(0, description="Infants in seat")
    infants_on_lap: Optional[int] = Field(0, description="Infants on lap")

class FlightsInputSchema(BaseModel):
    params: FlightsInput

@tool(args_schema=FlightsInputSchema)
def flights_finder(params: FlightsInput):
    """Find flights using the Google Flights engine via SerpAPI."""
    
    query_params = {
        "api_key": os.environ.get("SERPAPI_API_KEY"),
        "engine": "google_flights",
        "hl": "en",
        "gl": "us",
        "departure_id": params.departure_airport,
        "arrival_id": params.arrival_airport,
        "outbound_date": params.outbound_date,
        "return_date": params.return_date,
        "currency": "USD",
        "adults": params.adults,
        "children": params.children,
        "infants_in_seat": params.infants_in_seat,
        "infants_on_lap": params.infants_on_lap,
    }

    print("\n🔥 DEBUG: Calling SerpAPI with params:", query_params)
    
    try:
        search = GoogleSearch(query_params)  # Create a GoogleSearch instance
        results = search.get_dict().get("best_flights", [])
        print("\n✅ DEBUG: SerpAPI Response:", results)
        return results
    except Exception as e:
        print("\n❌ DEBUG: SerpAPI Error:", str(e))
        return {"error": str(e)}
