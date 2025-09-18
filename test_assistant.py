import asyncio
import os
from dotenv import load_dotenv

# Load environment variables first
load_dotenv()

from core.intent_detector import detect_intent
from features.weather_feature import handle_weather_intent

async def main():
    """
    Main function to run the assistant from the command line.
    """
    print("Assistant is running. Type 'exit' to quit.")
    while True:
        try:
            user_input = input("> ")
        except (KeyboardInterrupt, EOFError):
            print("\nExiting...")
            break

        if user_input.lower() == "exit":
            print("Exiting...")
            break

        intent_data = await detect_intent(user_input)
        intent = intent_data.get("intent")
        entities = intent_data.get("entities")

        response = ""
        if intent == "weather":
            response = await handle_weather_intent(entities)
        elif intent == "unknown":
            response = "I'm not sure how to help with that."
        elif intent == "error":
            response = f"An error occurred: {entities.get('message')}"
        else:
            response = f"Intent '{intent}' is not yet supported in this test script."

        print(response)

if __name__ == "__main__":
    asyncio.run(main())
