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