import os
import time
import chromadb
from pydantic import BaseModel,Field
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

chroma_client = chromadb.Client()
collection  = chroma_client.create_collection(name="enterprise_cloud_docs")

KNOWLEDGE_DOCS = [
    {
        "id" : "docs_1",
        "source" : "Enterprise_SLA_Policy_v4.pdf (Section 2.1)",
        "text" : "Enterprise tier Customers Receives a 99.95% Monthly uptime SLA gurantee. If Monthly available Fall Below 99.95% , Customers are Eligable for 10% service credits, increased to 25% if uptime drop below 99.0%."
    },
    {
        "id" : "docs_2",
        "source" : "API_Rate_Limits_Guide.pdf (Page 5)",
        "text" : "Production API keys Are Rate Limited to 1,200 requests per minute (RPM) and 50,000 tokens per minute (TPM) on Standard Plan. Burst traffic Exceeding 120% triggers HTTP 429 reponses with a Retry-After header."
    },
    {
        "id" : "docs_3",
        "source" : "DATA_Privacy_GDPR_Compliance.pdf (Section 4)",
        "text" : "Customer inference logs and prompts are encrypted at rest using AES-256 and automatically purged after 30 days by default. Zero-data-retention (ZDR) mode is available for healthcare and financial clients."
    },
    {
        "id" : "docs_4",
        "source" : "Incident_Escalation_Runbook.pdf (Page 11)",
        "text" : "Severity-1 (P1) production outages affecting core authentication or payment APIs require on-call engineering acknowledgment within 15 minutes and executive status updates every 30 minutes until resolved."
    }
]

collection.add(
    ids=[d["id"]for d in KNOWLEDGE_DOCS],
    documents=[d["text"]for d in KNOWLEDGE_DOCS],
    metadatas=[{"source":d["source"]}for d in KNOWLEDGE_DOCS],
)

def search_docs(query:str, n_results:int = 2) -> list[dict]:
    results = collection.query(query_texts=[query], n_results=n_results)
    docs = []
    for text, meta in zip (results["documents"][0],results["metadatas"][0]):
        docs.append({"source": meta["source"],"text": text})
    return docs


class GradeResult(BaseModel):
    relevent : bool = Field(description="True if the documents Contains facts usefull to user's question, else False")
    reason : str = Field(description="One short Sentence Explaining why Documents are Relevent or Irrelevent.")

def call_gemini(prompt:str, system_instruction:str, response_schema=None) -> str:
    config_args = {
        "system_instruction" : system_instruction,
        "temperature" : 0,
    }
    if response_schema:
        config_args["response_mime_type"] = "application/json"
        config_args["response_schema"] = response_schema

    for attempts in range (1, 4):
        try:
            response = client.models.generate_content(
                model= "gemini-3.5-flash-lite",
                contents= prompt,
                config=types.GenerateContentConfig(**config_args),
            )
            return response.text
        except Exception as e:
            if "503" in str(e) and attempts <3:
                print(f"[Server Busy (503), retrying in 3s... Attempt{attempts}/3]")
                time.sleep(3)
            else:
                raise


def grade_document(question:str, docs_text:str)-> GradeResult:
    system_prompt = (
        "Your are a strict Retrival relevance grader. Check whether the retrieved document"
        "contains direct information to answer the user's question. Be strict-if it is unrelated, set relevent=False."
        )
    user_prompt = f"User question: {question}\n\nRetrieved Document:\n{docs_text}"
    raw_json = call_gemini(prompt=user_prompt, system_instruction=system_prompt, response_schema=GradeResult)
    return GradeResult.model_validate_json(raw_json)


def rewrite_query(question:str)->str:
    system_prompt = (
        "You are a search query optimizer for an enterprise cloud & SaaS documentation database. "
        "Rewrite the user's question into concise technical keywords (e.g., 'SLA uptime service credits', "
        "'API rate limits RPM 429', 'GDPR data retention AES-256', 'P1 incident outage response'). "
        "Return ONLY the rewritten search query text."
    )
    return call_gemini(prompt=f"Original question{question}",system_instruction=system_prompt).strip()



def run_agentic_arg (question:str, max_retries: int=2)->str:
    print(f"\nUser question: '{question}'\n"+ "=" *60)
    current_query = question
    verified_docs   = []

    for attempts in range (1, max_retries + 1):
        print (f"[Search Attempts{attempts}/{max_retries}] Quering chromadb with: '{current_query}'")
        candidates = search_docs(current_query, n_results=2)

        for doc in candidates:
            grade = grade_document(question, doc["text"])
            status = "KEEP" if grade.relevent else "DROP"
            print(f"  -> [{status}] {doc['source']} ({grade.reason})")
            if grade.relevent and doc not in verified_docs:
                verified_docs.append(doc)
        if verified_docs:
            break

        if attempts < max_retries:
            current_query = rewrite_query(question)
            print(f"  [No Relevent Docs Found -> Rewrote query to: '{current_query}']")
            time.sleep(1)

    if not verified_docs:
        return "I cannot Find any verified information in the company documentation to answer that question"


    context = "\n\n".join([f"Source: {d["source"]}\nContent:{d["text"]}"for d in verified_docs])
    answer_system = (
        "You are an enterprise technical support assistant. Answer the user's question using ONLY the verified "
        "sources provided below. Always cite the exact document source name in brackets, e.g. [Source Name]."
    )

    answer_prompt = f"Verified Sources:\n{context}\n\nUser Question: {question}"
    return call_gemini(prompt=answer_prompt,system_instruction=answer_system)

        


if __name__ == "__main__":
    print("\n[Final Answer 1]:\n" + run_agentic_arg("What Happens if our Monthly uptime drop to 98.5%?"))
    print("\n[Final Answer 2]:\n" + run_agentic_arg("What Happens My app send too many request too fast?"))
    print("\n[Final Answer 3]:\n" + run_agentic_arg("What is the Office dress code policy?"))
