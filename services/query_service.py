from app.agents.rag_agent import call_agent


def process_query(request):
    """ receives query and json """
    user_query = request.get("question","")
    user_details = request.get("input_json",{})

    if not user_query:
        return {"status":"error","message": "No user query"}

    print("passing data to agent...")
    agent_respone = call_agent(user_query, customer_details= user_details)

    print("agent returned data...")
    return {"status":"success","answer": agent_respone}
