import json
import requests
from langchain.tools import tool
from unstructured.partition.html import partition_html

class BrowserTool:
    @tool("Scrape website content")
    def scrape_and_summarize_website(website: str) -> str:
        """
        Scrape the website content from the given URL and summarize it using a mock LLM.
        """
        url = "http://localhost:3000/content"
        payload = json.dumps({"url": website})
        headers = {"cache-control": "no-cache", "content-type": "application/json"}

        try:
            response = requests.post(url, headers=headers, data=payload)
            response.raise_for_status()
            content = response.text
        except requests.exceptions.RequestException as e:
            print(f"Error fetching content: {e}")
            return "Failed to fetch content"

        # Partition the HTML content into elements.
        elements = partition_html(text=content)
        text_content = "\n\n".join(str(el) for el in elements)

        # Break the text into manageable chunks.
        chunk_size = 8000
        text_chunks = [text_content[i:i+chunk_size] for i in range(0, len(text_content), chunk_size)]

        # Use our mock LLM for summarization.
        summarizer = MockLLM(model_name="mock-model", temperature=0.3)

        summaries = []
        for chunk in text_chunks:
            prompt = (
                "Summarize the following content succinctly, focusing on the key points only:\n\n"
                f"{chunk}"
            )
            response = summarizer.invoke(prompt)
            summaries.append(response.content)

        return "\n\n".join(summaries)
