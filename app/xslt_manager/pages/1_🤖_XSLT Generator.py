import streamlit as st
import os
import sys
import re
import difflib
from lxml import etree

if os.getenv("PYTHONPATH") is None:
    sys.path.append(os.path.abspath(os.getcwd()))
#sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '../..')))
from genie_core.common.user_interaction import init_objects_into_session,write_chat_message
# from genie_core.xml_processing.xml_utils import list_elements
from genie_core.xslt.xslt_utils import apply_xslt
from genie_core.common.confluence_utils import publish_content
from genie_core.xml_processing.xml_utils import process_xml
from genie_core.llm.llm_utils import process_user_response
#from genie_core.llm.TokenCostCalculator import *
prompt = None

# Handle missing module error
def handle_module_not_found_error(e):
    pattern = r"\'(.*)\'"
    module_name = re.search(pattern, str(e)).group(1)
    st.error(f"ModuleNotFoundError: please install the required module by running `pip install {module_name}`\n ({e})")

# Set up the page layout
#st.set_page_config(layout="wide")

# Initialize root element
root_element = None

# Function to handle file uploads in the sidebar
def handle_sidebar_file_uploads():
    transformation_type = st.radio(
        "Select Transformation Type",
        ("XSLT 1.0", "XSLT 2.0", "XSLT 3.0", "JOLT")
    )
    
    if transformation_type == "JOLT":
        st.warning("JOLT is not supported in this version yet, stay tuned!!")

    # st.session_state.recursive = st.radio(
    #     "Recursive generation?",
    #     ("Regular", "Recursive")
    # )

    st.header("Upload Files")
    source_xml_file = st.file_uploader("Upload Source XML", type=["xml"])
    target_xml_file = st.file_uploader("Upload Target XML", type=["xml"])
    
    st.header("Specifications")
    specs_input_type = st.radio("Specification Source:", ["URL", "File Upload"], horizontal=True)
    
    specs_url = None
    specs_file = None
    
    if specs_input_type == "URL":
        specs_url = st.text_input("Specifications URL", placeholder="Enter the URL containing specifications (e.g., Confluence page)")
        # Store specs URL in session state for processing
        if specs_url:
            st.session_state.specs_url_input = specs_url
            st.session_state.specs_file_input = None
    else:
        specs_file = st.file_uploader("Upload Specifications File", type=["html", "mhtml", "htm", "md", "csv"])
        # Store specs file in session state for processing
        if specs_file:
            st.session_state.specs_file_input = specs_file
            st.session_state.specs_url_input = None
    
    # Show status of inputs
    st.subheader("Input Status")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if source_xml_file:
            st.success("✅ Source XML")
        else:
            st.error("❌ Source XML")
    
    with col2:
        if target_xml_file:
            st.success("✅ Target XML") 
        else:
            st.error("❌ Target XML")
    
    with col3:
        specs_provided = specs_url or specs_file
        if specs_provided:
            specs_type = "Specs URL" if specs_url else f"Specs File ({specs_file.name})" if specs_file else "Specs"
            st.success(f"✅ {specs_type}")
        else:
            st.error("❌ Specifications")
    
    # Show ready status
    if source_xml_file and target_xml_file and specs_provided:
        st.success("🚀 All inputs ready! XSLT generation will start automatically.")
    else:
        missing_count = sum([not source_xml_file, not target_xml_file, not specs_provided])
        st.info(f"⏳ Please provide {missing_count} more input{'s' if missing_count != 1 else ''} to start automatic processing.")
    # if "specs_refiner_output" in st.session_state:
    #     use_existing_specs = st.checkbox("Use existing specifications from Specs Refiner")
    #     if use_existing_specs:
    #         specifications_file = st.session_state.specs_refiner_output
    #     else:
    #         specifications_file = st.file_uploader("Upload mapping specifications", type=["txt", "md"])
    # else:
    #     specifications_file = st.file_uploader("Upload mapping specifications", type=["txt", "md"])

    # if source_xml_file:
    #     st.session_state.source_xml = source_xml_file.read().decode('utf-8')
    #     elements = list_elements(st.session_state.source_xml)
    #     st.session_state.root_element = st.selectbox("Root element", elements)

    #     my_regex = rf"\t*<{re.escape(st.session_state.root_element)}>.*</{re.escape(st.session_state.root_element)}>"
    #     st.session_state.input_xml = re.findall(my_regex, st.session_state.source_xml, flags=re.DOTALL)[0]

    return source_xml_file, target_xml_file, transformation_type, specs_url, specs_file

