import streamlit as st
from pathlib import Path

# Function to retrieve the default system prompt from a file
current_dir = Path(__file__).resolve().parent
def get_default_system_prompt():
    """
    Retrieves the default system prompt from a file.
    
    Returns:
    str: The initial prompt
    None: If there's an error reading the file.
    """
    try:
        file_path = current_dir / "../config/prompts/generic/default_system_prompts.txt"
        # st.info(file_path)
        with file_path.open('r', encoding='utf-8') as file:
            initial_prompt = file.read()
        # with open('../config/prompts/generic/default_system_prompts.txt', 'r', encoding="utf-8") as file:
        #     initial_prompt = file.read()

            # Replace XSLT version with whichever version has been selected by the user.
            # initial_prompt = initial_prompt.replace("version 1.0", st.session_state.transformation_type)
            print(initial_prompt)
        return {'role': 'assistant', 'content': initial_prompt}  
    except IOError as e:
        st.error(f"Error reading default system prompts file: {e}")
        return None

# Function to retrieve the default system prompt from a file
def get_default_system_prompt_update_xslt():
    """
    Retrieves the default system prompt from a file.
    
    Returns:
    str: The initial prompt
    None: If there's an error reading the file.
    """
    try:
        file_path = current_dir / "../config/prompts/generic/default_system_prompts_for_update.txt"
        with file_path.open('r', encoding='utf-8') as file:
            initial_prompt = file.read()
        return {'role': 'assistant', 'content': initial_prompt}  
    except IOError as e:
        st.error(f"Error reading default system prompts file: {e}")
        return None

def get_default_user_prompts():
    """
    Retrieves the default user prompts from a file.
    
    Returns:
    dict: A dictionary with 'role' as 'user' and 'content' as the prompt text.
    None: If there's an error reading the file.
    """
    try:
        file_path = current_dir / "../config/prompts/generic/default_user_prompts.txt"
        with file_path.open('r', encoding='utf-8') as file:
            user_prompts = file.read()
        return {'role': 'user', 'content': user_prompts}
    except IOError as e:
        st.error(f"Error reading default user prompts file: {e}")
        return None

def get_default_system_prompt_md():
    """
    Retrieves the default system prompt from a file.
    
    Returns:
    str: The initial prompt
    None: If there's an error reading the file.
    """
    try:
        file_path = current_dir / "../config/prompts/generic/default_system_prompts_md.txt"
        with file_path.open('r', encoding='utf-8') as file:
            initial_prompt = file.read()
            print(initial_prompt)
        return {'role': 'assistant', 'content': initial_prompt}  
    except IOError as e:
        st.error(f"Error reading default system prompts file: {e}")
        return None

def get_default_system_prompt_html():
    """
    Retrieves the default system prompt from a file.
    
    Returns:
    str: The initial prompt
    None: If there's an error reading the file.
    """
    try:
        file_path = current_dir / "../config/prompts/generic/default_system_prompts_html.txt"
        with file_path.open('r', encoding='utf-8') as file:
            initial_prompt = file.read()
            print(initial_prompt)
        return {'role': 'assistant', 'content': initial_prompt}
    except IOError as e:
        st.error(f"Error reading default system prompts file: {e}")
        return None

def get_additional_user_instructions_prompts(user_instructions_file):
    """
    Retrieves additional user instruction prompts from a specified file.
    
    Args:
    user_instructions_file (str): Path to the file containing additional instructions.
    
    Returns:
    dict: A dictionary with 'role' as 'user' and 'content' as the prompt text.
    None: If the file doesn't exist or there's an error reading it.
    """
    if user_instructions_file:
        try:
            with open(user_instructions_file, 'r') as file:
                user_prompts = file.read()
            st.Info("Loading additional user instruction prompts")
            return {'role': 'user', 'content': user_prompts}
        except IOError as e:
            st.error(f"Error reading file: {e}")
            return None
    return None

def get_requested_system_prompts(file):
    """
    Retrieves additional user instruction prompts from a specified file.
    
    Args:
    user_instructions_file (str): Path to the file containing additional instructions.
    
    Returns:
    dict: A dictionary with 'role' as 'user' and 'content' as the prompt text.
    None: If the file doesn't exist or there's an error reading it.
    """
    if file:
        try:
            with open(file, 'r') as file:
                user_prompts = file.read()
            st.Info("Loading system instruction prompts")
            return {'role': 'system', 'content': user_prompts}
        except IOError as e:
            st.error(f"Error reading file: {e}")
            return None
    return None

def load_prompts(source_xml_file, target_xml_file, mapping_specifications, transformation_type):
    system_prompts = []
    system_prompts.append(get_default_system_prompt())
    # Enforce the root element to be whatever the user chooses.
    system_prompts.append({"role": "system", "content": f"Begin paths in the XSLT with: {st.session_state.root_element}"})
    system_prompts.append({"role": "user", "content": f"""Original question: Generate the XSLT stylesheet 
                           that transforms the provided input XML into the desired output XML. 
                           Use {transformation_type} version, output encoding=UTF-8 and use xsl:template='/'. indent=yes."""})
    
    system_prompts.append({"role": "user", "content": f"The input XML, enclosed in triple -. ---{st.session_state.input_xml}---"})
    system_prompts.append({"role": "user", "content": f"The output XML, enclosed in triple ~. ~~~{target_xml_file}~~~"})
    system_prompts.append(get_default_user_prompts())
    if mapping_specifications is not None:
        system_prompts.append({"role": "system", "content": f"For attributes and elements if optional use an if test."})
        instr_prompt = {'role': 'user', 'content': "Below are the specifications: take all hardcoded values from them.\n" + mapping_specifications}
        # st.info(instr_prompt)
        system_prompts.append(instr_prompt)
    return system_prompts

