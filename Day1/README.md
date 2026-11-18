# Day 1: Building a Custom AI Tool Wrapper from Scratch

## What I Built
- Implemented a reusable `Tool` class in Python (`calculator.py`) to wrap standard Python functions with metadata (`name`, `description`, `arguments`, and `outputs`).
- Added a `.to_string()` method to serialize tool metadata into text that can be injected into an LLM's system prompt.
- Implemented `__call__` so the wrapped tool can be invoked directly like a standard Python function.

## How to Run
```bash
python calculator.py
```