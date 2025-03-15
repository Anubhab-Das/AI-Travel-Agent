# multi_agents.py

import re
from typing import Dict, List
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from agents.base.base_agent import BaseAgent
from tools.tool_registry import tool_registry

from tools.flights_finder import flights_finder, FlightsInput
from tools.hotels_finder import hotels_finder, HotelsInput
# Import the weather_finder tool you created
from tools.weather_finder import weather_finder
from memory import GLOBAL_MEMORY  

load_dotenv()

class ConversationMemory:
    def __init__(self):
        self.history: List[str] = []
        self.known_trip_data = {}  

    def add_user_message(self, message: str):
        self.history.append(f"User: {message}")

    def add_assistant_message(self, message: str):
        self.history.append(f"Assistant: {message}")

    def update_trip_data(self, data: Dict[str, str]):
        self.known_trip_data.update(data)

    def get_trip_data_str(self) -> str:
        """Return a single string describing known trip data."""
        if not self.known_trip_data:
            return ""
        return " ".join(f"{k}:{v}" for k, v in self.known_trip_data.items())

    def get_full_history(self) -> str:
        return "\n".join(self.history)


class TripPlannerAgent(BaseAgent):
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7, max_tokens=200)

    def get_iata_code(self, city_name: str) -> str:
        prompt = f"Please provide only the IATA airport code for the city: {city_name}."
        response = self.llm.invoke([HumanMessage(content=prompt)])
        return response.content.strip()

    def format_flights_html(self, flight_data: list, departure_city: str, arrival_city: str) -> str:
        """Build an HTML string with the top 3 flight options."""
        if not flight_data:
            return "<p>No flight data found.</p>"
        
        limited_flights = flight_data[:3]
        html = f"<h2>Flights from {departure_city} to {arrival_city}</h2>"
        for i, option in enumerate(limited_flights, start=1):
            flight_list = option.get("flights", [])
            if not flight_list:
                continue
            flight = flight_list[0]
            airline = flight.get("airline", "Unknown Airline")
            departure_time = flight["departure_airport"].get("time", "")
            arrival_time = flight["arrival_airport"].get("time", "")
            airplane = flight.get("airplane", "")
            duration_minutes = flight.get("duration", 0)
            hours = duration_minutes // 60
            mins = duration_minutes % 60
            duration_str = f"{hours}h {mins}m"
            price = option.get("price", "N/A")
            airline_logo = flight.get("airline_logo") or option.get("airline_logo", "")

            html += f"""
            <div style="border:1px solid #ddd; padding:10px; margin:10px 0;">
              <h3>Option {i}: {airline}</h3>
              <ul>
                <li><strong>Departure:</strong> {departure_time}</li>
                <li><strong>Arrival:</strong> {arrival_time}</li>
                <li><strong>Duration:</strong> {duration_str}</li>
                <li><strong>Aircraft:</strong> {airplane}</li>
                <li><strong>Price:</strong> ${price}</li>
                <li><strong>Airline Logo:</strong> 
                    {f'<img src="{airline_logo}" alt="Airline Logo" width="60">' if airline_logo else 'N/A'}
                </li>
              </ul>
            </div>
            """
        return html

    def format_hotels_html(self, hotel_data: list, arrival_city: str) -> str:
        """Build an HTML string with the top 3 hotel options."""
        if not hotel_data:
            return "<p>No hotel data found.</p>"
        limited_hotels = hotel_data[:3]
        html = f"<h2>Hotels in {arrival_city}</h2>"
        for i, hotel in enumerate(limited_hotels, start=1):
            name = hotel.get("name", "Unknown Hotel")
            description = hotel.get("description", "")
            rate_info = hotel.get("rate_per_night", {})
            lowest_rate = rate_info.get("lowest", "N/A")
            images = hotel.get("images", [])
            thumbnail = images[0].get("thumbnail") if images else None

            html += f"""
            <div style="border:1px solid #ddd; padding:10px; margin:10px 0;">
              <h3>Option {i}: {name}</h3>
              <ul>
                <li><strong>Description:</strong> {description}</li>
                <li><strong>Rate per Night:</strong> {lowest_rate}</li>
                <li><strong>Hotel Image:</strong> 
                    {f'<img src="{thumbnail}" alt="Hotel Image" width="100">' if thumbnail else 'No image'}
                </li>
              </ul>
            </div>
            """
        return html

    def invoke_agent(self, messages, thread_id):
        # 1) Retrieve trip details from GLOBAL_MEMORY
        departure_city = GLOBAL_MEMORY.known_trip_data.get("departure_city", "")
        arrival_city = GLOBAL_MEMORY.known_trip_data.get("arrival_city", "")
        outbound_date = GLOBAL_MEMORY.known_trip_data.get("outbound_date", "")
        return_date = GLOBAL_MEMORY.known_trip_data.get("return_date", "")
        adults = int(GLOBAL_MEMORY.known_trip_data.get("adults", 1))
        children = int(GLOBAL_MEMORY.known_trip_data.get("children", 0))

        # 2) Convert city names to IATA codes
        departure_iata = self.get_iata_code(departure_city)
        arrival_iata = self.get_iata_code(arrival_city)

        # 3) Fetch flights and hotels using respective tools
        flight_results = flights_finder({
            "params": FlightsInput(
                departure_airport=departure_iata,
                arrival_airport=arrival_iata,
                outbound_date=outbound_date,
                return_date=return_date,
                adults=adults,
                children=children,
                infants_in_seat=0,
                infants_on_lap=0
            )
        })

        hotel_results = hotels_finder({
            "params": HotelsInput(
                q=arrival_city,
                check_in_date=outbound_date,
                check_out_date=return_date,
                adults=adults,
                children=children,
                rooms=1,
                hotel_class=None
            )
        })

        # 4) Format the results in HTML
        flights_html = self.format_flights_html(flight_results, departure_city, arrival_city)
        hotels_html = self.format_hotels_html(hotel_results, arrival_city)
        final_html = f"<div>{flights_html}{hotels_html}</div>"
        return final_html


