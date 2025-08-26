import streamlit as st
import os
import sys
import time
import difflib
from datetime import datetime

print("Python Path: ", os.getenv("PYTHONPATH"))
if os.getenv("PYTHONPATH") is None:
    sys.path.append(os.path.abspath(os.getcwd()))
    print(os.path.abspath(os.getcwd()))

from genie_core.common.utils import *
from genie_core.llm.llm_utils import initiate_conversation_with_LLM_xslt

inject_custom_css()

# Custom CSS for enhanced UI
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #1f77b4;
        font-size: 3rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
        background: linear-gradient(90deg, #1f77b4, #17becf);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .subtitle {
        text-align: center;
        color: #666;
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        box-shadow: 0 8px 32px rgba(31, 38, 135, 0.37);
        backdrop-filter: blur(8px);
        border: 1px solid rgba(255, 255, 255, 0.18);
        margin: 0.5rem 0;
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    
    .metric-label {
        font-size: 1rem;
        opacity: 0.9;
    }
    
    .success-card {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
    }
    
    .reduction-card {
        background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
    }
    
    .speed-card {
        background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
        color: #333;
    }
    
    .optimization-badge {
        background: #28a745;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 15px;
        font-size: 0.8rem;
        margin: 0.2rem;
        display: inline-block;
    }
    
    .feature-highlight {
        background: rgba(31, 119, 180, 0.1);
        border-left: 4px solid #1f77b4;
        padding: 1rem;
        margin: 0.5rem;
        border-radius: 0 10px 10px 0;
        min-height: 120px;
        display: flex;
        flex-direction: column;
        justify-content: center;

        word-wrap: break-word;
    }
    
    .feature-highlight h4 {
        margin: 0.5rem 0;
        font-size: 0.9rem;
        line-height: 1.3;
        word-break: keep-all;
        hyphens: none;
    }
    
    .feature-highlight p {
        margin: 0.3rem 0 0 0;
        font-size: 0.8rem;
        line-height: 1.4;
        color: #666;
        word-break: keep-all;
        hyphens: none;
    }
    
    .upload-area {
        border: 2px dashed #1f77b4;
        border-radius: 15px;
        padding: 2rem;
        text-align: center;
        background: rgba(31, 119, 180, 0.05);
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Header Section
st.markdown('<h1 class="main-header">🚀 XSLT Migrator Pro</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Transform Complex MapForce XSLT into Clean, Optimized Code</p>', unsafe_allow_html=True)

# Attractive selling points
col1, col2, col3, col4= st.columns(4)

with col1:
    st.markdown("""
    <div class="feature-highlight">
        <h4>🏆 High Optimization</h4>
        <p>Up to 77% size reduction</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="feature-highlight">
        <h4>📊 Detailed Metrics</h4>
        <p>Real-time analytics</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="feature-highlight">
        <h4>🔧 Smart Processing</h4>
        <p>Handles complex patterns</p>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div class="feature-highlight">
        <h4>🎨 Clean Output</h4>
        <p>Readable & maintainable</p>
    </div>
    """, unsafe_allow_html=True)

# File Upload Section
st.markdown("### 📁 Upload Your XSLT File")
uploaded_file = st.file_uploader("", type=["xslt", "xml"], help="Upload your MapForce-generated XSLT file for processing")


if uploaded_file:
    start_time = time.time()
    
    # Read and process the file
    xslt_content = uploaded_file.read()
    original_size = len(xslt_content)
    
    # Process XSLT with spinner
    try:
        with st.spinner("Processing XSLT..."):
            refined_xslt = refine_xslt(xslt_content)
            llm_response = initiate_conversation_with_LLM_xslt(refined_xslt)
            generated_xslt = st.session_state.generated_xslt
            
            # Calculate metrics
            generated_size = len(generated_xslt)
            total_reduction = ((original_size - generated_size) / original_size * 100) if original_size > 0 else 0
            
            processing_time = time.time() - start_time
            
        # Metrics Dashboard
        st.markdown("---")
        st.markdown("## 📈 Results")
        
        # Top-level metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card success-card">
                <div class="metric-value">{total_reduction:.1f}%</div>
                <div class="metric-label">Size Reduction</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card speed-card">
                <div class="metric-value">{processing_time:.2f}s</div>
                <div class="metric-label">Processing Time</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{generated_size:,}</div>
                <div class="metric-label">Final Size (chars)</div>
            </div>
            """, unsafe_allow_html=True)
        
        
        # Side-by-side comparison
        st.markdown("---")
        st.markdown("## 🔄 Before & After Comparison")
        
        tab1, tab2, tab3 = st.tabs(["📊 Overview", "📝 Original XSLT", "✨ Optimized XSLT"])
        
        with tab1:
            # Visual size comparison
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("#### 📉 Size Comparison")
                size_data = {
                    "Version": ["Original", "Generated"],
                    "Size (chars)": [original_size, generated_size],
                    "Reduction %": [0, total_reduction]
                }
                st.bar_chart(data=size_data, x="Version", y="Size (chars)")
            
            with col2:
                st.markdown("#### ⚡ Performance Summary")
                st.write(f"**Processing Speed**: {original_size/processing_time:.0f} chars/second")
                st.write(f"**Reduction Ratio**: {total_reduction/processing_time:.1f}% reduction/second")
                st.write(f"**Memory Efficiency**: {(original_size-generated_size)//1024:.1f}KB saved")
        
        with tab2:
            st.markdown("#### Original XSLT")
            st.code(xslt_content.decode(), language="xml", line_numbers=True)
        
        with tab3:
            st.markdown("#### Generated XSLT")
            st.code(generated_xslt, language="xml", line_numbers=True)
            
            # Download button for generated XSLT
            st.download_button(
                label="📥 Download Generated XSLT",
                data=generated_xslt,
                file_name=f"generated_{uploaded_file.name}",
                mime="application/xml",
                help="Download the generated XSLT file"
            )
        
    except Exception as e:
        st.error(f"❌ Error processing XSLT: {str(e)}")
        st.info("💡 Tip: Ensure your XSLT file is valid and properly formatted")

