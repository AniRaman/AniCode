import streamlit as st
import sys
import os
import tempfile
import pandas as pd
from pathlib import Path
import json

# Add the parent directory to the system path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '../..')))

# Import necessary modules
from genie_core.hive import Hive
from genie_core.hive.repl import run_gap_analyser
from agents import xml_handler_agent
from genie_core.llm.llm_utils import setup_agent
from genie_core.xml_processing.xml_utils import list_elements, chunk_xml_by_tags
from genie_core.database.sql_db_utils import connect_to_db, insert_data
from genie_core.llm.TokenCostCalculator import TokenCostCalculator

# Streamlit page configuration
st.set_page_config(layout="wide")

# Initialize session state variables
if 'tags_to_select' not in st.session_state:
    st.session_state.tags_to_select = {}

if 'pattern_responses' not in st.session_state:
    st.session_state.pattern_responses = {}

if 'gpt_model_used' not in st.session_state:
    st.session_state.gpt_model_used = None

if 'number_of_calls_to_llm' not in st.session_state:
    st.session_state.number_of_calls_to_llm = 0

if 'total_cost_per_tool' not in st.session_state:
    st.session_state.total_cost_per_tool = 0

shared_agent = setup_agent("GPT4O")
st.session_state.gpt_model_used = "GPT4O"

# Function to verify XML with a generated prompt
def verify_xml_with_generated_prompt(xml_content, selected_prompt):
    current_dir = Path(__file__).resolve().parent
    file_path = current_dir / "../../../genie_core/config/prompts/generic/default_system_prompt_for_pattern_verification.md"
    with file_path.open() as f:
        pattern_verifier_prompt = f.read()

    prompts = [
        {"role": "user", "content": pattern_verifier_prompt},
        {"role": "user", "content": f"Here is the XML content - {xml_content}"},
        {"role": "user", "content": f"Here is the prompt - {selected_prompt}"}
    ]
    shared_agent.set_prompts(prompts)
    with st.spinner("Verifying the XML with the given prompt."):
        cost, response = shared_agent.get_chat_completion()
        st.session_state.number_of_calls_to_llm += 1
        st.session_state.total_cost_per_tool += cost    
        # Extract the JSON content
        raw_content = response.choices[0].message.content

        
        # Remove the prefix (e.g., "json\n" or "```json\n") and trailing backticks
        if raw_content.startswith("json\n") or raw_content.startswith("```json\n"):
            raw_content = raw_content[raw_content.index("{"):]  # Remove everything before the first '{'
        
        # Remove trailing backticks
        raw_content = raw_content.rstrip("```")
        return raw_content

# Function to generate prompts from LLM
def generate_prompt_from_llm(content):    
    current_dir = Path(__file__).resolve().parent
    file_path = current_dir / "../../../genie_core/config/prompts/generic/default_system_prompt_for_pattern_identification.md"
    with file_path.open() as f:
        pattern_identifier_prompt = f.read()
    prompts = [
        {"role": "system", "content": pattern_identifier_prompt},
        {"role": "user", "content": f"Here is the combined XML content - {content}"}
    ]
    shared_agent.set_prompts(prompts)
    cost, response_content = shared_agent.get_chat_completion()
    st.session_state.total_cost_per_tool += cost
    st.session_state.number_of_calls_to_llm += 1
    response_json = json.loads(response_content.choices[0].message.content)
    patterns = [
        (pattern.get("pattern_path"), pattern.get("pattern_name"), pattern.get("pattern_description"), pattern.get("pattern_prompt"))
        for pattern in response_json
    ]
    return patterns