class DestinationResearchAgent(BaseAgent):
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7, max_tokens=200)

    def invoke_agent(self, messages, thread_id):
        system_msg = SystemMessage(content="You are the Destination Research Agent. Provide in-depth info if asked.")
        all_msgs = [system_msg] + messages
        response = self.llm.invoke(all_msgs)
        return response.content


class AccommodationAgent(BaseAgent):
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7, max_tokens=200)

    def invoke_agent(self, messages, thread_id):
        system_msg = SystemMessage(content="You are the Accommodation Agent. Provide advanced hotel info if asked.")
        all_msgs = [system_msg] + messages
        response = self.llm.invoke(all_msgs)
        return response.content


class TransportationAgent(BaseAgent):
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7, max_tokens=200)

    def invoke_agent(self, messages, thread_id):
        system_msg = SystemMessage(content="You are the Transportation Agent. Provide local transport or flight details.")
        all_msgs = [system_msg] + messages
        response = self.llm.invoke(all_msgs)
        return response.content


class WeatherAgent(BaseAgent):
    def __init__(self):
        # The LLM is still available for formatting if needed.
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7, max_tokens=200)

    def invoke_agent(self, messages, thread_id):
        """
        Parse the user query and known trip data to determine the city (and date if needed),
        then call weather_finder to fetch real weather data.
        Store the fetched weather info in memory for follow-up queries.
        """
        user_query = messages[-1].content.lower()
        # Use arrival_city as fallback
        arrival_city = GLOBAL_MEMORY.known_trip_data.get("arrival_city", "")
        import re
        city_match = re.search(r"weather.*in\s+([a-zA-Z\s]+)", user_query)
        if city_match:
            city = city_match.group(1).strip().title()
        else:
            city = arrival_city

        # For this example, we ignore specific date queries.
        weather_info = weather_finder(city)
        # Store the weather info in memory for follow-ups
        GLOBAL_MEMORY.update_trip_data({"weather_info": weather_info})
        return weather_info


class ItineraryPlannerAgent(BaseAgent):
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7, max_tokens=200)

    def invoke_agent(self, messages, thread_id):
        system_msg = SystemMessage(content="You are the Itinerary Planner Agent. Create day-by-day plans if asked.")
        all_msgs = [system_msg] + messages
        response = self.llm.invoke(all_msgs)
        return response.content


class BudgetAnalystAgent(BaseAgent):
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7, max_tokens=200)

    def invoke_agent(self, messages, thread_id):
        system_msg = SystemMessage(content="You are the Budget Analyst Agent. Provide cost breakdowns if asked.")
        all_msgs = [system_msg] + messages
        response = self.llm.invoke(all_msgs)
        return response.content


class ChatbotAgent(BaseAgent):
    def __init__(self, agents: Dict[str, BaseAgent], memory: ConversationMemory):
        self.agents = agents
        self.memory = memory
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7, max_tokens=400)

    def decide_which_agents(self, user_query: str):
        q_lower = user_query.lower()
        chosen = []
        if any(x in q_lower for x in ["flight", "plane", "airfare", "tickets"]):
            chosen.append("TripPlanner")
        if any(x in q_lower for x in ["weather", "umbrella", "rain"]):
            chosen.append("Weather")
        if any(x in q_lower for x in ["destination", "culture", "attractions"]):
            chosen.append("DestinationResearch")
        if any(x in q_lower for x in ["hotel", "accommodation"]):
            chosen.append("Accommodation")
        if any(x in q_lower for x in ["transport", "car rental", "train"]):
            chosen.append("Transportation")
        if "itinerary" in q_lower:
            chosen.append("ItineraryPlanner")
        if any(x in q_lower for x in ["budget", "cost", "price"]):
            chosen.append("BudgetAnalyst")
        if not chosen:
            chosen = ["TripPlanner"]
        return list(set(chosen))

    def invoke_agent(self, messages, thread_id):
        user_input = messages[-1].content
        self.memory.add_user_message(user_input)

        chosen_agents = self.decide_which_agents(user_input)
        responses = {}

        for name in chosen_agents:
            agent = self.agents.get(name)
            if not agent:
                responses[name] = f"{name} Agent not found."
                continue
            combined_msg = f"Known trip data: {self.memory.get_trip_data_str()}\nUser: {user_input}"
            try:
                resp = agent.invoke_agent([HumanMessage(content=combined_msg)], thread_id)
                responses[name] = f"{name} says:\n{resp}"
            except Exception as e:
                responses[name] = f"Error in {name}: {e}"

        combined = "\n".join(responses.values())
        final_prompt = (
            f"User asked: {user_input}\n"
            f"Here are the agent outputs:\n{combined}\n"
            f"Use known trip data: {self.memory.get_trip_data_str()}\n"
            "Combine them into a single helpful answer."
        )
        final_response = self.llm.invoke([HumanMessage(content=final_prompt)])
        answer = final_response.content

        self.memory.add_assistant_message(answer)
        return answer