# Function to handle automatic processing when all inputs are ready
def check_and_auto_process(source_xml_file, target_xml_file, specs_url, specs_file):
    """Check if all 3 inputs are provided and auto-start processing"""
    
    # Check if all three inputs are provided (either URL or file for specs)
    specs_provided = specs_url or specs_file
    if source_xml_file and target_xml_file and specs_provided:
        # Process XML files
        st.session_state.source_xml = process_xml(source_xml_file)
        st.session_state.target_xml = process_xml(target_xml_file)
        
        # Create unique identifier for this combination of inputs
        specs_identifier = specs_url if specs_url else f"file:{specs_file.name}"
        current_inputs = f"{source_xml_file.name}|{target_xml_file.name}|{specs_identifier}"
        
        if not hasattr(st.session_state, 'last_processed_inputs') or st.session_state.last_processed_inputs != current_inputs:
            st.session_state.last_processed_inputs = current_inputs
            
            # Auto-generate message for agentic processing
            if specs_url:
                auto_message = f"Generate XSLT from URL: {specs_url}"
            else:
                auto_message = f"Generate XSLT from file:/{specs_file.name}"
            
            with st.spinner("🚀 All inputs detected! Auto-processing XSLT generation..."):
                write_chat_message("assistant", ":blue[All inputs detected - starting automatic XSLT generation...]")
                write_chat_message("user", auto_message, None)
                
                # For file uploads, create the "file:" format the agentic processor expects
                if specs_file:
                    specs_param = f"file:{specs_file.name}"
                    # Store the file in session state for the agentic processor to access
                    st.session_state.specs_file_input = specs_file
                else:
                    specs_param = specs_url
                    
                user_req, bot_message, st.session_state.chat_history, st.session_state.generated_xslt = process_user_response(
                    auto_message, 
                    st.session_state.chat_history, 
                    st.session_state.source_xml, 
                    st.session_state.target_xml, 
                    st.session_state.generated_xslt, 
                    specs_param
                )
                
                write_chat_message("assistant", f":green[{bot_message}]")
                
                # Handle the response
                if user_req:
                    st.session_state.auto_processed = True
                    st.session_state.ask_yes_no = True  # Enable refinement options
                    st.success("✅ XSLT generated successfully! You can now refine it or download it.")
                    st.rerun()  # Refresh to show the pills
                else:
                    # If there was an error, show it
                    if "error" in bot_message.lower() or "missing" in bot_message.lower():
                        st.error(f"Auto-processing failed: {bot_message}")
                    else:
                        st.info(bot_message)
            
            return True  # Indicates auto-processing happened
    
    return False  # No auto-processing

# Function to handle chat input and LLM conversation  
def handle_chat_input(source_xml_file, target_xml_file, transformation_type, specs_url, specs_file, prompt):
    st.title(":blue[Conversational Bot]")
    init_objects_into_session()
    
    # Check for automatic processing first
    auto_processed = check_and_auto_process(source_xml_file, target_xml_file, specs_url, specs_file)
    
    # Show processing status
    if auto_processed or hasattr(st.session_state, 'auto_processed'):
        st.info("✅ Automatic processing completed! Use the chat below for refinements or ask questions.")
    
    # Display chat history
    for message in st.session_state.messages:
        avatar = "😎" if message["role"] == "user" else "🤖"
        with st.chat_message(message["role"],avatar = avatar):
            st.markdown(message["content"])

    # Simplified agentic chat interface - no more pills or complex state management
    specs_provided = specs_url or specs_file
    if source_xml_file and target_xml_file and specs_provided:
        prompt = st.chat_input("💬 Ask for refinements (e.g., 'Fix TaxAmount to include currency') or other questions")
    else:
        prompt = st.chat_input("📝 Provide all inputs above, or enter manual commands (e.g., 'Generate XSLT from [URL]')")
    #     llm_response = subsequent_call_to_LLM(
    #         st.session_state.source_xml, st.session_state.target_xml, specifications_file
    #     )
    #     add_to_messages(prompt)

    # Handle user input in the agentic chat
    if prompt:
        if source_xml_file and target_xml_file:
            # Only process XMLs if they haven't been processed in auto-processing
            if not hasattr(st.session_state, 'source_xml') or not st.session_state.source_xml:
                st.session_state.source_xml = process_xml(source_xml_file)
                st.session_state.target_xml = process_xml(target_xml_file)
                
            write_chat_message("user", prompt, None)
            
            # Process user request with agentic approach
            if specs_file:
                specs_param = f"file:{specs_file.name}"
                st.session_state.specs_file_input = specs_file
            else:
                specs_param = specs_url or getattr(st.session_state, 'specs_file', None)
                
            user_req, bot_message, st.session_state.chat_history, st.session_state.generated_xslt = process_user_response(
                prompt, 
                st.session_state.chat_history, 
                st.session_state.source_xml, 
                st.session_state.target_xml, 
                st.session_state.generated_xslt, 
                specs_param
            )           
            write_chat_message("assistant", f":green[{bot_message}]")
            st.rerun()
        else:
            st.warning("Please upload input XML and output XML files first.")

