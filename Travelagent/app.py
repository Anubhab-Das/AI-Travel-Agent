import base64
import re
import json
import requests
import streamlit as st

MAIN_AGENT_URL = "http://localhost:8000/main-agent"
CHAT_AGENT_URL = "http://localhost:8000/chat"

def set_background_image(image_file: str, overlay_opacity: float = 0.1):
    """Set a background image in the Streamlit app."""
    with open(image_file, "rb") as f:
        data = f.read()
    encoded = base64.b64encode(data).decode()
    st.markdown(
        f"""
        <style>
        .stApp {{
            background:
                linear-gradient(
                    rgba(255, 255, 255, {overlay_opacity}),
                    rgba(255, 255, 255, {overlay_opacity})
                ),
                url("data:image/jpg;base64,{encoded}") no-repeat center center fixed;
            background-size: cover;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

def show_floating_chat_button():
    """Renders a floating chat button on the bottom-right of the screen."""
    st.markdown(
        """
        <style>
        #chat-button {
            position: fixed;
            bottom: 25px;
            right: 25px;
            background-color: #3498db;
            color: #fff;
            padding: 14px 18px;
            border-radius: 30px;
            cursor: pointer;
            font-size: 16px;
            z-index: 9999;
            box-shadow: 2px 2px 5px rgba(0,0,0,0.3);
        }
        #chat-button:hover {
            background-color: #2c7fb8;
        }
        </style>
        <div id="chat-button" onclick="document.getElementById('chat-section').scrollIntoView({behavior: 'smooth'});">
            💬 Chat
        </div>
        """,
        unsafe_allow_html=True
    )

def build_flights_html(flight_data, departure_city, arrival_city):
    """Convert up to 3 flights from the JSON into a nicely formatted HTML block."""
    if not flight_data:
        return "<p>No flight data found.</p>"

    limited_flights = flight_data[:3]
    html = f"<h2>Flights from {departure_city} to {arrival_city}</h2>"

    for i, flight_option in enumerate(limited_flights, start=1):
        # Each flight_option is typically a dict with "flights": [ {...} ], "price", etc.
        flights_list = flight_option.get("flights", [])
        if not flights_list:
            continue

        # We'll just use the first flight segment
        flight = flights_list[0]
        airline = flight.get("airline", "Unknown Airline")
        departure_time = flight["departure_airport"].get("time", "")
        arrival_time = flight["arrival_airport"].get("time", "")
        price = flight_option.get("price", "N/A")
        airline_logo = flight.get("airline_logo", "")

        html += f"""
        <div style="border:1px solid #ddd; padding:10px; margin:10px 0;">
          <h3>Option {i}: {airline}</h3>
          <ul>
            <li><strong>Departure:</strong> {departure_time}</li>
            <li><strong>Arrival:</strong> {arrival_time}</li>
            <li><strong>Price:</strong> ${price}</li>
            <li><strong>Airline Logo:</strong> 
                {f'<img src="{airline_logo}" alt="Airline Logo" width="60">' if airline_logo else 'N/A'}
            </li>
          </ul>
        </div>
        """
    return html

def build_hotels_html(hotel_data, arrival_city):
    """Convert up to 3 hotels from the JSON into a nicely formatted HTML block."""
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
        # Use the first image if available
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

def main():
    st.set_page_config(page_title="AI Travel Agent", layout="centered")
    set_background_image("images/travel_background.jpg", overlay_opacity=0.1)

    if "recommendations_done" not in st.session_state:
        st.session_state["recommendations_done"] = False

    st.title("AI Travel Agent")

    # Sidebar image
    st.sidebar.image("images/ai-travel.png", caption="AI Travel Assistant", use_container_width=True)

    # === Plan Trip Form ===
    st.subheader("Plan Your Trip")
    departure_airport = st.text_input("Departure City", placeholder="e.g. New York")
    arrival_airport = st.text_input("Arrival City", placeholder="e.g. Paris")
    outbound_date = st.text_input("Outbound Date (YYYY-MM-DD)", placeholder="e.g. 2025-03-15")
    return_date = st.text_input("Return Date (YYYY-MM-DD)", placeholder="e.g. 2025-03-20")
    adults = st.number_input("Number of Adults", min_value=1, value=1)
    children = st.number_input("Number of Children", min_value=0, value=0)
    additional_info = st.text_input("Additional Info (Optional)", placeholder="e.g. Preferences, budget, etc.")

    if st.button("Get Flight & Hotel Recommendations"):
        if not departure_airport or not arrival_airport or not outbound_date or not return_date:
            st.error("Please fill out all required fields (airport codes, dates).")
        else:
            payload = {
                "departure_airport": departure_airport,
                "arrival_airport": arrival_airport,
                "outbound_date": outbound_date,
                "return_date": return_date,
                "adults": adults,
                "children": children,
                "additional_info": additional_info
            }
            with st.spinner("Fetching recommendations..."):
                resp = requests.post(MAIN_AGENT_URL, json=payload)
            
            if resp.status_code == 200:
                data = resp.json()
                raw_result = data.get("result", "")

                # The agent typically returns a string like:
                # "Here are your flight and hotel options: { 'flights': [...], 'hotels': [...] }"
                # We'll parse out the JSON portion.
                pattern = r"Here are your flight.*options:\s*(\{.*\})"
                match = re.search(pattern, raw_result, re.DOTALL)
                if match:
                    json_str = match.group(1)
                    try:
                        result_dict = json.loads(json_str)
                        flight_data = result_dict.get("flights", [])
                        hotel_data = result_dict.get("hotels", [])

                        # Build the user-friendly HTML
                        flights_html = build_flights_html(flight_data, departure_airport, arrival_airport)
                        hotels_html = build_hotels_html(hotel_data, arrival_airport)
                        final_html = f"<div>{flights_html}{hotels_html}</div>"

                        st.success("✅ Here are your flight & hotel recommendations!")
                        st.markdown(final_html, unsafe_allow_html=True)
                        st.session_state["recommendations_done"] = True
                    except json.JSONDecodeError:
                        # If JSON parsing fails, fallback to raw HTML
                        st.markdown(raw_result, unsafe_allow_html=True)
                        st.session_state["recommendations_done"] = True
                else:
                    # If the agent returns HTML directly, just show it
                    st.markdown(raw_result, unsafe_allow_html=True)
                    st.session_state["recommendations_done"] = True
            else:
                st.error("⚠️ Failed to retrieve recommendations.")

    # Floating chat bubble if we have recommendations
    if st.session_state["recommendations_done"]:
        show_floating_chat_button()

    # Chat section
    st.markdown("<div id='chat-section'></div>", unsafe_allow_html=True)
    if st.session_state["recommendations_done"]:
        st.subheader("Chat with the AI Assistant")
        user_query = st.text_area("Your Message", height=100, placeholder="e.g., How's the weather in Paris?")
        
        if st.button("Send Chat"):
            if user_query.strip():
                with st.spinner("Assistant is thinking..."):
                    resp = requests.post(CHAT_AGENT_URL, json={"query": user_query})
                if resp.status_code == 200:
                    data = resp.json()
                    st.success("Assistant's Reply")
                    st.markdown(data.get("result", "No data returned."), unsafe_allow_html=True)
                else:
                    st.error("⚠️ Failed to process your query.")
            else:
                st.error("Please enter your question.")

if __name__ == "__main__":
    main()
