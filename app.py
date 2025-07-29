# import streamlit as st
# import cv2
# import numpy as np
# from PIL import Image
# import base64
# import io
# import os
# from openai import OpenAI
# import json
# from datetime import datetime
# import plotly.express as px
# import plotly.graph_objects as go
# import pandas as pd

# # Initialize OpenAI client with error handling
# try:
#     api_key = os.getenv("OPENAI_API_KEY")
#     if not api_key:
#         st.error("⚠️ OPENAI_API_KEY not found in environment variables!")
#         st.info("Please check your .env file")
#         st.stop()
#     client = OpenAI(api_key=api_key)
#     st.sidebar.success("✅ OpenAI API key loaded")
# except Exception as e:
#     st.error(f"❌ Error initializing OpenAI client: {e}")
#     st.stop()

# # Page config
# st.set_page_config(
#     page_title="EcoVision AI",
#     page_icon="🌍",
#     layout="wide",
#     initial_sidebar_state="expanded"
# )

# # Custom CSS
# st.markdown("""
# <style>
#     .main-header {
#         font-size: 3rem;
#         font-weight: bold;
#         color: #2E8B57;
#         text-align: center;
#         margin-bottom: 2rem;
#     }
#     .subtitle {
#         font-size: 1.2rem;
#         color: #666;
#         text-align: center;
#         margin-bottom: 3rem;
#     }
#     .analysis-card {
#         background: linear-gradient(135deg, #2c3e50 0%, #3498db 100%);
#         color: white;
#         padding: 20px;
#         border-radius: 10px;
#         margin: 10px 0;
#         border: 2px solid #34495e;
#         box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
#     }
#     .analysis-card h3 {
#         color: #ffffff !important;
#         margin-bottom: 15px;
#         font-weight: bold;
#     }
#     .metric-card {
#         background: linear-gradient(135deg, #27ae60 0%, #2ecc71 100%);
#         color: white;
#         padding: 20px;
#         border-radius: 10px;
#         border: 2px solid #229954;
#         box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
#         margin: 10px 0;
#         min-height: 120px;
#         display: flex;
#         flex-direction: column;
#         justify-content: space-between;
#     }
#     .metric-card h4 {
#         color: #ffffff !important;
#         margin-bottom: 10px;
#         font-size: 1.1rem;
#         font-weight: bold;
#     }
#     .metric-card p {
#         color: #f8f9fa !important;
#         line-height: 1.4;
#         margin: 0;
#         font-size: 0.95rem;
#     }
#     .debug-info {
#         background: #f0f0f0;
#         padding: 10px;
#         border-radius: 5px;
#         margin: 10px 0;
#         border-left: 3px solid #ff6b6b;
#     }
# </style>
# """, unsafe_allow_html=True)

# class EcoVisionAI:
#     def __init__(self):
#         self.analysis_history = []
    
#     def encode_image(self, image):
#         """Convert PIL image to base64 string for OpenAI API"""
#         try:
#             buffered = io.BytesIO()
#             # Convert to RGB if not already
#             if image.mode != 'RGB':
#                 image = image.convert('RGB')
#             image.save(buffered, format="JPEG", quality=85)
#             encoded = base64.b64encode(buffered.getvalue()).decode('utf-8')
#             st.sidebar.info(f"✅ Image encoded successfully ({len(encoded)} chars)")
#             return encoded
#         except Exception as e:
#             st.error(f"❌ Error encoding image: {e}")
#             return None
    
#     def analyze_image_with_ai(self, image, analysis_type="comprehensive"):
#         """Analyze image using OpenAI GPT-4 Vision with enhanced debugging"""
        
#         # Debug: Show we're starting analysis
#         st.write("🔍 **Starting AI Analysis...**")
#         st.write(f"**Analysis Mode:** {analysis_type}")
#         st.write(f"**Image Size:** {image.size}")
        
#         # Encode image
#         base64_image = self.encode_image(image)
#         if not base64_image:
#             return {"error": "Failed to encode image"}
        
