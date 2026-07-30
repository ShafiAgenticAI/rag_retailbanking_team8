from rag_retailbanking_team8.agents.rag_agent import call_agent

def process_query(request):
    """ receives query and json """
    user_query = request.get("question","")
    customer_details = request.get("customer_details")
    session_id = request.get("session_id")

    if not user_query:
        return {"status":"error","message": "No user query"}

    print("Passing data to agent...")
    agent_respone = call_agent(user_query, customer_details=customer_details,session_id=session_id)

    print("Agent returned data...")
    return {"status":"success","answer": agent_respone}
