# Set up the page layout
import streamlit as st
st.set_page_config(layout="wide")

import os
import sys
import difflib
import pandas as pd
import json

if os.getenv("PYTHONPATH") is None:
    sys.path.append(os.path.abspath(os.getcwd()))
#sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '../..')))
from genie_core.xml_processing.xml_utils import *
from genie_core.xslt.xslt_utils import *
from genie_core.llm.llm_response_handler_utils import *
from genie_core.llm.llm_utils import *
from genie_core.prompts.prompt_utils import *
from genie_core.database.database_utils import *
from genie_core.common.user_interaction import init_objects_into_session
import genie_core.common.confluence_utils as confluence_utils
from pathlib import Path

if st.button("🔄 Clear All Cache & Conversation"):
    # clear new‐style caches
    try:
        st.cache_data.clear()
        st.cache_resource.clear()
    except AttributeError:
        # fallback for older Streamlit
        st.legacy_caching.clear_cache()

    # clear any memoized calls
    try:
        st.experimental_memo.clear()
    except AttributeError:
        pass

    # wipe out everything in session_state (llm inputs/outputs, html, etc.)
    for key in list(st.session_state.keys()):
        del st.session_state[key]

    # clear any lru_cache on your get_chat_completion
    try:
        get_chat_completion.cache_clear()
    except AttributeError:
        pass
    st.rerun()
    
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
            
st.subheader("XSLT Updater")
st.markdown(":blue[Need to update an existing XSLT with new requirements? The XSLT Updater does just that. It automatically updates the generated XSLT and generates new specifications based on the revised requirements, ensuring your XSLT is always up-to-date and aligned with your latest needs.]")
# Main code
update_tab, optimize_tab, analysis_and_review_tab, testing_tab, cook_book_tab = st.tabs(["Update", "Optimize", "Analysis & Review", "Testing", "cook-book"])

shared_agent = setup_agent("GPT4O")
st.session_state.gpt_model_used = "GPT4O"
init_objects_into_session()
with update_tab:
    # Inject custom CSS styles
    st.markdown("""
        <style>
        .stDownloadButton button {
            background-color: #007bff;
            color: white;
        }
        </style>
        """, unsafe_allow_html=True)

    with st.sidebar:
        st.header("Upload Files")
        # source_xml_file = st.file_uploader("Upload Source XML", type=["xml"])
        # target_xml_file = st.file_uploader("Upload Target XML", type=["xml"])
        xslt = st.file_uploader("Upload XSLT", type=["xslt","xsl"])
        text_input = st.text_input("Enter Confluence URL 👇")
    # Create columns for the chatbot and the text area
    col1, col2 = st.columns([1, 1])
    with st.container():
        output_placeholder = st.empty()
        human_readable_questions = None
        LLM_readable_questions = None

        with st.form('addition'):
            user_requirement_prompt = st.text_area(":blue[Please enter your requirement here.]", 
                                height=100,
                                key="custom-text-area")        
            submit = st.form_submit_button('Submit')
        if submit:
            start_prompt = {"role":"user", "content": user_requirement_prompt}
            add_to_prompts(start_prompt)
            add_to_messages(user_requirement_prompt)
            # if source_xml_file and xslt and text_input:
            if xslt and text_input:
                # st.session_state.source_xml = source_xml_file.read().decode('utf-8')
                st.session_state.xslt = xslt.read().decode('utf-8')
                st.session_state.specs_file = text_input
                
                current_dir = Path(__file__).resolve().parent
                directory_path = current_dir / "../../../genie_core/config/cookbooks"
                cooks_books = "Cook-book instructions:\n"
                if os.path.exists(directory_path):
                    for root, dirs, files in os.walk(directory_path):
                        for file in files:
                            with st.expander(file):
                                with open(os.path.join(root, file), 'r') as f:
                                    cooks_books += f.read() + "\n"
                st.session_state.cook_books = cooks_books         
                initiate_conversation_with_LLM_update(st.session_state.source_xml, st.session_state.target_xml, 
                                                         st.session_state.xslt, st.session_state.specs_file, st.session_state.cook_books, user_requirement_prompt, shared_agent)
                shared_agent = None
            else:
                st.warning("Please upload the input files.")
                
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    with st.container():
        st.title("Generated XSLT")
        output_placeholder = st.empty()
        updated_xslt = st.session_state.updated_xslt
        if updated_xslt != None:
            height = min(400, len(updated_xslt) * 30)
            output_placeholder.text_area("", updated_xslt, height)
            st.download_button(
                label="Download XSLT",
                data=updated_xslt,
                file_name="updated_xslt.xslt",
                mime="application/xslt"
            )
        
        elif updated_xslt == None:
            height = min(100, 200)
            output_placeholder.markdown(f"<div style='border: 1px solid #3c3c73; padding: 10px; height: {height}px; overflow-y: auto;'>XSLT will appear here</div>", unsafe_allow_html=True)    
    with st.container():    
        st.title("Generated specs")
        output_placeholder = st.empty()
        generated_specs = st.session_state.updated_specs
        if generated_specs != None:
            height = min(400, len(generated_specs) * 30)
            output_placeholder.text_area("", generated_specs, height)
            st.download_button(
                label="Download Specs",
                data=generated_specs,
                file_name="generated_specs.txt",
                mime="application/txt"
            )
        elif generated_specs == None:
            height = min(100, 200)
            output_placeholder.markdown(f"<div style='border: 1px solid #3c3c73; padding: 10px; height: {height}px; overflow-y: auto;'>Specs will appear here</div>", unsafe_allow_html=True)
            
