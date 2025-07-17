import streamlit as st
import pandas as pd
import json
import os
import sys
from pathlib import Path

sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '../..')))
from genie_core.llm.llm_utils import *
from genie_core.xml_processing.Filechunker import parse_xml_file_to_tree, select_tags

st.set_page_config(layout="wide")

def show_pattern_extractor():
    source_xml_file = st.file_uploader("Upload Source XML", accept_multiple_files=True, type=["xml", "xslt"])
    chunk_index = st.selectbox("Select Depth", range(1, 10), index=4, key="chunk_selector")
    
    # Initialize session state for tags_to_select if not already present
    if 'tags_to_select' not in st.session_state:
        st.session_state.tags_to_select = {}
    if 'pattern_responses' not in st.session_state:
        st.session_state.pattern_responses = {}
    
    if st.button("Submit"):
        if source_xml_file:
            for file in source_xml_file:
                tree = parse_xml_file_to_tree(file)
                tags_to_select = select_tags(tree, st.session_state.tags_to_select, chunk_index)
                st.session_state.tags_to_select = tags_to_select

        if st.session_state.tags_to_select:
            with st.spinner("Please wait while I analyse the XML and identify patterns."):
                progress_text = "Operation in progress. Please wait."
                my_bar = st.progress(0, text=progress_text)
                for i, (tag, xml_content_combined) in enumerate(st.session_state.tags_to_select.items()):
                    my_bar.progress(i / len(st.session_state.tags_to_select), text=progress_text)
                    pattern_name, pattern_description = generate_prompt_from_llm(xml_content_combined)
                    st.session_state.pattern_responses[tag] = [pattern_name, pattern_description]
        return st.session_state.pattern_responses

def generate_prompt_from_llm(content):
    patternAgent = setup_agent("GPT4O")
    current_dir = Path(__file__).resolve().parent
    file_path = current_dir / "../../../config/prompts/generic/default_system_prompt_for_pattern_identification.md"
    with file_path.open() as f:
        pattern_identifier_prompt = f.read()
    prompts = []
    prompts.append({"role":"system", "content": pattern_identifier_prompt})
    user_prompt = {"role": "user", "content": f"Here is the combined XML content - {content}"}
    prompts.append(user_prompt)
    patternAgent.set_prompts(prompts)
    response_content = patternAgent.get_chat_completion()
    response_json = json.loads(response_content.choices[0].message.content)
    pattern_name = response_json.get("pattern_name")
    pattern_description = response_json.get("pattern_description")
    return pattern_name, pattern_description

def display_dataframe():
    if 'pattern_responses' in st.session_state and st.session_state.pattern_responses:
        # Create a DataFrame with separate columns for each element in the array
        data = []
        for tag, values in st.session_state.pattern_responses.items():
            pattern_name, pattern_description = values
            data.append([tag, pattern_name, pattern_description])
        
        df = pd.DataFrame(data, columns=['Tag', 'Pattern Name', 'Pattern Description'])
        st.dataframe(df)

def verify_prompts():
    if st.session_state.pattern_responses:
        selected_tag = st.selectbox("Select a tag to verify", list(st.session_state.pattern_responses.keys()), key="tag_selector", index=0)
        selected_prompt = None
        if selected_tag:
            pattern_name, pattern_description = st.session_state.pattern_responses[selected_tag]
            st.text_area("Pattern Name", pattern_name, height=100, key=f"pattern_name_{selected_tag}")
            st.text_area("Pattern Description", pattern_description, height=100, key=f"pattern_description_{selected_tag}")
            xml_content = st.text_area("Please enter the XML snippet to verify the pattern", height=100)
            if st.button("Verify", key="verifier_submit"):
                response = verify_xml_with_generated_prompt(xml_content, pattern_description)
                st.session_state.verification_response = response
    else:
        st.info("No patterns")
    if 'verification_response' in st.session_state:
        st.info(st.session_state.verification_response)

def verify_xml_with_generated_prompt(xml_content, selected_prompt):
    verifierAgent = setup_agent("GPT4O")
    prompts = []
    system_prompt = {"role": "system", "content": """
                            You are a helpful assistant and expert in XML analysis.
                            Given a XML content and the prompt, your role is to verify the XML using the given prompt."""}
    prompts.append(system_prompt)
    user_prompt = {"role": "user", "content": f"Here is the XML content - {xml_content}"}
    prompts.append(user_prompt)
    user_prompt = {"role": "user", "content": f"Here is the prompt - {selected_prompt}"}
    prompts.append(user_prompt)
    verifierAgent.set_prompts(prompts)
    with st.spinner("Verifying the XML with the given prompt."):
        response = verifierAgent.get_chat_completion()
        return response.choices[0].message.content

def store_patterns():
    pass

tab1, tab2, tab3 = st.tabs(["Extract", "Store", "Verify"])
with tab1:
    patterns = show_pattern_extractor()
    display_dataframe()
        
with tab2:
    store_patterns()
    

with tab3:
    verify_prompts()