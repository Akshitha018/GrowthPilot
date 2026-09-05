from dotenv import load_dotenv
from google import genai
import os


# Load .env
load_dotenv()


# Get API key
api_key = os.getenv("GEMINI_API_KEY")

print("API key loaded:", bool(api_key))


if not api_key:
    raise ValueError(
        "GEMINI_API_KEY is missing from .env"
    )


# Create Gemini client
client = genai.Client(
    api_key=api_key
)


# Send request using the current Interactions API
interaction = client.interactions.create(
    model="gemini-3.6-flash",
    input="Say hello to GrowthPilot in one sentence."
)


# Print response
print("\nGemini response:")
print(interaction.output_text)