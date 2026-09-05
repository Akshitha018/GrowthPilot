import os
import json

from dotenv import load_dotenv
from google import genai

load_dotenv()


# ============================================================
# GEMINI CLIENT
# ============================================================

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError(
        "GEMINI_API_KEY is not set in the .env file."
    )

client = genai.Client(api_key=API_KEY)


# ============================================================
# GENERATE GROWTH RECOMMENDATION
# ============================================================

def generate_growth_recommendation(analysis):

    try:

        experiment_id = analysis.get(
            "experiment_id",
            "Unknown"
        )

        control = analysis.get(
            "control",
            {}
        )

        variant_a = analysis.get(
            "variant_a",
            {}
        )

        variant_b = analysis.get(
            "variant_b",
            {}
        )

        winner = analysis.get(
            "winner",
            "TIE"
        )

        improvement = analysis.get(
            "improvement_percent",
            0
        )

        prompt = f"""
You are GrowthPilot, an AI growth experimentation agent.

Analyze the following A/B experiment results.

Experiment ID:
{experiment_id}

CONTROL:
Customers: {control.get("customers", 0)}
Conversions: {control.get("conversions", 0)}
Conversion Rate: {control.get("conversion_rate", 0)}%

VARIANT A:
Customers: {variant_a.get("customers", 0)}
Conversions: {variant_a.get("conversions", 0)}
Conversion Rate: {variant_a.get("conversion_rate", 0)}%

VARIANT B:
Customers: {variant_b.get("customers", 0)}
Conversions: {variant_b.get("conversions", 0)}
Conversion Rate: {variant_b.get("conversion_rate", 0)}%

Current Winner:
{winner}

Improvement:
{improvement}%

Provide a practical growth recommendation.

Return ONLY valid JSON in exactly this format:

{{
    "recommendation": "A clear action the business should take.",
    "reason": "Explain why this action is recommended based on the experiment results."
}}

Do not include markdown.
Do not include ```json.
"""


        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt
        )

        text = response.text.strip()

        # Remove markdown if Gemini happens to return it
        if text.startswith("```json"):
            text = text[7:]

        if text.startswith("```"):
            text = text[3:]

        if text.endswith("```"):
            text = text[:-3]

        text = text.strip()

        recommendation = json.loads(text)

        return {
            "recommendation": recommendation.get(
                "recommendation",
                "No recommendation generated."
            ),
            "reason": recommendation.get(
                "reason",
                "No reason provided."
            )
        }


    except Exception as e:

        print(
            "Gemini recommendation error:",
            str(e)
        )

        return {
            "recommendation":
                "AI recommendation unavailable.",

            "reason":
                str(e)
        }