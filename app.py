import json
import hashlib

import streamlit as st
from google import genai
from google.genai import types


from prompts import (
    INVOICE_EXTRACTION_PROMPT,
    CHAT_PROMPT
)

from utils import (
    check_policy,
    detect_anomaly,
    check_duplicate,
    generate_final_status,
    send_whatsapp_message
)

# ==================================================
# PAGE CONFIGURATION
# ==================================================

st.set_page_config(
    page_title="InvoiceGuard AI",
    page_icon="🛡️",
    layout="wide"
)


# ==================================================
# APP TITLE
# ==================================================

st.title("🛡️ InvoiceGuard AI")
st.subheader("Intelligent Invoice & Expense Analyzer")


# ==================================================
# GEMINI SETUP
# ==================================================

api_key = st.secrets["GEMINI_API_KEY"]
modelname = "gemini-3.8-flash"

client = genai.Client(
    api_key=api_key
)

# ==================================================
# TWILIO WHATSAPP SETUP
# ==================================================

twilio_account_sid = st.secrets["TWILIO_ACCOUNT_SID"]
twilio_auth_token = st.secrets["TWILIO_AUTH_TOKEN"]
twilio_whatsapp_number = st.secrets["TWILIO_WHATSAPP_NUMBER"]

# ==================================================
# SESSION STATE INITIALIZATION
# ==================================================

# These values survive Streamlit reruns.

if "analysis_done" not in st.session_state:
    st.session_state.analysis_done = False

if "result" not in st.session_state:
    st.session_state.result = None

if "policy_result" not in st.session_state:
    st.session_state.policy_result = None

if "anomaly_result" not in st.session_state:
    st.session_state.anomaly_result = None

if "duplicate_result" not in st.session_state:
    st.session_state.duplicate_result = None

if "final_result" not in st.session_state:
    st.session_state.final_result = None

if "report" not in st.session_state:
    st.session_state.report = None

if "file_hash" not in st.session_state:
    st.session_state.file_hash = None


# ==================================================
# HISTORICAL DATA
# ==================================================

previous_amounts = [
    850,
    1100,
    950,
    1250,
    900
]


previous_invoices = [
    {
        "vendor": "ABC Travels",
        "invoice_number": "INV-1023",
        "total": 4500
    }
]


# ==================================================
# INVOICE UPLOAD
# ==================================================

uploaded_file = st.file_uploader(
    "Upload an invoice or receipt",
    type=[
        "jpg",
        "jpeg",
        "png",
        "webp"
    ]
)


# ==================================================
# DETECT NEW FILE
# ==================================================

