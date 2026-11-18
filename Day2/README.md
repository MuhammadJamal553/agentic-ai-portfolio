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