with optimize_tab:
    output_placeholder = st.empty()

    try:
        updated_xslt = st.session_state.updated_xslt
    except AttributeError:
        updated_xslt = None

    try:
        source_xml = st.session_state.source_xml
    except AttributeError:
        source_xml = None

    if updated_xslt and source_xml:
        try:
            height = min(800, len(updated_xslt) * 30)
            logs = []
            formatted_xml, logs = apply_xslt(updated_xslt, source_xml, logs, None)
            if formatted_xml:
                st.session_state.llm_target_xml = formatted_xml
                st.download_button(
                    label="Download XML",
                    data=formatted_xml,
                    file_name="generated_xml.xml",
                    mime="application/xml"
                )
            output_placeholder.text_area("Transformed XML", formatted_xml, height)
        except Exception as e:
            st.error(f"An error occurred during the XSLT transformation: {e}")
    else:
        st.info("XSLT is missing. Please upload the required files and generate the XSLT first.")

with analysis_and_review_tab:
    
    # Logic to compare existing_xslt and updated_xslt
    def normalize_lines(xslt_str):
        # Unify line endings, replace tabs with spaces, remove trailing (not leading) whitespace
        return [
            line.rstrip().replace('\t', '    ')
            for line in xslt_str.replace('\r\n', '\n').replace('\r', '\n').split('\n')
        ]
    def compare_xslt(existing_xslt, updated_xslt):
        existing_lines = normalize_lines(existing_xslt)
        updated_lines = normalize_lines(updated_xslt)
        diff = difflib.HtmlDiff().make_table(
            existing_lines,
            updated_lines,
            fromdesc='Existing XSLT',
            todesc='Updated XSLT',
            context=False,
            numlines=0
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
        #return diff
    
    def get_files():
        if "xslt" not in st.session_state:
            with open("/Users/nlepakshi/Documents/GitHub/update_xslt/content-transformer-new/1_6_1_openai/learning/xslt_generator/config/test_data/NDC_Cancel/xslt.xslt", 'r') as file:
                    existing_xslt = file.read()
        else:
            existing_xslt = st.session_state.xslt
        
        if "specs_file" not in st.session_state:
            with open("/Users/nlepakshi/Documents/GitHub/update_xslt/content-transformer-new/1_6_1_openai/learning/xslt_generator/config/test_data/NDC_Cancel/specs.md", 'r') as file:
                    existing_specs = file.read()
        else:
            existing_specs = st.session_state.specs_file
        
        if "updated_xslt" not in st.session_state:
            with open("/Users/nlepakshi/Documents/GitHub/update_xslt/content-transformer-new/1_6_1_openai/learning/xslt_generator/config/test_data/NDC_Cancel/updated_xslt.xslt", 'r') as file:
                    updated_xslt = file.read()
        else:
            updated_xslt = st.session_state.updated_xslt
        
        if "updated_specs" not in st.session_state:
            with open("/Users/nlepakshi/Documents/GitHub/update_xslt/content-transformer-new/1_6_1_openai/learning/xslt_generator/config/test_data/NDC_Cancel/updated_specs.md", 'r') as file:
                    updated_specs = file.read()
        else:
            updated_specs = st.session_state.updated_specs
        return existing_xslt, existing_specs, updated_xslt, updated_specs

    # Logic to compare existing_specs and updated_specs
    def compare_specs(existing_specs, updated_specs):
        diff = difflib.HtmlDiff().make_table(
            existing_specs.splitlines(keepends=True),
            updated_specs.splitlines(keepends=True),
            fromdesc='Existing Specs',
            todesc='Updated Specs',
            context=False,
            numlines=0
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
        #return diff


    def finetune_specs_llm():
        with open("/Users/nlepakshi/Documents/GitHub/demo_master/content-transformer-new/xslt_generator/config/prompts/generic/system_read_spec_file_for_publish.txt") as file:
            specs_read_prompt = file.read()
        
        prompts = []
        prompts.append({"role":"system", "content":specs_read_prompt})
        
        if "specs_file" not in st.session_state:
            with open("/Users/nlepakshi/Documents/GitHub/demo_master/content-transformer-new/xslt_generator/config/test_data/Ord_cancel/generated_specs.txt") as file:
                spec_file = file.read()
        else:
            spec_file = st.session_state.updated_specs

        prompts.append({"role":"user", "content":spec_file})
            
        llm_response = get_chat_completion(prompts)
        response_obj = None
        if llm_response:
            response_obj = llm_response.choices[0].message.content
            st.download_button(
                label="Download Specs",
                data=response_obj,
                file_name="updated_specs.html",
                mime="application/html"
            )

    def publish(body):
        confluence_utils.reupload_page(2354569017,'OrderRetrieve Request Specifications copy', body=body)

    existing_xslt, existing_specs, updated_xslt, updated_specs = get_files()
    if existing_xslt and updated_xslt:
        try:
            diff = compare_xslt(existing_xslt, updated_xslt)
            st.title("Differences between Existing and Updated XSLT")
            st.markdown(diff, unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Error comparing XSLT files: {str(e)}")
            
    if existing_specs and updated_specs:
        try:
            diff = compare_specs(existing_specs, updated_specs)
            st.title("Differences between Existing and Updated Specs")
            if st.button("Update Confluence Page", type="primary"):
                publish_content(st.session_state.space, st.session_state.page_name, st.session_state.html)
            st.markdown(diff, unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Error comparing specs files: {str(e)}")
        # #finetune_specs_llm()

    else:
        st.info("XSLT is missing. Please upload the required files and generate the XSLT first.")

    # st.markdown("""
    #     <style>
    #     .diff_add { background-color: #ccffcc; }  /* Green background for additions */
    #     .diff_sub { background-color: #ffcccc; }  /* Red background for deletions */
    #     table { width: 100%; }                    /* Full width table */
    #     td { padding: 8px; border: 1px solid #ddd; } /* Table cell styling */
    #     </style>
    #     """, unsafe_allow_html=True)
    
with testing_tab:
    display_testing()
    
with cook_book_tab:
    current_dir = Path(__file__).resolve().parent
    directory_path = current_dir / "../../../genie_core/config/cookbooks"
    if os.path.exists(directory_path):
        files = [f for f in os.listdir(directory_path) if os.path.isfile(os.path.join(directory_path, f))]
        if files:
            selected_file = st.selectbox("Select a cookbook file to edit", files)
            file_path = os.path.join(directory_path, selected_file)

            # Read and extract all JSON objects robustly
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # Remove comments
                content = re.sub(r'<!--.*?-->', '', content, flags=re.DOTALL)
                # Robustly extract JSON objects by counting braces
                data = []
                buf = ''
                depth = 0
                in_obj = False
                for c in content:
                    if c == '{':
                        if depth == 0:
                            buf = ''
                            in_obj = True
                        depth += 1
                    if in_obj:
                        buf += c
                    if c == '}':
                        depth -= 1
                        if depth == 0 and in_obj:
                            try:
                                data.append(json.loads(buf))
                            except Exception as e:
                                logging.error(f"Failed to parse JSON object: {e}. Problematic snippet: {buf}")
                            in_obj = False

            # Build a list of keys for the dropdown
            key_list = ["Select key to edit..."]
            key_map = {}  # Map key to index in data
            for idx, item in enumerate(data):
                k = item.get("key", f"Item {idx+1}")
                key_list.append(k)
                key_map[k] = idx

            selected_key = st.selectbox("Select key to edit", key_list)

            # --- Edit Section ---
            if selected_key != "Select key to edit...":
                selected_idx = key_map[selected_key]
                selected_item = data[selected_idx]
                st.markdown("### Edit Selected Key")
                new_key = st.text_input("Key", value=selected_item.get("key", ""), key="edit_key")
                edit_key_valid = True
                if new_key and not re.fullmatch(r'[A-Z0-9]+(_[A-Z0-9]+)*', new_key):
                    st.error("Invalid key! Use only uppercase letters, numbers, and underscores between words (e.g., DUMMY_PATTERN_PATH).")
                    edit_key_valid = False

                new_code = st.text_area("Code", value=selected_item.get("code", ""), key="edit_code")
                new_example = st.text_area("Example", value=selected_item.get("example", ""), key="edit_example")
                new_description = st.text_area("Description (optional)", value=selected_item.get("description", ""), key="edit_description")

                if st.button("Save Changes to Key"):
                    if not edit_key_valid:
                        st.warning("Please fix the key before saving.")
                    else:
                        updated_item = {
                            "key": new_key,
                            "code": new_code,
                            "example": new_example
                        }
                        if new_description.strip():
                            updated_item["description"] = new_description
                        data[selected_idx] = updated_item
                        try:
                            with open(file_path, 'w', encoding='utf-8') as f:
                                json.dump(data, f, ensure_ascii=False, indent=2)
                            st.success("Key updated successfully!")
                        except Exception as e:
                            st.error(f"Failed to save: {e}")

            # --- Add Section ---
            st.markdown("---")
            st.markdown("### Add New Key")
            add_key = st.text_input("New Key", key="add_key")
            key_valid = True
            if add_key and not re.fullmatch(r'[A-Z0-9]+(_[A-Z0-9]+)*', add_key):
                st.error("Invalid key! Use only uppercase letters, numbers, and underscores between words (e.g., DUMMY_PATTERN_PATH).")
                key_valid = False

            add_code = st.text_area("New Code", key="add_code")
            add_example = st.text_area("New Example", key="add_example")
            add_description = st.text_area("New Description (optional)", key="add_description")
            if st.button("Add New Key"):
                if not key_valid:
                    st.warning("Please fix the key before adding.")
                else:
                    new_item = {
                        "key": add_key,
                        "code": add_code,
                        "example": add_example
                    }
                    if add_description.strip():
                        new_item["description"] = add_description
                    data.append(new_item)
                    try:
                        with open(file_path, 'w', encoding='utf-8') as f:
                            for i, obj in enumerate(data):
                                json_str = json.dumps(obj, ensure_ascii=False, indent=2)
                                if i != 0:
                                    f.write(",\n")
                                f.write(json_str)
                            f.write("\n")
                        st.success("New key added successfully!")
                    except Exception as e:
                        st.error(f"Failed to add: {e}")
        else:
            st.warning("No files found in the directory.")
    else:
        st.warning("Cookbook directory does not exist.")
        
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