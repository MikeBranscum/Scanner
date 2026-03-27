import cv2
import pytesseract
import gspread
import streamlit as st
from oauth2client.service_account import ServiceAccountCredentials
import numpy as np
from PIL import Image

# 1. SETUP GOOGLE SHEETS (Using Streamlit Cloud Secrets)
def sync_to_sheets(card_name, category, price):
    # Define the scope for Google Sheets and Drive
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    
    # Pull credentials directly from your Streamlit Cloud "Secrets" TOML
    creds_dict = st.secrets["gcp_service_account"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    
    # Authorize and open the specific sheet
    client = gspread.authorize(creds)
    
    try:
        # Opens your existing "Mikey's Database"
        sheet = client.open("Mikey's Database").sheet1
        
        # Appends to your columns: id (blank), name, category, price
        # This matches the headers you already have in that sheet
        sheet.append_row(["", card_name, category, price])
        return True
    except Exception as e:
        st.error(f"Sheet Error: {e}")
        return False

# 2. IMAGE PROCESSING & OCR
def scan_card(image):
    # Convert Streamlit/PIL image to OpenCV format
    img = np.array(image.convert('RGB'))
    
    # Crop to the top 15% of the image (where the Name usually is)
    height, width, _ = img.shape
    roi = img[0:int(height*0.15), 0:width] 
    
    # Pre-process for better OCR (Grayscale -> Threshold)
    gray = cv2.cvtColor(roi, cv2.COLOR_RGB2GRAY)
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
    
    # Extract text
    text = pytesseract.image_to_string(thresh)
    return text.strip()

# 3. STREAMLIT UI (Mobile Friendly)
st.set_page_config(page_title="Mikey's Collector Scanner", page_icon="🎴")
st.title("🎴 Mikey's Collector Scanner")
st.write("Snap a photo to update **Mikey's Database**.")

# This triggers the native camera on your iPhone or Android
uploaded_file = st.camera_input("Scan Card or Memorabilia")

if uploaded_file:
    img = Image.open(uploaded_file)
    
    with st.spinner('Analyzing image...'):
        detected_name = scan_card(img)
    
    # Verification Section
    st.divider()
    card_name = st.text_input("Confirm Name", value=detected_name)
    category = st.selectbox("Category", ["Pokemon", "Sports Memorabilia", "Figures", "Glass"])
    price = st.text_input("Estimated Value (USD)", value="0.00")
    
    if st.button("🚀 Upload to Mikey's Database"):
        if sync_to_sheets(card_name, category, price):
            st.balloons()
            st.success(f"Successfully added '{card_name}' to your sheet!")
