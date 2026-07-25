from rag_retailbanking_team8.agents.rag_agent import call_agent
import json


def process_query(request):
    """Receives query and json and returns plain text content."""
    user_query = request.get("question", "")
    user_details = request.get("input_json", {})

    if not user_query:
        return "No user query"

    normalized_query = user_query.strip().lower()
    if normalized_query in {
        "hi",
        "hello",
        "hey",
        "hiya",
        "good morning",
        "good afternoon",
        "good evening",
    }:
        return "Hello! How can I assist you today?"

    print("passing data to agent...")
    agent_response = call_agent(user_query, customer_details=user_details)

    if isinstance(agent_response, dict) and agent_response.get("status") == "error":
        return agent_response.get("message", "Agent failed to provide a response.")

    print("agent returned data...")
    if isinstance(agent_response, str):
        return agent_response

    try:
        if hasattr(agent_response, "model_dump"):
            agent_response = agent_response.model_dump()
        if isinstance(agent_response, dict):
            answer = agent_response.get("output_response") or agent_response.get(
                "answer"
            )
            if answer:
                return str(answer)
            return json.dumps(agent_response, indent=2)
        return str(agent_response)
    except Exception as e:
        return f"Failed to format agent response: {e}"
