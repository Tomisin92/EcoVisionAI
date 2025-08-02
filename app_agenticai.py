# app.py

import streamlit as st
import cv2
import numpy as np
from PIL import Image
import base64
import io
import os
from openai import OpenAI
import json
from datetime import datetime

# --- API key handling for the runtime environment ---
# The API key is not loaded from a .env file but is provided by the canvas environment.
# We set it to the environment variable here for the OpenAI client to pick it up.
# For local development, you would uncomment `load_dotenv()` and have a .env file.
# from dotenv import load_dotenv
# load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY", "")

# Page config
st.set_page_config(
    page_title="EcoVision AI",
    page_icon="🌍",
    layout="wide", # Changed to wide layout
    initial_sidebar_state="expanded" # Set to expanded for better visibility of sidebar content
)

# Initialize OpenAI client
try:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        st.error("⚠️ OPENAI_API_KEY not found in environment variables!")
        # We use st.info instead of st.stop() to allow the UI to load
        st.info("Please provide your OpenAI API key in the environment variables.")
        # We can stop the app logic from proceeding further by returning early
        def main():
            st.warning("Application halted due to missing API key.")
        if __name__ == "__main__":
            main()
        exit() # Exit the script
    client = OpenAI(api_key=api_key)
except Exception as e:
    st.error(f"❌ Error initializing OpenAI client: {e}")
    exit()

# Custom CSS for ChatGPT-style interface and sidebar
st.markdown("""
<style>
    /* Global styling */
    .stApp {
        background-color: #212121;
        color: #ffffff;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    }
    
    /* Header styling */
    .main-header {
        text-align: center;
        color: #10a37f;
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 10px;
    }
    
    .subtitle {
        text-align: center;
        color: #8e8ea0;
        font-size: 1rem;
        margin-bottom: 30px;
    }
    
    /* Chat message styling */
    .user-message {
        background: #2f2f2f;
        padding: 15px;
        border-radius: 12px;
        margin: 10px 0;
        border-left: 4px solid #10a37f;
    }
    
    .ai-message {
        background: #1a1a1a;
        padding: 15px;
        border-radius: 12px;
        margin: 10px 0;
        border-left: 4px solid #ff6b35;
    }
    
    .message-header {
        font-weight: bold;
        color: #10a37f;
        font-size: 14px;
        margin-bottom: 8px;
    }
    
    .ai-message .message-header {
        color: #ff6b35;
    }
    
    /* Input styling */
    .stTextArea textarea {
        background: #2f2f2f !important;
        border: 2px solid #404040 !important;
        border-radius: 8px !important;
        color: #ffffff !important;
        font-size: 16px !important;
    }
    
    .stTextArea textarea:focus {
        border-color: #10a37f !important;
        box-shadow: 0 0 0 2px rgba(16, 163, 127, 0.2) !important;
    }
    
    /* Button styling */
    .stButton > button {
        background: #10a37f !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 12px 24px !important;
        font-weight: 600 !important;
        width: 100% !important;
    }
    
    .stButton > button:hover {
        background: #0d8f6b !important;
    }
    
    /* File uploader styling */
    .stFileUploader {
        background: #2f2f2f !important;
        border: 2px dashed #404040 !important;
        border-radius: 8px !important;
        padding: 20px !important;
    }
    
    /* Image styling */
    .uploaded-image {
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        margin: 15px 0;
    }
    
    /* Chat container */
    .chat-container {
        max-height: 600px;
        overflow-y: auto;
        padding: 10px 0;
    }
    
    /* Hide Streamlit elements */
    .stDeployButton {display:none;}
    footer {visibility: hidden;}
    .stApp > header {visibility: hidden;}
    
    /* Scrollbar styling */
    ::-webkit-scrollbar {
        width: 8px;
    }
    ::-webkit-scrollbar-track {
        background: #2f2f2f;
    }
    ::-webkit-scrollbar-thumb {
        background: #404040;
        border-radius: 4px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: #505050;
    }

    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #1a1a1a; /* Darker background for sidebar */
        color: #ffffff;
        padding-top: 20px;
        box-shadow: 2px 0 5px rgba(0,0,0,0.2);
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    }
    
    .sidebar-header {
        font-size: 1.5rem;
        color: #10a37f;
        text-align: center;
        margin-bottom: 20px;
        font-weight: bold;
    }
    .sidebar-section-header {
        font-size: 1.2rem;
        color: #10a37f;
        margin-bottom: 10px;
        font-weight: bold;
        padding-left: 15px;
    }
    .sidebar-info {
        font-size: 0.9rem;
        color: #cccccc;
        text-align: justify;
        padding: 0 15px;
        margin-bottom: 20px;
        line-height: 1.6;
    }
    .sidebar-bullet {
        margin-bottom: 10px;
        color: #eeeeee;
        padding: 0 15px;
        display: flex;
        align-items: center;
    }
    .sidebar-bullet strong {
        color: #ff6b35;
        font-weight: 600;
        margin-right: 8px;
    }
    .sidebar-footer {
        font-size: 0.8rem;
        color: #888888;
        text-align: center;
        margin-top: 30px;
        padding: 10px 0;
        border-top: 1px solid #333333;
    }
    /* Updated debug section styling */
    .debug-container {
        background-color: #2f2f2f;
        border-radius: 8px;
        padding: 15px;
        margin: 20px 15px;
        border: 1px solid #404040;
        display: flex;
        flex-direction: column;
    }
    .debug-status-text {
        font-weight: bold;
        color: #10a37f;
        font-size: 1rem;
        margin-bottom: 5px;
    }
    .debug-info-block {
        display: flex;
        flex-direction: column;
        margin-top: 10px;
    }
    .debug-info-block p {
        margin: 0;
        padding: 0;
    }
</style>
""", unsafe_allow_html=True)

