import streamlit as st
from PIL import Image
import pytesseract
import time
import os
import io
import base64
import logging
from langchain.prompts import PromptTemplate
from langchain_core.messages import HumanMessage
from langchain.chains import LLMChain
#from langchain_google_genai import GoogleGenerativeAI
from langchain_google_genai import ChatGoogleGenerativeAI
from gtts import gTTS

# ================================
# Configuration and Initialization
# ================================

# Set Tesseract OCR path
pytesseract.pytesseract.tesseract_cmd = r"/usr/bin/tesseract"

# Read the API key from a text file
# try:
#     with open("API Key.txt", "r") as f:
#         key = f.read().strip()
# except FileNotFoundError:
#     st.error("API Key file not found. Please provide a valid API Key.")
#     st.stop()

# Api Key from cloud
key = os.getenv("API Key")

# Initialize models through LangChain
llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro-latest", api_key=key)  
vision_llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro-latest", api_key=key)  

# Function to stream response data
# Scene Understanding
def stream_data(description):
    for word in description.split(" "):
        yield word + " "
        time.sleep(0.06)

# Text Extraction
def stream_data(text):
    for word in text.split(" "):
        yield word + " "
        time.sleep(0.06)

# ================================
# Helper Functions
# ================================

# Error handling function
def handle_error(error):
    logging.error(error)
    st.error(f"Error: {str(error)}")

# Scene understanding function
def scene_understanding(image):
    try:
        image_bytes = io.BytesIO()
        image.save(image_bytes, format='PNG')
        image_bytes = image_bytes.getvalue()

        message = HumanMessage(
            content=[
                {
                    "type": "text",
                    "text": """As an AI assistant for visually impaired individuals, provide a detailed description of this image.
                    Include:
                    1. Overall scene layout
                    2. Main objects and their positions
                    3. People and their activities (if any)
                    4. Colors and lighting
                    5. Notable features or points of 

                    Format the response in clear, easy-to-understand sections."""
                },
                {
                    "type": "image_url",
                    "image_url": f"data:image/png;base64,{base64.b64encode(image_bytes).decode()}"
                }
            ]
        )

        response = vision_llm.invoke([message])
        return response.content
    except Exception as e:
        handle_error(e)


# Text extraction function
def extract_and_process_text(image):
    try:
        extracted_text = pytesseract.image_to_string(image)

        if not extracted_text.strip():
            return "No text detected in the image."

        template = """
        Enhance and structure the following extracted text for a visually impaired person:
        TEXT: {text}

        Please:
        1. Correct obvious OCR errors
        2. Format text in clear sections
        3. Highlight important information
        4. Add relevant context
        5. Organize numbers, dates, and key details

        Return the text in a clear, well-structured format.
        """

        prompt = PromptTemplate(input_variables=["text"], template=template)
        chain = LLMChain(llm=llm, prompt=prompt)

        return chain.run({"text": extracted_text})
    except Exception as e:
        handle_error(e)

# Utility Functions
# Text to speech recognition
def text_to_speech(text):
    try:
        tts = gTTS(text=text, lang='en')
        mp3_fp = io.BytesIO()
        tts.write_to_fp(mp3_fp)
        mp3_fp.seek(0)
        return mp3_fp.getvalue()
    except Exception as e:
        handle_error(e)

# ================================
# Streamlit App Layout and Logic
# ================================        

