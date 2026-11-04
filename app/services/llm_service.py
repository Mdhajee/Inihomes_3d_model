import json
import ollama


# =====================================================
# OLLAMA CONFIGURATION
# =====================================================

MODEL_NAME = "qwen2.5:3b"


# =====================================================
# HOUSE REQUIREMENTS EXTRACTION
# =====================================================

def generate_house_requirements(user_prompt: str) -> dict:
    """
    Use Ollama LLM to convert a natural-language
    house description into structured JSON.
    """

    if not user_prompt or not user_prompt.strip():
        raise ValueError("House prompt cannot be empty.")

    system_prompt = """
    You are an AI assistant for the IniHome 3D house
    generation platform.

    Your task is to understand the user's house description
    and extract the requirements.

    Return ONLY valid JSON.

    Required JSON structure:

    {
        "architectural_style": "modern",
        "plot_width": 9.144,
        "plot_length": 12.192,
        "number_of_floors": 2,
        "bedrooms": 2,
        "bathrooms": 2,
        "kitchens": 1,
        "living_rooms": 1,
        "dining_rooms": 1,
        "balconies": 0,
        "parking_spaces": 0
    }

    Rules:

    1. Convert plot dimensions into meters.
    2. If dimensions are given in feet, convert them into meters.
    3. Use numbers, not strings, for dimensions and counts.
    4. Use zero when a room type is not requested.
    5. Use "unspecified" if architectural style is not mentioned.
    6. Do not invent plot dimensions.
    7. Do not invent room requirements.
    8. If plot dimensions are missing, return null for
       plot_width and plot_length.
    9. Return only JSON without Markdown code fences.
    """

    response = ollama.chat(
        model=MODEL_NAME,
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ],
        format="json",
        options={
            "temperature": 0
        }
    )

    response_text = response["message"]["content"]

    try:
        requirements = json.loads(response_text)

    except json.JSONDecodeError as error:
        raise ValueError(
            f"Ollama returned invalid JSON: {error}"
        )

    if not isinstance(requirements, dict):
        raise ValueError("LLM response must be a JSON object.")

    return requirements