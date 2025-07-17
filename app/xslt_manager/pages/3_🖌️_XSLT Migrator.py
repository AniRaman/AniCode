import streamlit as st
import os
import sys
print("Python Path: ", os.getenv("PYTHONPATH"))
if os.getenv("PYTHONPATH") is None:
    sys.path.append(os.path.abspath(os.getcwd()))
    print(os.path.abspath(os.getcwd()))
from genie_core.common.utils import *
from genie_core.llm.llm_utils import initiate_conversation_with_LLM_xslt, subsequent_conversation_with_LLM_xslt, subsequent_conversation_with_LLM_html

inject_custom_css()

st.title("XSLT Migrator")
st.markdown(":blue[Need to simplify a complex MapForce-generated XSLT? The XSLT streamliner does just that. It refines the XSLT, making it more readable and manageable, while also generating clear specifications that help guide the transformation logic, ensuring your XSLT is both efficient and easy to understand.]")

uploaded_file = st.file_uploader("Upload XSLT file", type="xslt")

if uploaded_file:
    xslt_content = uploaded_file.read()
    refined_xslt = refine_xslt(xslt_content)
    llm_response = initiate_conversation_with_LLM_xslt(refined_xslt)
    generated_xslt = st.session_state.generated_xslt
    #st.code(refined_xslt, language="xml")
    st.markdown("### Generated XSLT")
    st.code(generated_xslt, language="xml")
    col1, col2 = st.columns(2)

    with col1:
        st.header("Original XSLT")
        st.code(xslt_content.decode(), language="xml")

    with col2:
        st.header("Refined XSLT")
        st.code(generated_xslt, language="xml")
    
    # st.header("Generated Specifications")
    # llm_response = subsequent_conversation_with_LLM_xslt(refined_xslt)
    # generated_md = st.session_state.generated_md
    # llm_response = subsequent_conversation_with_LLM_html(generated_md)
    # generated_html = st.session_state.generated_html
    # output_placeholder = st.empty()
    # output_placeholder.markdown(generated_html, unsafe_allow_html=True)
