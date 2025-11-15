from google import genai
from django.conf import settings

# Create a client using the API key stored in settings.py
client = genai.Client(api_key=settings.GEMINI_API_KEY)

def ask_gemini(prompt: str) -> str:
    response = client.models.generate_content(
        model="gemini-2.5-flash",   # or another Gemini model name
        contents=prompt,
    )
    return response.text
