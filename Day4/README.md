
# Day 4: Self-Reflection & Error-Correcting Agent (Generator + Critic Pattern)

## What I Built
- Implemented a two-role **Reflection Agent** (`reflection_agent.py`) using Google Gemini and Pydantic structured outputs.
- **Generator Agent:** Drafts concise, recruiter-focused technical LinkedIn posts and revises them dynamically using structured critique feedback.
- **Critic Agent:** Evaluates every draft against strict formatting, length, and anti-hallucination rules using a validated `CriticResult` Pydantic schema (`score`, `passed`, `feedback`).

## How to Run

1. **Install dependencies:**
   ```bash
   pip install google-genai python-dotenv pydantic
   ```

2. **Run the self-reflection loop:**
   ```bash
   python Day4/reflection_agent.py
   ```
