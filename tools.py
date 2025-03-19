from langchain.tools import tool
import requests

@tool
def search_tool(query: str) -> str:
    """Search the web for information."""
    response = requests.get(f"https://www.googleapis.com/customsearch/v1?q={query}&key=YOUR_GOOGLE_API_KEY&cx=YOUR_SEARCH_ENGINE_ID")
    if response.status_code == 200:
        results = response.json().get('items', [])
        return "\n".join([item.get('title', '') + ": " + item.get('link', '') for item in results[:5]])
    return "No search results found."

@tool
def wiki_tool(query: str) -> str:
    """Search Wikipedia for information."""
    response = requests.get(f"https://en.wikipedia.org/w/api.php?action=query&format=json&list=search&srsearch={query}")
    if response.status_code == 200:
        results = response.json().get('query', {}).get('search', [])
        return "\n".join([result['title'] for result in results[:5]])
    return "No Wikipedia results found."

@tool
def save_tool(data: str) -> str:
    """Save research to a file."""
    with open("research.txt", "a") as file:
        file.write(data + "\n")
    return "Data saved to research.txt"