class EcoVisionAI:
    def __init__(self):
        pass
    
    def encode_image(self, image):
        """Convert PIL image to base64 string for OpenAI API"""
        try:
            buffered = io.BytesIO()
            if image.mode != 'RGB':
                image = image.convert('RGB')
            image.save(buffered, format="JPEG", quality=85)
            encoded = base64.b64encode(buffered.getvalue()).decode('utf-8')
            return encoded
        except Exception as e:
            st.error(f"❌ Error encoding image: {e}")
            return None
    
    def analyze_image_with_question(self, image, question):
        """Analyze image with user question using OpenAI GPT-4 Vision"""
        
        base64_image = self.encode_image(image)
        if not base64_image:
            return "Sorry, I couldn't process the image. Please try again."
        
        # Comprehensive prompt for environmental analysis
        system_prompt = """You are EcoVision AI, an expert environmental analyst. You can analyze any environmental image and answer questions about it comprehensively and accurately.

You excel at:
- Identifying all objects, people, animals, plants, and environmental features. Be sure to correctly distinguish between living things (like humans, plants, and animals) and non-living things (like equipment, fire, or rocks).
- Assessing environmental health and sustainability.
- Providing conservation recommendations.
- Answering specific questions about what you observe.
- Explaining ecological processes and relationships.

Always provide detailed, accurate, and helpful responses. If asked about specific counts (like "how many people"), be precise. Maintain a logical and factual tone. Answer naturally as if you're having a conversation."""

        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text", 
                                "text": f"Please analyze this environmental image and answer my question: {question}"
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}",
                                    "detail": "high"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=1500,
                temperature=0.1
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"I encountered an error while analyzing the image: {str(e)}. Please try again."

# Initialize the AI
eco_ai = EcoVisionAI()

def is_polite_response(text):
    """
    Checks if the user's input is a simple polite phrase like "thank you".
    """
    polite_phrases = ["thank you", "thanks", "thanks a lot", "thank you so much", "cheers"]
    normalized_text = text.lower().strip()
    return any(phrase in normalized_text for phrase in polite_phrases)

