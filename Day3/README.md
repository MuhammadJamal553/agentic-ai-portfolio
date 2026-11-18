# Day 3: Live API Travel & Currency Agent with Pydantic Structured Outputs

## What I Built
- Connected an autonomous Gemini agent to two live, real-time REST APIs (`Open-Meteo` for live city weather and `ExchangeRate-API` for live AED-to-USD rates).
- Implemented a 2-stage production pipeline: Stage 1 gathers live tool observations, and Stage 2 validates the final response into a strict `TravelBriefing` **Pydantic** schema (`model_validate_json`).
- Added retry resilience to gracefully handle temporary `503` API demand spikes.

## How to Run
