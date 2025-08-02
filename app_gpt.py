

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
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Page config MUST be first Streamlit command
st.set_page_config(
    page_title="EcoVision AI",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize OpenAI client with error handling
try:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        st.error("⚠️ OPENAI_API_KEY not found in environment variables!")
        st.info("Please check your .env file")
        st.stop()
    client = OpenAI(api_key=api_key)
    st.sidebar.success("✅ OpenAI API key loaded")
except Exception as e:
    st.error(f"❌ Error initializing OpenAI client: {e}")
    st.stop()

# Custom CSS combining both styles
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global Dark Mode Styling */
    .stApp {
        background: linear-gradient(135deg, #0f1419 0%, #1a1f2e 50%, #0f1419 100%);
        font-family: 'Inter', sans-serif;
        color: #e1e5e9;
    }
    
    /* Header Styling */
    .main-header {
        font-size: 3.5rem;
        font-weight: 700;
        background: linear-gradient(45deg, #64ffda, #1de9b6, #00bcd4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 1rem;
        text-shadow: 0 0 30px rgba(100, 255, 218, 0.3);
    }
    
    .subtitle {
        font-size: 1.3rem;
        color: #8892b0;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: 400;
    }
    
    /* ChatGPT-style message styling for Q&A mode */
    .user-message {
        background: #2f2f2f;
        padding: 15px;
        border-radius: 12px;
        margin: 10px 0;
        border-left: 4px solid #10a37f;
        color: #ffffff;
    }
    
    .ai-message {
        background: #1a1a1a;
        padding: 15px;
        border-radius: 12px;
        margin: 10px 0;
        border-left: 4px solid #ff6b35;
        color: #ffffff;
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
    
    /* Chat container */
    .chat-container {
        max-height: 600px;
        overflow-y: auto;
        padding: 10px 0;
    }
    
    /* Analysis Card - Dark Glassmorphism */
    .analysis-card {
        background: rgba(20, 25, 40, 0.8);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(100, 255, 218, 0.2);
        color: #e1e5e9;
        padding: 25px;
        border-radius: 12px;
        margin: 15px 0;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
        transition: all 0.3s ease;
    }
    
    .analysis-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 12px 40px rgba(100, 255, 218, 0.1);
        border-color: rgba(100, 255, 218, 0.4);
    }
    
    .analysis-card h3 {
        color: #64ffda !important;
        margin-bottom: 15px;
        font-weight: 600;
        font-size: 1.4rem;
    }
    
    /* Recommendation Cards - Dark Theme */
    .metric-card {
        background: linear-gradient(135deg, #1a1f2e 0%, #232946 100%);
        color: #e1e5e9;
        padding: 25px;
        border-radius: 12px;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
        margin: 15px 0;
        min-height: 140px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        transition: all 0.3s ease;
        border: 1px solid rgba(100, 255, 218, 0.15);
        position: relative;
        overflow: hidden;
    }
    
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, #64ffda, #1de9b6);
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 35px rgba(100, 255, 218, 0.2);
        border-color: rgba(100, 255, 218, 0.3);
    }
    
    .metric-card h4 {
        color: #64ffda !important;
        margin-bottom: 12px;
        font-size: 1.2rem;
        font-weight: 600;
    }
    
    .metric-card p {
        color: #8892b0 !important;
        line-height: 1.6;
        margin: 0;
        font-size: 0.95rem;
        font-weight: 400;
    }
    
    /* Sidebar Dark Styling */
    .css-1d391kg {
        background: rgba(15, 20, 25, 0.95) !important;
        backdrop-filter: blur(10px) !important;
        border-right: 1px solid rgba(100, 255, 218, 0.1) !important;
    }
    
    /* Buttons - Dark Theme */
    .stButton > button {
        background: linear-gradient(45deg, #64ffda, #1de9b6) !important;
        color: #0f1419 !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 12px 24px !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(100, 255, 218, 0.3) !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 25px rgba(100, 255, 218, 0.4) !important;
        background: linear-gradient(45deg, #1de9b6, #64ffda) !important;
    }
    
    /* Metrics - Dark Theme */
    [data-testid="metric-container"] {
        background: rgba(20, 25, 40, 0.6);
        border: 1px solid rgba(100, 255, 218, 0.2);
        padding: 15px;
        border-radius: 8px;
        backdrop-filter: blur(10px);
    }
    
    [data-testid="metric-container"] > div {
        color: #e1e5e9 !important;
    }
    
    [data-testid="metric-container"] [data-testid="metric-value"] {
        color: #64ffda !important;
        font-weight: 600;
    }
    
    /* File Uploader - Dark Theme */
    .stFileUploader {
        background: rgba(20, 25, 40, 0.6) !important;
        border-radius: 8px !important;
        border: 2px dashed rgba(100, 255, 218, 0.3) !important;
    }
    
    .stFileUploader label {
        color: #8892b0 !important;
    }
    
    /* Messages - Dark Theme */
    .stSuccess {
        background: rgba(29, 233, 182, 0.1) !important;
        border: 1px solid rgba(29, 233, 182, 0.3) !important;
        border-radius: 8px !important;
        color: #1de9b6 !important;
    }
    
    .stInfo {
        background: rgba(100, 255, 218, 0.1) !important;
        border: 1px solid rgba(100, 255, 218, 0.3) !important;
        border-radius: 8px !important;
        color: #64ffda !important;
    }
    
    .stWarning {
        background: rgba(255, 193, 7, 0.1) !important;
        border: 1px solid rgba(255, 193, 7, 0.3) !important;
        border-radius: 8px !important;
        color: #ffc107 !important;
    }
    
    .stError {
        background: rgba(244, 67, 54, 0.1) !important;
        border: 1px solid rgba(244, 67, 54, 0.3) !important;
        border-radius: 8px !important;
        color: #f44336 !important;
    }
    
    /* Headers - Dark Theme */
    h1, h2, h3 {
        color: #e1e5e9 !important;
        font-weight: 600 !important;
    }
    
    /* Subheaders with accent */
    .stApp h2 {
        color: #64ffda !important;
        border-bottom: 2px solid rgba(100, 255, 218, 0.2);
        padding-bottom: 8px;
    }
    
    /* DataFrames - Dark Theme */
    .stDataFrame {
        background: rgba(20, 25, 40, 0.8) !important;
        border-radius: 8px !important;
        border: 1px solid rgba(100, 255, 218, 0.2) !important;
        backdrop-filter: blur(10px) !important;
    }
    
    /* Radio buttons and selectbox - Dark Theme */
    .stRadio > div {
        background: rgba(20, 25, 40, 0.6);
        border-radius: 8px;
        padding: 10px;
        border: 1px solid rgba(100, 255, 218, 0.1);
    }
    
    .stSelectbox > div > div {
        background: rgba(20, 25, 40, 0.8);
        border: 1px solid rgba(100, 255, 218, 0.2);
        border-radius: 8px;
    }
    
    /* Text Input and TextArea - Dark Theme */
    .stTextInput > div > div > input, .stTextArea textarea {
        background: rgba(20, 25, 40, 0.8) !important;
        border: 1px solid rgba(100, 255, 218, 0.2) !important;
        border-radius: 8px !important;
        color: #e1e5e9 !important;
        padding: 8px 12px !important;
    }
    
    .stTextInput > div > div > input:focus, .stTextArea textarea:focus {
        border-color: rgba(100, 255, 218, 0.5) !important;
        box-shadow: 0 0 10px rgba(100, 255, 218, 0.2) !important;
    }
    
    /* Expander - Dark Theme */
    .streamlit-expanderHeader {
        background: rgba(20, 25, 40, 0.6) !important;
        border: 1px solid rgba(100, 255, 218, 0.2) !important;
        border-radius: 8px !important;
    }
    
    .streamlit-expanderContent {
        background: rgba(15, 20, 25, 0.8) !important;
        border: 1px solid rgba(100, 255, 218, 0.1) !important;
    }
    
    /* Scrollbars - Dark Theme */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(20, 25, 40, 0.3);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: rgba(100, 255, 218, 0.3);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(100, 255, 218, 0.5);
    }
    
    /* Text color fixes */
    .stMarkdown, .stText, p, span, div {
        color: #8892b0 !important;
    }
    
    /* Keep specific elements bright */
    .metric-card *, .analysis-card *, .user-message *, .ai-message * {
        color: inherit !important;
    }
</style>
""", unsafe_allow_html=True)

class EcoVisionAI:
    def __init__(self):
        self.analysis_history = []
        # Initialize chat history in session state
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []
        if 'current_image_base64' not in st.session_state:
            st.session_state.current_image_base64 = None
    
    def is_polite_response(self, text):
        """Check if the user's input is a simple polite phrase like 'thank you'"""
        polite_phrases = ["thank you", "thanks", "thanks a lot", "thank you so much", "cheers"]
        normalized_text = text.lower().strip()
        return any(phrase in normalized_text for phrase in polite_phrases)
    
    def encode_image(self, image):
        """Convert PIL image to base64 string for OpenAI API"""
        try:
            buffered = io.BytesIO()
            # Convert to RGB if not already
            if image.mode != 'RGB':
                image = image.convert('RGB')
            image.save(buffered, format="JPEG", quality=85)
            encoded = base64.b64encode(buffered.getvalue()).decode('utf-8')
            st.sidebar.info(f"✅ Image encoded successfully ({len(encoded)} chars)")
            return encoded
        except Exception as e:
            st.error(f"❌ Error encoding image: {e}")
            return None
    
    def analyze_image_with_ai(self, image, analysis_type="comprehensive"):
        """Analyze image using OpenAI GPT-4 Vision with enhanced debugging"""
        
        # Debug: Show we're starting analysis
        st.write("🔍 **Starting AI Analysis...**")
        st.write(f"**Analysis Mode:** {analysis_type}")
        st.write(f"**Image Size:** {image.size}")
        
        # Encode image
        base64_image = self.encode_image(image)
        if not base64_image:
            return {"error": "Failed to encode image"}
        
        # Store the encoded image for chat functionality
        st.session_state.current_image_base64 = base64_image
        
        # Enhanced prompt for better forest detection and human activities
        prompt = """Analyze this environmental image and provide detailed insights in JSON format.

Pay special attention to:
- Individual trees, forest areas, canopy coverage
- Vegetation types (moss, ferns, undergrowth, grass, saplings, young trees)
- Water features (streams, rivers, lakes)
- Soil and ground coverage
- Human activities (tree planting, farming, conservation work, gardening)
- People engaged in environmental activities
- Tools or evidence of environmental work (shovels, seedlings, planted areas)
- Any human-made structures or impacts

Detect ALL visible elements including people, activities, and environmental objects.

Return your response as valid JSON with this exact structure:
{
  "summary": "Detailed description of the environmental scene including forest density, ecosystem type, and any human activities",
  "objects_detected": [
    {
      "name": "specific object, organism, or activity name (be detailed: 'people planting trees', 'tree saplings', 'reforestation activity', 'environmental workers', etc.)",
      "type": "living or non-living",
      "confidence": 0.9,
      "environmental_impact": "positive, negative, or neutral",
      "sustainability_score": 8,
      "description": "detailed description including size, density, health, or activity purpose",
      "recommended_action": "specific recommended action"
    }
  ],
  "overall_analysis": {
    "environmental_health_score": 8.5,
    "biodiversity_level": "high",
    "key_concerns": ["list of environmental concerns"],
    "positive_aspects": ["list of positive environmental aspects"],
    "recommendations": ["list of actionable recommendations"]
  }
}

Please ensure your response is valid JSON only. Detect as many distinct environmental elements AND human activities as possible."""
        
        try:
            st.write("📡 **Sending request to OpenAI...**")
            
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
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
            
            result_text = response.choices[0].message.content.strip()
            st.write("✅ **Received response from OpenAI**")
            
            # Debug: Show raw response
            with st.expander("🔧 Debug - Raw AI Response"):
                st.text(result_text[:500] + "..." if len(result_text) > 500 else result_text)
            
            # Clean up the response to ensure it's valid JSON
            if result_text.startswith("```json"):
                result_text = result_text.replace("```json", "").replace("```", "").strip()
            elif result_text.startswith("```"):
                result_text = result_text.replace("```", "").strip()
            
            # Try to parse as JSON
            try:
                parsed_result = json.loads(result_text)
                st.write("✅ **JSON parsing successful**")
                return parsed_result
            except json.JSONDecodeError as json_error:
                st.write(f"⚠️ **JSON parsing failed:** {json_error}")
                # Create a fallback structured response
                fallback_result = {
                    "summary": result_text[:200] + "..." if len(result_text) > 200 else result_text,
                    "raw_analysis": result_text,
                    "objects_detected": [
                        {
                            "name": "Environmental Scene Analysis",
                            "type": "comprehensive",
                            "confidence": 0.85,
                            "environmental_impact": "positive",
                            "sustainability_score": 7,
                            "description": "AI analysis completed successfully",
                            "recommended_action": "Review detailed analysis below"
                        }
                    ],
                    "overall_analysis": {
                        "environmental_health_score": 7.5,
                        "biodiversity_level": "medium",
                        "key_concerns": ["See detailed analysis"],
                        "positive_aspects": ["Natural environment detected"],
                        "recommendations": ["Continue environmental monitoring"]
                    }
                }
                return fallback_result
                
        except Exception as e:
            error_msg = f"Analysis failed: {str(e)}"
            st.write(f"❌ **Error:** {error_msg}")
            return {
                "error": error_msg,
                "debug_info": f"Error type: {type(e).__name__}",
                "summary": "Analysis encountered an error"
            }
    
    def analyze_image_with_question(self, image, question):
        """Analyze image with user question using OpenAI GPT-4 Vision - ChatGPT style method"""
        
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
    
    def generate_recommendations(self, analysis_result):
        """Generate actionable environmental recommendations"""
        recommendations = []
        
        if "overall_analysis" in analysis_result:
            recommendations = analysis_result["overall_analysis"].get("recommendations", [])
        
        # If no recommendations or empty, generate based on analysis content
        if not recommendations or len(recommendations) == 0:
            if "objects_detected" in analysis_result:
                objects = analysis_result["objects_detected"]
                if any("tree" in obj.get("name", "").lower() or "forest" in obj.get("name", "").lower() for obj in objects):
                    recommendations.extend([
                        "🌳 Protect existing tree canopy by avoiding development in forested areas",
                        "🌱 Support reforestation initiatives in your local community", 
                        "🚫 Avoid disturbing wildlife habitats and maintain natural corridors"
                    ])
                elif any("waste" in obj.get("name", "").lower() or "plastic" in obj.get("name", "").lower() for obj in objects):
                    recommendations.extend([
                        "♻️ Implement proper waste sorting and recycling practices",
                        "🚯 Reduce single-use plastics and choose sustainable alternatives",
                        "🔄 Support circular economy initiatives in your community"
                    ])
                else:
                    recommendations.extend([
                        "🔍 Continue monitoring environmental conditions regularly",
                        "📊 Document changes over time to track environmental health",
                        "🤝 Share findings with local environmental groups"
                    ])
            elif "raw_analysis" in analysis_result:
                analysis_text = analysis_result["raw_analysis"].lower()
                if "forest" in analysis_text or "tree" in analysis_text:
                    recommendations.extend([
                        "🌲 Preserve forest ecosystems through conservation efforts",
                        "🌿 Promote biodiversity by protecting natural habitats",
                        "🏞️ Support sustainable forestry practices"
                    ])
                elif "waste" in analysis_text or "recycl" in analysis_text:
                    recommendations.extend([
                        "♻️ Improve waste management and recycling systems",
                        "🌍 Reduce environmental impact through better disposal practices", 
                        "💡 Educate others about proper waste sorting"
                    ])
                else:
                    recommendations.extend([
                        "🌱 Take action to improve environmental sustainability",
                        "📈 Monitor and measure environmental impact regularly",
                        "🤝 Collaborate with others on conservation efforts"
                    ])
            else:
                recommendations = [
                    "🔍 Upload an image to receive personalized environmental recommendations",
                    "🌍 Start by analyzing your local environment for improvement opportunities", 
                    "📱 Use this tool regularly to track environmental changes"
                ]
        
        # Ensure we have at least 3 recommendations
        while len(recommendations) < 3:
            additional_recs = [
                "🌳 Plant native species to support local ecosystems",
                "💧 Conserve water resources through mindful usage",
                "🔋 Choose renewable energy sources when possible",
                "🚴‍♂️ Use sustainable transportation options",
                "📚 Educate others about environmental conservation",
                "🧹 Participate in local environmental cleanup efforts"
            ]
            for rec in additional_recs:
                if rec not in recommendations and len(recommendations) < 3:
                    recommendations.append(rec)
        
        return recommendations[:3]  # Return max 3 recommendations

# Initialize the app
eco_ai = EcoVisionAI()

# Main app
def main():
    st.markdown('<div class="main-header">🌍 EcoVision AI</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Advanced Computer Vision for Environmental Analysis</div>', unsafe_allow_html=True)
    
    # Initialize session state variables
    if 'app_mode' not in st.session_state:
        st.session_state.app_mode = "comprehensive_analysis"
    if 'analysis_count' not in st.session_state:
        st.session_state.analysis_count = 0
    
    # Sidebar with Navigation Mode Selection (only 2 modes)
    with st.sidebar:
        st.header("🚀 Navigation Mode")
        app_mode = st.selectbox(
            "Choose Mode",
            ["comprehensive_analysis", "qa_mode"],
            format_func=lambda x: {
                "comprehensive_analysis": "🔬 Comprehensive Analysis",
                "qa_mode": "💬 Q&A Mode"
            }[x]
        )
        
        # Store app mode in session state
        st.session_state.app_mode = app_mode
        
        # Show different content based on mode
        if app_mode == "comprehensive_analysis":
            st.header("🔧 Analysis Settings")
            analysis_mode = st.selectbox(
                "Analysis Type",
                ["comprehensive", "waste_detection", "biodiversity"],
                format_func=lambda x: {
                    "comprehensive": "🔍 Comprehensive Analysis",
                    "waste_detection": "♻️ Waste & Recycling",
                    "biodiversity": "🦋 Biodiversity Assessment"
                }[x]
            )

            st.header("📊 Environmental Metrics")
            
            # Learning Progress - Always show for comprehensive analysis
            st.metric("Environmental Insights", st.session_state.analysis_count, 
                      help="Number of environmental scenes analyzed for learning")
            
            # ENHANCED CO₂ CALCULATION - Dynamic metrics based on current analysis
            if 'current_analysis' in st.session_state and 'objects_detected' in st.session_state.current_analysis:
                analysis = st.session_state.current_analysis
                
                # Calculate enhanced CO₂ impact based on detected objects
                co2_impact = 0
                co2_details = []
                forest_multiplier = 1

                # Check for forest density indicators
                forest_keywords = ["tree", "forest", "vegetation", "plant", "woods", "canopy"]
                detected_forest_objects = sum(1 for obj in analysis.get("objects_detected", []) 
                                             if any(keyword in obj.get("name", "").lower() 
                                                   for keyword in forest_keywords))

                # Determine forest density multiplier
                if detected_forest_objects >= 3:
                    forest_multiplier = 4  # Dense forest
                    forest_type = "Dense Forest Ecosystem"
                elif detected_forest_objects >= 2:
                    forest_multiplier = 2.5  # Moderate forest
                    forest_type = "Forest Area"
                else:
                    forest_multiplier = 1  # Single trees
                    forest_type = "Individual Trees"

                for obj in analysis.get("objects_detected", []):
                    name = obj.get("name", "").lower()
                    
                    # Trees and vegetation (CO₂ absorption)
                    if any(keyword in name for keyword in ["tree", "forest", "vegetation", "plant", "woods", "canopy", "sapling"]):
                        base_absorption = 2.5
                        enhanced_absorption = base_absorption * forest_multiplier
                        co2_impact += enhanced_absorption
                        co2_details.append(f"🌳 {obj.get('name', 'Forest')}: +{enhanced_absorption:.1f} kg CO₂/day")
                    
                    # Tree planting activities
                    elif any(keyword in name for keyword in ["planting", "reforestation", "tree planting", "environmental work", "conservation"]):
                        planting_impact = 15.0 * forest_multiplier
                        co2_impact += planting_impact
                        co2_details.append(f"🌱 {obj.get('name', 'Tree Planting Activity')}: +{planting_impact:.1f} kg CO₂/day")
                    
                    # People in environmental activities
                    elif any(keyword in name for keyword in ["people", "person", "human", "worker", "volunteer"]) and any(env_keyword in name for env_keyword in ["plant", "environment", "conservation", "garden"]):
                        human_env_impact = 10.0
                        co2_impact += human_env_impact
                        co2_details.append(f"👥 {obj.get('name', 'Environmental Workers')}: +{human_env_impact:.1f} kg CO₂/day")

                # Add ecosystem bonuses
                if detected_forest_objects >= 2:
                    ecosystem_bonus = 5.0 * detected_forest_objects
                    co2_impact += ecosystem_bonus
                    co2_details.append(f"🌲 {forest_type} Bonus: +{ecosystem_bonus:.1f} kg CO₂/day")

                # Display CO₂ impact
                if co2_impact > 0:
                    st.metric("🌱 CO₂ Impact", f"+{co2_impact:.1f} kg/day", 
                              help="Estimated positive daily CO₂ impact")
                elif co2_impact < 0:
                    st.metric("⚠️ CO₂ Impact", f"{co2_impact:.1f} kg/day", 
                              help="Estimated negative daily CO₂ impact")
                else:
                    st.metric("🔄 CO₂ Impact", "Neutral", 
                              help="No significant CO₂ impact detected")
                
                # Show calculation details
                if co2_details:
                    with st.expander("CO₂ Calculation Details"):
                        for detail in co2_details:
                            st.write(detail)
                
                # Environmental Health Score
                health_score = 60
                for obj in analysis.get("objects_detected", []):
                    impact = obj.get("environmental_impact", "neutral")
                    if impact == "positive":
                        health_score += 15
                    elif impact == "negative":
                        health_score -= 20

                health_score = max(0, min(100, health_score))
                health_icon = "🌿" if health_score >= 70 else "⚠️" if health_score >= 40 else "🔴"
                st.metric(f"{health_icon} Environment Score", f"{health_score}/100", 
                          help="Environmental health assessment")
                
                # Biodiversity Index
                living_count = sum(1 for obj in analysis.get("objects_detected", []) 
                                  if obj.get("type", "").lower() == "living")
                total_objects = len(analysis.get("objects_detected", []))
                
                if total_objects > 0:
                    biodiversity = (living_count / total_objects) * 100
                    st.metric("🦋 Biodiversity", f"{biodiversity:.0f}%", 
                              help=f"Living organisms: {living_count} of {total_objects} detected")
                
            else:
                # Placeholder metrics when no analysis available
                st.metric("🌍 CO₂ Calculator", "Upload image", 
                          help="Analyze an environmental image to calculate CO₂ impact")
                st.metric("🌿 Environment Score", "—", 
                          help="Environmental health assessment")
                st.metric("🦋 Biodiversity", "—", 
                          help="Percentage of living organisms detected")
        
        elif app_mode == "qa_mode":
            # Q&A Mode - Simplified sidebar
            st.header("EcoVision AI Assistant")
            st.info("Upload an image and ask questions about it!")
            
            # Show chat statistics only
            if st.session_state.chat_history:
                # Count only user questions, not AI responses
                user_questions = sum(1 for msg in st.session_state.chat_history if msg["type"] == "user")
                if user_questions > 0:
                    st.metric("💬 Questions Asked", user_questions, 
                              help="Number of questions asked about environmental images")
            
            # Show image status
            if st.session_state.current_image_base64:
                st.success("✅ Image ready for questions")
            else:
                st.warning("📸 Upload an image first")
            
            # Clear Chat History Button
            if st.session_state.chat_history:
                if st.button("🗑️ Clear Chat History", help="Clear all conversation history"):
                    st.session_state.chat_history = []
                    st.session_state.current_image = None
                    st.rerun()
        
        # Debug info (appears in both modes)
        st.header("🔧 Debug Info")
        st.info(f"API Key Status: {'✅ Loaded' if api_key else '❌ Missing'}")
        
        # Format the mode display properly
        mode_display = app_mode.replace('_', ' ').title()
        if mode_display == "Qa Mode":
            mode_display = "Q&A Mode"
        st.info(f"Current Mode: {mode_display}")
    
    # Main content - different layout based on app mode
    if st.session_state.app_mode == "comprehensive_analysis":
        # Comprehensive Analysis Mode
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.header("📷 Image Input")
            
            # Image upload options
            input_method = st.radio(
                "Choose input method:",
                ["Upload Image", "Camera Capture"]
            )
            
            uploaded_image = None
            
            if input_method == "Upload Image":
                uploaded_file = st.file_uploader(
                    "Choose an image...",
                    type=['png', 'jpg', 'jpeg'],
                    help="Upload an image for environmental analysis"
                )
                if uploaded_file:
                    uploaded_image = Image.open(uploaded_file)
            
            elif input_method == "Camera Capture":
                camera_image = st.camera_input("Take a picture")
                if camera_image:
                    uploaded_image = Image.open(camera_image)
            
            if uploaded_image:
                st.image(uploaded_image, caption="Input Image", width=None)
                
                # Analysis button
                if st.button("🚀 Analyze with AI", type="primary", key="analyze_comp"):
                    with st.spinner("🤖 AI is analyzing the environment..."):
                        # Clear previous results
                        if 'current_analysis' in st.session_state:
                            del st.session_state.current_analysis
                        
                        # Perform AI analysis
                        analysis_result = eco_ai.analyze_image_with_ai(uploaded_image, analysis_mode)
                        
                        # Store in session state
                        st.session_state.current_analysis = analysis_result
                        st.session_state.analysis_count += 1
                        
                        # Force rerun to show results
                        st.rerun()
        
        with col2:
            st.header("🔬 Analysis Results")
            
            if 'current_analysis' in st.session_state:
                analysis = st.session_state.current_analysis
                
                if "error" in analysis:
                    st.error(f"❌ {analysis['error']}")
                else:
                    # Display summary
                    if "summary" in analysis:
                        st.markdown(f"""
                        <div class="analysis-card">
                            <h3>📋 Environmental Analysis Summary</h3>
                            <p style="font-size: 1.1rem; line-height: 1.6;">{analysis['summary']}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Display overall analysis
                    if "overall_analysis" in analysis:
                        overall = analysis["overall_analysis"]
                        
                        # Metrics
                        col_a, col_b = st.columns(2)
                        with col_a:
                            score = overall.get("environmental_health_score", 0)
                            st.metric("🌱 Environmental Health", f"{score}/10")
                        with col_b:
                            biodiversity = overall.get("biodiversity_level", "Unknown")
                            st.metric("🦋 Biodiversity Level", biodiversity.title())
                        
                        # Key findings
                        if "key_concerns" in overall and overall["key_concerns"]:
                            st.subheader("⚠️ Key Concerns")
                            for concern in overall["key_concerns"]:
                                st.warning(f"• {concern}")
                        
                        if "positive_aspects" in overall and overall["positive_aspects"]:
                            st.subheader("✅ Positive Aspects")
                            for aspect in overall["positive_aspects"]:
                                st.success(f"• {aspect}")
                    
                    # Display detected objects
                    if "objects_detected" in analysis and analysis["objects_detected"]:
                        st.subheader("🔍 Detected Objects")
                        
                        try:
                            objects_df = pd.DataFrame(analysis["objects_detected"])
                            if not objects_df.empty:
                                # Check if required columns exist for plotting
                                required_cols = ["sustainability_score", "confidence"]
                                if all(col in objects_df.columns for col in required_cols):
                                    # Create enhanced visualization with dark theme
                                    fig = px.scatter(
                                        objects_df,
                                        x="sustainability_score",
                                        y="confidence",
                                        color="environmental_impact",
                                        size="sustainability_score",
                                        hover_data=["name", "type"],
                                        title="🌍 Environmental Objects Analysis",
                                        color_discrete_map={
                                            "positive": "#1de9b6",
                                            "negative": "#ff6b6b", 
                                            "neutral": "#ffd93d"
                                        }
                                    )
                                    
                                    # Dark theme styling for the plot
                                    fig.update_layout(
                                        plot_bgcolor='rgba(0,0,0,0)',
                                        paper_bgcolor='rgba(15,20,25,0.8)',
                                        font_color='#8892b0',
                                        title_font_size=18,
                                        title_font_color='#64ffda',
                                        title_x=0.5,
                                        showlegend=True,
                                        legend=dict(
                                            bgcolor="rgba(20,25,40,0.8)",
                                            bordercolor="rgba(100,255,218,0.3)",
                                            borderwidth=1,
                                            font_color='#8892b0'
                                        ),
                                        margin=dict(l=10, r=10, t=50, b=10)
                                    )
                                    
                                    fig.update_xaxes(
                                        gridcolor='rgba(100,255,218,0.1)',
                                        title_font_color='#8892b0',
                                        tickfont_color='#8892b0',
                                        showgrid=True,
                                        zeroline=False
                                    )
                                    
                                    fig.update_yaxes(
                                        gridcolor='rgba(100,255,218,0.1)', 
                                        title_font_color='#8892b0',
                                        tickfont_color='#8892b0',
                                        showgrid=True,
                                        zeroline=False
                                    )
                                    
                                    # Style the traces (data points)
                                    fig.update_traces(
                                        marker=dict(
                                            line=dict(width=1, color='rgba(255,255,255,0.3)'),
                                            opacity=0.8
                                        ),
                                        hoverlabel=dict(
                                            bgcolor="rgba(20,25,40,0.9)",
                                            font_color="#e1e5e9",
                                            bordercolor="rgba(100,255,218,0.3)"
                                        )
                                    )
                                    
                                    st.plotly_chart(fig, use_container_width=True)
                                
                                # Display full table with all columns
                                st.subheader("📊 Detailed Analysis Table")
                                
                                # Clean the dataframe to remove any empty or invalid rows
                                clean_df = objects_df.dropna(subset=['name']).copy()  # Remove rows with empty names
                                clean_df = clean_df[clean_df['name'].str.strip() != '']  # Remove rows with blank names
                                
                                if not clean_df.empty:
                                    # Show all available columns, prioritizing the most important ones
                                    preferred_cols = ["name", "type", "environmental_impact", "sustainability_score", "confidence", "description", "recommended_action"]
                                    available_cols = list(clean_df.columns)
                                    
                                    # Order columns by preference, then add any remaining columns
                                    display_cols = []
                                    for col in preferred_cols:
                                        if col in available_cols:
                                            display_cols.append(col)
                                    
                                    # Add any remaining columns not in preferred list
                                    for col in available_cols:
                                        if col not in display_cols:
                                            display_cols.append(col)
                                    
                                    # Display the complete dataframe with proper sizing
                                    st.dataframe(
                                        clean_df[display_cols], 
                                        use_container_width=True,
                                        height=min(400, len(clean_df) * 35 + 50)  # Dynamic height based on number of rows
                                    )
                                    
                                    st.info(f"📋 Analysis complete: {len(clean_df)} objects detected and analyzed")
                                    
                                    # Add download option for the data
                                    csv = clean_df.to_csv(index=False)
                                    st.download_button(
                                        label="📥 Download Analysis Data as CSV",
                                        data=csv,
                                        file_name=f"ecovision_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                                        mime="text/csv"
                                    )
                                else:
                                    st.warning("No valid objects detected in the analysis.")
                                
                        except Exception as viz_error:
                            st.error(f"Error creating visualization: {viz_error}")
                            # Fallback: show objects as list
                            for i, obj in enumerate(analysis["objects_detected"]):
                                st.write(f"**{i+1}. {obj.get('name', 'Unknown Object')}**")
                                st.write(f"   - Type: {obj.get('type', 'Unknown')}")
                                st.write(f"   - Impact: {obj.get('environmental_impact', 'Unknown')}")
                                if 'description' in obj:
                                    st.write(f"   - Description: {obj['description']}")
                                if 'confidence' in obj:
                                    st.write(f"   - Confidence: {obj['confidence']}")
                                if 'sustainability_score' in obj:
                                    st.write(f"   - Sustainability Score: {obj['sustainability_score']}")
                                if 'recommended_action' in obj:
                                    st.write(f"   - Recommended Action: {obj['recommended_action']}")
                                st.write("---")
            else:
                st.info("👆 Upload an image and click 'Analyze with AI' to see results here!")
        
        # Recommendations section for comprehensive analysis
        st.header("💡 AI Environmental Recommendations")
        
        if 'current_analysis' in st.session_state:
            recommendations = eco_ai.generate_recommendations(st.session_state.current_analysis)
            
            if recommendations:
                col1, col2, col3 = st.columns(3)
                for i, rec in enumerate(recommendations[:3]):
                    with [col1, col2, col3][i % 3]:
                        st.markdown(f"""
                        <div class="metric-card">
                            <h4>💡 Action Item {i+1}</h4>
                            <p>{rec}</p>
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.info("Upload and analyze an image to see personalized recommendations!")
        else:
            # Show default recommendations
            default_recs = [
                "🌱 Upload an environmental image to get started with AI-powered analysis",
                "🔍 Try different analysis modes to explore various environmental aspects", 
                "🌍 Share your findings to promote environmental awareness"
            ]
            col1, col2, col3 = st.columns(3)
            for i, rec in enumerate(default_recs):
                with [col1, col2, col3][i % 3]:
                    st.markdown(f"""
                    <div class="metric-card">
                        <h4>💡 Getting Started {i+1}</h4>
                        <p>{rec}</p>
                    </div>
                    """, unsafe_allow_html=True)
    
    elif st.session_state.app_mode == "qa_mode":
        # Q&A Mode - ChatGPT-style centered layout
        # Initialize chat history with greeting if empty
        if not st.session_state.chat_history:
            st.session_state.chat_history.append({
                "type": "ai",
                "content": "Hello there! I'm EcoVision AI, your environmental intelligence assistant. You can upload an image or take a picture with your camera, then ask me anything you'd like to know about the environment it depicts!",
                "timestamp": datetime.now().strftime("%H:%M")
            })

        # Create centered container for ChatGPT-style layout
        col_left, col_center, col_right = st.columns([1, 3, 1])
        
        with col_center:
            # Image input section - centered and compact
            st.subheader("📸 Choose Image Source")
            image_source_option = st.radio(
                "Select your preferred image input method:",
                ("Upload Image", "Take Picture with Camera"),
                key="qa_image_source_radio"
            )

            if image_source_option == "Upload Image":
                uploaded_file = st.file_uploader(
                    "Choose an environmental image...",
                    type=['png', 'jpg', 'jpeg'],
                    help="Upload an image to analyze",
                    key="qa_file_uploader"
                )
                if uploaded_file:
                    image = Image.open(uploaded_file)
                    # Store the image and encode it
                    st.session_state.current_image = image
                    base64_image = eco_ai.encode_image(image)
                    if base64_image:
                        st.session_state.current_image_base64 = base64_image
                    # Display image with max width for ChatGPT-style layout
                    st.image(image, caption="Uploaded Image", width=500)
                else:
                    st.session_state.current_image = None
                    st.session_state.current_image_base64 = None
                    
            elif image_source_option == "Take Picture with Camera":
                camera_image = st.camera_input("Take a picture for analysis", key="qa_camera")
                if camera_image:
                    image = Image.open(camera_image)
                    # Store the image and encode it
                    st.session_state.current_image = image
                    base64_image = eco_ai.encode_image(image)
                    if base64_image:
                        st.session_state.current_image_base64 = base64_image
                    # Display image with max width for ChatGPT-style layout
                    st.image(image, caption="Captured Image", width=500)
                else:
                    st.session_state.current_image = None
                    st.session_state.current_image_base64 = None

            # Question input section - ChatGPT style
            st.subheader("💬 Ask Your Question")
            
            # Create a form for better UX
            with st.form(key="qa_question_form", clear_on_submit=True):
                user_question = st.text_area(
                    "What would you like to know about this image?",
                    placeholder="e.g., 'What environmental issues do you see?', 'Is this ecosystem healthy?', 'Identify the species present.'",
                    height=100,
                    key="qa_question_input"
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
                    if eco_ai.is_polite_response(user_question.strip()):
                        ai_response = "You're very welcome! Feel free to ask me anything else about the image."
                    # Check if an image is present
                    elif st.session_state.current_image is None:
                        ai_response = "Please upload an image or take a picture with your camera first!"
                    else:
                        # Get AI response using the ChatGPT-style method
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
            
            # Display chat history - ChatGPT style with limited width
            if st.session_state.chat_history:
                st.subheader("💬 Chat History")
                
                # Create chat container with custom styling
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
                            <div class="message-header">🤖 EcoVision AI • {message["timestamp"]}</div>
                            <div>{message["content"]}</div>
                        </div>
                        """, unsafe_allow_html=True)
            
            # Clear chat button - centered
            if len(st.session_state.chat_history) > 1:  # More than just the greeting
                if st.button("🗑️ Clear Chat History"):
                    st.session_state.chat_history = []
                    st.session_state.current_image = None
                    st.session_state.current_image_base64 = None
                    st.rerun()
    
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666;">
        🌍 EcoVision AI - Powered by Computer Vision & GPT-4 Vision<br>
        Making environmental analysis accessible through AI • Now with Interactive Q&A
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()