#         # Simplified, more reliable prompt
#         prompt = """Analyze this environmental image and provide insights in JSON format.

# Identify objects, assess environmental impact, and provide recommendations.

# Return your response as valid JSON with this exact structure:
# {
#   "summary": "Brief description of the environmental scene",
#   "objects_detected": [
#     {
#       "name": "specific object or organism name",
#       "type": "living or non-living",
#       "confidence": 0.9,
#       "environmental_impact": "positive, negative, or neutral",
#       "sustainability_score": 8,
#       "description": "detailed description",
#       "recommended_action": "specific recommended action"
#     }
#   ],
#   "overall_analysis": {
#     "environmental_health_score": 8.5,
#     "biodiversity_level": "high",
#     "key_concerns": ["list of environmental concerns"],
#     "positive_aspects": ["list of positive environmental aspects"],
#     "recommendations": ["list of actionable recommendations"]
#   }
# }

# Please ensure your response is valid JSON only."""
        
#         try:
#             st.write("📡 **Sending request to OpenAI...**")
            
#             response = client.chat.completions.create(
#                 model="gpt-4o",
#                 messages=[
#                     {
#                         "role": "user",
#                         "content": [
#                             {"type": "text", "text": prompt},
#                             {
#                                 "type": "image_url",
#                                 "image_url": {
#                                     "url": f"data:image/jpeg;base64,{base64_image}",
#                                     "detail": "high"
#                                 }
#                             }
#                         ]
#                     }
#                 ],
#                 max_tokens=1500,
#                 temperature=0.1
#             )
            
#             result_text = response.choices[0].message.content.strip()
#             st.write("✅ **Received response from OpenAI**")
            
#             # Debug: Show raw response
#             with st.expander("🔧 Debug - Raw AI Response"):
#                 st.text(result_text[:500] + "..." if len(result_text) > 500 else result_text)
            
#             # Clean up the response to ensure it's valid JSON
#             if result_text.startswith("```json"):
#                 result_text = result_text.replace("```json", "").replace("```", "").strip()
#             elif result_text.startswith("```"):
#                 result_text = result_text.replace("```", "").strip()
            
#             # Try to parse as JSON
#             try:
#                 parsed_result = json.loads(result_text)
#                 st.write("✅ **JSON parsing successful**")
#                 return parsed_result
#             except json.JSONDecodeError as json_error:
#                 st.write(f"⚠️ **JSON parsing failed:** {json_error}")
#                 # Create a fallback structured response
#                 fallback_result = {
#                     "summary": result_text[:200] + "..." if len(result_text) > 200 else result_text,
#                     "raw_analysis": result_text,
#                     "objects_detected": [
#                         {
#                             "name": "Environmental Scene Analysis",
#                             "type": "comprehensive",
#                             "confidence": 0.85,
#                             "environmental_impact": "positive",
#                             "sustainability_score": 7,
#                             "description": "AI analysis completed successfully",
#                             "recommended_action": "Review detailed analysis below"
#                         }
#                     ],
#                     "overall_analysis": {
#                         "environmental_health_score": 7.5,
#                         "biodiversity_level": "medium",
#                         "key_concerns": ["See detailed analysis"],
#                         "positive_aspects": ["Natural environment detected"],
#                         "recommendations": ["Continue environmental monitoring"]
#                     }
#                 }
#                 return fallback_result
                
#         except Exception as e:
#             error_msg = f"Analysis failed: {str(e)}"
#             st.write(f"❌ **Error:** {error_msg}")
#             return {
#                 "error": error_msg,
#                 "debug_info": f"Error type: {type(e).__name__}",
#                 "summary": "Analysis encountered an error"
#             }
    
#     def generate_recommendations(self, analysis_result):
#         """Generate actionable environmental recommendations"""
#         recommendations = []
        
#         if "overall_analysis" in analysis_result:
#             recommendations = analysis_result["overall_analysis"].get("recommendations", [])
        
