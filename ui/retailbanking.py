import streamlit as st
import requests
import json
import logging

# =====================================================
# RetailBanking AI Wealth Advisor Configuration
# =====================================================

APP_NAME = "RetailBanking_Personalized_Advisor"
API_URL = "http://localhost:8000/query"


# =====================================================
# Logging Configuration
# =====================================================

logging.basicConfig(
    filename="retailbanking_advisor.log",
    level=logging.INFO,
    format="%(asctime)s | RETAILBANKING | %(levelname)s | %(message)s",
)

logger = logging.getLogger("RetailBankingAdvisor")


# =====================================================
# Streamlit Page Setup
# =====================================================

st.set_page_config(
    page_title="RetailBanking AI Wealth Advisor", page_icon="◆", layout="wide"
)


# =====================================================
# UI Styling
# =====================================================

st.markdown(
    """
    <style>

    .stApp {
        background: linear-gradient(
            135deg,
            #f5f8fc,
            #eaf1f8
        );
    }

    .title {
        font-size: 42px;
        font-weight: 700;
        color: #0B2E4F;
        text-align: center;
        margin-bottom: 5px;
    }

    .subtitle {
        font-size: 18px;
        color: #526777;
        text-align: center;
        margin-bottom: 35px;
    }


    h3 {
        color: #0B2E4F;
        font-weight: 700;
    }


    textarea {
        border-radius: 12px !important;
        border: 1px solid #B7C9DA !important;
        background-color: white !important;
        font-size: 15px !important;
    }


    .stButton button {

        background: linear-gradient(
            90deg,
            #0B2E4F,
            #1F6F9F
        );

        color:white;

        border-radius:10px;

        height:45px;

        font-size:16px;

        font-weight:600;

        width:100%;

        border:none;

    }


    .stButton button:hover {

        background: linear-gradient(
            90deg,
            #1F6F9F,
            #0B2E4F
        );

    }


    .result {

        background:white;

        padding:25px;

        border-radius:15px;

        border-left:6px solid #1F6F9F;

        box-shadow:
        0px 5px 18px rgba(0,0,0,0.08);

    }


    </style>
    """,
    unsafe_allow_html=True,
)


# =====================================================
# Header
# =====================================================

st.markdown(
    "<div class='title'>RetailBanking AI Wealth Advisor</div>", unsafe_allow_html=True
)

st.markdown(
    """
    <div class='subtitle'>
    Intelligent customer-focused financial advisory powered by AI, 
    retrieval intelligence, and personalized recommendations.
    </div>
    """,
    unsafe_allow_html=True,
)


logger.info("RetailBanking Advisor application started")


# =====================================================
# Input Section
# =====================================================

left, right = st.columns([1, 1], gap="large")


with left:

    st.markdown("### Customer Profile")

    customer_profile = st.text_area(
        "Customer JSON Input",
        placeholder="Paste customer profile JSON here...",
        height=350,
    )


with right:

    st.markdown("### Customer Financial Query")

    question = st.text_area(
        "Query", placeholder="Enter customer financial question...", height=200
    )


# =====================================================
# Recommendation Request
# =====================================================

st.write("")


if st.button("Generate Personalized Recommendation"):

    logger.info("RetailBanking recommendation request initiated")

    if not customer_profile.strip():

        st.warning("Please provide customer profile JSON.")

        logger.warning("Request rejected - missing customer profile")

        st.stop()

    if not question.strip():

        st.warning("Please enter customer financial query.")

        logger.warning("Request rejected - missing query")

        st.stop()

    try:

        profile = json.loads(customer_profile)

        payload = {
            "application": APP_NAME,
            "customer_profile": profile,
            "question": question,
        }

        logger.info(
            "Sending RetailBanking request for customer: %s",
            profile.get("customer_id", "UNKNOWN"),
        )

        with st.spinner("Generating personalized financial recommendation..."):

            response = requests.post(API_URL, json=payload, timeout=120)

        if response.status_code == 200:

            logger.info("Recommendation generated successfully")

            st.markdown("### Advisory Recommendation")

            st.markdown("<div class='result'>", unsafe_allow_html=True)

            result = response.json()

            st.write(result)

            st.markdown("</div>", unsafe_allow_html=True)

        else:

            logger.error("API failure: %s", response.status_code)

            st.error("RetailBanking service unavailable.")

            st.write(response.text)

    except json.JSONDecodeError:

        logger.error("Invalid customer JSON")

        st.error("Customer profile JSON is invalid.")

    except requests.exceptions.ConnectionError:

        logger.error("FastAPI connection failed")

        st.error("Unable to connect to RetailBanking Advisor API.")

    except Exception as e:

        logger.exception("Unexpected error")

        st.error(str(e))
