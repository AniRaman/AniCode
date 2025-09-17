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
from genie_core.llm.xslt_spec_generator import XsltSpecGenerator
from genie_core.common.confluence_utils import publish_content, publish_content_with_parent
import json
import tempfile
import pandas as pd

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
uploaded_xslt = st.file_uploader("XSLT File", type=["xslt", "xml"], help="Upload your MapForce-generated XSLT file for processing")

# Main application tabs
tab1, tab2 = st.tabs(["🔧 XSLT Refinement", "📋 Spec Generation"])

# Tab 1: XSLT Refinement
with tab1:
    if uploaded_xslt:
        # Check if this XSLT has already been processed
        xslt_file_id = f"{uploaded_xslt.name}_{uploaded_xslt.size}"

        if 'processed_xslt_id' not in st.session_state or st.session_state.processed_xslt_id != xslt_file_id:
            # New XSLT file or first time processing
            start_time = time.time()

            # Read and process the file
            xslt_content = uploaded_xslt.read()
            original_size = len(xslt_content)

            # Store the original content for spec generation
            st.session_state.original_xslt_content = xslt_content
            st.session_state.processed_xslt_id = xslt_file_id

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

                    # Store results in session state
                    st.session_state.refinement_results = {
                        'original_size': original_size,
                        'generated_size': generated_size,
                        'total_reduction': total_reduction,
                        'processing_time': processing_time,
                        'xslt_content': xslt_content,
                        'generated_xslt': generated_xslt
                    }

            except Exception as e:
                st.error(f"❌ Error processing XSLT: {str(e)}")
                st.info("💡 Tip: Ensure your XSLT file is valid and properly formatted")
        else:
            # XSLT already processed, show cached results
            st.info("✅ XSLT already processed. Showing cached results.")

        # Display results (either fresh or cached)
        if 'refinement_results' in st.session_state:
            results = st.session_state.refinement_results
            original_size = results['original_size']
            generated_size = results['generated_size']
            total_reduction = results['total_reduction']
            processing_time = results['processing_time']
            xslt_content = results['xslt_content']
            generated_xslt = results['generated_xslt']

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

            subtab1, subtab2, subtab3 = st.tabs(["📊 Overview", "📝 Original XSLT", "✨ Optimized XSLT"])

            with subtab1:
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

            with subtab2:
                st.markdown("#### Original XSLT")
                st.code(xslt_content.decode(), language="xml", line_numbers=True)

            with subtab3:
                st.markdown("#### Generated XSLT")
                st.code(generated_xslt, language="xml", line_numbers=True)

                # Download button for generated XSLT
                st.download_button(
                    label="📥 Download Generated XSLT",
                    data=generated_xslt,
                    file_name=f"generated_{uploaded_xslt.name}",
                    mime="application/xml",
                    help="Download the generated XSLT file"
                )
    else:
        st.info("📤 Please upload an XSLT file to start refinement processing.")