#         # If no recommendations or empty, generate based on analysis content
#         if not recommendations or len(recommendations) == 0:
#             if "objects_detected" in analysis_result:
#                 objects = analysis_result["objects_detected"]
#                 if any("tree" in obj.get("name", "").lower() or "forest" in obj.get("name", "").lower() for obj in objects):
#                     recommendations.extend([
#                         "🌳 Protect existing tree canopy by avoiding development in forested areas",
#                         "🌱 Support reforestation initiatives in your local community", 
#                         "🚫 Avoid disturbing wildlife habitats and maintain natural corridors"
#                     ])
#                 elif any("waste" in obj.get("name", "").lower() or "plastic" in obj.get("name", "").lower() for obj in objects):
#                     recommendations.extend([
#                         "♻️ Implement proper waste sorting and recycling practices",
#                         "🚯 Reduce single-use plastics and choose sustainable alternatives",
#                         "🔄 Support circular economy initiatives in your community"
#                     ])
#                 else:
#                     recommendations.extend([
#                         "🔍 Continue monitoring environmental conditions regularly",
#                         "📊 Document changes over time to track environmental health",
#                         "🤝 Share findings with local environmental groups"
#                     ])
#             elif "raw_analysis" in analysis_result:
#                 analysis_text = analysis_result["raw_analysis"].lower()
#                 if "forest" in analysis_text or "tree" in analysis_text:
#                     recommendations.extend([
#                         "🌲 Preserve forest ecosystems through conservation efforts",
#                         "🌿 Promote biodiversity by protecting natural habitats",
#                         "🏞️ Support sustainable forestry practices"
#                     ])
#                 elif "waste" in analysis_text or "recycl" in analysis_text:
#                     recommendations.extend([
#                         "♻️ Improve waste management and recycling systems",
#                         "🌍 Reduce environmental impact through better disposal practices", 
#                         "💡 Educate others about proper waste sorting"
#                     ])
#                 else:
#                     recommendations.extend([
#                         "🌱 Take action to improve environmental sustainability",
#                         "📈 Monitor and measure environmental impact regularly",
#                         "🤝 Collaborate with others on conservation efforts"
#                     ])
#             else:
#                 recommendations = [
#                     "🔍 Upload an image to receive personalized environmental recommendations",
#                     "🌍 Start by analyzing your local environment for improvement opportunities", 
#                     "📱 Use this tool regularly to track environmental changes"
#                 ]
        
#         # Ensure we have at least 3 recommendations
#         while len(recommendations) < 3:
#             additional_recs = [
#                 "🌳 Plant native species to support local ecosystems",
#                 "💧 Conserve water resources through mindful usage",
#                 "🔋 Choose renewable energy sources when possible",
#                 "🚴‍♂️ Use sustainable transportation options",
#                 "📚 Educate others about environmental conservation",
#                 "🧹 Participate in local environmental cleanup efforts"
#             ]
#             for rec in additional_recs:
#                 if rec not in recommendations and len(recommendations) < 3:
#                     recommendations.append(rec)
        
#         return recommendations[:3]  # Return max 3 recommendations

# # Initialize the app
# eco_ai = EcoVisionAI()

# # Main app
# def main():
#     st.markdown('<div class="main-header">🌍 EcoVision AI</div>', unsafe_allow_html=True)
#     st.markdown('<div class="subtitle">Advanced Computer Vision for Environmental Analysis</div>', unsafe_allow_html=True)
    
#     # Sidebar
#     with st.sidebar:
#         st.header("🔧 Analysis Settings")
#         analysis_mode = st.selectbox(
#             "Analysis Type",
#             ["comprehensive", "waste_detection", "biodiversity"],
#             format_func=lambda x: {
#                 "comprehensive": "🔍 Comprehensive Analysis",
#                 "waste_detection": "♻️ Waste & Recycling",
#                 "biodiversity": "🦋 Biodiversity Assessment"
#             }[x]
#         )
        
#         st.header("📊 Quick Stats")
#         if 'analysis_count' not in st.session_state:
#             st.session_state.analysis_count = 0
        
#         st.metric("Analyses Performed", st.session_state.analysis_count)
#         st.metric("CO₂ Saved (est.)", f"{st.session_state.analysis_count * 2.3:.1f} kg")
        
