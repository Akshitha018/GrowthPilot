import os

from google import genai


# ---------------------------------------------------------
# GEMINI CLIENT
# ---------------------------------------------------------

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError(
        "GEMINI_API_KEY is not set in the environment."
    )


client = genai.Client(
    api_key=api_key
)


# ---------------------------------------------------------
# AI GROWTH RECOMMENDATION
# ---------------------------------------------------------

def generate_growth_recommendation(
    experiment_name,
    goal,
    analysis,
    decision
):

    prompt = f"""
You are GrowthPilot, an AI-powered growth experimentation agent.

Your job is to analyze an A/B experiment and provide a practical
business recommendation.

==================================================
EXPERIMENT
==================================================

Experiment name:
{experiment_name}


==================================================
BUSINESS GOAL
==================================================

{goal}


==================================================
EXPERIMENT ANALYSIS
==================================================

{analysis}


==================================================
CURRENT DECISION ENGINE OUTPUT
==================================================

{decision}


==================================================
YOUR TASK
==================================================

Analyze the information above and provide:

1. Winner
2. Key performance insight
3. Recommended decision:
   - SCALE
   - KEEP_TESTING
   - STOP
4. Recommended business action
5. Main risk or limitation
6. What additional data should be collected next

Important rules:

- Do NOT invent numbers.
- Use only the information provided.
- If the sample size is small, clearly mention that.
- Do not claim statistical significance unless it is provided.
- If there is insufficient data, recommend KEEP_TESTING.
- Explain the result in simple business language.
- Keep the recommendation concise but useful.
- Make the recommendation actionable for a growth team.

Use exactly these headings:

Winner:
Key Insight:
Decision:
Recommended Action:
Risk / Limitation:
Next Data to Collect:
"""


    # -----------------------------------------------------
    # GEMINI INTERACTIONS API
    # -----------------------------------------------------

    interaction = client.interactions.create(
        model="gemini-3.6-flash",
        input=prompt
    )


    # -----------------------------------------------------
    # RETURN RESPONSE
    # -----------------------------------------------------

    return interaction.output_text