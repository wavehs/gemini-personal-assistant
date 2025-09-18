import os
import google.generativeai as genai
import json

# It's recommended to load the API key once and reuse the client
try:
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    # Initialize the generative model
    model = genai.GenerativeModel('models/gemini-1.5-flash-latest')
except Exception as e:
    print(f"Error configuring Gemini API: {e}")
    model = None

# --- Intent Detection Prompt ---

INTENT_PROMPT = """
You are an expert intent detection model for a personal assistant bot.
Your task is to analyze the user's message and identify their intent and any relevant entities.
Provide the output in JSON format with two keys: "intent" and "entities".
The "intent" should be one of the following:
- 'weather': for checking the weather.
- 'create_event': for creating a calendar event.
- 'commute': for getting travel directions.
- 'pantry_add': for adding items to a pantry list.
- 'pantry_remove': for removing items from a pantry list.
- 'pantry_list': for listing items in the pantry.
- 'unknown': if the intent cannot be determined.

The "entities" should be a dictionary of extracted information.
For 'weather', the entity is 'location'.
For 'create_event', the entities are 'title' and 'datetime'.
For 'commute', the entities are 'origin' and 'destination'.
For 'pantry_add' or 'pantry_remove', the entity is 'item'.

Here are some examples:
User: "What's the weather like in London?"
{"intent": "weather", "entities": {"location": "London"}}

User: "Add milk to my pantry"
{"intent": "pantry_add", "entities": {"item": "milk"}}

User: "How do I get from home to work?"
{"intent": "commute", "entities": {"origin": "home", "destination": "work"}}

User: "Schedule a meeting with John tomorrow at 2pm"
{"intent": "create_event", "entities": {"title": "meeting with John", "datetime": "tomorrow at 2pm"}}
"""

async def detect_intent(text: str) -> dict:
    """
    Detects the intent and entities from the user's text using the Gemini API.
    """
    if not model:
        return {"intent": "error", "entities": {"message": "Gemini model not initialized"}}

    try:
        full_prompt = f"{INTENT_PROMPT}\nUser: \"{text}\"\n"
        response = model.generate_content(full_prompt)

        # Clean up the response to extract the JSON part
        json_response_str = response.text.strip().replace('```json', '').replace('```', '').strip()

        parsed_response = json.loads(json_response_str)
        return parsed_response
    except Exception as e:
        print(f"Error during intent detection: {e}")
        return {"intent": "error", "entities": {"message": str(e)}}