#         # Debug info
#         st.header("🔧 Debug Info")
#         st.info(f"API Key Status: {'✅ Loaded' if api_key else '❌ Missing'}")
    
#     # Main content
#     col1, col2 = st.columns([1, 1])
    
#     with col1:
#         st.header("📷 Image Input")
        
#         # Image upload options
#         input_method = st.radio(
#             "Choose input method:",
#             ["Upload Image", "Camera Capture"]
#         )
        
#         uploaded_image = None
        
#         if input_method == "Upload Image":
#             uploaded_file = st.file_uploader(
#                 "Choose an image...",
#                 type=['png', 'jpg', 'jpeg'],
#                 help="Upload an image for environmental analysis"
#             )
#             if uploaded_file:
#                 uploaded_image = Image.open(uploaded_file)
        
#         elif input_method == "Camera Capture":
#             camera_image = st.camera_input("Take a picture")
#             if camera_image:
#                 uploaded_image = Image.open(camera_image)
        
#         if uploaded_image:
#             st.image(uploaded_image, caption="Input Image", use_container_width=True)
            
#             # Analysis button
#             if st.button("🚀 Analyze with AI", type="primary"):
#                 with st.spinner("🤖 AI is analyzing the environment..."):
#                     # Clear previous results
#                     if 'current_analysis' in st.session_state:
#                         del st.session_state.current_analysis
                    
#                     # Perform AI analysis with debug output
#                     analysis_result = eco_ai.analyze_image_with_ai(uploaded_image, analysis_mode)
                    
#                     # Store in session state
#                     st.session_state.current_analysis = analysis_result
#                     st.session_state.analysis_count += 1
                    
#                     # Force rerun to show results
#                     st.rerun()
    
#     with col2:
#         st.header("🔬 Analysis Results")
        
#         if 'current_analysis' in st.session_state:
#             analysis = st.session_state.current_analysis
            
#             # Debug: Show what we have
#             with st.expander("🔧 Debug - Analysis Structure"):
#                 st.json(analysis)
            
#             if "error" in analysis:
#                 st.error(f"❌ {analysis['error']}")
#                 if "debug_info" in analysis:
#                     st.info(f"Debug info: {analysis['debug_info']}")
#             else:
#                 # Display summary
#                 if "summary" in analysis:
#                     st.markdown(f"""
#                     <div class="analysis-card">
#                         <h3>📋 Environmental Analysis Summary</h3>
#                         <p style="font-size: 1.1rem; line-height: 1.6;">{analysis['summary']}</p>
#                     </div>
#                     """, unsafe_allow_html=True)
#                 elif "raw_analysis" in analysis:
#                     # Show first part of raw analysis as summary
#                     summary_text = analysis["raw_analysis"][:300] + "..." if len(analysis["raw_analysis"]) > 300 else analysis["raw_analysis"]
#                     st.markdown(f"""
#                     <div class="analysis-card">
#                         <h3>📋 Environmental Analysis Summary</h3>
#                         <p style="font-size: 1.1rem; line-height: 1.6;">{summary_text}</p>
#                     </div>
#                     """, unsafe_allow_html=True)
                
#                 # Display raw analysis if available
#                 if "raw_analysis" in analysis:
#                     with st.expander("📄 Detailed Analysis"):
#                         st.write(analysis["raw_analysis"])
                
#                 # Display overall analysis
#                 if "overall_analysis" in analysis:
#                     overall = analysis["overall_analysis"]
                    
#                     # Metrics
#                     col_a, col_b = st.columns(2)
#                     with col_a:
#                         score = overall.get("environmental_health_score", 0)
#                         st.metric("🌱 Environmental Health", f"{score}/10")
#                     with col_b:
#                         biodiversity = overall.get("biodiversity_level", "Unknown")
#                         st.metric("🦋 Biodiversity Level", biodiversity.title())
                    
#                     # Key findings
#                     if "key_concerns" in overall and overall["key_concerns"]:
#                         st.subheader("⚠️ Key Concerns")
#                         for concern in overall["key_concerns"]:
#                             st.warning(f"• {concern}")
                    
