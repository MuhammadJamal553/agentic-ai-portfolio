import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

# 1. Load your GEMINI_API_KEY from the root .env file
load_dotenv()

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))


# 2. Define real Python functions (Notice type hints + docstrings are all Gemini needs!)
def multiply(a: int, b: int) -> dict:
    """Multiply two integers together."""
    print(f"[Tool Executed] -> multiply(a={a}, b={b})")
    return {"result": a * b}


def calculate_uae_vat(amount_aed: float) -> dict:
    """Calculate 5% UAE VAT and total price in AED."""
    print(f"[Tool Executed] -> calculate_uae_vat(amount_aed={amount_aed})")
    vat = round(amount_aed * 0.05, 2)
    total = round(amount_aed + vat, 2)
    return {
        "base_amount_aed": amount_aed,
        "vat_5_percent": vat,
        "total_aed": total
    }
def convert_aed_to_usd(amount_aed: float) -> dict:
    """Convert an amount from UAE Dirhams (AED) to US Dollars (USD)."""
    print(f"[Tool Executed] -> convert_aed_to_usd(amount_aed={amount_aed})")
    usd = round(amount_aed * 0.2723, 2)
    return {"amount_aed": amount_aed, "amount_usd": usd}



# 3. Run the Agent using Gemini's native tool-chaining loop
def run_agent(user_query: str):
    print(f"\nUser Query: {user_query}\n" + "-" * 50)

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=user_query,
        config=types.GenerateContentConfig(
            system_instruction="You are a precise financial assistant. Always use your tools for multiplication, UAE VAT, and AED-to-USD currency conversion instead of guessing.",
            tools=[multiply, calculate_uae_vat, convert_aed_to_usd],
            temperature=0,
        ),
    )

    print(f"\n[Final Answer]:\n{response.text}")


if __name__ == "__main__":
    run_agent("I am buying 12 laptops at 3,200 AED each. What is the subtotal, the final total after 5% UAE VAT, and the final total in USD?")