# Function to display patterns in a DataFrame
def display_patterns():
    # st.session_state.pattern_responses = {'ContactInfoList/ContactInfo': ['CONTACT_INFO_STRUCTURE', 'Defines the structure for contact information including ID, email, and phone details.', "Verify that each <ContactInfo> element contains a <ContactInfoID>, an <EmailAddress> with <EmailAddressText>, and a <Phone> with <ContactTypeText> and <PhoneNumber>. Reply with 'YES' if all elements are present and correctly structured, or 'NO' if any element is missing or incorrectly structured, providing a detailed reason to support your conclusion.", False], 'DatedMarketingSegmentList/DatedMarketingSegment': ['MARKETING_SEGMENT_DETAILS', 'Contains details of a dated marketing segment including arrival, departure, carrier code, and flight number.', "Verify that each <DatedMarketingSegment> contains <Arrival> and <Dep> elements with <AircraftScheduledDateTime> and <IATA_LocationCode>, a <CarrierDesigCode>, a <DatedMarketingSegmentId>, a <DatedOperatingSegmentRefId>, and a <MarketingCarrierFlightNumberText>. Reply with 'YES' if all elements are present and correctly structured, or 'NO' if any element is missing or incorrectly structured, providing a detailed reason to support your conclusion.", False], 'DatedOperatingLegList/DatedOperatingLeg': ['DatedOperatingLeg_Structure', 'Defines the structure of a dated operating leg with arrival and departure details, including scheduled times and location codes.', "Verify that each <DatedOperatingLeg> contains an <Arrival> and <Dep> section with <AircraftScheduledDateTime> and <IATA_LocationCode> elements, as well as a <CarrierAircraftType> with a <CarrierAircraftTypeCode>. Ensure the presence of a <DatedOperatingLegID>. Reply with 'YES' if the structure is correct, or 'NO' if any element is missing or incorrectly structured, providing details of the discrepancy.", False]}
    data = [
        [tag] + values[:-1]  # Exclude the last element (Verified) from the values
        for tag, values in st.session_state.pattern_responses.items()
    ]
    if data:
        # st.info(data)
        df = pd.DataFrame(data, columns=['XPATH', 'Name', 'Description', 'Prompt'])  # Exclude 'Verified' from columns
        st.markdown(":blue[Here are the patterns identified for the given XML]")
        st.dataframe(df, hide_index=True)

# Function to overwrite a prompt with hints
def overwrite_prompt_with_hints(selected_tag, pattern_name, pattern_description, hints):
    # Overwrite the prompt with the provided hints
    new_prompt = hints
    st.session_state.pattern_responses[selected_tag] = [pattern_name, pattern_description, new_prompt, False]
    st.success(f"Prompt for tag '{selected_tag}' has been overwritten.")

# Function to improve a prompt
def improve_prompt(selected_tag, pattern_name, pattern_description, pattern_prompt, hints):
    # Combine the existing prompt with the provided hints
    improved_prompt = f"{pattern_prompt}\n\nHints for improvement:\n{hints}"
    st.session_state.pattern_responses[selected_tag] = [pattern_name, pattern_description, improved_prompt, False]
    st.success(f"Prompt for tag '{selected_tag}' has been improved.")

# Function to improve or overwrite a prompt
def improve_or_overwrite_prompt(selected_tag, pattern_name, pattern_description, pattern_prompt):
    regen_radio = st.radio("Do you want to improve the prompt?", ["No", "Yes"])
    if regen_radio == "Yes":
        hints = st.text_area("Hints to improve the prompt", height=100)
        hints_overwrite_checkbox = st.checkbox(":red[I want to overwrite the prompt with my instructions.]")
        if st.button("Regenerate Prompt"):
            if hints_overwrite_checkbox:
                overwrite_prompt_with_hints(selected_tag, pattern_name, pattern_description, hints)
            else:
                improve_prompt(selected_tag, pattern_name, pattern_description, pattern_prompt, hints)