if uploaded_file:

    # Create a unique fingerprint for the uploaded file
    current_file_hash = hashlib.md5(
        uploaded_file.getvalue()
    ).hexdigest()

    # If user uploads a different invoice,
    # clear the previous analysis.
    if (
        st.session_state.file_hash is not None
        and st.session_state.file_hash != current_file_hash
    ):

        st.session_state.analysis_done = False
        st.session_state.result = None
        st.session_state.policy_result = None
        st.session_state.anomaly_result = None
        st.session_state.duplicate_result = None
        st.session_state.final_result = None
        st.session_state.report = None

    st.session_state.file_hash = current_file_hash


    # ==================================================
    # SHOW UPLOADED IMAGE
    # ==================================================

    st.image(
        uploaded_file,
        caption="Uploaded Invoice",
        width=500
    )


    # ==================================================
    # ANALYZE BUTTON
    # ==================================================

    if st.button("🔍 Analyze Invoice"):

        with st.spinner("Analyzing invoice..."):

            try:

                # ------------------------------------------
                # READ IMAGE
                # ------------------------------------------

                image_bytes = uploaded_file.getvalue()


                # ------------------------------------------
                # CREATE GEMINI IMAGE PART
                # ------------------------------------------

                image_part = types.Part.from_bytes(
                    data=image_bytes,
                    mime_type=uploaded_file.type
                )


                # ------------------------------------------
                # SEND IMAGE TO GEMINI
                # ------------------------------------------

                response = client.models.generate_content(
                    model=modelname,
                    contents=[
                        INVOICE_EXTRACTION_PROMPT,
                        image_part
                    ]
                )

                # st.write("1. Sending image to Gemini...")

                # response = client.models.generate_content(
                #     model="gemini-3.8-flash",
                #     contents=[
                #         INVOICE_EXTRACTION_PROMPT,
                #         image_part
                #     ]
                # )

                # st.write("2. Gemini response received!")

                # response_text = response.text.strip()

                # st.write("3. Response parsed!")


                # ------------------------------------------
                # GET RESPONSE
                # ------------------------------------------

                response_text = response.text.strip()


                # ------------------------------------------
                # REMOVE JSON MARKDOWN FENCES
                # ------------------------------------------

                if response_text.startswith("```json"):

                    response_text = response_text[7:]

                elif response_text.startswith("```"):

                    response_text = response_text[3:]


                if response_text.endswith("```"):

                    response_text = response_text[:-3]


                response_text = response_text.strip()


                # ------------------------------------------
                # CONVERT JSON TO PYTHON DICTIONARY
                # ------------------------------------------

                result = json.loads(
                    response_text
                )


                # ------------------------------------------
                # VALIDATE REQUIRED FIELDS
                # ------------------------------------------

                required_fields = [
                    "vendor",
                    "invoice_number",
                    "date",
                    "total",
                    "category"
                ]


                missing_fields = [
                    field
                    for field in required_fields
                    if field not in result
                ]


                if missing_fields:

                    st.error(
                        "The invoice response is missing "
                        "required fields."
                    )

                    st.write(
                        "Missing fields:",
                        missing_fields
                    )

                    st.stop()


                # ------------------------------------------
                # INTELLIGENCE CHECKS
                # ------------------------------------------

                policy_result = check_policy(
                    result["category"],
                    result["total"]
                )


                anomaly_result = detect_anomaly(
                    result["total"],
                    previous_amounts
                )


                duplicate_result = check_duplicate(
                    result,
                    previous_invoices
                )


                final_result = generate_final_status(
                    policy_result,
                    anomaly_result,
                    duplicate_result
                )


                # ------------------------------------------
                # CREATE REPORT
                # ------------------------------------------

                report = f"""
InvoiceGuard AI Report
======================

Vendor: {result['vendor']}

Invoice Number: {result['invoice_number']}

Date: {result['date']}

Category: {result['category']}

Total: ₹{result['total']:,.2f}


Policy Check
------------
{policy_result['message']}


Anomaly Detection
-----------------
{anomaly_result['message']}


Duplicate Check
---------------
{duplicate_result['message']}


Final Status
------------
{final_result['status']}
"""


                # ==========================================
                # SAVE EVERYTHING IN SESSION STATE
                # ==========================================

                st.session_state.result = result

                st.session_state.policy_result = (
                    policy_result
                )

                st.session_state.anomaly_result = (
                    anomaly_result
                )

                st.session_state.duplicate_result = (
                    duplicate_result
                )

                st.session_state.final_result = (
                    final_result
                )

                st.session_state.report = report

                st.session_state.analysis_done = True


                st.success(
                    "Invoice analysis completed successfully!"
                )


            # ==============================================
            # JSON ERROR
            # ==============================================

            except json.JSONDecodeError:

                st.error(
                    "Gemini returned an unexpected response "
                    "instead of valid JSON."
                )

                st.write(
                    "Gemini response:"
                )

                st.code(
                    response_text
                )


            # ==============================================
            # OTHER ERROR
            # ==============================================

            except Exception as e:

                st.error(
                    "Unable to analyze the invoice."
                )

                st.write(
                    "Technical details:"
                )

                st.code(
                    str(e)
                )


# ==================================================
# DISPLAY ANALYSIS
# ==================================================

