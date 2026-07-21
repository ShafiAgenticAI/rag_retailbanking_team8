from langchain.agents import create_agent
from dotenv import load_dotenv
from app.tools.tools import _search_vector, _search_fts, _search_hybrid
from pydantic import BaseModel, Field
from typing import List

# load env variables
load_dotenv()

class Citation(BaseModel):
    source: str
    page: str

class Recommendation(BaseModel):
    title: str
    description: str
    priority: str

class RiskAssessment(BaseModel):
    risk_level: str
    explanation: str

class FinancialAdvice(BaseModel):
    summary: str = Field(description="Short summary of customer's financial situation")
    financial_health: str = Field(description="Assessment of the customer's current financial health")
    strengths: List[str]
    concerns: List[str]
    recommendations: List[Recommendation]
    risk_assessment: RiskAssessment
    reasoning: str = Field(description="Why these recommendation were given")
    citations: List[Citation]

def create_rag_agent():
    financial_agent = create_agent(
        model="openai:gpt-5.5",  # brain
        tools=[_search_vector, _search_fts, _search_hybrid],  # register tool
        response_format=FinancialAdvice,
        system_prompt=""" 
            You are an intelligent Customer 360 Financial Advisor. 

            You have access to three retrieval tools:
            1. _search_vector - use for semantic questions.
            2. _search_fts - use for keyword based questions.
            3. _search_hybrid - use when both semantic understanding and exact keyword matching are important.

            rules:
            - always choose exactly one search tool.
            - always pass:
            query = user's question
            k=5
            collection_name="retailbanking_knowledge_base"
             
            The retrieved context contains financial FAQs.

            You will also receive customer financial information in json.

            Your job is to:

            1. Retrieve relevant FAQ information using one search tool.
            2. Analyze the customer's financial profile.
            3. Combine both sources of information.
            4. Provide practical, personalized financial advice.
            5. If the retreived FAQ does not contain enough information, state that clearly instead of inventing facts.
            6. At the end of your response include citation section listing the metadata of every document used.
            7. Do not fabricate  citations, only cite metadata returned by the retrieval tool.

            Do not accept any other requests.
            """,  # role
    )
    return financial_agent

def call_agent(question, customer_details):
    agent = create_rag_agent()

    response = agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": f"""
                    User question: {question}
                    Customer financial details in json :{customer_details}
                    
                    """,
                }
            ]
        }
    )

    return response["structured_response"]

question = """Should I invest in FD or debt funds for buying a car in 2 years?"""

customer_details = {
    "customer_id": "CUST001",
    "age": 40,
    "income": 1200000,
    "employment": "Salaried",
    "risk_appetite": "Moderate",
    "goals": [{"goal": "Car Purchase", "target_amount": 1000000, "years": 2}],
    "existing_investments": {"equity": 300000, "debt": 200000, "fd": 100000},
    "liabilities": {"home_loan": 2000000},
    "monthly_expenses": 50000,
    "credit_score": 750,
}

res = call_agent(question, customer_details)   # call agent
print(res)
# print(response["messages"][-1].text)
# print(news.model_dump_json(indent=2))
# uv run python -m app.agents.rag_agent
