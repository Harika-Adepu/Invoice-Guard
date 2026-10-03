# 🛡️ InvoiceGuard AI

InvoiceGuard AI is an AI-powered invoice and expense analyzer built using Python, Streamlit, Gemini, and Twilio.

It allows users to upload an invoice or receipt image, extracts important information using Gemini Vision, and performs automated expense checks.

## 🚀 Features

- Upload invoice or receipt images
- Extract invoice details using Gemini Vision
- Identify vendor, invoice number, date, amount, items, and category
- Check expenses against predefined company policies
- Detect unusually high expenses
- Detect possible duplicate invoices
- Generate a final approval/review status
- Ask questions about the invoice using an AI assistant
- Download an invoice analysis report
- Send notifications through WhatsApp using Twilio

## 🔄 Workflow

Invoice Image
→ Gemini Vision
→ Structured Invoice Data
→ Policy Check
→ Anomaly Detection
→ Duplicate Detection
→ Final Assessment
→ AI Assistant / Report / WhatsApp

## 🛠️ Technologies Used

- Python
- Streamlit
- Google Gemini API
- NumPy
- Pandas
- Pillow
- Twilio WhatsApp API
- JSON

## 📁 Project Structure

InvoiceGuard-AI/
├── .streamlit/
│   └── secrets.toml
├── app.py
├── prompts.py
├── utils.py
├── requirements.txt
├── .gitignore
└── README.md

## 🧠 How It Works

### 1. Invoice Extraction

The user uploads an invoice image.

Gemini analyzes the image and extracts information such as:

- Vendor
- Invoice number
- Date
- Items
- Subtotal
- Tax
- Total
- Expense category

### 2. Policy Check

The application checks whether the invoice amount is within the configured spending limit for its category.

Example limits:

- Food → ₹1,500
- Travel → ₹5,000
- Software → ₹10,000
- Office Supplies → ₹3,000

If the amount exceeds the limit, the invoice is marked for review.

### 3. Anomaly Detection

The current invoice amount is compared with previous expense amounts to identify unusually high spending.

### 4. Duplicate Detection

The application checks the vendor, invoice number, and total amount against previously stored invoices to identify possible duplicates.

### 5. Final Assessment

The results of all checks are combined.

Possible results:

- APPROVED FOR PROCESSING
- REQUIRES MANUAL REVIEW

### 6. AI Assistant

Users can ask questions about the analyzed invoice.

Examples:

- What is the total amount?
- Why was this invoice flagged?
- Is this expense within the policy?
- What category does this invoice belong to?

### 7. Report

A text report containing the invoice details and analysis results can be downloaded.

### 8. WhatsApp

Twilio WhatsApp integration can be used to send an invoice notification using a WhatsApp Content Template.

## ⚙️ Installation

Clone the repository:

    git clone https://github.com/Harika-Adepu/Invoice-Guard
    cd Invoice-Guard

Create a virtual environment:

    python3 -m venv venv
    source venv/bin/activate

Install dependencies:

    pip install -r requirements.txt

## 🔑 API Keys

Create:

    .streamlit/secrets.toml

Add your API credentials:

    GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"

    TWILIO_ACCOUNT_SID = "YOUR_TWILIO_ACCOUNT_SID"
    TWILIO_AUTH_TOKEN = "YOUR_TWILIO_AUTH_TOKEN"
    TWILIO_WHATSAPP_NUMBER = "+14155238886"
    TWILIO_CONTENT_SID = "YOUR_CONTENT_SID"

Do not upload secrets.toml to GitHub.

## ▶️ Run the Application

    streamlit run app.py

The application will open in your browser.

## 🔐 Security

API keys and authentication tokens are stored in Streamlit secrets and should never be committed to GitHub.

The following file should be included in .gitignore:

    .streamlit/secrets.toml

