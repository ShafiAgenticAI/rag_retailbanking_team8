import json
import requests
import streamlit as ui
import uuid

# ==========================================================
# Application Configuration
# ==========================================================

SERVER_URL = "http://127.0.0.1:8000"

DOCUMENT_UPLOAD_ENDPOINT = f"{SERVER_URL}/api/v1/upload/"
COMPLIANCE_QUERY_ENDPOINT = f"{SERVER_URL}/api/v1/query"


# ==========================================================
# Streamlit Configuration
# ==========================================================

ui.set_page_config(
    page_title="Retail Banking Intelligence",
    page_icon="🏦",
    layout="wide",
)


ui.title("🏦 Retail Banking Intelligence")

ui.caption(
    "AI-powered banking assistant using customer profile and knowledge documents."
)


# ==========================================================
# Session State
# ==========================================================
if "session_id" not in ui.session_state:
    ui.session_state.session_id = str(uuid.uuid4())

if "chat_history" not in ui.session_state:
    ui.session_state.chat_history = []


# ==========================================================
# Backend Calls
# ==========================================================


def send_compliance_question(question, customer_details):

    payload = {
        "question": question,
        "customer_details": customer_details,
        "session_id": ui.session_state.session_id,
    }

    return requests.post(
        COMPLIANCE_QUERY_ENDPOINT,
        json=payload,
        timeout=120,
    )


def upload_document(document):

    files = {
        "file": (
            document.name,
            document,
            "application/pdf",
        )
    }

    return requests.post(
        DOCUMENT_UPLOAD_ENDPOINT,
        files=files,
        timeout=120,
    )


# ==========================================================
# Helper Functions
# ==========================================================


def extract_json_context(text):

    if not text.strip():
        return None

    try:
        return json.loads(text)

    except json.JSONDecodeError:
        return None


def format_agent_response(response):
    """
    Convert JSON response into readable text.
    """

    if response is None:
        return "No response generated."

    # If backend sends JSON string
    if isinstance(response, str):

        try:
            response = json.loads(response)

        except Exception:
            return response

    # If backend sends dictionary
    if isinstance(response, dict):

        readable_text = ""

        for key, value in response.items():

            title = key.replace("_", " ").title()

            readable_text += f"### {title}\n"

            if isinstance(value, list):

                for item in value:
                    readable_text += f"- {item}\n"

            elif isinstance(value, dict):

                for k, v in value.items():

                    readable_text += f"**{k.replace('_',' ').title()}:** {v}\n\n"

            else:

                readable_text += f"{value}\n\n"

        return readable_text

    return str(response)


# ==========================================================
# Sidebar
# ==========================================================

with ui.sidebar:

    ui.header("📁 Knowledge Base")

    uploaded_file = ui.file_uploader(
        "Upload PDF",
        type=["pdf"],
    )

    if uploaded_file:

        if ui.button(
            "Process Document",
            use_container_width=True,
        ):

            with ui.spinner("Processing document..."):

                result = upload_document(uploaded_file)

                if result.ok:

                    ui.success("Document processed successfully.")

                else:

                    ui.error(result.text)

    ui.divider()

    if ui.button(
        "🗑 Clear Chat",
        use_container_width=True,
    ):

        ui.session_state.chat_history = []

        ui.session_state.session_id = str(uuid.uuid4())

        ui.rerun()


# ==========================================================
# Display Previous Chat
# ==========================================================

for message in ui.session_state.chat_history:

    with ui.chat_message(message["role"]):

        ui.markdown(message["message"])


# ==========================================================
# Customer Details Input
# ==========================================================

ui.subheader("Customer Profile (Optional)")


customer_json = ui.text_area(
    "Enter customer JSON",
    height=220,
    placeholder="""
{
    "customer_id":"CUST001",
    "age":40,
    "income":1200000,
    "employment":"Salaried",
    "risk_appetite":"Moderate"
}
""",
)


customer_details = extract_json_context(customer_json)


if customer_json.strip():

    if customer_details:

        ui.success("Customer profile loaded.")

    else:

        ui.error("Invalid JSON format.")


# ==========================================================
# Chat Input
# ==========================================================

question = ui.chat_input("Ask your question...")


if question:

    ui.session_state.chat_history.append(
        {
            "role": "user",
            "message": question,
        }
    )

    with ui.chat_message("user"):

        ui.markdown(question)

    with ui.chat_message("assistant"):

        with ui.spinner("Analyzing..."):

            try:

                response = send_compliance_question(
                    question,
                    customer_details,
                )

                if response.ok:

                    api_response = response.json()

                    # query_service returns:
                    #
                    # {
                    #    "status":"success",
                    #    "answer":{}
                    # }

                    answer = api_response.get("answer", {})

                    # ======================================
                    # Display Agent Response ONLY
                    # ======================================

                    agent_response = answer.get(
                        "output_response", "No response generated."
                    )

                    formatted_response = format_agent_response(agent_response)

                    ui.markdown(formatted_response)

                    # ======================================
                    # Customer Details Dropdown
                    # ======================================

                    customer = answer.get("customer_details")
                    print("customer", customer)
                    if customer and customer != "None":

                        with ui.expander("👤 Customer Details"):

                            if isinstance(customer, dict):

                                ui.json(customer)

                            else:

                                ui.write(customer)

                    # ======================================
                    # Retrieved Chunks Dropdown
                    # ======================================

                    chunks = answer.get("retrieved_chunks", [])

                    if chunks:

                        with ui.expander("📚 Supporting References"):

                            for index, chunk in enumerate(chunks, start=1):

                                metadata = chunk.get("metadata", {})

                                ui.markdown(f"### Reference {index}")

                                ui.write(
                                    f"**Document:** {metadata.get('file_name','-')}"
                                )

                                ui.write(f"**Page:** {metadata.get('page_number','-')}")

                                ui.write(
                                    f"**Type:** {metadata.get('file_extension','-')}"
                                )

                                ui.divider()

                                ui.write(chunk.get("content", "No content available."))

                    ui.session_state.chat_history.append(
                        {
                            "role": "assistant",
                            "message": formatted_response,
                        }
                    )

                else:

                    ui.error(f"Request failed: {response.status_code}")

                    ui.code(response.text)

            except Exception as error:

                ui.error(f"Error: {error}")
