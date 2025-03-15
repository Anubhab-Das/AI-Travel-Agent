import json
import requests
from langchain.tools import tool
import os
from dotenv import load_dotenv
load_dotenv()
import streamlit as st

# Use Streamlit secrets if available; otherwise, fall back to the environment variable.
SERPER_API = st.secrets.get("SERPER_API_KEY") if "SERPER_API_KEY" in st.secrets else os.getenv("SERPER_API_KEY")

class SearchTools:
    @tool("Search the internet")
    def search_internet(query):
        """
        Search the internet for a given query and return relevant results.
        """
        top_result_to_return = 4
        url = "https://google.serper.dev/search"
        payload = json.dumps({"q": query})
        headers = {
            'X-API-KEY': SERPER_API,
            'content-type': 'application/json'
        }
        try:
            response = requests.post(url, headers=headers, data=payload)
            data = response.json()
        except Exception as e:
            return f"Error fetching search results: {e}"
        
        if 'organic' not in data:
            return "Sorry, no results found. Please check your SERPER API key."
        else:
            results = data['organic']
            strings = []
            for result in results[:top_result_to_return]:
                try:
                    strings.append('\n'.join([
                        f"Title: {result['title']}",
                        f"Link: {result['link']}",
                        f"Snippet: {result['snippet']}",
                        "-----------------"
                    ]))
                except KeyError:
                    continue
            return "\n".join(strings)
