Here's a concise workflow overview with the main function names and steps:

Streamlit Frontend:
render_custom_css(): Sets up the UI styling.

plan_trip(): Collects destination, arrival city, and travel date; sends a POST request to the /main-agent endpoint.

chat_with_agent(): Collects follow-up queries from the user; sends a POST request to the /chat endpoint.

main(): Organizes the UI into tabs for trip planning and chatbot interaction.

FastAPI Backend:
/main-agent Endpoint: Receives initial travel details and calls TripPlannerAgent.invoke_agent().

/chat Endpoint: Receives follow-up queries and instantiates multiple mini agents; aggregates their outputs using ChatbotAgent.invoke_agent().

Agent Workflow (in agents/multi_agents.py):
TripPlannerAgent.invoke_agent(): Uses the tool registry to fetch flight/hotel search results and generates recommendations.

DestinationResearchAgent.invoke_agent(), AccommodationAgent.invoke_agent(), TransportationAgent.invoke_agent(), WeatherAgent.invoke_agent(), ItineraryPlannerAgent.invoke_agent(), BudgetAnalystAgent.invoke_agent(): Each calls the appropriate tools (via the tool registry) to fetch data specific to their expertise.

ChatbotAgent.invoke_agent(): Iterates through the specialized agents, aggregates their responses, and produces a final summarized answer.

Tool Registry (in tools/tool_registry.py):
Registers all helper tools (e.g., search_internet, scrape_and_summarize_website, calculate, flights_finder, hotels_finder) for easy reuse in agent functions.

This sequential flow lets the user first get travel recommendations and then interact with a multi-agent chatbot for further details, all while leveraging a centralized tool registry for consistent external data retrieval.