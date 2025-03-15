# AI-Travel-Agent

**AI-Travel-Agent** is an intelligent travel assistant that leverages a multi-agent architecture powered by ChatGPT, FastAPI, and Streamlit. It fetches real-time flight and hotel details via SerpAPI and provides interactive travel-related information—including weather forecasts from OpenWeatherMap—through an engaging chat interface.

## Features

- **Trip Planning & Recommendations**  
  Plan your trip by entering your departure/arrival cities and travel dates. Receive real-time flight and hotel recommendations with details like pricing, durations, and images.

- **Real-Time Weather Forecasts**  
  Query the weather for your destination (using the OpenWeatherMap API) to get current conditions and short-term forecasts.

- **Interactive Chat**  
  Ask follow-up questions such as “Do I need an umbrella?” or “What attractions are near my hotel?” The chatbot uses conversation memory to provide coherent and context-aware responses.

- **Memory Support**  
  The system saves your trip details and agent responses, allowing for accurate follow-up queries.

## Setup

1. **Clone the repository:**

2. **Install dependencies:**

   pip install -r requirements.txt

3. **Configure Environment Variables:**
   Create a .env file in the root directory and add your API keys and other configuration variables:

    SERPAPI_API_KEY=your_serpapi_key
    OPENWEATHER_API_KEY=your_openweather_key
    OPENAI_API_KEY=your_openai_key
   
4. **Run the API Server:**
   
   uvicorn api:app --reload

5. **Run the Streamlit App:**

   streamlit run app.py

## Sample Output

![1](https://github.com/user-attachments/assets/c0561e5d-83ea-43a6-80c0-a02433812fe2)
![2](https://github.com/user-attachments/assets/a0b971ed-8a29-4707-a0fa-bf5da9052633)
![3](https://github.com/user-attachments/assets/c9e5d301-d55d-45fa-b002-e22240478552)
![4](https://github.com/user-attachments/assets/1f9966b1-d75e-435e-9fd9-b9cc6aa24ba5)





 
