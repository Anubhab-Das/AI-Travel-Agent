# api.py

from fastapi import FastAPI
from pydantic import BaseModel
import uuid
from langchain_core.messages import HumanMessage
from agents.multi_agents import (
    TripPlannerAgent,
    DestinationResearchAgent,
    AccommodationAgent,
    TransportationAgent,
    WeatherAgent,
    ItineraryPlannerAgent,
    BudgetAnalystAgent,
    ChatbotAgent,
    ConversationMemory 
)
from dotenv import load_dotenv
from typing import Optional
from memory import GLOBAL_MEMORY  

load_dotenv()
app = FastAPI()


class TravelRequest(BaseModel):
    departure_airport: str
    arrival_airport: str
    outbound_date: str
    return_date: str
    adults: int
    children: int
    additional_info: Optional[str] = None

@app.get("/")
async def welcome():
    return {"message": "Welcome to AI Travel Agent API with Chatbot and Multi-Agents!"}

@app.post("/main-agent")
async def main_agent(req: TravelRequest):
    # Update memory with the trip data
    GLOBAL_MEMORY.update_trip_data({
        "departure_city": req.departure_airport,
        "arrival_city": req.arrival_airport,
        "outbound_date": req.outbound_date,
        "return_date": req.return_date,
        "adults": str(req.adults),
        "children": str(req.children),
    })
    if req.additional_info:
        GLOBAL_MEMORY.update_trip_data({"additional_info": req.additional_info})

    prompt = (
        f"Departure city: {req.departure_airport}, "
        f"Arrival city: {req.arrival_airport}, "
        f"Outbound: {req.outbound_date}, Return: {req.return_date}, "
        f"Adults: {req.adults}, Children: {req.children}. "
        f"Additional: {req.additional_info or ''}"
    )
    thread_id = str(uuid.uuid4())
    messages = [HumanMessage(content=prompt)]

    # For the main "get flight/hotel" logic, call TripPlannerAgent directly:
    agent = TripPlannerAgent()
    result = agent.invoke_agent(messages, thread_id)

    # Also store the assistant's reply in memory
    GLOBAL_MEMORY.add_assistant_message(result)
    return {"result": result}

class ChatRequest(BaseModel):
    query: str

@app.post("/chat")
async def chat_with_agent(req: ChatRequest):
    thread_id = str(uuid.uuid4())
    user_msg = HumanMessage(content=req.query)

    # Build the specialized agents
    agents_dict = {
        "TripPlanner": TripPlannerAgent(),
        "DestinationResearch": DestinationResearchAgent(),
        "Accommodation": AccommodationAgent(),
        "Transportation": TransportationAgent(),
        "Weather": WeatherAgent(),
        "ItineraryPlanner": ItineraryPlannerAgent(),
        "BudgetAnalyst": BudgetAnalystAgent()
    }

    # Pass the global memory to ChatbotAgent
    chatbot_agent = ChatbotAgent(agents=agents_dict, memory=GLOBAL_MEMORY)
    response = chatbot_agent.invoke_agent([user_msg], thread_id)
    return {"result": response}