# Function to verify prompts
def verify_prompts():
    if st.session_state.pattern_responses:
        st.session_state.is_verified = False
        selected_tag = st.selectbox("Select a tag to verify", list(st.session_state.pattern_responses.keys()), key="tag_selector", index=0)
        st.session_state.verification_response = None
        if selected_tag:
            pattern_name, pattern_description, pattern_prompt, is_verified = st.session_state.pattern_responses[selected_tag]
            st.markdown(f"Name: :blue-background[{pattern_name}]")
            st.markdown(f"Description: :blue-background[{pattern_description}]")
            st.markdown(f"Prompt: :blue-background[{pattern_prompt}]")
            improve_or_overwrite_prompt(selected_tag, pattern_name, pattern_description, pattern_prompt)
            xml_content = st.text_area("Please enter the XML snippet to verify the pattern", height=100)
            if st.button("Verify", key="verifier_submit"):
                response = verify_xml_with_generated_prompt(xml_content, pattern_prompt)
                response_json = json.loads(response)
                reason = response_json['confirmation']
                is_verified = response_json['is_confirmed']
                st.session_state.verification_response = reason
                st.session_state.is_verified = is_verified
                st.session_state.pattern_responses[selected_tag] = [pattern_name, pattern_description, pattern_prompt, is_verified]
    else:
        st.error("No patterns to verify. Please upload the XML to extract patterns.")
    if 'verification_response' in st.session_state and st.session_state.verification_response is not None:
        if st.session_state.is_verified == "True":
            st.markdown(f":green-background[{st.session_state.verification_response}]")
        else:
            st.subheader(f":red-background[{st.session_state.verification_response}]")
    display_patterns()

# Function to save patterns to the database
def save_patterns_to_database():
    conn = connect_to_db("api_analysis.db")
    for tag, values in st.session_state.pattern_responses.items():
        pattern_name, pattern_description, pattern_prompt, is_verified = values
        insert_data(conn, "api_section", (1, tag, tag))
        insert_data(conn, "pattern_details", (pattern_name, pattern_description, pattern_prompt))
        insert_data(conn, "section_pattern_mapping", (1, tag, tag))
        insert_data(conn, "api_section", (1, tag, tag))
    # Add logic to save patterns to the database
    st.success("Patterns saved to the database!")

# Function to handle the "Save" tab
def save_patterns():
    display_patterns()
    if st.button("Save"):
        save_patterns_to_database()
        
def generate_prompt_from_manual_input(xml_chunk, tag, name, desription):
    current_dir = Path(__file__).resolve().parent
    file_path = current_dir / "../../../genie_core/config/prompts/generic/default_system_prompt_for_manual_pattern_addition.md"
    with file_path.open() as f:
        pattern_identifier_prompt = f.read()
    prompts = [
        {"role": "system", "content": pattern_identifier_prompt},
        {"role": "user", "content": f"Here is the XML - {xml_chunk}"},
        {"role": "user", "content": f"XML XPath - {tag}, Name - {name}, Description - {desription}"}
    ]
    shared_agent.set_prompts(prompts)
    cost, response_content = shared_agent.get_chat_completion()
    st.session_state.total_cost_per_tool += cost
    st.session_state.number_of_calls_to_llm += 1
    response_json = json.loads(response_content.choices[0].message.content)
    is_valid_xml = response_json.get("valid_xml")
    prompt =  response_json.get("generated_prompt")
    return is_valid_xml, prompt

# Sidebar for file upload
with st.sidebar:
    st.title("Upload Input Files")
    uploaded_file = st.file_uploader("Choose a file", type=["xml"])
    debug_mode = st.checkbox("Debug Mode", key="debug")

# Tabs for different functionalities
tab1, tab2, tab3 = st.tabs(["Extract", "Verify", "Save"])

