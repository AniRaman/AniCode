import streamlit as st
import os
import sys
import html2text

# Add project directories to the system path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '../..')))
from genie_core.llm.llm_utils import setup_agent
from genie_core.common.user_interaction import init_objects_into_session, add_to_prompts

def handle_chat_input(source_xml_file, target_xml_file, specification_file):
    st.title(":blue[Conversational Bot]")
    init_objects_into_session()
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if st.button("Compare"):
        if source_xml_file and target_xml_file:
            with st.spinner("Please wait while I compare the APIs"):
                st.session_state.source_xml = source_xml_file.read().decode('utf-8')
                st.session_state.target_xml = target_xml_file.read().decode('utf-8')
                st.session_state.specifications_file = specification_file.read().decode('utf-8')
                llm_response = compare_xmls(st.session_state.source_xml, st.session_state.target_xml, st.session_state.specifications_file)
                if llm_response:
                    html_response = convert_html_to_markdown(llm_response)
                    st.markdown(html_response)
        else:
            st.warning("Missing input files, please check")

def convert_html_to_markdown(html_content):
    h = html2text.HTML2Text()
    h.ignore_links = False  # Set to True if you want to ignore links
    h.ignore_images = False  # Set to True if you want to ignore images
    return h.handle(html_content)

def compare_xmls(source_xml, target_xml, specification_file):
    # current_dir = Path(__file__).resolve().parent
    # file_path = current_dir / "../../../../../config/prompts/generic/default_system_prompt_for_xml_comparison.txt"
    
    with open("/Users/nlepakshi/Documents/GitHub/demo_master/content-transformer-new/xslt_generator/config/prompts/generic/default_system_prompt_for_xml_comparison.txt", "r") as file:
        system_prompt = file.read()
    all_system_prompts = []
    # with file_path.open() as file:
    #     system_prompt = file.read()
    system_prompt = {"role": "system", "content": system_prompt}
    all_system_prompts.append(system_prompt)
    xml_comparator_agent = setup_agent("GPT4O")
    
    
    input_file_prompt = {"role": "user", "content": f"The input XML file is enclosed with --- {source_xml} ---"}
    output_file_prompt = {"role": "user", "content": f"The output XML file is enclosed with *** {target_xml} ***"}
    spec_file_prompt = {"role": "user", "content": f"The specifications file is enclosed with +++ {specification_file} +++"}
    all_system_prompts.append(input_file_prompt)
    all_system_prompts.append(output_file_prompt)
    all_system_prompts.append(spec_file_prompt)
    xml_comparator_agent.set_prompts(all_system_prompts)
    add_to_prompts(all_system_prompts)
    st.session_state.xml_comparator_agent = xml_comparator_agent
    
    llm_response = xml_comparator_agent.get_chat_completion()
    
    if not llm_response.choices[0].message.content:
        st.error("Error in generating XSLT. No response was generated.")
        return
    return llm_response.choices[0].message.content

def handle_sidebar_file_uploads():
    st.header("Upload Files")
    source_xml_file = st.file_uploader("Upload Source XML", type=["xml"])
    target_xml_file = st.file_uploader("Upload Target XML", type=["xml"])
    specifications_file = st.file_uploader("Upload mapping specifications", type=["txt", "md"])
    return source_xml_file, target_xml_file, specifications_file
        
def write_code():
    pass
# Main function to run the app
def main():
    st.subheader("XML Comparator")
    tab1, tab2 = st.tabs(["Compare", "Generate Code"])

    with tab1:
        with st.sidebar:
            source_xml_file, target_xml_file, specification_file = handle_sidebar_file_uploads()
        handle_chat_input(source_xml_file, target_xml_file, specification_file)
        
    with tab2:
        write_code()

if __name__ == "__main__":
    main()