def main():
    # Sidebar content
    with st.sidebar:
        st.markdown('<div class="sidebar-header">🌿 EcoVision Insights</div>', unsafe_allow_html=True)
        st.markdown("""
            <div class="sidebar-info">
                EcoVision AI is designed to help you understand and monitor environmental aspects through image analysis. Upload a photo of nature, wildlife, pollution, or any environmental scene, and I'll provide insights.
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('<p class="sidebar-bullet"><strong>📸</strong> Camera Input: Capture real-time images for instant analysis.</p>', unsafe_allow_html=True)
        st.markdown('<p class="sidebar-bullet"><strong>📂</strong> File Upload: Analyze images from your device.</p>', unsafe_allow_html=True)
        st.markdown('<p class="sidebar-bullet"><strong>🧠</strong> Intelligent Analysis: Powered by advanced AI for detailed environmental understanding.</p>', unsafe_allow_html=True)
        st.markdown('<p class="sidebar-bullet"><strong>💡</strong> Conservation Tips: Get recommendations for environmental protection.</p>', unsafe_allow_html=True)

        st.markdown("---")
        
        # Updated Debug Info section
        st.markdown("""
        <div class="debug-container">
            <p class="debug-status-text">✅ OpenAI API key loaded</p>
            <div class="debug-info-block">
                <p>🔧 Debug Info</p>
                <p>API Key Status: <span style="color: #10a37f; font-weight: bold;">✅ Loaded</span></p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('<div class="sidebar-footer">© 2025 EcoVision AI. All rights reserved.</div>', unsafe_allow_html=True)


    # Main content area
    st.markdown('<div class="main-header">🌍 EcoVision AI</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Ask me anything about environmental images</div>', unsafe_allow_html=True)
    
    # Initialize session state for chat history
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
        # Add the initial AI greeting message
        st.session_state.chat_history.append({
            "type": "ai",
            "content": "Hello there! I'm EcoVision AI, your environmental intelligence assistant. You can upload an image or take a picture with your camera, then ask me anything you'd like to know about the environment it depicts!",
            "timestamp": datetime.now().strftime("%H:%M")
        })
    if 'current_image' not in st.session_state:
        st.session_state.current_image = None
    
    # Image input selection (radio buttons for choice)
    st.subheader("📸 Choose Image Source")
    image_source_option = st.radio(
        "Select your preferred image input method:",
        ("Upload Image", "Take Picture with Camera"),
        key="image_source_radio"
    )

    if image_source_option == "Upload Image":
        uploaded_file = st.file_uploader(
            "Choose an environmental image...",
            type=['png', 'jpg', 'jpeg'],
            help="Upload an image to analyze"
        )
        if uploaded_file:
            image = Image.open(uploaded_file)
            st.session_state.current_image = image
            st.image(image, caption="Uploaded Image", use_container_width=True, output_format="auto") # Removed class_name
        else:
            st.session_state.current_image = None # Reset if no file is uploaded after selection
            
    elif image_source_option == "Take Picture with Camera":
        camera_image = st.camera_input("Take a picture for analysis")
        if camera_image:
            image = Image.open(camera_image)
            st.session_state.current_image = image
            st.image(image, caption="Captured Image", use_container_width=True, output_format="auto") # Removed class_name
        else:
            st.session_state.current_image = None # Reset if no picture is taken

    # Question input section
    st.subheader("💬 Ask Your Question")
    
    # Create a form for better UX
    with st.form(key="question_form", clear_on_submit=True):
        user_question = st.text_area(
            "What would you like to know about this image?",
            placeholder="e.g., 'What environmental issues do you see?', 'Is this ecosystem healthy?', 'Identify the species present.'",
            height=100,
            key="question_input"
        )
        
        submit_button = st.form_submit_button("Send Message")
        
        # Handle form submission
        if submit_button and user_question.strip():
            # Add user message to chat history
            st.session_state.chat_history.append({
                "type": "user",
                "content": user_question.strip(),
                "timestamp": datetime.now().strftime("%H:%M")
            })
            
            ai_response = ""

            # Check if the user's input is a simple polite phrase
            if is_polite_response(user_question.strip()):
                ai_response = "You're very welcome! Feel free to ask me anything else about the image."
            # Check if an image is present. If not, prompt the user.
            elif st.session_state.current_image is None:
                ai_response = "Please upload an image or take a picture with your camera first!"
            else:
                # If an image is present, send the user's question to the AI model
                with st.spinner("🤖 Analyzing..."):
                    ai_response = eco_ai.analyze_image_with_question(
                        st.session_state.current_image, 
                        user_question.strip()
                    )
            
            # Add AI response to chat history
            st.session_state.chat_history.append({
                "type": "ai",
                "content": ai_response,
                "timestamp": datetime.now().strftime("%H:%M")
            })
            
            # Rerun to show new messages
            st.rerun()
            
        elif submit_button and not user_question.strip():
            st.warning("Please enter a question!")
    
    # Display chat history
    if st.session_state.chat_history:
        st.subheader("💬 Chat History")
        
        # Create chat container
        chat_container = st.container()
        
        with chat_container:
            for i, message in enumerate(st.session_state.chat_history):
                if message["type"] == "user":
                    st.markdown(f"""
                    <div class="user-message">
                        <div class="message-header">You • {message["timestamp"]}</div>
                        <div>{message["content"]}</div>
                    </div>
                    """, unsafe_allow_html=True)
                else:  # AI message
                    st.markdown(f"""
                    <div class="ai-message">
                        <div class="message-header">EcoVision AI • {message["timestamp"]}</div>
                        <div>{message["content"]}</div>
                    </div>
                    """, unsafe_allow_html=True)
    
    # Clear chat button (optional)
    if st.session_state.chat_history:
        if st.button("🗑️ Clear Chat History"):
            st.session_state.chat_history = []
            st.session_state.current_image = None # Also clear the image
            st.rerun()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #8e8ea0; padding: 10px;">
        🌍 EcoVision AI - Environmental Intelligence Through Computer Vision
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