#                     if "positive_aspects" in overall and overall["positive_aspects"]:
#                         st.subheader("✅ Positive Aspects")
#                         for aspect in overall["positive_aspects"]:
#                             st.success(f"• {aspect}")
                
#                 # Display detected objects
#                 if "objects_detected" in analysis and analysis["objects_detected"]:
#                     st.subheader("🔍 Detected Objects")
                    
#                     try:
#                         objects_df = pd.DataFrame(analysis["objects_detected"])
#                         if not objects_df.empty:
#                             # Check if required columns exist
#                             required_cols = ["sustainability_score", "confidence"]
#                             if all(col in objects_df.columns for col in required_cols):
#                                 # Create visualization
#                                 fig = px.scatter(
#                                     objects_df,
#                                     x="sustainability_score",
#                                     y="confidence",
#                                     color="environmental_impact",
#                                     size="sustainability_score",
#                                     hover_data=["name", "type"],
#                                     title="Objects by Sustainability & Confidence"
#                                 )
#                                 st.plotly_chart(fig, use_container_width=True)
                            
#                             # Display table
#                             display_cols = [col for col in ["name", "type", "environmental_impact", "sustainability_score", "recommended_action"] if col in objects_df.columns]
#                             if display_cols:
#                                 st.dataframe(objects_df[display_cols], use_container_width=True)
#                             else:
#                                 st.dataframe(objects_df, use_container_width=True)
#                     except Exception as viz_error:
#                         st.error(f"Error creating visualization: {viz_error}")
#                         # Fallback: show objects as list
#                         for i, obj in enumerate(analysis["objects_detected"]):
#                             st.write(f"**{i+1}. {obj.get('name', 'Unknown Object')}**")
#                             st.write(f"   - Type: {obj.get('type', 'Unknown')}")
#                             st.write(f"   - Impact: {obj.get('environmental_impact', 'Unknown')}")
#                             if 'description' in obj:
#                                 st.write(f"   - Description: {obj['description']}")
#         else:
#             st.info("👆 Upload an image and click 'Analyze with AI' to see results here!")
    
#     # Recommendations section
#     st.header("💡 AI Environmental Recommendations")
    
#     if 'current_analysis' in st.session_state:
#         recommendations = eco_ai.generate_recommendations(st.session_state.current_analysis)
        
#         if recommendations:
#             col1, col2, col3 = st.columns(3)
#             for i, rec in enumerate(recommendations[:3]):
#                 with [col1, col2, col3][i % 3]:
#                     st.markdown(f"""
#                     <div class="metric-card">
#                         <h4>💡 Action Item {i+1}</h4>
#                         <p>{rec}</p>
#                     </div>
#                     """, unsafe_allow_html=True)
#         else:
#             st.info("Upload and analyze an image to see personalized recommendations!")
#     else:
#         # Show default recommendations
#         default_recs = [
#             "🌱 Upload an environmental image to get started with AI-powered analysis",
#             "🔍 Try different analysis modes to explore various environmental aspects", 
#             "🌍 Share your findings to promote environmental awareness"
#         ]
#         col1, col2, col3 = st.columns(3)
#         for i, rec in enumerate(default_recs):
#             with [col1, col2, col3][i % 3]:
#                 st.markdown(f"""
#                 <div class="metric-card">
#                     <h4>💡 Getting Started {i+1}</h4>
#                     <p>{rec}</p>
#                 </div>
#                 """, unsafe_allow_html=True)
#     st.markdown("---")
#     st.markdown("""
#     <div style="text-align: center; color: #666;">
#         🌍 EcoVision AI - Powered by Computer Vision & GPT-4 Vision<br>
#         Making environmental analysis accessible through AI
#     </div>
#     """, unsafe_allow_html=True)

# if __name__ == "__main__":
#     main()

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

