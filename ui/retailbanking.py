import streamlit as st
import requests
import json
import logging

# =====================================================
# Configuration
# =====================================================

APP_NAME = "RetailBanking_Personalized_Advisor"

QUERY_API = "http://localhost:8000/query"

UPLOAD_API = "http://localhost:8000/upload"


# =====================================================
# Logging
# =====================================================

logging.basicConfig(
    filename="retailbanking_advisor.log",
    level=logging.INFO,
    format="%(asctime)s | RETAILBANKING | %(levelname)s | %(message)s",
)

logger = logging.getLogger("RetailBankingAdvisor")


# =====================================================
# Streamlit Configuration
# =====================================================

st.set_page_config(
    page_title="RetailBanking AI Wealth Advisor", page_icon="💬", layout="wide"
)


# =====================================================
# Load CSS
# =====================================================


def load_css(file):

    try:

        with open(file) as f:

            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    except Exception:

        logger.warning("CSS file not found")


load_css("styles.css")


# =====================================================
# Session State
# =====================================================

if "cancel_request" not in st.session_state:

    st.session_state.cancel_request = False


# =====================================================
# Sidebar Navigation
# =====================================================

page = st.sidebar.radio("Navigation", ["AI Advisor", "PDF Knowledge Upload"])


# =====================================================
# PDF Upload Page
# =====================================================

if page == "PDF Knowledge Upload":

    st.markdown("<div class='title'>PDF Knowledge Upload</div>", unsafe_allow_html=True)

    st.markdown(
        """
        <div class="subtitle">
        Upload PDF documents for advisor knowledge enrichment
        </div>
        """,
        unsafe_allow_html=True,
    )

    uploaded_files = st.file_uploader(
        "Upload PDF Documents", type=["pdf"], accept_multiple_files=True
    )

    if st.button("Upload PDF", use_container_width=False):

        if not uploaded_files:

            st.warning("Please select PDF file(s)")

            st.stop()

        files = []

        for file in uploaded_files:

            files.append(("files", (file.name, file.getvalue(), "application/pdf")))

        try:

            with st.spinner("Uploading documents..."):

                response = requests.post(UPLOAD_API, files=files, timeout=300)

            if response.status_code == 200:

                st.success("PDF uploaded successfully")

                try:

                    st.json(response.json())

                except:

                    st.write(response.text)

            else:

                st.error(response.text)

        except requests.exceptions.ConnectionError:

            st.error("Unable to connect to upload service")

        except Exception as e:

            st.error(str(e))


# =====================================================
# AI Advisor Chat Page
# =====================================================

else:

    st.markdown(
        "<div class='title'>RetailBanking AI Wealth Advisor</div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="subtitle">
        Your intelligent financial advisory assistant
        </div>
        """,
        unsafe_allow_html=True,
    )

    # =================================================
    # Small Customer Context
    # =================================================

    customer_profile = st.text_area(
        "Customer Context (Optional)",
        placeholder='{"customer_id":"123","age":35}',
        height=55,
    )

    # =================================================
    # Retailbanking Style Question Box
    # =================================================

    question = st.text_area(
        "Query", placeholder="Ask your financial question here...", height=220
    )

    col1, col2 = st.columns([5, 1])

    with col1:

        Advise = st.button("Advise", use_container_width=True)

    with col2:

        stop = st.button("Stop", use_container_width=True)

    if stop:

        st.session_state.cancel_request = True

        st.warning("Request stopped")

    if Advise:

        st.session_state.cancel_request = False

        if not question.strip():

            st.warning("Please enter your question")

            st.stop()

        profile = None

        if customer_profile.strip():

            try:

                profile = json.loads(customer_profile)

            except:

                st.error("Customer JSON is invalid")

                st.stop()

        payload = {
            "application": APP_NAME,
            "customer_profile": profile,
            "question": question,
        }

        logger.info("Query submitted")

        try:

            with st.spinner("Generating response..."):

                response = requests.post(QUERY_API, json=payload, timeout=300)

            if st.session_state.cancel_request:

                st.info("Request cancelled")

                st.stop()

            if response.status_code == 200:

                result = response.json()

                st.markdown("### AI Recommendation")

                st.markdown("<div class='result'>", unsafe_allow_html=True)

                if isinstance(result, dict):

                    if "answer" in result:

                        st.markdown(result["answer"])

                    elif "response" in result:

                        st.markdown(result["response"])

                    elif "recommendation" in result:

                        st.markdown(result["recommendation"])

                    else:

                        st.json(result)

                else:

                    st.write(result)

                st.markdown("</div>", unsafe_allow_html=True)

                logger.info("Response generated successfully")

            else:

                st.error("Advisor API error")

                st.write(response.text)

        except requests.exceptions.ConnectionError:

            st.error("Unable to connect to advisor service")

        except Exception as e:

            logger.exception("Unexpected error")

            st.error(str(e))
