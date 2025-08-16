import streamlit as st
from PIL import Image
import pytesseract
from pdf2image import convert_from_bytes
import google.generativeai as genai
import datetime

# Set your Gemini API key here
genai.configure(api_key="AIzaSyD0fj_TemTvuk10TNmrmdxu1nPJ8j7SeuU")

# Windows users: set Tesseract OCR path if needed
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# App UI
st.set_page_config(page_title="Invoice Email Generator (Gemini)", page_icon="🧾")
st.title("🧾 Invoice Email Generator using Gemini AI")
st.write("Upload an invoice or enter details manually to generate a polite follow-up email.")

# Input Method
input_mode = st.radio("Choose Input Method", ["Upload Invoice", "Manual Entry"])

# Email Fields
st.subheader("📧 Email Details")
client_name = st.text_input("Client Name")
to_email = st.text_input("To Email ID")
email_subject = st.text_input("Email Subject", value="Reminder: Invoice Payment Due")
your_name = st.text_input("Your Name / Company")

# Manual Input
invoice_data = {}
if input_mode == "Manual Entry":
    st.subheader("📝 Invoice Info")
    invoice_data["invoice_number"] = st.text_input("Invoice Number")
    invoice_data["invoice_date"] = st.date_input("Invoice Date", datetime.date.today())
    invoice_data["due_date"] = st.date_input("Due Date", datetime.date.today())
    invoice_data["amount"] = st.text_input("Invoice Amount (₹)")

# Upload Invoice Option
elif input_mode == "Upload Invoice":
    file = st.file_uploader("Upload Invoice File (PDF or Image)", type=["pdf", "png", "jpg", "jpeg"])

    def extract_text(file):
        if file.type == "application/pdf":
            images = convert_from_bytes(file.read())
            return "".join([pytesseract.image_to_string(img) for img in images])
        else:
            image = Image.open(file)
            return pytesseract.image_to_string(image)

    if file:
        extracted_text = extract_text(file)
        st.text_area("Extracted Invoice Text", extracted_text, height=250)
        invoice_data["raw_text"] = extracted_text

# Generate Email
if st.button("📧 Generate Email"):
    with st.spinner("Generating email using Gemini..."):
        model = genai.GenerativeModel("gemini-1.5-flash")

        if input_mode == "Manual Entry":
            prompt = f"""
Generate a professional, polite email to remind a client about their unpaid invoice.

Client: {client_name}
To Email: {to_email}
Subject: {email_subject}
Invoice Number: {invoice_data['invoice_number']}
Invoice Date: {invoice_data['invoice_date']}
Due Date: {invoice_data['due_date']}
Amount: ₹{invoice_data['amount']}
Sender: {your_name}

Use a friendly and professional tone.
"""
        else:
            prompt = f"""
Using the extracted invoice text below, generate a polite and professional follow-up email to remind the client ({client_name}) at {to_email}.

Subject: {email_subject}
From: {your_name}

Invoice Text:
{invoice_data['raw_text']}
"""

        response = model.generate_content(prompt)
        generated_email = response.text

        st.subheader("📨 Generated Email")
        st.markdown(f"**To:** {to_email}")
        st.markdown(f"**Subject:** {email_subject}")
        st.text_area("Email Body", generated_email, height=300)
        st.success("Email generated successfully!")