# Tab 2: Spec Generation
with tab2:
    st.markdown("### 📋 XML Mapping Specification Generator")
    st.markdown("Upload an XML file to generate detailed mapping specifications showing how XSLT processes each XML element.")

    # XML file uploader
    uploaded_xml = st.file_uploader("XML File", type=["xml"], help="Upload the XML file that corresponds to your XSLT transformation", key="xml_uploader")

    if uploaded_xslt and uploaded_xml:
        # Check if specs have already been generated for these files
        xml_file_id = f"{uploaded_xml.name}_{uploaded_xml.size}"
        xslt_file_id = f"{uploaded_xslt.name}_{uploaded_xslt.size}"
        combined_file_id = f"{xslt_file_id}_{xml_file_id}"

        if 'generated_specs_id' not in st.session_state or st.session_state.generated_specs_id != combined_file_id:
            # New files or first time generating specs
            try:
                with st.spinner("Generating specifications..."):
                    # Use stored original XSLT content (before refinement) for spec generation
                    original_xslt = st.session_state.get('original_xslt_content')
                    if original_xslt is None:
                        # Fallback: read from uploaded file if not in session state
                        original_xslt = uploaded_xslt.getvalue()

                    # Save uploaded files to temporary files
                    with tempfile.NamedTemporaryFile(mode='wb', suffix='.xslt', delete=False) as xslt_temp:
                        xslt_temp.write(original_xslt)
                        xslt_temp_path = xslt_temp.name

                    with tempfile.NamedTemporaryFile(mode='wb', suffix='.xml', delete=False) as xml_temp:
                        xml_temp.write(uploaded_xml.getvalue())
                        xml_temp_path = xml_temp.name

                    # Generate specifications using original XSLT
                    spec_generator = XsltSpecGenerator(xslt_temp_path)
                    spec_generator.load()
                    specs = spec_generator.generate_specs_for_xml(xml_temp_path)

                    # Store specs in session state
                    st.session_state.generated_specs = specs
                    st.session_state.generated_specs_id = combined_file_id

                    # Clean up temporary files
                    os.unlink(xslt_temp_path)
                    os.unlink(xml_temp_path)

            except Exception as e:
                st.error(f"❌ Error generating specifications: {str(e)}")
                st.info("💡 Tip: Ensure both XSLT and XML files are valid and properly formatted")
                # Don't display results if generation failed
                specs = None
        else:
            # Specs already generated, show cached results
            st.info("✅ Specifications already generated. Showing cached results.")

        # Display results (either fresh or cached)
        if 'generated_specs' in st.session_state and st.session_state.generated_specs is not None:
            specs = st.session_state.generated_specs
            st.success(f"✅ {len(specs)} mapping specifications available")

            # Metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Mappings", len(specs))
            with col2:
                element_specs = [s for s in specs if s.get('spec_type') == 'element']
                st.metric("Element Mappings", len(element_specs))
            with col3:
                attr_specs = [s for s in specs if s.get('spec_type') == 'attribute']
                st.metric("Attribute Mappings", len(attr_specs))

            # Display specifications
            st.markdown("---")
            st.markdown("### 🔍 Generated Specifications")

            # Expandable JSON view
            with st.expander("📄 View Full Specification (JSON)", expanded=False):
                st.json(specs)

            # Table view of key information
            st.markdown("#### 📊 Mapping Summary")
            if specs:
                # Create a summary table
                summary_data = []
                for spec in specs:
                    summary_data.append({
                        'Field Name': spec.get('field_name', 'N/A'),
                        'Input XPath': ', '.join(spec.get('inputs', [])) if spec.get('inputs') else 'None',
                        'Output XPath': spec.get('xml_output_node_path', 'N/A'),
                        'Node Type': spec.get('spec_type', 'N/A'),
                        'Remarks': spec.get('remarks', 'N/A')[:100] + '...' if len(spec.get('remarks', '')) > 100 else spec.get('remarks', 'N/A')
                    })

                df = pd.DataFrame(summary_data)
                # Reset index to start from 1
                df.index = df.index + 1
                st.dataframe(df, use_container_width=True, height=400)

            # Download button
            specs_json = json.dumps(specs, indent=2)
            st.download_button(
                label="📥 Download Specifications (JSON)",
                data=specs_json,
                file_name=f"specs_{uploaded_xslt.name}_{uploaded_xml.name}.json",
                mime="application/json",
                help="Download the complete mapping specifications"
            )

            # Confluence Publishing Section
            st.markdown("---")
            st.markdown("### 📋 Publish to Confluence")

            col1, col2 = st.columns(2)
            with col1:
                confluence_page = st.text_input("Page Name", placeholder="e.g., XSLT Mapping Specifications", help="Enter the name for the new page")
            with col2:
                confluence_url = st.text_input("Page URL (Optional)", placeholder="e.g., https://company.atlassian.net/wiki/spaces/SPACE/pages/123456", help="Optional: Confluence page URL where you want to create the page")

            if confluence_page:
                if st.button("📤 Publish to Confluence", type="primary"):
                    try:
                        with st.spinner("Publishing to Confluence..."):
                            # Parse URL if provided
                            space_key = None
                            parent_page_id = None

                            if confluence_url:
                                import re
                                # Extract space from URL: /spaces/SPACE/
                                space_match = re.search(r'/spaces/([^/]+)/', confluence_url)
                                if space_match:
                                    space_key = space_match.group(1)

                                # Extract page ID from URL: pages/123456 or homepageId=123456
                                page_id_match = re.search(r'(?:pages/|homepageId=)(\d+)', confluence_url)
                                if page_id_match:
                                    parent_page_id = page_id_match.group(1)

                                if not space_key:
                                    st.error("❌ Could not extract space from URL. Please check the URL format.")
                                    return

                            # Convert specs to HTML table format
                            html_table = "<table border='1' cellpadding='5' cellspacing='0'>"
                            html_table += "<tr><th>Field Name</th><th>Input XPath</th><th>Output XPath</th><th>Node Type</th><th>Remarks</th></tr>"

                            for spec in specs:
                                html_table += "<tr>"
                                html_table += f"<td>{spec.get('field_name', 'N/A')}</td>"
                                html_table += f"<td>{', '.join(spec.get('inputs', [])) if spec.get('inputs') else 'None'}</td>"
                                html_table += f"<td>{spec.get('xml_output_node_path', 'N/A')}</td>"
                                html_table += f"<td>{spec.get('spec_type', 'N/A')}</td>"
                                html_table += f"<td>{spec.get('remarks', 'N/A')}</td>"
                                html_table += "</tr>"

                            html_table += "</table>"

                            # Publish to Confluence
                            if space_key and parent_page_id:
                                # Create page under parent
                                publish_content_with_parent(space_key, parent_page_id, confluence_page, html_table)
                                st.success(f"✅ Successfully published specifications to Confluence page: {confluence_page} under parent page")
                            elif space_key:
                                # Create page at root of space
                                publish_content(space_key, confluence_page, html_table)
                                st.success(f"✅ Successfully published specifications to Confluence page: {confluence_page} in space {space_key}")
                            else:
                                st.error("❌ Please provide a valid Confluence URL or contact admin for space configuration")

                    except Exception as e:
                        st.error(f"❌ Error publishing to Confluence: {str(e)}")
                        st.info("💡 Tip: Check your Confluence credentials and URL format")
            else:
                st.info("💡 Enter a page name to enable publishing")

    elif uploaded_xslt and not uploaded_xml:
        st.info("📤 Please upload an XML file to generate mapping specifications.")
        st.markdown("**Note:** The same XSLT file from the refinement tab will be used for specification generation.")
    elif not uploaded_xslt:
        st.warning("⚠️ Please upload an XSLT file first (in the main upload section above).")
    else:
        st.info("📤 Please upload both XSLT and XML files to generate mapping specifications.")