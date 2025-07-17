import streamlit as st
import os
import sys
import re
import difflib
from lxml import etree
import pandas as pd

# Add project directories to the system path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '../..')))
from genie_core.llm.llm_utils import initiate_conversation_with_LLM, subsequent_call_to_LLM, initiate_conversation_with_LLM_for_gap_analysis
from genie_core.common.user_interaction import init_objects_into_session, add_to_prompts, add_to_messages, write_chat_message
from genie_core.xml_processing.xml_utils import list_elements
from genie_core.xslt.xslt_utils import apply_xslt
from genie_core.database.sql_db_utils import verify_and_confirm_airline

st.set_page_config(layout="wide")

st.markdown(
    """
    <style>
    .word-wrap-table table {
        width: 100%;
        word-wrap: break-word;
        word-break: break-word;
    }
    .word-wrap-table th, .word-wrap-table td {
        white-space: normal !important;
        text-align: left;
        vertical-align: top;
    }
    </style>
    """,
    unsafe_allow_html=True
)

airlines = [
    "ALL", "ALTEA 21.3", "AFKL 18.2", "LH 17.2"
]

# Handle missing module error
def handle_module_not_found_error(e):
    pattern = r"\'(.*)\'"
    module_name = re.search(pattern, str(e)).group(1)
    st.error(f"ModuleNotFoundError: please install the required module by running `pip install {module_name}`\n ({e})")

try:
    import streamlit as st
    import os
    import sys
    import re
    import difflib
    from lxml import etree
except ModuleNotFoundError as e:
    handle_module_not_found_error(e)

# Set up the page layout

# Initialize root element
root_element = None

# Function to handle file uploads in the sidebar
def handle_sidebar_file_uploads():

    st.header("Upload Files")
    source_xml_file = st.file_uploader("Upload Source XML", type=["xml"])
    if source_xml_file:
        st.session_state.source_xml = source_xml_file.read().decode('utf-8')
    return source_xml_file

# Function to handle chat input and LLM conversation
def handle_chat_input(selected_airlines=None):
    init_objects_into_session()
    # st.subheader(f"Selected Airline: {selected_airlines}")
    
    # st.markdown(f"Comparing <span style='color:red'><strong>LATAM 21.3</strong></span> with the selected airline version(s) <span style='color:green'><strong>{selected_airlines}</strong></span>", unsafe_allow_html=True)    
    # prompt = st.chat_input("Type START to continue")
    if st.button("Start Analysis"):
        if st.session_state.source_xml:
            # write_chat_message("user", prompt, None)
            analysis = verify_and_confirm_airline(st.session_state.source_xml, selected_airlines)
            display_api_analysis(analysis)
            # add_to_messages(analysis)
        else:
            st.warning("Missing input files, please check")
    
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

st.markdown(
    """
    <style>
    .word-wrap-table table {
        width: 100%;
        word-wrap: break-word;
        word-break: break-word;
    }
    .word-wrap-table th, .word-wrap-table td {
        white-space: normal !important;
        text-align: left;
        vertical-align: top;
    }
    </style>
    """,
    unsafe_allow_html=True
)

def display_api_analysis(data):
    sections = data.get('sections', [])
    matched_airlines = data.get('matched_airlines', [])
    rows = []
    for section in sections:
        section_name = section.get('sectionName')
        rules = section.get('rules', [])
        for rule in rules:
            rows.append({
                'Airline': rule.get('airline'),
                'Section': section_name,
                'Validation Rule': rule.get('verificationRule'),
                'Verified': 'Yes' if rule.get('matched') else 'No',
                'Reason': rule.get('reason')
            })
    df = pd.DataFrame(rows)
    
    def color_rows(row):
        return ['color: green' if row['Verified'] == 'Yes' else 'color:red' for _ in row]
    
    styled_df = df.style.apply(color_rows, axis=1)
    
    
    st.dataframe(styled_df)

    # st.markdown(
    #     df.to_html(classes="word-wrap-table", escape=False, index=False),
    #     unsafe_allow_html=True
    # )
    
    st.subheader("Matched Airline(s):")
    if matched_airlines:
        st.write(", ".join(matched_airlines))
    else:
        st.write(":red[No airline(s) matched.]")

