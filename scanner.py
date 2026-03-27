import cv2
import pytesseract
import gspread
import streamlit as st
from oauth2client.service_account import ServiceAccountCredentials
import numpy as np
from PIL import Image

# 1. SETUP GOOGLE SHEETS (Connected to "Mikey's Database")
def sync_to_sheets(card_name, category, price):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)
    client = gspread.authorize(creds)
    
    # Matching your exact sheet name
    sheet = client.open("Mikey's Database").sheet1
    
    # Appending to your columns: id (empty for now), name, category, price
    sheet.append_row(["", card_name, category, price])

# 2. IMAGE PROCESSING
def scan_card(image):
    img = np.array(image.convert('RGB'))
    
    # Focus on the top 15% of the card where the name is
    height, width, _ = img.shape
    roi = img[0:int(height*0.15), 0:width] 
    
    gray = cv2.cvtColor(roi, cv2.COLOR_RGB2GRAY)
    text = pytesseract.image_to_string(gray)
    return text.strip()

# 3. STREAMLIT UI
st.set_page_config(page_title="Mikey's Collector Scanner")
st.title("🎴 Mikey's TCG & Collectible Scanner")

uploaded_file = st.camera_input("Scan your card") # This uses your webcam/phone camera!

if uploaded_file:
    img = Image.open(uploaded_file)
    
    with st.spinner('Reading card...'):
        detected_name = scan_card(img)
    
    # Manual Entry/Verification
    card_name = st.text_input("Confirm Card Name", value=detected_name)
    category = st.selectbox("Category", ["Pokemon", "Sports Memorabilia", "Figures", "Glass"])
    price = st.text_input("Estimated Price (USD)", value="0.00")
    
    if st.button("🚀 Upload to Mikey's Database"):
        sync_to_sheets(card_name, category, price)
        st.success(f"Added {card_name} to your Google Sheet!")