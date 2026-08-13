import os
import httpx
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Securely fetch the token from the environment variable
AI_API_TOKEN = os.getenv("AI_API_TOKEN")

# Base URL configured specifically for the Userfacet proxy environment
AI_API_URL = "https://ai-api.userfacet.com/v1/chat/completions" 

async def generate_book_summary(title: str, author: str) -> str:
    """
    Calls the external Userfacet LLM API to generate a brief summary of a book.
    Uses HTTPX for asynchronous, non-blocking network requests to ensure the 
    FastAPI event loop is not blocked during external network latency.
    """
    prompt = f"Provide a brief, engaging summary for the book '{title}' by {author}."
    
    headers = {
        "Authorization": f"Bearer {AI_API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "gpt-4o-mini",  # The Userfacet API strictly locks to this specific model
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7       # Adds a slight amount of natural variance/creativity to the text
    }

    async with httpx.AsyncClient() as client:
        try:
            # A strict 10-second timeout prevents the backend from hanging if the AI service goes down
            response = await client.post(AI_API_URL, headers=headers, json=payload, timeout=10.0)
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
        except Exception as e:
            # Graceful degradation: Return an error string rather than crashing the HTTP request
            return f"Summary temporarily unavailable. (Error: {str(e)})"