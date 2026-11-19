import os
import time
from dotenv import load_dotenv
from pydantic import BaseModel,Field
from google import genai
from google.genai import types

load_dotenv()
client  = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

class CriticResult (BaseModel):
    score:int=Field(description="Quality Score From 1 to 10")
    passed:bool=Field(description="True Only if score is 8 or Higher and All Rules are Meet")
    feedback:str=Field(description="Specific, Actionable Improvement is needed is Passed is False")








def call_gemini(prompt:str, system_instruction:str, response_schema=None) -> str:
    config_args = {
        "system_instruction": system_instruction,
        "temperature"       : 0.4 if response_schema is None else 0,
    }

    if response_schema:
        config_args["response_mime_type"] = "application/json"
        config_args["response_schema"] = response_schema

    for attempt in range (1, 4):
        try:
            response = client.models.generate_content(
                model   = "gemini-3.5-flash-lite",
                contents= prompt,
                config  = types.GenerateContentConfig(**config_args),
            )
            return response.text
        except Exception as e :
            if "503" in str(e) and attempt < 3:
                print(f"[Server Busy 503],retrying in 3s.... {attempt}/3")
                time.sleep(3)
            else:
                raise


def generate_post (topic:str, previous_draft:str="", feedback:str="") -> str:
    system_prompt = (
        "You are and Ai Engineer Writing Concise LinkedIn post for Recruiters in Dubai and London"
        "Keep Post punchy, practical and easy to Scan."
    )

    if not feedback:
        user_prompt = f"Write a Short LinkedIn Post about.{topic}"
    else:
        user_prompt = (
            f"Topic: {topic}\n\n"
            f"Your Previous draft:\n{previous_draft}\n\n"
            f"Critic FeedBack to Fix:\n{feedback}\n\n"
            "Rewrite the Post to fix Every issue mentioned in the feedback."
        )

    return call_gemini (prompt=user_prompt, system_instruction=system_prompt)



def critique_post (draft:str) -> CriticResult:
    system_prompt   = (
        "You Are a strict LinkedIn Technical Editor. Evaluate the Draft Againt these 4 Rules:\n"
        "1. Must Be Under 130 Words.\n"
        "2. Must not Contain Code Blocks (```).\n"
        "3. Must Not Mention Libraries not Explicitly provided in the topic (e.g., do not invent Pydantic or OpenAI).\n"
        "4. Must End With Clear, Engaging Questions For Recruiters or Engineers.\n"
        "Only Said Passed=True if the Score is 8 or Higher And All 4 Rules Are strictly met. "
    )

    raw_json = call_gemini(
        prompt= f"Evalute this LinkedIn draft{draft}",
        system_instruction= system_prompt,
        response_schema = CriticResult
    )
    return CriticResult.model_validate_json(raw_json)

def run_reflection_agent(topic:str, max_attempts: int=3) -> str:
    print(f"\nStarting Self-Reflection Agent on Topics:'{topic}'\n"+"="*60)
    draft = ""
    feedback= ""

    for attempt in range (1, max_attempts + 1):
        print(f"\n ---Attempt {attempt}/{max_attempts} Generating Draft---")
        draft = generate_post(topic=topic,previous_draft=draft,feedback=feedback)
        print(draft)


        print(f"\n ---Attempt {attempt}/{max_attempts}:Critic Evaluating..---")
        critique = critique_post(draft)
        print(f"Score: {critique.score}/10 | passed :{critique.passed}" )
        print(f"FeedBack:{critique.feedback}")

        if critique.passed:
            print(f"\n[SUCCESS] Draft Passed Quality Gate!")
            return draft

        feedback = critique.feedback
        time.sleep(2)

    print("\n [MAX ATTEMPTS REACHED] Returning best available draft.")
    return draft

if __name__ == "__main__":
    final_post = run_reflection_agent("Buiding a Live Weather and Currency Exchange AI Agent with Pydantic.")
    print("\n"+"="*60 + "\nFINAL APPROVED POST:\n"+"="*60)
    print (final_post)