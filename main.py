import json
import asyncio
import warnings
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

warnings.filterwarnings("ignore", message="Field name .* shadows an attribute")
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from example_agent import get_weather, weather_agent
from google.genai import types


async def call_agent_async(query: str, runner: Runner, user_id, session_id):
    """Sends a query to the agent and prints the final response."""
    content = types.Content(role="user", parts=[types.Part(text=query)])
    final_response_text = "Agent did not produce a final response."

    async for event in runner.run_async(
        user_id=user_id, session_id=session_id, new_message=content
    ):

        if event.is_final_response():
            if event.content and event.content.parts:
                final_response_text = event.content.parts[0].text
            elif event.actions and event.actions.escalate:
                final_response_text = (
                    f"Agent escalted: {event.error_message or 'No specific message.'}"
                )
            break

    print(f"<<< Agent Response: {final_response_text}")


async def main():

    session_service = InMemorySessionService()

    # Get environment variables
    APP_NAME = os.getenv("APP_NAME")
    USER_ID = os.getenv("USER_ID")
    SESSION_ID = os.getenv("SESSION_ID")

    session = await session_service.create_session(
        app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
    )

    runner = Runner(
        agent=weather_agent, app_name=APP_NAME, session_service=session_service
    )

    await call_agent_async(
        "What is the weather like in London?",
        runner=runner,
        user_id=USER_ID,
        session_id=SESSION_ID,
    )

    await call_agent_async(
        "How about Paris?", runner=runner, user_id=USER_ID, session_id=SESSION_ID
    )  # Expecting the tool's error message

    await call_agent_async(
        "Tell me the weather in New York",
        runner=runner,
        user_id=USER_ID,
        session_id=SESSION_ID,
    )

    # await call_agent_async(
    #     "How about Paris?", runner=runner, user_id=USER_ID, session_id=SESSION_ID
    # )  # Expecting the tool's error message

    # await call_agent_async(
    #     "Tell me the weather in New York",
    #     runner=runner,
    #     user_id=USER_ID,
    #     session_id=SESSION_ID,
    # )

    # # Test the weather function with different cities
    # cities = ["New York", "London", "Tokyo", "Invalid City"]

    # for city in cities:
    #     result = get_weather(city)
    #     print(f"\nWeather for {city}:")
    #     print(json.dumps(result, indent=2))


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
