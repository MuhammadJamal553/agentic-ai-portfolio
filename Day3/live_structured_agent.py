import os
import requests
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from google import genai
from google.genai import types

load_dotenv()
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))


class TravelBriefing(BaseModel):
    destination: str = Field(description="City and country name")
    temperature_celsius: float = Field(description="Current live temperature in Celsius")
    weather_summary: str = Field(description="Short description of current weather conditions")
    budget_aed: float = Field(description="Original budget in UAE Dirhams (AED)")
    converted_usd: float = Field(description="Live converted amount in US Dollars (USD)")
    exchange_rate_used: float = Field(description="Live AED to USD exchange rate used")
    packing_tips: list[str] = Field(description="3 practical packing tips based on the live weather")


def get_live_weather(city: str) -> dict:
    """Fetch real-time temperature and wind speed for any city using Open-Meteo API."""
    print(f"[Live API Call] -> Fetching weather for '{city}'...")
    try:
        geo_url = "".join([
            "https://", "geocoding-api.open-meteo.com", "/v1/search?name=", city, "&count=1"
        ])
        geo_res = requests.get(geo_url, timeout=10).json()
        if not geo_res.get("results"):
            return {"error": f"City '{city}' not found."}

        first_match = geo_res["results"][0]
        lat = first_match["latitude"]
        lon = first_match["longitude"]
        resolved_name = f"{first_match['name']}, {first_match.get('country', '')}"

        weather_url = "".join([
            "https://", "api.open-meteo.com", "/v1/forecast?latitude=",
            str(lat), "&longitude=", str(lon), "&current_weather=true"
        ])
        weather_res = requests.get(weather_url, timeout=10).json()
        current = weather_res["current_weather"]

        result = {
            "location": resolved_name,
            "temperature_celsius": current["temperature"],
            "windspeed_kmh": current["windspeed"],
        }
        print(f"   -> Weather Result: {result}")
        return result
    except Exception as e:
        print(f"   -> Weather Error: {e}")
        return {"error": str(e)}


def get_live_aed_to_usd(amount_aed: float) -> dict:
    """Convert UAE Dirhams (AED) to US Dollars (USD) using live market exchange rates."""
    print(f"[Live API Call] -> Fetching live AED to USD rate for {amount_aed} AED...")
    try:
        url = "".join(["https://", "open.er-api.com", "/v6/latest/AED"])
        res = requests.get(url, timeout=10).json()
        rate = res["rates"]["USD"]
        converted = round(amount_aed * rate, 2)
        result = {
            "amount_aed": amount_aed,
            "live_rate_aed_to_usd": rate,
            "converted_usd": converted,
        }
        print(f"   -> Currency Result: {result}")
        return result
    except Exception as e:
        print(f"   -> Currency Error: {e}")
        return {"error": str(e)}

def run_travel_agent(user_query: str) -> TravelBriefing:
    print(f"\nUser Query: {user_query}\n" + "-" * 60)

    chat = client.chats.create(
        model="gemini-3.5-flash-lite",
        config=types.GenerateContentConfig(
            system_instruction="You are a live travel and finance researcher. Always call your live API tools to get real-time weather and exchange rates.",
            tools=[get_live_weather, get_live_aed_to_usd],
            temperature=0,
        ),
    )
    raw_research = chat.send_message(user_query)
    print(f"\n[Stage 1 - Raw Research Gathered]:\n{raw_research.text}\n")

    structured_response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=f"Extract the verified facts from this research into the required schema:\n\n{raw_research.text}",
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=TravelBriefing,
            temperature=0,
        ),
    )

    briefing = TravelBriefing.model_validate_json(structured_response.text)
    return briefing


if __name__ == "__main__":
    result = run_travel_agent("I am flying from Ajman to London tomorrow with a budget of 8,500 AED. Check the live weather in London and convert my budget to USD.")

    print("[Stage 2 - Validated Pydantic JSON Output]:")
    print(result.model_dump_json(indent=2))
    print(f"\nProgrammatic Access Check -> Destination: {result.destination} | USD Budget: ${result.converted_usd}")