def compare_func(existing_func, updated_func, task):
    diff = difflib.HtmlDiff().make_table(
        existing_func.splitlines(keepends=True),
        updated_func.splitlines(keepends=True),
        fromdesc= f'Existing {task}',
        todesc= f'Updated {task}',
        context=False,
        numlines=1
    )
    # Custom styling to fix column widths
    custom_style = """
    <style>
        table {
            width: 120%;
            border-collapse: collapse;
        }
        th, td {
            padding: 8px;
            text-align: left;
            word-break: break-word; /* Break long words */
            white-space: pre-wrap;  /* Preserve formatting but allow wrapping */
        }

        td:nth-child(2), th:nth-child(2) {
        width: 5%;
        min-width: 25px;
        }
        td:nth-child(5), th:nth-child(5) {
        width: 5%;
        min-width: 25px;
        }


        th {
            background-color: #f2f2f2;
        }
        .diff_next {
            display: none;
        }
        pre {
            white-space: pre-wrap;
        }
        .diff_header {
            font-weight: bold;
            background-color: #ddd;
        }
        .diff_add {
            background-color: #d4fcbc;
        }
        .diff_chg {
            background-color: #ffeeba;
        }
        .diff_sub {
            background-color: #ffbaba;
        }
    </style>
    """

    return custom_style + diff
    
# Function to display generated XSLT
def display_generated_xslt():
    st.title(":blue[Generated XSLT]")
    height = 100
    output_placeholder = st.markdown(
        f"""<div style='border: 1px solid #3c3c73; padding: 10px; height: {height}px; overflow-y: auto;'>XSLT will appear here</div>""",
        unsafe_allow_html=True
    )
    generated_xslt = st.session_state.generated_xslt
    if generated_xslt is not None:
        height = 800
        output_placeholder.text_area("", generated_xslt, height)
        st.download_button(
            label="Download XSLT",
            data=generated_xslt,
            file_name="generated_xslt.xslt",
            mime="application/xml"
        )

def display_xslt_diff():
    
    if st.session_state.current_xslt:
        try:
            diff = compare_func(st.session_state.existing_xslt, st.session_state.generated_xslt, "XSLT")

            st.title("Differences between Existing and Updated XSLT")
            st.markdown(diff, unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Error comparing XSLT files: {str(e)}")
    else :
        st.info("Please generate atleast 2 versions of XSLTs.")

def display_spec_diff():
    
    if st.session_state.current_xslt and st.session_state.updated_specs:
        try:
            diff = compare_func(st.session_state.existing_specs, st.session_state.updated_specs, "Specs")
            if st.button("Update Confluence Page", type="primary"):
                publish_content(st.session_state.space, st.session_state.page_name, st.session_state.html)
            st.title("Differences between Existing and Updated Specs")
            st.markdown(diff, unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Error comparing Spec files: {str(e)}")
    else :
        st.info("Please generate atleast 2 versions of XSLTs.")

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
    diff = difflib.HtmlDiff().make_table(xml1_normalized, xml2_normalized, "Source XML", "Target XML", context=False)
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

def display_testing():
    output_placeholder = st.empty()
    in_xml = st.file_uploader("Upload Input XML", type=["xml"], accept_multiple_files=True)
    # out_xml = st.file_uploader("Upload Target XML", type=["xml"])
    xslt = st.file_uploader("Upload XSLT", type=["xslt"])

    # if in_xml:
    #     st.session_state.source_xml = in_xml[0].read().decode('utf-8')
    #     elements = list_elements(st.session_state.source_xml)
    #     st.session_state.root_element = st.selectbox("Root element", elements)

    #     my_regex = rf"\t*<{re.escape(st.session_state.root_element)}>.*</{re.escape(st.session_state.root_element)}>"
    #     st.session_state.input_xml = re.findall(my_regex, st.session_state.source_xml, flags=re.DOTALL)[0]
    
    logs = []
    if in_xml and xslt:

        xslt = xslt.read().decode('utf-8')

        for i in range(len(in_xml)):
            in_xml[i] = in_xml[i].read().decode('utf-8')
            formatted_xml, logs = apply_xslt(xslt, in_xml[i], logs, None)
            st.text_area(f"Transformed xml {i+1}", formatted_xml, height=800)
            st.download_button(
                label=f"Download XML {i+1}",
                data=formatted_xml,
                file_name=f"tranformed_xml_{i+1}.xml",
                mime="application/xml"
            )


# Main function to run the app
def main():
    prompt = None
    st.header(":blue[Welcome to GENIE]")
    # st.subheader("XSLT Generator")
    st.markdown(":blue[Transform your input XML into the desired output XML with ease. This feature takes the input XML, output XML, and a specification file to generate the corresponding XSLT. It simplifies the process of conversion, saving your time and effort.]")

    
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Generate", "Output", "XML Analysis","XSLT Analysis","Specs Analysis"])


    with tab1:
        with st.sidebar:
            source_xml_file, target_xml_file, transformation_type, specs_url, specs_file = handle_sidebar_file_uploads()

        handle_chat_input(source_xml_file, target_xml_file, transformation_type, specs_url, specs_file, prompt)
        display_generated_xslt()

    with tab2:
        display_transformed_xml()

    with tab3:
        display_xml_comparison()

    with tab4:
        display_xslt_diff()

    with tab5:
        display_spec_diff()


if __name__ == "__main__":
    main()