if st.session_state.analysis_done:

    result = st.session_state.result

    policy_result = (
        st.session_state.policy_result
    )

    anomaly_result = (
        st.session_state.anomaly_result
    )

    duplicate_result = (
        st.session_state.duplicate_result
    )

    final_result = (
        st.session_state.final_result
    )


    # ==================================================
    # INVOICE DETAILS
    # ==================================================

    st.divider()

    st.header("🧾 Invoice Details")


    col1, col2, col3 = st.columns(3)


    with col1:

        st.metric(
            "Vendor",
            result["vendor"]
        )


    with col2:

        st.metric(
            "Invoice Number",
            result["invoice_number"]
        )


    with col3:

        st.metric(
            "Total",
            f"₹{result['total']:,.2f}"
        )


    # ==================================================
    # ADDITIONAL INFORMATION
    # ==================================================

    col4, col5 = st.columns(2)


    with col4:

        st.write("### Date")

        st.write(
            result["date"]
        )


    with col5:

        st.write("### Category")

        st.info(
            result["category"]
        )


    # ==================================================
    # INTELLIGENCE
    # ==================================================

    st.divider()

    st.header("🧠 Intelligence")


    # --------------------------------------------------
    # POLICY CHECK
    # --------------------------------------------------

    if policy_result["status"] == "VIOLATION":

        st.error(
            f"⚠️ Policy Violation\n\n"
            f"{policy_result['message']}"
        )

    else:

        st.success(
            f"✓ Policy Check\n\n"
            f"{policy_result['message']}"
        )


    # --------------------------------------------------
    # ANOMALY CHECK
    # --------------------------------------------------

    if anomaly_result["is_anomaly"]:

        st.warning(
            f"🚨 Unusual Expense\n\n"
            f"{anomaly_result['message']}"
        )

    else:

        st.success(
            f"✓ Anomaly Check\n\n"
            f"{anomaly_result['message']}"
        )


    # --------------------------------------------------
    # DUPLICATE CHECK
    # --------------------------------------------------

    if duplicate_result["is_duplicate"]:

        st.error(
            f"🔄 Possible Duplicate\n\n"
            f"{duplicate_result['message']}"
        )

    else:

        st.success(
            "✓ No duplicate invoice detected."
        )


    # ==================================================
    # RAW EXTRACTED DATA
    # ==================================================

    with st.expander(
        "🔧 View Extracted Data"
    ):

        st.json(result)


    # ==================================================
    # FINAL ASSESSMENT
    # ==================================================

    st.divider()

    st.header("📋 Final Assessment")


    if final_result["status"] == "REQUIRES REVIEW":

        st.error(
            "⚠️ REQUIRES MANUAL REVIEW"
        )

        st.write("Reasons:")

        for issue in final_result["issues"]:

            st.write(
                f"- {issue}"
            )

    else:

        st.success(
            "✅ APPROVED FOR PROCESSING"
        )


    # ==================================================
    # AI EXPENSE ASSISTANT
    # ==================================================

    st.divider()

    st.header("💬 Ask InvoiceGuard AI")


    question = st.text_input(
        "Ask something about this invoice",
        key="invoice_question"
    )


    if question:

        with st.spinner("Thinking..."):

            try:

                chat_prompt = CHAT_PROMPT.format(
                    invoice=result,
                    policy=policy_result,
                    anomaly=anomaly_result,
                    duplicate=duplicate_result,
                    final_result=final_result
                )


                chat_response = (
                    client.models.generate_content(
                        model=modelname,
                        contents=[
                            chat_prompt,
                            f"\nUser question: {question}"
                        ]
                    )
                )


                st.markdown(
                    "### 🤖 InvoiceGuard AI"
                )

                st.write(
                    chat_response.text
                )


            except Exception as e:

                st.error(
                    "Unable to generate an AI response."
                )

                st.code(
                    str(e)
                )


    # ==================================================
    # DOWNLOAD REPORT
    # ==================================================

    st.divider()

    st.header("📄 Report")


    st.download_button(
        label="📥 Download Invoice Report",
        data=st.session_state.report,
        file_name="invoiceguard_report.txt",
        mime="text/plain",
        key="download_report"
    )

    # ==================================================
# WHATSAPP REPORT
# ==================================================

st.divider()

st.header("📱 Send Report to WhatsApp")

whatsapp_number = st.text_input(
    "Enter WhatsApp number",
    placeholder="+919876543210"
)

st.caption(
    "Use the international format, for example: "
    "+919876543210"
)


if st.button("📲 Send Report to WhatsApp"):

    if not whatsapp_number:

        st.warning(
            "Please enter a WhatsApp number."
        )

    else:

        try:

            with st.spinner(
                "Sending report to WhatsApp..."
            ):

                # Twilio requires:
                # whatsapp:+91XXXXXXXXXX

                if not whatsapp_number.startswith(
                    "whatsapp:"
                ):

                    whatsapp_to = (
                        f"whatsapp:{whatsapp_number}"
                    )

                else:

                    whatsapp_to = whatsapp_number


                # Create a WhatsApp-friendly report

                whatsapp_report = f"""
                    🛡️ *InvoiceGuard AI Report*

                    Vendor: {result['vendor']}

                    Invoice: {result['invoice_number']}

                    Date: {result['date']}

                    Category: {result['category']}

                    💰 Total: ₹{result['total']:,.2f}


                    🧠 *Intelligence*

                    Policy:
                    {policy_result['message']}

                    Anomaly:
                    {anomaly_result['message']}

                    Duplicate:
                    {duplicate_result['message']}


                    📋 *Final Status*

                    {final_result['status']}

                    — InvoiceGuard AI
                    """


                message_sid = send_whatsapp_message(
                    account_sid=twilio_account_sid,
                    auth_token=twilio_auth_token,
                    from_number=twilio_whatsapp_number,
                    to_number=whatsapp_to,
                    content_sid=st.secrets["TWILIO_CONTENT_SID"],
                    variables={
                        "1": result["date"],
                        "2": "10:00 AM"
                    }
                )


            st.success(
                "✅ Report sent successfully to WhatsApp!"
            )

            st.caption(
                f"Message ID: {message_sid}"
            )


        except Exception as e:

            st.error(
                "Unable to send the WhatsApp report."
            )

            st.code(
                str(e)
            )