# Tab 1: Extract patterns
with tab1:
    if uploaded_file is None:
        st.warning("Please upload a file to proceed")
    chunk_method = st.radio("Please select how you would like to chunk the XML.", ["I will select tags by myself 🛒", "Let Genie decide! 🤖"])
    if uploaded_file:
        xml_text = uploaded_file.read().decode('utf-8')
        if chunk_method == "I will select tags by myself 🛒":
            elements = list_elements(xml_text)
            nodes_to_select = st.multiselect("Select the tags you would like to extract", elements, key="tags")
        if st.button("Submit"):
            if chunk_method == "I will select tags by myself 🛒":
                chunks = chunk_xml_by_tags(xml_text, nodes_to_select)
                st.markdown(":blue[Expand the tags to view the XML content]")
                for tag, content_list in chunks.items():
                    with st.expander(f"Tag: {tag}"):
                        for content in content_list:
                            st.code(content, language='xml')
                with st.spinner(":rainbow[Extracting patterns, please wait!!]"):
                    for tag, content_list in chunks.items():
                        for content in content_list:
                            patterns = generate_prompt_from_llm(content)
                            for pattern_path, pattern_name, pattern_description, pattern_prompt in patterns:
                                st.session_state.pattern_responses[pattern_path] = [pattern_name, pattern_description, pattern_prompt, False]
                display_patterns()
            else:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".xml") as temp_file:
                    temp_file.write(uploaded_file.getvalue())
                    temp_file_path = temp_file.name
                run_gap_analyser(temp_file_path, xml_handler_agent, None, debug_mode)
    
        with st.expander("**Do you want to add more patterns manually?**"):
            chunks = chunk_xml_by_tags(xml_text, nodes_to_select)

            # First row: xml_chunk and tag
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Pattern name", key="name_input")
            with col2:
                tag = st.text_input("Tag name", key="tag_input")

            # Second row: name and description
            col3, col4 = st.columns(2)
            with col3:
                xml_chunk = st.text_area("XML chunk", height=150, key="xml_chunk")
            with col4:
                description = st.text_area("Pattern description", height=150, key="description_input")
        
            if xml_chunk == "" or tag == "" or name == "" or description == "":
                st.warning("Please fill all the fields to add a pattern.")

            manual_add_pattern_checkbox = st.checkbox("I will provide the prompt")

            # Initialize final_prompt in session state
            if "final_prompt" not in st.session_state:
                st.session_state.final_prompt = None

            if manual_add_pattern_checkbox:
                prompt_input = st.text_area("Enter the prompt", height=100)
                st.session_state.final_prompt = prompt_input
            else:
                if st.button("Generate Prompt"):
                    with st.spinner("Generating prompt, please wait!!"):
                        is_valid_xml, prompt_from_llm = generate_prompt_from_manual_input(xml_chunk, tag, name, description)
                        if is_valid_xml:
                            st.session_state.final_prompt = prompt_from_llm
                            st.info("Prompt generated successfully!")
                            st.markdown(f"Prompt: :blue-background[{st.session_state.final_prompt}]")
                        else:
                            st.warning("Failed to generate prompt, please try again!")

            if st.button("Add Pattern"):
                if st.session_state.final_prompt is None:
                    st.warning("No prompt available. Please generate or provide a prompt before adding the pattern.")
                else:
                    st.session_state.pattern_responses[tag] = [name, description, st.session_state.final_prompt, False]
                    st.success(f"Pattern for tag '{tag}' added successfully.")
                    # Reset final_prompt after adding the pattern
                    st.session_state.final_prompt = None

                display_patterns()
        

# Tab 2: Verify patterns
with tab2:
    verify_prompts()

# Tab 3: Save patterns
with tab3:
    save_patterns()

with st.sidebar:
    with st.container():
        st.markdown(
            """
            <div style='border: 2px solid #ccc; padding: 15px; border-radius: 10px; background-color: #f9f9f9;'>
                <h3 style='text-align: left;color:black'>Model Information and Metrics</h4>
                <p><strong>GPT Model used:</strong> <span style='color:green; font-weight:bold;'>{gpt_model}</span></p>
                <p><strong>Total number of calls to LLM:</strong> <span style='color:blue; font-weight:bold;'>{calls}</span></p>
                <p><strong>Total Cost:</strong> <span style='color:red; font-weight:bold;'>{cost_eur} EUR / {cost_inr} INR</span></p>
            </div>
            """.format(
                gpt_model=st.session_state.gpt_model_used,
                calls=st.session_state.number_of_calls_to_llm,
                cost_eur=st.session_state.total_cost_per_tool,
                cost_inr=TokenCostCalculator.convert_cost(st.session_state.total_cost_per_tool, "INR")
            ),
            unsafe_allow_html=True,
        )