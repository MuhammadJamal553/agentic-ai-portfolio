# Day 1: Building a Custom AI Tool Wrapper from Scratch

## What I Built
- Implemented a reusable `Tool` class in Python (`calculator.py`) to wrap standard Python functions with metadata (`name`, `description`, `arguments`, and `outputs`).
- Added a `.to_string()` method to serialize tool metadata into text that can be injected into an LLM's system prompt.
- Implemented `__call__` so the wrapped tool can be invoked directly like a standard Python function.

## How to Run
```bash
python calculator.py
```
# Day 2: Multi-Step Tool-Chaining Financial Agent

## What I Built
- Built a live tool-calling agent in Python (`live_tool_agent.py`) powered by Google's `google-genai` SDK (`gemini-3.5-flash-lite`).
- Implemented 3 custom Python tools (`multiply`, `calculate_uae_vat`, and `convert_aed_to_usd`) with strict type hints and docstrings so the LLM can automatically chain them in sequence.
- Secured API credentials using `python-dotenv` and `.gitignore`.

## How to Run
```bash
pip install google-genai python-dotenv
python Day2/live_tool_agent.py
```
# Day 3: Live API Travel & Currency Agent with Pydantic Structured Outputs

## What I Built
- Connected an autonomous Gemini agent to two live, real-time REST APIs (`Open-Meteo` for live city weather and `ExchangeRate-API` for live AED-to-USD rates).
- Implemented a 2-stage production pipeline: Stage 1 gathers live tool observations, and Stage 2 validates the final response into a strict `TravelBriefing` **Pydantic** schema (`model_validate_json`).
- Added retry resilience to gracefully handle temporary `503` API demand spikes.

## How to Run

1. **Install dependencies:**
   ```bash
   pip install google-genai python-dotenv requests pydantic
   ```

2. **Set your API key** in the root `.env` file:
   ```env
   GEMINI_API_KEY=your_google_ai_studio_key_here
   ```

3. **Run the agent:**
   ```bash
   python Day3/live_structured_agent.py
   ```
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
# Day 5: Self-Grading Enterprise Agentic RAG Pipeline

## What I Built
- Built a self-correcting **Agentic RAG** pipeline (`agentic_rag.py`) using **ChromaDB**, **Google Gemini**, and **Pydantic** structured outputs.
- **Document Relevance Grader:** Evaluates every retrieved chunk against a strict `GradeResult` Pydantic schema (`relevant: bool`, `reason: str`) to filter out noisy vector search matches before answering.
- **Query Rewriter & Anti-Hallucination Guardrail:** Automatically rewrites queries when zero relevant documents are found, cites exact source documents (`[Source Name]`), and refuses to answer out-of-scope questions.

## How to Run

1. **Install dependencies:**
   ```bash
   pip install chromadb google-genai python-dotenv pydantic
   ```

2. **Run the Agentic RAG tests:**
   ```bash
   python Day5/agentic_rag.py