def load_prompts_update(xslt):
    system_prompts = []
    system_prompts.append(get_default_system_prompt_update_xslt())
    system_prompts.append({"role": "system", "content": f"Ignore any blocks of code that are enclosed within <!--Manual change-->."})
    system_prompts.append({"role": "user", "content": f"The existing XSLT, enclosed in triple ^. ^^^{xslt}^^^"})
    return system_prompts

def load_prompts_update_specs(mapping_specifications):
    system_prompts = []
        
    if mapping_specifications is not None:
        system_prompts.append({"role": "system", "content": f"For attributes and elements if optional use an if test."})
        instr_prompt = {'role': 'user', 'content': "Here are the specification :\n" + mapping_specifications}
        system_prompts.append(instr_prompt)
    return system_prompts

def load_prompts_xslt(xslt_file):
    system_prompts = []
    # system_prompts.append(get_default_system_prompt())
    # Enforce the root element to be whatever the user chooses.
    # system_prompts.append({"role": "system", "content": f"Begin paths in the XSLT with: {st.session_state.root_element}"})
    system_prompts.append({"role": "user", "content": """Original question: Simplify the given XSLT to a more readable format. 
                           Do not use the current variable names. 
                           Attributes must not be mentioned seperately but instead with the parent node. 
                           Use output encoding=UTF-8 and use xsl:template='/'. indent=yes."""})
    system_prompts.append({"role": "user", "content": f"The input XSLT, enclosed in triple -. ---{xslt_file}---"})
    # system_prompts.append(get_default_user_prompts())
    return system_prompts

def get_default_system_prompt_gap_analysis():
    """
    Retrieves the default system prompt from a file for gap analysis.
    
    Returns:
    str: The initial prompt
    None: If there's an error reading the file.
    """
    try:
        with open('../../config/prompts/generic/default_system_prompt_for_gap_analysis.txt', 'r', encoding="utf-8") as file:
            initial_prompt = file.read()
        return {'role': 'assistant', 'content': initial_prompt}  
    except IOError as e:
        st.error(f"Error reading default system prompts file: {e}")
        return None
    
def load_prompts_gap_analysis(source_xml_file, target_xml_file, mapping_specifications,  onboarding_ai, reference_ai):
    system_prompts = []
    system_prompts.append(get_default_system_prompt_gap_analysis())
    system_prompts.append({"role": "user", "content": f"The input XML, enclosed in triple -. ---{source_xml_file}---"})
    system_prompts.append({"role": "user", "content": f"The output XML, enclosed in triple ~. ~~~{target_xml_file}~~~"})
    system_prompts.append({"role": "user", "content": f"Treat and mention the first XML as {onboarding_ai}"})
    system_prompts.append({"role": "user", "content": f"Treat and mention the second XML as {reference_ai}"})
    if mapping_specifications is not None:
        instr_prompt = {'role': 'user', 'content': "Here are the specifications :\n" + mapping_specifications}
        # st.info(instr_prompt)
        system_prompts.append(instr_prompt)
    return system_prompts

def load_prompts_xslt(xslt_file):
    system_prompts = []
    system_prompts.append(get_default_system_prompt())
    # Enforce the root element to be whatever the user chooses.
    # system_prompts.append({"role": "system", "content": f"Begin paths in the XSLT with: {st.session_state.root_element}"})
    system_prompts.append({"role": "user", "content": """Original question: Simplify the given XSLT to a more readable format. 
                           Do not use the current variable names. 
                           Attributes must not be mentioned seperately but instead with the parent node. 
                           Use output encoding=UTF-8 and use xsl:template='/'. indent=yes."""})
    system_prompts.append({"role": "user", "content": f"The input XSLT, enclosed in triple -. ---{xslt_file}---"})
    system_prompts.append(get_default_user_prompts())
    return system_prompts

def load_prompts_md(xslt_file):
    system_prompts = []
    system_prompts.append(get_default_system_prompt_md())
    # Enforce the root element to be whatever the user chooses.
    system_prompts.append({"role": "user", "content": """Original question: Generate a markdown file for the given XSLT following the below format:
                           <index>. Input: <input xpath>
                            Output: <output xpath>
                            Remarks: <any logic required to generate the output>
                           Repeat for all nodes in the above format.
                           If the ouput is hardcoded, mention Input as NA and Remarks as Hardcoded as <value>.
                           If the ouput is directly mapped from input, mention Remarks as NA. indent=yes."""})
    system_prompts.append({"role": "user", "content": f"The input XSLT, enclosed in triple -. ---{xslt_file}---"})
    return system_prompts

def load_prompts_html(md_file):
    system_prompts = []
    system_prompts.append(get_default_system_prompt_html())
    # Enforce the root element to be whatever the user chooses.
    system_prompts.append({"role": "user", "content": """Original question: Generate a HTML file for the given Markdown creating three columns for Input, Output and Remarks. indent=yes."""})
    system_prompts.append({"role": "user", "content": f"The input Markdown, enclosed in triple -. ---{md_file}---"})
    return system_prompts