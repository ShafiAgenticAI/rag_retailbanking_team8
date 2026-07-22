import json
import requests
import streamlit as ui

# ==========================================================
# Application Configuration
# ==========================================================

SERVER_URL = "http://127.0.0.1:8000"

DOCUMENT_UPLOAD_ENDPOINT = f"{SERVER_URL}/api/v1/upload/"
COMPLIANCE_QUERY_ENDPOINT = f"{SERVER_URL}/api/v1/query"


# ==========================================================
# Streamlit Page Setup
# ==========================================================

ui.set_page_config(
    page_title="Retail Banking Compliance Intelligence",
    page_icon="🏦",
    layout="wide",
)


ui.title("🏦 Retail Banking Compliance Intelligence")

ui.caption(
    "Review document with Json details provide, "
    " receive suggested compliance insights from AI."
)


# ==========================================================
# Session Initialization
# ==========================================================

if "chat_history" not in ui.session_state:
    ui.session_state.chat_history = []


# ==========================================================
# Backend Communication Functions
# ==========================================================


def send_compliance_question(question, context):
    """
    Submit compliance question and optional context to backend.
    """

    request_body = {
        "question": question,
        "input_json": context,
    }

    return requests.post(
        COMPLIANCE_QUERY_ENDPOINT,
        json=request_body,
    )


def upload_document(document):
    """
    Upload regulatory document for processing.
    """

    upload_payload = {
        "file": (
            document.name,
            document,
            "application/pdf",
        )
    }

    return requests.post(
        DOCUMENT_UPLOAD_ENDPOINT,
        files=upload_payload,
    )


# ==========================================================
# Data Processing Helpers
# ==========================================================


def extract_json_context(raw_text):
    """
    Convert user-provided JSON text into Python object.
    """

    if not raw_text.strip():
        return None

    try:
        return json.loads(raw_text)

    except json.JSONDecodeError:
        return None


def show_document_reference(reference, number):
    """
    Render source document details and extracted content.
    """

    document_name = reference.get(
        "file_name",
        "Unnamed Document",
    )

    with ui.expander(f"📄 Reference {number}: {document_name}"):

        details = {
            "Document": reference.get("file_name"),
            "Reference ID": reference.get("document_id"),
            "Page": reference.get("page_number"),
            "Section": reference.get("section_number"),
            "Category": reference.get("regulation_type"),
            "Search Approach": reference.get("retrieval_method"),
            "Semantic Match Score": reference.get("vector_score"),
            "Keyword Match Score": reference.get("fts_score"),
            "Combined Score": reference.get("hybrid_score"),
        }

        ui.markdown("#### 📋 Document Details")

        ui.json(details)

        ui.markdown("#### 📝 Extracted Content")

        ui.info(
            reference.get(
                "snippet",
                "No relevant text available.",
            )
        )


# ==========================================================
# Document Upload Panel
# ==========================================================

with ui.sidebar:

    ui.header("📁 Retail Banking Knowledge base")

    uploaded_file = ui.file_uploader(
        "Choose PDF file",
        type=["pdf"],
    )

    if uploaded_file:

        if ui.button(
            "⬆️ Process Document",
            use_container_width=True,
        ):

            with ui.spinner("Preparing document for analysis..."):

                upload_result = upload_document(uploaded_file)

                if upload_result.ok:

                    ui.success("Document processed and added to the knowledge base.")

                else:

                    ui.error(upload_result.text)


# ==========================================================
# Previous Conversation Display
# ==========================================================

for message in ui.session_state.chat_history:

    with ui.chat_message(message["role"]):

        ui.markdown(message["message"])


# ==========================================================
# Optional Structured Context
# ==========================================================

ui.markdown("###### 📑 JSON Context (Optional)")


json_text = ui.text_area(
    "Enter structured information",
    height=100,
    placeholder="""
{
    "organization": "Retail Banking",
    "assessment_type": "Regulatory Review",
    "priority": "High"
}
""",
)


structured_context = extract_json_context(json_text)


if json_text.strip():

    if structured_context is None:

        ui.warning("⚠️ The JSON format is not valid. Please review the structure.")

    else:

        ui.success("✅ Structured context accepted.")


# ==========================================================
# Compliance Conversation
# ==========================================================

user_question = ui.chat_input("Enter your query...")


if user_question:

    ui.session_state.chat_history.append(
        {
            "role": "user",
            "message": user_question,
        }
    )

    with ui.chat_message(
        "user",
        avatar="👤",
    ):

        ui.markdown(user_question)

    with ui.chat_message(
        "assistant",
        avatar="🤖",
    ):

        with ui.spinner(" Json information Review..."):

            response = send_compliance_question(
                user_question,
                structured_context,
            )

            if response.ok:

                response_data = response.json()

                assistant_reply = response_data.get(
                    "answer",
                    "Unable to generate a response.",
                )

                ui.markdown(assistant_reply)

                supporting_documents = response_data.get(
                    "sources",
                    [],
                )

                if supporting_documents:

                    ui.markdown("### 📚 Regulatory References")

                    for position, document in enumerate(
                        supporting_documents,
                        start=1,
                    ):

                        show_document_reference(
                            document,
                            position,
                        )

                ui.session_state.chat_history.append(
                    {
                        "role": "assistant",
                        "message": assistant_reply,
                    }
                )

            else:

                ui.error(f"Unable to complete request ({response.status_code})")

                ui.code(response.text)