# Streamlit App Configuration
st.set_page_config(page_title="AI Vision Companion", layout="wide", page_icon="🤖")
st.markdown(
    """
    <style>
    body {
        background-color: #f4f4f4;
        font-family: 'Arial', sans-serif;
    }
    .main-title {
        font-size: 50px;
        font-weight: 700;
        text-align: center;
        color: #2c3e50;
        margin: 20px 0;
    }
    .subtitle {
        font-size: 18px;
        text-align: center;
        color: #7f8c8d;
        margin-bottom: 30px;
    }
    .feature-header {
        font-size: 24px;
        color: #34495e;
        font-weight: bold;
        margin-top: 30px;
    }
    .sidebar-section {
        font-size: 16px;
        color: #2c3e50;
    }
    footer {
        text-align: center;
        padding: 10px;
        font-size: 14px;
        color: #7f8c8d;
        border-top: 1px solid #ddd;
        margin-top: 30px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="main-title">Vision360 🔬</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Empowering Accessibility through AI - Scene Insights, Text Recognition, and Speech Conversion</div>', unsafe_allow_html=True)

# Sidebar Configuration
logo_path = r"C:\Users\rjsek\OneDrive\Documents\Work and Professional documents\Innomatics Research Labs\Data Science Internship Sep 2024\Tasks\Gen AI App for Visually Impaired People - Final Project\logo.png"
if os.path.exists(logo_path):
    st.sidebar.image(logo_path, width=300)
else:
    st.sidebar.warning("Logo file not found. Please ensure 'logo.png' is in the app directory.")

st.sidebar.title("ℹ️ About")
st.sidebar.markdown(
    """
        💡 **Purpose**:
    - **Enhancing accessibility for visually impaired users by combining AI technologies.**

    📌 **Features**:
    - **Visual Insights**: Get an AI-generated description of the uploaded image.
    - **Text Extraction**: Detect and extract textual content from images.
    - **Speech Conversion**: Convert extracted text into speech for audio playback.

    🤖 **Powered by**:
    - Google Gemini 1.5 Turbo API for image scene insights.
    - Tesseract OCR for text extraction.
    - gTTS for speech synthesis.
    """
)

st.sidebar.text_area("🔜 Instructions", "1. Upload an image. \n2. Select an option to process the image for AI assistance!")

# File Upload Section
st.markdown("<h3 class='feature-header'>🗣️ Upload an Image</h3>", unsafe_allow_html=True)
uploaded_file = st.file_uploader("Drag and drop or browse an image (JPG, JPEG, PNG)", type=["jpg", "jpeg", "png"])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", use_container_width=True)

# Feature Buttons
st.markdown("<h3 class='feature-header'>⚙️ Features</h3>", unsafe_allow_html=True)
col1, col2, col3 = st.columns(3)

scene_button = col1.button("🔍 Describe Scene")
ocr_button = col2.button("🖋️ Extract Text")
tts_button = col3.button("🔊 Convert to Speech")

if uploaded_file:
    try:
        if scene_button:
            with st.spinner("Analyzing the image..."):
                description = scene_understanding(image)
                st.markdown("<h3 class='feature-header'>🔍 Scene Description</h3>", unsafe_allow_html=True)
                st.write("AI-Generated Scene Insights :")
                st.write(stream_data(description))
                audio_bytes = text_to_speech(description)
                st.audio(audio_bytes, format='audio/mp3')

        if ocr_button:
            with st.spinner("Extracting text from the image..."):
                text = extract_and_process_text(image)
                if text:
                    st.markdown("<h3 class='feature-header'>🖋️ Extracted Text</h3>", unsafe_allow_html=True)
                    st.write("Text from Image :")
                    st.write(stream_data(text))
                else:
                    st.warning("No text detected in the image.")

        if tts_button:
            with st.spinner("Processing speech synthesis..."):
                text = extract_and_process_text(image)
                audio_bytes = text_to_speech(text)
                st.markdown("<h3 class='feature-header'>🔊 Text to Speech</h3>", unsafe_allow_html=True)
                st.audio(audio_bytes, format='audio/mp3')
    except Exception as e:
        handle_error(e)

# App Footer
# Footer
st.markdown(
    """
    <footer>
        <p>© 2024 <strong>Vision360 🔬</strong> | Powered by <strong>Google Generative AI</strong> | Built with <strong>Streamlit</strong> | Designed by <strong>Raja Sekhar Rapaka</strong></p>
    </footer>
    """,
    unsafe_allow_html=True,
)

# Note: Uncomment the line below to run the Streamlit app
# streamlit run app.py