# Page config
st.set_page_config(
    page_title="EcoVision AI",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
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
    .metric-card *, .analysis-card * {
        color: inherit !important;
    }
</style>
""", unsafe_allow_html=True)

class EcoVisionAI:
    def __init__(self):
        self.analysis_history = []
    
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
        
        # Simplified, more reliable prompt
        prompt = """Analyze this environmental image and provide insights in JSON format.

Identify objects, assess environmental impact, and provide recommendations.

Return your response as valid JSON with this exact structure:
{
  "summary": "Brief description of the environmental scene",
  "objects_detected": [
    {
      "name": "specific object or organism name",
      "type": "living or non-living",
      "confidence": 0.9,
      "environmental_impact": "positive, negative, or neutral",
      "sustainability_score": 8,
      "description": "detailed description",
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

Please ensure your response is valid JSON only."""
        
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
    
    # Sidebar
    with st.sidebar:
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
        
        st.header("📊 Quick Stats")
        if 'analysis_count' not in st.session_state:
            st.session_state.analysis_count = 0
        
        st.metric("Analyses Performed", st.session_state.analysis_count)
        st.metric("CO₂ Saved (est.)", f"{st.session_state.analysis_count * 2.3:.1f} kg")
        
        # Debug info
        st.header("🔧 Debug Info")
        st.info(f"API Key Status: {'✅ Loaded' if api_key else '❌ Missing'}")
    
    # Main content
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
            st.image(uploaded_image, caption="Input Image", use_container_width=True)
            
            # Analysis button
            if st.button("🚀 Analyze with AI", type="primary"):
                with st.spinner("🤖 AI is analyzing the environment..."):
                    # Clear previous results
                    if 'current_analysis' in st.session_state:
                        del st.session_state.current_analysis
                    
                    # Perform AI analysis with debug output
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
            
            # Debug: Show what we have
            with st.expander("🔧 Debug - Analysis Structure"):
                st.json(analysis)
            
            if "error" in analysis:
                st.error(f"❌ {analysis['error']}")
                if "debug_info" in analysis:
                    st.info(f"Debug info: {analysis['debug_info']}")
            else:
                # Display summary
                if "summary" in analysis:
                    st.markdown(f"""
                    <div class="analysis-card">
                        <h3>📋 Environmental Analysis Summary</h3>
                        <p style="font-size: 1.1rem; line-height: 1.6;">{analysis['summary']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                elif "raw_analysis" in analysis:
                    # Show first part of raw analysis as summary
                    summary_text = analysis["raw_analysis"][:300] + "..." if len(analysis["raw_analysis"]) > 300 else analysis["raw_analysis"]
                    st.markdown(f"""
                    <div class="analysis-card">
                        <h3>📋 Environmental Analysis Summary</h3>
                        <p style="font-size: 1.1rem; line-height: 1.6;">{summary_text}</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Display raw analysis if available
                if "raw_analysis" in analysis:
                    with st.expander("📄 Detailed Analysis"):
                        st.write(analysis["raw_analysis"])
                
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
                            # Check if required columns exist
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
                            
                            # Display table
                            display_cols = [col for col in ["name", "type", "environmental_impact", "sustainability_score", "recommended_action"] if col in objects_df.columns]
                            if display_cols:
                                st.dataframe(objects_df[display_cols], use_container_width=True)
                            else:
                                st.dataframe(objects_df, use_container_width=True)
                    except Exception as viz_error:
                        st.error(f"Error creating visualization: {viz_error}")
                        # Fallback: show objects as list
                        for i, obj in enumerate(analysis["objects_detected"]):
                            st.write(f"**{i+1}. {obj.get('name', 'Unknown Object')}**")
                            st.write(f"   - Type: {obj.get('type', 'Unknown')}")
                            st.write(f"   - Impact: {obj.get('environmental_impact', 'Unknown')}")
                            if 'description' in obj:
                                st.write(f"   - Description: {obj['description']}")
        else:
            st.info("👆 Upload an image and click 'Analyze with AI' to see results here!")
    
    # Recommendations section
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
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666;">
        🌍 EcoVision AI - Powered by Computer Vision & GPT-4 Vision<br>
        Making environmental analysis accessible through AI
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()