# Function to display generated XSLT
def display_analysis():
    st.title(":blue[Analysis]")
    height = 100
    output_placeholder = st.markdown(
        f"""<div style='border: 1px solid #3c3c73; padding: 10px; height: {height}px; overflow-y: auto;'></div>""",
        unsafe_allow_html=True
    )
    analysis = st.session_state.analysis
    if analysis is not None:
        height = 800
        output_placeholder.text_area("", analysis, height)

# Function to apply XSLT and display transformed XML
def display_transformed_xml():
    output_placeholder = st.empty()
    generated_xslt = st.session_state.generated_xslt
    source_xml = st.session_state.source_xml

    if generated_xslt:
        height = min(800, len(generated_xslt) * 30)
        logs = []
        try:
            formatted_xml, logs = apply_xslt(generated_xslt, source_xml, logs, None)
            if formatted_xml:
                st.session_state.llm_target_xml = formatted_xml
                st.download_button(
                    label="Download XML",
                    data=formatted_xml,
                    file_name="generated_xml.xml",
                    mime="application/xml"
                )
                output_placeholder.text_area("Transformed XML", formatted_xml, height)
            else:
                output_placeholder.text_area("Error", "An error occurred while applying XSLT \n" + logs[0], height)
        except Exception as e:
            st.error(f"An exception occurred: {str(e)}")
            output_placeholder.text_area("Error", f"An exception occurred while applying XSLT: {str(e)}", height)
    else:
        st.info("Please generate the XSLT.")

# Function to remove XML encoding declaration
def remove_encoding_declaration(xml_string):
    return re.sub(r'<\?xml.*?\?>', '', xml_string)

# Function to pretty print XML and remove unnecessary spaces
def normalize_xml(xml_string):
    xml_clean = remove_encoding_declaration(xml_string)
    parser = etree.XMLParser(remove_blank_text=True)
    xml_tree = etree.fromstring(xml_clean.encode('utf-8'), parser)
    pretty_xml = etree.tostring(xml_tree, pretty_print=True).decode('utf-8')
    return pretty_xml.strip().splitlines()

# Function to compare two XMLs with pretty printing and whitespace removal
def compare_xmls(xml1, xml2):
    xml1_normalized = normalize_xml(xml1)
    xml2_normalized = normalize_xml(xml2)
    diff = difflib.HtmlDiff().make_table(xml1_normalized, xml2_normalized, "Source XML", "Target XML", context=True)
    matcher = difflib.SequenceMatcher(None, xml1_normalized, xml2_normalized)
    match_percentage = matcher.ratio() * 100
    return diff, match_percentage

# Function to display XML comparison
def display_xml_comparison():
    llm_target_xml = st.session_state.llm_target_xml
    source_xml = st.session_state.target_xml

    xml1 = llm_target_xml
    xml2 = source_xml

    st.markdown("""
        <style>
        .diff_sub { background-color: #ffcccc; }
        .diff_add { background-color: #ccffcc; }
        .diff_chg { background-color: #ffffcc; }
        table { width: 100%; }
        td { padding: 8px; border: 1px solid #ddd; }
        </style>
        """, unsafe_allow_html=True)

    if xml1 and xml2:
        try:
            result, match_percentage = compare_xmls(xml1, xml2)
            st.write(f"**Match Percentage:** {match_percentage:.2f}%")
            st.markdown(result, unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Error comparing XMLs: {str(e)}")
    else:
        st.info("Please generate the XSLT.")

# Main function to run the app
def main():
    # selected_airline = st.multiselect("Select Airline Version(s):", airlines)
    tab1, tab2 = st.tabs(["Analyse", " "])

    with tab1:
        with st.sidebar:
            source_xml_file = handle_sidebar_file_uploads()
        # handle_chat_input(selected_airline)
        handle_chat_input()
        # display_analysis()

    with tab2:
        pass

if __name__ == "__main__":
    main()
