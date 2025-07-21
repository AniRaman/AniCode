import os
import json
import pandas as pd
import streamlit as st
import re
import numpy as np
import chromadb
from openai import AzureOpenAI
from dotenv import load_dotenv, find_dotenv
from genie_core.llm import TokenCostCalculator
from genie_core.llm.TokenCostCalculator import TokenCostCalculator
from genie_core.prompts.prompt_utils import *
from genie_core.common.confluence_utils import publish_content
from genie_core.database.database_utils import parse_questions_and_retreive_answers
from genie_core.llm.llm_response_handler_utils import get_answer, get_answer_md, get_answer_html, consolidating_questions
from genie_core.common.user_interaction import add_to_prompts, add_to_messages, write_chat_message
from genie_core.common.utils import extract_space_and_page_name,get_body,refine_and_display_markdown,convert_html_to_csv, convert_html_to_markdown, refine_and_display_markdown_update, markdown_to_html_table
from genie_core.database.llamaIndex import query_eng_setup,get_answer_llm
from genie_core.xml_processing.xml_utils import verify_prerequisite
from genie_core.data_processing.cleanup import row_extraction
import httpx
pd.set_option('display.max_colwidth', None)
pd.set_option('display.max_columns', None)
httpx_client = httpx.Client(verify=False)
_ = load_dotenv(find_dotenv())

global model_name_used

gpt4o_model_name = os.getenv("GPT4O_MODEL_DEPLOYMENT_NAME")
o1_model_name = os.getenv("o1_MODEL_DEPLOYMENT_NAME")
o3_mini_model_name = os.getenv("o3_mini_MODEL_DEPLOYMENT_NAME")

o1client = AzureOpenAI(
  azure_endpoint = os.getenv("o1_AZURE_OPENAI_ENDPOINT"), 
  api_key=os.getenv("o1_AZURE_OPENAI_KEY"),  
  api_version=os.getenv("o1_AZURE_API_VERSION"),
  http_client=httpx_client
)

o3client = AzureOpenAI(
  azure_endpoint = os.getenv("o3_mini_AZURE_OPENAI_ENDPOINT"), 
  api_key=os.getenv("o3_mini_AZURE_OPENAI_KEY"),  
  api_version=os.getenv("o3_mini_AZURE_API_VERSION"),
  http_client=httpx_client
)

gpt4oclient = AzureOpenAI(
  azure_endpoint = os.getenv("GPT4O_AZURE_OPENAI_ENDPOINT"), 
  api_key=os.getenv("GPT4O_AZURE_OPENAI_KEY"),  
  api_version=os.getenv("GPT4O_AZURE_API_VERSION"),
  http_client=httpx_client
)

text_embd_client = AzureOpenAI(
 azure_endpoint = os.getenv("ADA_EMBD_AZURE_OPENAI_ENDPOINT"), 
 api_key=os.getenv("ADA_EMBD_AZURE_OPENAI_KEY"),  
 api_version=os.getenv("ADA_EMBD_AZURE_API_VERSION"),
 http_client=httpx_client
)

def generate_embedding(client, text, deployment_name="text-embedding-ada-002"):
    response = client.embeddings.create(
        model=deployment_name,  # The deployment name of the embedding model
        input=[text]
    )
    # Return the embedding vector
    return response.data[0].embedding

class Agent:
    calculator = None
    def __init__(self, prompts, gpt_client, model_name) -> None:
        self.prompts = prompts
        self.gpt_client = gpt_client
        self.model_name = model_name
        self.temperature = 0
        self.responses = []
     
    def add_message(self, prompt):
        self.prompts.append(prompt)

    def add_user_message(self, prompt):
        self.prompts.append({"role": "user", "content": prompt})

    def get_all_prompts(self):
        return self.prompts

    def set_temperature(self, temperature):
        self.temperature = temperature

    def set_prompts(self, prompts):
        self.prompts = prompts

    def get_all_responses(self):
        return self.responses

    def get_chat_completion(self):
        """
        Generate a chat completion using the specified model.
        """
        try:
            response = self.gpt_client.chat.completions.create(
                model=self.model_name,
                messages=self.get_all_prompts()
                # temperature=self.temperature,
                # top_p = 0.9,
                )

            prompt_tokens = response.usage.prompt_tokens
            completion_tokens = response.usage.completion_tokens
            calculator = TokenCostCalculator(self.model_name)
            cost_eur = calculator.calculate_cost(prompt_tokens, completion_tokens)
            return cost_eur, response
        except Exception as e:
            print(f"Error in get_chat_completion: {e.__cause__}")
            st.error(f"Error in get_chat_completion: {e}")
            return None

def setup_agent(model_name):
    """
    Sets up an agent with the specified model name by loading environment variables and initializing the GPT client.

    Args:
        model_name (str): The name of the model to be used for the agent.

    Returns:
        Agent: An instance of the Agent class initialized with the specified model.
    """

    _ = load_dotenv(find_dotenv())
    deployment_model = os.getenv(f"{model_name}_MODEL_DEPLOYMENT_NAME")
    azure_endpoint = os.getenv(f"{model_name}_AZURE_OPENAI_ENDPOINT")
    api_key = os.getenv(f"{model_name}_AZURE_OPENAI_KEY")
    api_version = os.getenv(f"{model_name}_AZURE_API_VERSION")

    print("deployment: ", deployment_model)
    print("azure_endpoint: ", azure_endpoint)
    print("api_key: ", api_key)
    print("api_version:", api_version)

    gpt_client = AzureOpenAI(
        azure_endpoint=azure_endpoint,
        api_key=api_key,
        api_version=api_version,
        http_client=httpx.Client(verify=False)
    )

    agent = Agent([], gpt_client, deployment_model)
    return agent

def get_chat_completion(input_messages, model_name=o3_mini_model_name):
    try:
        if model_name == gpt4o_model_name:
            print(f"Model Used: {model_name}")
            response = gpt4oclient.chat.completions.create(
                model=model_name,
                messages=input_messages,
                temperature=0,
                top_p=0.9,  # this is the degree of randomness of the model's output
            )

        elif model_name == o1_model_name:
            print(f"Model Used: {o1_model_name}")
            response = o1client.chat.completions.create(
                model=model_name,
                messages=input_messages)
            
        else:
            print(f"Model Used: {o3_mini_model_name}")
            response = o3client.chat.completions.create(
                model=model_name,
                messages=input_messages
            )

        # Calculate token cost
        # prompt_tokens = response.usage.prompt_tokens
        # completion_tokens = response.usage.completion_tokens
        # calculator = TokenCostCalculator(model_name)
        # cost_eur = calculator.calculate_cost(prompt_tokens, completion_tokens, currency="EUR")
        # st.info(f"Token Cost: €{cost_eur} EUR")
        return response
    except Exception as e:
        # print(f"Error in get_chat_completion: {e.__cause__}")
        st.error(f"Error in get_chat_completion: {e}")
        return None
    
def show_result(result):
    print(result.choices[0].message.content)

def get_result(result):
    return result.choices[0].message.content
    
def show_result_with_stats(result):
    """
    Print the content of the first message and token usage statistics.
    """
    print(result.choices[0].message.content)
    print(f"prompt_tokens={result.usage.prompt_tokens}, completion_tokens={result.usage.completion_tokens}, total_tokens={result.usage.total_tokens}")

def show_stats(result):
    """
    Print token usage statistics for the chat completion.
    """
    print(f"prompt_tokens={result.usage.prompt_tokens}, completion_tokens={result.usage.completion_tokens}, total_tokens={result.usage.total_tokens}")

def initiate_conversation_with_LLM(source_xml_file, target_xml_file, mapping_specifications_file, transformation_type):
    """
    Initiates a conversation with the LLM using the provided input files.

    Args:
        source_xml_file (str): The path to the source XML file.
        target_xml_file (str): The path to the target XML file.
        mapping_specifications_file (str): The path to the mapping specifications file.

    """

    # Load prompts and create GPT client
    system_prompts = load_prompts(source_xml_file, target_xml_file, mapping_specifications_file, transformation_type)
    xslt_generator_agent = setup_agent("GPT4O")
    xslt_generator_agent.set_prompts(system_prompts)
    st.session_state.generator_agent = xslt_generator_agent

    # Invoke LLM
    with st.spinner('Analysing the inputs, processing!'):
        llm_response = xslt_generator_agent.get_chat_completion()
        if not llm_response.choices[0].message.content:
            st.error("Error in generating XSLT. No response was generated.")
            return

    with st.spinner('Processing the response!'):
        has_questions = process_response(llm_response)

    if has_questions:
        with st.spinner('Hang on, fine tuning the XSLT!'):
            subsequent_call_to_LLM(source_xml_file, target_xml_file, mapping_specifications_file)
    # else:
    #     write_chat_message("assistant", ":green[No questions, XSLT generated successfully.]")
    if not st.session_state.has_human_feedback:
        write_chat_message("assistant", ":green[No questions, XSLT generated successfully.]")
        add_to_messages(":green[No questions, XSLT generated successfully.]")

def initiate_conversation_with_LLM_coe(source_xml_file, target_xml_file, mapping_specifications_file):
    pass

def initiate_conversation_with_LLM_update(source_xml_file, target_xml_file, xslt, mapping_specifications_file, 
                                          cookbooks, user_requirement_prompt, shared_agent):
    combined_prompts = []
    print("mapping_specifications_file : ", mapping_specifications_file)
    space, page_name = extract_space_and_page_name(mapping_specifications_file)
    st.session_state.url = mapping_specifications_file
    page_name = page_name.replace("+", " ")
    st.session_state.space,st.session_state.page_name = space,page_name
    if space and page_name:
        html_content = get_body(space, page_name)
        if html_content:
            #mapping_specifications_file = convert_html_to_markdown(html_content)
            csv_data,dataFrame = convert_html_to_csv(html_content)
            markdown_table = dataFrame.to_markdown(index=False)
            print("Markdown file before refinement : ", markdown_table)
            mapping_specifications_file = refine_and_display_markdown_update(markdown_table)
            st.session_state.specs_file = mapping_specifications_file
            print("Markdown file after refinement : ", mapping_specifications_file)
        else:
            st.error("Invalid Page")
    else:
        st.error("Invalid URL format")

    system_prompts = load_prompts_update(xslt)
    combined_prompts = []
    for prompt in system_prompts:
        combined_prompts.append(prompt)
    combined_prompts.append({"role":"user", "content": "The user instruction to update the XSLT" + user_requirement_prompt})
    combined_prompts.append({"role":"user", "content": "Return only JSON with 'updated_XSLT'."})

    shared_agent.set_prompts(combined_prompts)
    with st.spinner('Updating XSLT...'):
        cost, llm_response = shared_agent.get_chat_completion()
        st.session_state.number_of_calls_to_llm += 1
        st.session_state.total_cost_per_tool += cost
    if llm_response:
        print(llm_response.choices[0].message.content)
        response = re.sub(r'[\x00-\x1F\x7F]', '', llm_response.choices[0].message.content)
        if response.lstrip().lower().startswith('json'):
            response = response.lstrip()[4:].lstrip()
        try:
            resp_json = json.loads(response)
            st.session_state.updated_xslt = resp_json['updated_XSLT']
            print(resp_json['updated_XSLT'])
            add_to_messages("XSLT has been updated. Now updating specs in the next step.")
        except json.JSONDecodeError:
            add_to_messages(response)

    # Step 2: update specs
    system_prompts = load_prompts_update_specs(mapping_specifications_file)
    combined_prompts = []
    for prompt in system_prompts:
        combined_prompts.append(prompt)
    combined_prompts.append({"role":"user", "content": "Now update the specification file based on user requirement : " + user_requirement_prompt})
    combined_prompts.append({
        "role":"system",
        "content": 
            "Your reply must be exactly a JSON object with one field:\n"
            "{\n"
            '  "updated_specs": "<the entire spec file as one JSON string>"\n'
            "}\n\n"
            "Example:\n"
            '{\n'
            '  "updated_specs": ""Input: , Output: OrderCreateRQ/@Version, Remarks: Hardcoded as 17.2, Type: Attribute\nInput: Request/Context/correlationid, Output: OrderCreateRQ/@Correlationid, Remarks: Optional, Type: \nInput: Request/Context/correlationID, Output: OrderCreateRQ/@TransactionIdentifier, Remarks: Optional, Type: \n'
            "}"
        })
    print(combined_prompts)
    shared_agent.set_prompts(combined_prompts)
    with st.spinner('Updating specs...'):
        cost, llm_response = shared_agent.get_chat_completion()
        st.session_state.number_of_calls_to_llm += 1
        st.session_state.total_cost_per_tool += cost
    if llm_response:
        print(llm_response.choices[0].message.content)
        response = re.sub(r'[\x00-\x1F\x7F]', '', llm_response.choices[0].message.content)
        if response.lstrip().lower().startswith('json'):
            response = response.lstrip()[4:].lstrip()
        try:
            resp_json = json.loads(response)
            st.session_state.updated_specs = resp_json['updated_specs']
            print(resp_json['updated_specs'])
            html_table = markdown_to_html_table(st.session_state.updated_specs)
            st.session_state.html = html_table
            add_to_messages("Specifications have been updated. Please check.")
        except json.JSONDecodeError:
            add_to_messages(response)
                
def initiate_conversation_with_LLM_for_gap_analysis(source_xml_file, target_xml_file, mapping_specifications_file, onboarding_ai, reference_ai):
    system_prompts = load_prompts_gap_analysis(source_xml_file, target_xml_file, mapping_specifications_file, onboarding_ai, reference_ai)
    for prompt in system_prompts:
        add_to_prompts(prompt)
    # user_instruction_prompt = {"role":"user", "content": "The user instruction to update the XSLT" + user_prompt}
    # system_prompts.append(user_instruction_prompt)
    # add_to_prompts(user_instruction_prompt)
    with st.spinner('Analysing the inputs, processing!'):
        llm_response = get_chat_completion(system_prompts)
        if llm_response:
            response_obj = llm_response.choices[0].message.content
            response = re.sub(r'[\x00-\x1F\x7F]', '', response_obj)

            # Check if response starts with 'json' and remove it
            if response.lstrip().startswith('json'):
                response = response.lstrip()[4:].lstrip()

            try:
                response_obj_json = json.loads(response)
                if response_obj_json.get('analysis'):
                    st.session_state.analysis = response_obj_json['analysis']
                    st.session_state.analysis_html = response_obj_json['analysis']
                    st.markdown(st.session_state.analysis_html, unsafe_allow_html=True)
                    st.session_state.questions_map = response_obj_json['questions']
                    add_to_messages(st.session_state.analysis_html)
                    if st.session_state.questions_map:
                        add_to_messages(st.session_state.questions_map)
                else:
                    add_to_messages(response)
            except json.JSONDecodeError:
                add_to_messages(response)
                
def subsequent_call_to_LLM(source_xml_file, target_xml_file, mapping_specifications_file ):
    """
    Handles subsequent calls to the LLM if there are questions requiring human feedback.

    Args:
        source_xml_file (str): The path to the source XML file.
        target_xml_file (str): The path to the target XML file.
        mapping_specifications_file (str): The path to the mapping specifications file.
    """
    questions_for_human_feedback = []

    for question, count in st.session_state.questions_map.items():
        if count > 1:
            questions_for_human_feedback.append(question)

    if not questions_for_human_feedback:
        st.session_state.has_human_feedback = False
        llm_response = st.session_state.generator_agent.get_chat_completion()
        has_questions = process_response(llm_response)
        if has_questions:
            subsequent_call_to_LLM(source_xml_file, target_xml_file, mapping_specifications_file)

    else:
        st.session_state.has_human_feedback = True
        questions_humanfeedback = ":red[Below questions require feedback from the user, please assist.]\n\n"

        for index, question in enumerate(questions_for_human_feedback):
                st.session_state.questions_map[question] = 0 # reset the count to 0 as user
                questions_humanfeedback += f"{index + 1}. {question}\n\n"
        write_chat_message("user", questions_humanfeedback)

def process_response_q(llm_response):

    response_obj = llm_response.choices[0].message.content
    generated_xslt = get_answer(response_obj)
    st.session_state.generated_xslt = generated_xslt

def process_response(llm_response):

    response_obj = llm_response.choices[0].message.content
    generated_xslt = get_answer(response_obj)
    st.session_state.generated_xslt = generated_xslt

    # Save generated XSLT to a file
    # output_path = "../../config/results/MH/generated_xslt.xslt"
    # with open(output_path, "w") as file:
    #     file.write(generated_xslt)
    has_questions, LLM_readable_questions, human_readable_questions = consolidating_questions(response_obj)

    # If any questions, retreive answers from documents (RAG)
    with st.spinner('Querying answers. Processing the given information, please wait!'):
        parse_questions_and_retreive_answers(human_readable_questions)
    return has_questions

def process_response_md(llm_response):

    response_obj = llm_response.choices[0].message.content
    generated_md = get_answer_md(response_obj)
    st.session_state.generated_md = generated_md

    # has_questions, LLM_readable_questions, human_readable_questions = consolidating_questions(response_obj)

    # # If any questions, retreive answers from documents (RAG)
    # with st.spinner('Querying answers. Processing the given information, please wait!'):
    #     parse_questions_and_retreive_answers(human_readable_questions)
    # return has_questions

def process_response_html(llm_response):

    response_obj = llm_response.choices[0].message.content
    generated_html = get_answer_html(response_obj)
    st.session_state.generated_html = generated_html

    # has_questions, LLM_readable_questions, human_readable_questions = consolidating_questions(response_obj)

    # # If any questions, retreive answers from documents (RAG)
    # with st.spinner('Querying answers. Processing the given information, please wait!'):
    #     parse_questions_and_retreive_answers(human_readable_questions)
    # return has_questions

def initiate_conversation_with_LLM_xslt(xslt_content):
    import re
    from lxml import etree
    # Pre-clean: remove unnecessary <xsl:variable> boilerplate
    var_pattern = r'<xsl:variable\s+name="var\d+_[^"]*"\s+select="\."\s*/>'
    xslt_clean = re.sub(var_pattern, "", xslt_content)
    # Parse XSLT
    tree = etree.fromstring(xslt_clean.encode() if isinstance(xslt_clean, str) else xslt_clean)
    NSMAP = {"xsl": "http://www.w3.org/1999/XSL/Transform"}
    from .refine_cache import (
        compute_fingerprint,
        get_cached_actions,
        cache_actions,
        rule_based_refine,
        apply_actions,
    )
    from .intelligent_chunk_processor import IntelligentChunkProcessor
    # Extract templates and IDs
    templates = []
    for tmpl in tree.findall(".//xsl:template", namespaces=NSMAP):
        text = etree.tostring(tmpl, encoding="unicode", pretty_print=True)
        tmpl_id = tmpl.get("name") or tmpl.get("match") or text
        fingerprint = compute_fingerprint(tmpl)
        templates.append({"id": tmpl_id, "text": text, "elem": tmpl, "fp": fingerprint})
    # Sequential one-by-one refinement with cache → rules → LLM (new flow)
    import hashlib
    from .refine_cache import _compute_edit_actions  # Import the diff function

    char_budget = 5000 # maximum characters for a single LLM prompt / chunk
    
    
    # Initialize intelligent chunk processor
    intelligent_processor = IntelligentChunkProcessor()

    def _process_chunk_intelligently(chunk_text: str) -> str:
        """Process chunk using intelligent pattern separation."""
        def llm_function(pattern_text):
            # Use the existing LLM processing logic
            return _process_chunk_with_llm_only(pattern_text)
        
        return intelligent_processor.process_chunk_intelligently(chunk_text, llm_function)
    
    def _process_chunk_with_llm_only(chunk_text: str) -> str:
        """Process chunk with LLM only (for complex patterns)."""
        # Use existing LLM processing logic
        return _process_chunk_original(chunk_text)
    
    def _process_chunk(chunk_text: str) -> str:
        """Refine a template (or segment) using cache, deterministic rules, then LLM."""
        # Check if we should use intelligent processing
        if len(chunk_text) > 1000:  # Use intelligent processing for larger chunks
            print("Using intelligent chunk processing")
            return _process_chunk_intelligently(chunk_text)
        else:
            print("Using standard chunk processing")
            return _process_chunk_original(chunk_text)
    
    def _process_chunk_original(chunk_text: str) -> str:
        """Original chunk processing logic (renamed for clarity)."""

        seed_before = """	<xsl:template name="tbf:tbf2_">
                                <xsl:param name="input" select="/.."/>
                                <xsl:for-each select="$input/@AbsoluteDeadline">
                                    <xsl:variable name="var1_current" select="."/>
                                    <xsl:attribute name="AbsoluteDeadline">
                                        <xsl:value-of select="."/>
                                    </xsl:attribute>
                                </xsl:for-each>
                                <xsl:for-each select="$input/@OffsetUnitMultiplier">
                                    <xsl:variable name="var3_current" select="."/>
                                    <xsl:attribute name="OffsetUnitMultiplier">
                                        <xsl:value-of select="."/>
                                    </xsl:attribute>
                                </xsl:for-each>
                                <xsl:for-each select="$input/@OffsetDropTime">
                                    <xsl:variable name="var4_current" select="."/>
                                    <xsl:attribute name="OffsetDropTime">
                                        <xsl:value-of select="."/>
                                    </xsl:attribute>
                                </xsl:for-each>
                            </xsl:template> """
        seed_after = """<xsl:template name="tbf:tbf2_">
                            <xsl:param name="input"/>
                            <xsl:copy-of select="$input/@AbsoluteDeadline | 
                                                $input/@OffsetUnitMultiplier | 
                                                $input/@OffsetDropTime"/>
                        </xsl:template>"""
        # --- fingerprint ---
        try:
            fp_elem = etree.fromstring(chunk_text.encode())
            fp = compute_fingerprint(fp_elem)
        except Exception:
            # Fallback to raw hash when snippet is not well-formed XML (e.g. split mid-tag)
            fp = hashlib.sha256(chunk_text.encode()).hexdigest()

        # 1) cache lookup
        cached = get_cached_actions(fp)
        if cached:
            print("Inside DB, found the pattern, Applying actions....")
            return apply_actions(chunk_text, cached)

        # 2) deterministic rules (always run)
        ruled_text, rule_actions = rule_based_refine(chunk_text)
        print("Inside Rules finder")
        if rule_actions:
            cache_actions(fp, rule_actions)
            # If deterministic merge_attr_loops applied, skip LLM – fully refined already
            if any(a.get('op') == 'merge_attr_loops' for a in rule_actions):
                print("merge_attr_loops applied – skipping LLM call")
                print("Ruled text inside merge_attr_loops: ", ruled_text)
                return ruled_text
        else:
            ruled_text = chunk_text  # unchanged

        # 3) LLM refinement – single template
        print("Before LLM XSLT : ", ruled_text)
        agent = setup_agent("o3_mini")
        print("Inside LLM")
        prompts = [
            {"role": "system", "content": '''You are an expert XSLT refiner. Return only the refined <xsl:template> element without commentary or markdown. 
                                                Follow the example given for refining Efficiently : "Example before sending to LLM :\n{seed_before}\nExample after receiving from LLM:\n{seed_after}" '''},
            {"role": "user", "content": ruled_text},
        ]
        agent.set_prompts(prompts)
        _, response = agent.get_chat_completion()
        llm_out = response.choices[0].message.content.strip()
        m = re.search(r'(<xsl:template[\s\S]*?</xsl:template>)', llm_out)
        refined_llm = m.group(1) if m else llm_out
        print("Refined LLM", refined_llm)
        
        try:
            # Parse before/after for diffing
            before_elem = etree.fromstring(ruled_text.encode())
            after_elem = etree.fromstring(refined_llm.encode())
            
            # Compute and store the edit actions
            actions = _compute_edit_actions(before_elem, after_elem)
            if actions:
                cache_actions(fp, actions)
            return refined_llm
            
        except Exception as e:
            print(f"Error computing diff actions: {e}")
            # Fallback to passthrough if diff fails
            cache_actions(fp, [{"op": "llm_passthrough", "refined": refined_llm}])
            return refined_llm

    def _create_well_formed_chunks(body: str, max_chars: int) -> list:
        """Create well-formed XML chunks from template body that can be parsed by lxml."""
        # For very large templates, use a more efficient element-based approach
        if len(body) > 50000:  # For templates larger than 50KB
            return _element_based_chunking(body, max_chars)
        
        try:
            # Wrap the body in a temporary root to make it parseable with proper namespaces
            temp_xml = f'<temp xmlns:xsl="http://www.w3.org/1999/XSL/Transform">{body}</temp>'
            root = etree.fromstring(temp_xml.encode())
            
            chunks = []
            current_chunk = []
            current_size = 0
            
            def element_to_string(elem):
                """Convert element to string and get its size."""
                return etree.tostring(elem, encoding="unicode", pretty_print=True)
            
            def add_element_to_chunk(elem):
                """Add element to current chunk if it fits, otherwise start new chunk."""
                nonlocal current_chunk, current_size, chunks
                
                elem_str = element_to_string(elem)
                elem_size = len(elem_str)
                
                # If adding this element would exceed limit and we have content, start new chunk
                if current_size + elem_size > max_chars and current_chunk:
                    # Finalize current chunk
                    chunk_content = ''.join(current_chunk)
                    chunks.append(chunk_content)
                    current_chunk = []
                    current_size = 0
                
                # Add element to current chunk
                current_chunk.append(elem_str)
                current_size += elem_size
            
            # Process all children of the temporary root
            for child in root:
                add_element_to_chunk(child)
            
            # Add any remaining content as the last chunk
            if current_chunk:
                chunk_content = ''.join(current_chunk)
                chunks.append(chunk_content)
            
            return chunks if chunks else [body]
            
        except Exception as e:
            # If XML parsing fails, fall back to element-based chunking
            print(f"XML parsing failed for chunking: {e}")
            return _element_based_chunking(body, max_chars)
    
    def _element_based_chunking(body: str, max_chars: int) -> list:
        """Create chunks based on complete XML elements for very large templates."""
        # For very large templates, use a simpler approach that prioritizes parseable chunks
        # This approach looks for natural break points in XSLT like </xsl:for-each>
        
        chunks = []
        current_chunk = ""
        current_size = 0
        
        # Split on natural XSLT boundaries
        # Look for patterns like "</xsl:for-each>" followed by whitespace and then another element
        import re
        
        # Find all for-each blocks
        for_each_pattern = r'(<xsl:for-each[^>]*>.*?</xsl:for-each>)'
        matches = list(re.finditer(for_each_pattern, body, re.DOTALL))
        
        if not matches:
            # If no for-each blocks found, fall back to safe text chunking
            return _safe_text_chunking(body, max_chars)
        
        pos = 0
        for match in matches:
            # Add content before this for-each block
            before_content = body[pos:match.start()]
            if before_content.strip():
                if current_size + len(before_content) <= max_chars:
                    current_chunk += before_content
                    current_size += len(before_content)
                else:
                    if current_chunk:
                        chunks.append(current_chunk)
                    current_chunk = before_content
                    current_size = len(before_content)
            
            # Add the for-each block itself
            for_each_block = match.group(0)
            block_size = len(for_each_block)
            
            if current_size + block_size <= max_chars:
                current_chunk += for_each_block
                current_size += block_size
            else:
                # Block doesn't fit, start new chunk
                if current_chunk:
                    chunks.append(current_chunk)
                
                # If block is too large, break it safely
                if block_size > max_chars:
                    large_chunks = _safe_text_chunking(for_each_block, max_chars)
                    chunks.extend(large_chunks)
                    current_chunk = ""
                    current_size = 0
                else:
                    current_chunk = for_each_block
                    current_size = block_size
            
            pos = match.end()
        
        # Add any remaining content
        remaining = body[pos:]
        if remaining.strip():
            if current_size + len(remaining) <= max_chars:
                current_chunk += remaining
            else:
                if current_chunk:
                    chunks.append(current_chunk)
                chunks.append(remaining)
        
        # Add final chunk if it has content
        if current_chunk:
            chunks.append(current_chunk)
        
        return chunks if chunks else [body]
    
    def _find_complete_element_end(text: str, start: int) -> int:
        """Find the end of a complete XML element starting at 'start' position."""
        if start >= len(text) or text[start] != '<':
            return -1
        
        # Find the end of the opening tag
        tag_end = text.find('>', start)
        if tag_end == -1:
            return -1
        
        # Check if it's a self-closing tag
        if text[tag_end - 1] == '/':
            return tag_end + 1
        
        # Check if it's a comment, CDATA, or processing instruction
        if text[start:start + 4] == '<!--':
            comment_end = text.find('-->', start + 4)
            return comment_end + 3 if comment_end != -1 else -1
        
        if text[start:start + 9] == '<![CDATA[':
            cdata_end = text.find(']]>', start + 9)
            return cdata_end + 3 if cdata_end != -1 else -1
        
        if text[start:start + 2] == '<?':
            pi_end = text.find('?>', start + 2)
            return pi_end + 2 if pi_end != -1 else -1
        
        # It's a regular element, find the matching closing tag
        # Extract tag name
        tag_start = start + 1
        tag_name_end = tag_end
        for i in range(tag_start, tag_end):
            if text[i] in ' \t\n\r':
                tag_name_end = i
                break
        
        tag_name = text[tag_start:tag_name_end]
        if not tag_name:
            return tag_end + 1
        
        # Find matching closing tag
        closing_tag = f'</{tag_name}>'
        pos = tag_end + 1
        depth = 1
        
        while pos < len(text) and depth > 0:
            # Look for next tag
            next_open = text.find(f'<{tag_name}', pos)
            next_close = text.find(closing_tag, pos)
            
            if next_close == -1:
                return -1  # No matching closing tag
            
            # Check if there's an opening tag before the closing tag
            if next_open != -1 and next_open < next_close:
                # Make sure it's actually the same tag (not a prefix)
                char_after_pos = next_open + len(tag_name) + 1
                if char_after_pos < len(text):
                    char_after = text[char_after_pos]
                    if char_after in ' \t\n\r>/':
                        depth += 1
                        pos = next_open + len(tag_name) + 1
                    else:
                        pos = next_open + 1
                else:
                    # At end of text, treat as opening tag
                    depth += 1
                    pos = next_open + len(tag_name) + 1
            else:
                depth -= 1
                pos = next_close + len(closing_tag)
        
        return pos if depth == 0 else -1
    
    def _break_large_element(element: str, max_chars: int) -> list:
        """Break a large XML element into smaller chunks while trying to preserve structure."""
        if len(element) <= max_chars:
            return [element]
        
        # Try to find natural break points within the element
        chunks = []
        current_pos = 0
        
        while current_pos < len(element):
            end_pos = min(current_pos + max_chars, len(element))
            
            # Look for safe break points
            if end_pos < len(element):
                # Try to break at element boundaries
                safe_break = element.rfind('>', current_pos, end_pos)
                if safe_break > current_pos:
                    end_pos = safe_break + 1
                else:
                    # Break at whitespace
                    safe_break = element.rfind('\n', current_pos, end_pos)
                    if safe_break > current_pos:
                        end_pos = safe_break + 1
                    else:
                        safe_break = element.rfind(' ', current_pos, end_pos)
                        if safe_break > current_pos:
                            end_pos = safe_break + 1
            
            chunk = element[current_pos:end_pos]
            chunks.append(chunk)
            current_pos = end_pos
        
        return chunks
    
    def _regex_based_chunking(body: str, max_chars: int) -> list:
        """Efficient regex-based chunking for very large XSLT templates."""
        # Use element-based chunking for better XML structure preservation
        return _element_based_chunking(body, max_chars)
    
    def _find_matching_end_tag(text: str, start_pos: int, end_tag: str) -> int:
        """Find the position of the matching closing tag."""
        pos = start_pos
        depth = 1
        open_tag_name = end_tag.replace('</', '<').replace('>', '')
        
        while pos < len(text) and depth > 0:
            # Look for opening or closing tags
            next_open = text.find(open_tag_name, pos)
            next_close = text.find(end_tag, pos)
            
            if next_close == -1:
                return -1  # No matching closing tag found
            
            if next_open != -1 and next_open < next_close:
                depth += 1
                pos = next_open + len(open_tag_name)
            else:
                depth -= 1
                pos = next_close + len(end_tag)
                if depth == 0:
                    return pos
        
        return -1 if depth > 0 else pos
    
    def _find_safe_break_point(text: str, start: int, end: int) -> int:
        """Find a safe point to break the text without cutting through XML tags."""
        if end >= len(text):
            return len(text)
        
        # Look for the end of an element
        safe_break = text.rfind('>', start, end)
        if safe_break > start:
            return safe_break + 1
        
        # Look for whitespace
        safe_break = text.rfind('\n', start, end)
        if safe_break > start:
            return safe_break + 1
        
        # Look for space
        safe_break = text.rfind(' ', start, end)
        if safe_break > start:
            return safe_break + 1
        
        # If no safe break found, use the end position
        return end
    
    def _safe_text_chunking(text: str, max_chars: int) -> list:
        """Fallback chunking that tries to break at safe boundaries."""
        if len(text) <= max_chars:
            return [text]
        
        chunks = []
        current_pos = 0
        
        while current_pos < len(text):
            # Find the end position for this chunk
            end_pos = min(current_pos + max_chars, len(text))
            
            # If we're not at the end, try to find a safe break point
            if end_pos < len(text):
                # Look for the best break point in order of preference
                
                # 1. End of a complete element (</...>)
                safe_break = text.rfind('</xsl:for-each>', current_pos, end_pos)
                if safe_break > current_pos:
                    end_pos = safe_break + len('</xsl:for-each>')
                else:
                    # 2. End of any element
                    safe_break = text.rfind('>', current_pos, end_pos)
                    if safe_break > current_pos:
                        end_pos = safe_break + 1
                    else:
                        # 3. Look for whitespace break
                        safe_break = text.rfind('\n', current_pos, end_pos)
                        if safe_break > current_pos:
                            end_pos = safe_break + 1
                        else:
                            # 4. Look for space
                            safe_break = text.rfind(' ', current_pos, end_pos)
                            if safe_break > current_pos:
                                end_pos = safe_break + 1
                            # 5. If no safe break found, use the end position (may break XML)
            
            chunk = text[current_pos:end_pos]
            chunks.append(chunk)
            current_pos = end_pos
        
        return chunks

    def _process_large_template(tmpl_text: str) -> str:
        """Split oversized template body into well-formed XML chunks, refine each, then stitch back."""
        m = re.search(r'(<xsl:template[^>]*>)([\s\S]*?)(</xsl:template>)', tmpl_text)
        if not m:
            return _process_chunk(tmpl_text)
        open_tag, body, close_tag = m.groups()
        
        # Create well-formed XML chunks instead of character-based splitting
        chunks = _create_well_formed_chunks(body, char_budget)
        
        refined_bodies = []
        for chunk in chunks:
            seg_text = f"{open_tag}{chunk}{close_tag}"
            refined_seg = _process_chunk(seg_text)
            # strip wrappers again to join bodies cleanly
            inner = refined_seg[len(open_tag):-len(close_tag)] if refined_seg.startswith(open_tag) and refined_seg.endswith(close_tag) else chunk
            refined_bodies.append(inner)
        return f"{open_tag}{''.join(refined_bodies)}{close_tag}"

    # --- iterate templates in document order ---

    for t in templates:
        original = t["text"]
        if len(original) <= char_budget:
            print("Inside ProcessChunk")
            refined = _process_chunk(original)
        else:
            print("Inside ProcessLargeTemplate")
            refined = _process_large_template(original)
            
        # Replace in XML tree
        try:
            new_elem = etree.fromstring(refined.encode())
            t["elem"].getparent().replace(t["elem"], new_elem)
        except Exception:
            # In case of malformed refined snippet – keep original
            pass

    final_xslt = etree.tostring(tree, encoding="unicode", pretty_print=True)
    st.session_state.generated_xslt = final_xslt
           
    print("Inside 9")
    return

#     # ---------------------------------------------------------------------
#     # Legacy batch logic (kept for reference, will never be executed)
#     # ---------------------------------------------------------------------
#     refined_map = {}
#     templates_for_llm = []
#     for t in templates:
#         actions = get_cached_actions(t["fp"])
#         if actions:
#             print(f"Pattern {t['fp'][:8]} found in DB/cache – applying recorded actions, no LLM call.")
#             refined_map[t["text"]] = apply_actions(t["text"], actions)
#             continue
#         # apply deterministic rules
#         auto_refined, actions_new = rule_based_refine(t["text"])
#         if actions_new:
#             print(f"Pattern {t['fp'][:8]} handled by rule-based refinement – no LLM call.")
#             refined_map[t["text"]] = auto_refined
#             cache_actions(t["fp"], actions_new)
#             continue
#         # else needs LLM
#         templates_for_llm.append(t)

#     if not templates_for_llm:
#         # all done via cache/rules
#         final_templates = [refined_map.get(t["text"], t["text"]) for t in templates]
#         return "".join(final_templates)  # quick exit, caller handles assembly

#     # Build dependency graph using templates_for_llm
#     deps = {t["id"]: set() for t in templates_for_llm}
#     for t in templates_for_llm:
#         for call in t["elem"].findall(".//xsl:call-template", namespaces=NSMAP):
#             callee = call.get("name")
#             if callee in deps:
#                 deps[t["id"]].add(callee)
#     # Topological sort
#     sorted_ids = []
#     temp_deps = {k: set(v) for k, v in deps.items()}
#     while temp_deps:
#         ready = [k for k, v in temp_deps.items() if not v]
#         if not ready:
#             ready = list(temp_deps.keys())
#         for rid in ready:
#             sorted_ids.append(rid)
#             temp_deps.pop(rid)
#             for vals in temp_deps.values():
#                 vals.discard(rid)
#     sorted_templates = [next(t for t in templates_for_llm if t["id"] == sid) for sid in sorted_ids]

#     # Preserve header/footer
#     # Determine header and footer around templates
#     template_pattern = re.compile(r'<xsl:template[\s\S]*?</xsl:template>')
#     matches = list(template_pattern.finditer(xslt_clean))
#     if matches:
#         first, last = matches[0], matches[-1]
#         header = xslt_clean[: first.start()]
#         footer = xslt_clean[last.end() :]
#     else:
#         header = ''
#         footer = ''
    
#     # Chunk templates by size and handle oversized templates
#     char_budget = 1000
#     chunks_data = []
#     current_content = ""
#     current_templates = []
#     for t in sorted_templates:
#         s = t["text"]
#         if len(s) > char_budget:
#             # flush existing chunk
#             if current_content:
#                 chunks_data.append({"content": current_content, "template_texts": current_templates, "segmented": False})
#                 current_content = ""
#                 current_templates = []
#             # split oversized template into segments
#             match = re.search(r'(<xsl:template[^>]*>)([\s\S]*?)(</xsl:template>)', s)
#             if match:
#                 open_tag, body, close_tag = match.groups()
#                 parts = [body[i:i+char_budget] for i in range(0, len(body), char_budget)]
#                 for part in parts:
#                     seg = open_tag + part + close_tag
#                     chunks_data.append({
#                         "content": seg,
#                         "template_texts": [seg],
#                         "segmented": True,
#                         "template_id": t["id"],
#                         "open_tag": open_tag,
#                         "close_tag": close_tag,
#                         "full_template": s
#                     })
#             else:
#                 # fallback to single chunk
#                 chunks_data.append({"content": s, "template_texts": [s], "segmented": False})
#         else:
#             # within budget, try adding to current chunk
#             if current_content and len(current_content) + len(s) > char_budget:
#                 chunks_data.append({"content": current_content, "template_texts": current_templates, "segmented": False})
#                 current_content = ""
#                 current_templates = []
#             current_content += s
#             current_templates.append(s)
#     # flush last chunk
#     if current_content:
#         chunks_data.append({"content": current_content, "template_texts": current_templates, "segmented": False})
#     #print(chunks)
#     # Seed example for first chunk
#     seed_before = """	<xsl:template name="tbf:tbf2_">
# 		<xsl:param name="input" select="/.."/>
# 		<xsl:for-each select="$input/@AbsoluteDeadline">
# 			<xsl:variable name="var1_current" select="."/>
# 			<xsl:attribute name="AbsoluteDeadline">
# 				<xsl:value-of select="."/>
# 			</xsl:attribute>
# 		</xsl:for-each>
# 		<xsl:for-each select="$input/@OffsetUnitMultiplier">
# 			<xsl:variable name="var3_current" select="."/>
# 			<xsl:attribute name="OffsetUnitMultiplier">
# 				<xsl:value-of select="."/>
# 			</xsl:attribute>
# 		</xsl:for-each>
# 		<xsl:for-each select="$input/@OffsetDropTime">
# 			<xsl:variable name="var4_current" select="."/>
# 			<xsl:attribute name="OffsetDropTime">
# 				<xsl:value-of select="."/>
# 			</xsl:attribute>
# 		</xsl:for-each>
# 	</xsl:template> """
#     seed_after = """<xsl:template name="tbf:tbf2_">
#   <xsl:param name="input"/>
#   <xsl:copy-of select="$input/@AbsoluteDeadline | 
#                      $input/@OffsetUnitMultiplier | 
#                      $input/@OffsetDropTime"/>
# </xsl:template>"""
#     # refined_map already partially filled
#     # Batch refine over template chunks
#     for idx, chunk in enumerate(chunks_data):
#         # Debug: show chunk info
#         print(f"Refining chunk {idx+1}/{len(chunks_data)} with {len(chunk['template_texts'])} templates")
#         agent = setup_agent("o3_mini")
#         # System prompt to return only refined templates
#         prompts = [
#             {"role": "system", "content": "You are an expert XSLT transformation refiner. Only return the refined <xsl:template> elements without any additional commentary or markdown formatting."}
#         ]
#         if idx == 0:
#             prompts.append({"role": "user", "content": f"Example before:\n{seed_before}\nExample after:\n{seed_after}"})
#         prompts.append({"role": "user", "content": f"Global header:\n{header}"})
#         prompts.append({"role": "user", "content": f"Refine these templates for readability & performance within 2000 tokens:\n{chunk['content']}"})
#         agent.set_prompts(prompts)
#         _, response = agent.get_chat_completion()
#         print("Inside 1")
#         # Extract refined template snippets
#         refined_snips = re.findall(r'(<xsl:template[\s\S]*?</xsl:template>)', response.choices[0].message.content)
#         # Debug: number of snippets extracted
#         print(f"Extracted {len(refined_snips)} template snippets from LLM response")
#         # Map each original to its refined version
#         for orig, new in zip(chunk["template_texts"], refined_snips):
#             print("Inside 2")
#             refined_map[orig] = new
#             # cache for future
#             # Compute fingerprint again (same as t['fp'])
#             fp = compute_fingerprint(etree.fromstring(orig.encode()))
#             # TODO: derive generic actions from LLM diff; skipping for now

#         # Merge segmented template parts back into full templates
#     seg_map = {}
#     for chunk in chunks_data:
#         print("Inside 3")
#         if chunk.get('segmented'):
#             print("Inside 4")
#             tid = chunk['template_id']
#             entry = seg_map.setdefault(tid, {'open': chunk['open_tag'], 'close': chunk['close_tag'], 'full': chunk['full_template'], 'bodies': []})
#             refined_chunk = refined_map.get(chunk['content'], chunk['content'])
#             # strip open/close tags
#             body = refined_chunk[len(entry['open']):-len(entry['close'])]
#             entry['bodies'].append(body)
#     for entry in seg_map.values():
#         print("Inside 5")
#         full_refined = entry['open'] + ''.join(entry['bodies']) + entry['close']
#         refined_map[entry['full']] = full_refined
#     # Reassemble final XSLT via AST to avoid duplication
#     from copy import deepcopy
#     XSLT_NS = "http://www.w3.org/1999/XSL/Transform"
#     # Create a new stylesheet root preserving namespace and attributes
#     new_root = etree.Element(tree.tag, tree.attrib, nsmap=tree.nsmap)
#     # Append children in original order, replacing templates with refined versions
#     for child in tree:
#         print("Inside 6")
#         if isinstance(child.tag, str) and etree.QName(child.tag).namespace == XSLT_NS and etree.QName(child.tag).localname == "template":
#             print("Inside 7")
#             orig_text = etree.tostring(child, encoding="unicode", pretty_print=True)
#             refined_text = refined_map.get(orig_text, orig_text)
#             try:
#                 # Try parsing snippet directly
#                 new_elem = etree.fromstring(refined_text)
#             except etree.XMLSyntaxError:
#                 # Inject xsl namespace declaration into <xsl:template> tag
#                 ns_injected = re.sub(r'(<xsl:template\b)', r'\1 xmlns:xsl="' + XSLT_NS + '"', refined_text, count=1)
#                 new_elem = etree.fromstring(ns_injected)
#             new_root.append(new_elem)
#         else:
#             print("Inside 8")
#             new_root.append(deepcopy(child))
#     # Serialize final XSLT
#     final_xslt = etree.tostring(new_root, encoding="unicode", pretty_print=True)
#     st.session_state.generated_xslt = final_xslt
#     print("Inside 9")
#     return
    
#     # final_xslt = header + "".join(refined_map.get(t["text"], t["text"]) for t in templates) + footer
#     # st.session_state.generated_xslt = final_xslt
#     # return

def subsequent_conversation_with_LLM_xslt(xslt_file):
    # Load prompts and create GPT client
    system_prompts = load_prompts_md(xslt_file)
    xslt_generator_agent = setup_agent("GPT4O")
    xslt_generator_agent.set_prompts(system_prompts)
    st.session_state.generator_agent = xslt_generator_agent

    # Invoke LLM
    with st.spinner('Analysing the inputs, processing!'):
        cost, llm_response = xslt_generator_agent.get_chat_completion()
        if not llm_response.choices[0].message.content:
            st.error("Error in generating MD. No response was generated.")
            return
        
    with st.spinner('Processing the response!'):
        has_questions = process_response_md(llm_response)
        if has_questions:
            st.error('Hang on, fine tuning the MD!')

def subsequent_conversation_with_LLM_html(md_file):
    # Load prompts and create GPT client
    system_prompts = load_prompts_html(md_file)
    xslt_generator_agent = setup_agent("o3_mini")
    xslt_generator_agent.set_prompts(system_prompts)
    st.session_state.generator_agent = xslt_generator_agent

    # Invoke LLM
    with st.spinner('Analysing the inputs, processing!'):
        cost, llm_response = xslt_generator_agent.get_chat_completion()
        if not llm_response.choices[0].message.content:
            st.error("Error in generating specs. No response was generated.")
            return
        
    with st.spinner('Processing the response!'):
        has_questions = process_response_html(llm_response)
        if has_questions:
            st.error('Hang on, fine tuning the specs!')

def question_from_user(context, message, input_xml_1, output_xml_1):
    
    prompt = [
    {"role": "system", "content": "You are a helpful assistant, who is an expert in XMLs & XSLT. "}, #setting the behavior
    {"role": "user", "content": message},
    {"role": "assistant",  "content": f'''Generate only XSLT 1.0 code by fetching information from the 'Input XPATH', 'Description', and 'Output XPATH' columns in the provided context: {context}. 
                                        Generate XSLT 1.0 code STRICTLY without usage of any unnecessary libraries and for only the elements mentioned in message. Do not include any additional elements or code for additional elements beyond the one requested.
                                        The XSLT should start with '<xsl:stylesheet version="1.0"'
                                        Use this context as the primary source for generating the XSLT. Refer to the input XML ({input_xml_1}) and output XML ({output_xml_1}) to check XPaths.
                                        Focus on the formatting provided in the output XML and check for Missing Delimiters.                                        
                                        All elements in the XML use the `ns0` namespace prefix. Always include `ns0:` before each element in the XPath expressions. For example, "ns0:insuranceOptionSection/ns0:insuranceOptionDetails/ns0:pricingInformations/preferredCurrencyCode" here preferredCurrencyCode is missing the namespace ns0 which is wrong, correct thing would be "ns0:insuranceOptionSection/ns0:insuranceOptionDetails/ns0:pricingInformations/ns0:preferredCurrencyCode".
                                        Provide the XSLT in a single template as much as possible & Do not assume any details that are not explicitly mentioned in the context.'''
                                        }
            ]
    gpt_response = get_chat_completion(prompt)
    show_stats(gpt_response)
    complete_response = gpt_response.__str__()
    print(f"COMPLETE_RESPONSE: {complete_response}")
    response = gpt_response.choices[0].message.content
    print(f"RESPONSE: {response}")
    return (response,complete_response,prompt.__str__())

def compare_text(specs_text, user_text):

    embedding1 = generate_embedding(text_embd_client, specs_text)
    embedding2 = generate_embedding(text_embd_client, user_text)
    # Calculate similarity
    similarity_score = np.dot(embedding1, embedding2) / (np.linalg.norm(embedding1) * np.linalg.norm(embedding2))
    if similarity_score > 0.9:
        print("Inside compare_text and the output is True")
        return True  
    else:
        print("Inside compare_text and the output is False")
        return False

def refine_external(response, input_xml, transformed_xml, main_xslt,chat_history):
        
    prompt = [
        {"role": "system", "content": "You are a helpful assistant and an expert in XML and XSLT 1.0. Always provide accurate refinements, ensuring the new XSLT adheres to the input and output XML structure. Address specific questions or errors without making assumptions unless explicitly stated."},
        {"role": "user", "content": response},
        {"role": "assistant", "content": f"""
                                                Here is the previous XSLT you provided:
                                                ```xslt
                                                {main_xslt}
                                                ```
                                                This was the input XML:
                                                ```xml
                                                {input_xml}
                                                ```
                                                And the expected output XML:
                                                ```xml
                                                {transformed_xml}
                                                ``` 

                                                Providing the chat history so that you have more reference:
                                                ```Chat History
                                                {chat_history}
                                                ```
                                                Please refine only the mentioned field(s), add the necessary changes to the provided XSLT, and return the updated version. 
                                                Unchanged fields must remain exactly as they are.
                                                """}
            ]
    print("inside refine External xslt")
    gpt_response = get_chat_completion(prompt, o3_mini_model_name)
    show_stats(gpt_response)
    complete_response = gpt_response.__str__()
    print(f"COMPLETE_RESPONSE: {complete_response}")
    response = gpt_response.choices[0].message.content
    print(f"RESPONSE: {response}")
    return (response,complete_response,prompt.__str__())

# %%
###Main Function####
def combine_xslt_2(curr_xslt,main_xslt):
    
    startCode = '''<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" 
           xmlns:ns0="http://www.amadeus.net" exclude-result-prefixes="ns0">
           <xsl:output method="xml" indent="yes"/>'''
    
    prompt = [
    {"role": "system", "content": "You are a helpful assistant, who is an expert in XMLs & XSLT. "}, #setting the behavior
    {"role": "user", "content": "Combine the XSLTs provided without adding extra elements."},
    {"role": "assistant",  "content": f'''I have two XSLT snippets: XSLT 1 {main_xslt} and XSLT 2 {curr_xslt}.
                                            1.Merge all elements from both XSLT 1 and XSLT 2 into a single XSLT document.
                                            2.Include all elements from XSLT 1, and add any unique elements from XSLT 2 that are not already present in XSLT 1.
                                            3.If an element exists in both XSLTs, use the version from XSLT 2.
                                            4.Do not include any elements that were not generated by the XSLTs. Focus strictly on elements present in XSLT 1 and XSLT 2, and do not introduce new or unrelated elements.
                                            5.Ensure that the following conditions are met:
                                                No placeholders like <!-- ... (rest of the template remains unchanged) ... --> or similar comments should be used. The output must contain all merged elements in full detail, with nothing omitted or summarized.
                                                Include namespaces (e.g., ns0) in every XPath expression, even if the elements are conditionally checked or missing. Ensure proper namespace usage in all XPath expressions.
                                            6.Use the following code as the first two lines of the final XSLT: {startCode}.
                                            7.Organize the XSLT as follows:
                                                Group all templates, variables, and parameters under appropriate sections.
                                                Ensure that the final XSLT is well-formed, properly indented, and ready for execution.'''
                                        }
            ]
    print("inside combine 2 xslt")
    gpt_response = get_chat_completion(prompt,gpt4o_model_name)
    show_stats(gpt_response)
    complete_response = gpt_response.__str__()
    print(f"COMPLETE_RESPONSE: {complete_response}")
    response = gpt_response.choices[0].message.content
    print(f"RESPONSE: {response}")
    return (response,complete_response)

# %%
def refine_internal(main_xslt,output_xml_1):
    startCode = '''<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" 
           xmlns:ns0="http://www.amadeus.net" exclude-result-prefixes="ns0">
           <xsl:output method="xml" indent="yes"/>'''
    prompt = [
    {"role": "system", "content": "You are a helpful assistant, who is an expert in XMLs & XSLT."}, #setting the behavior
    {"role": "user", "content": "Refine the provided XSLT if errors are found as mentioned ."},
    {"role": "assistant",  "content": f'''Given the following XSLT 1.0 : {main_xslt} and output XML : {output_xml_1}, Assume that the Xpaths in XSLT are correct and generate a new output XML with this XSLT.
                                        1.Strictly compare only the fields that were directly generated by the XSLT with the corresponding fields in the provided output XML.
                                        2.Do not include, process, or consider any elements or fields present in the output XML that were not generated by the XSLT. These fields should be ignored entirely.
                                        3.If the elements generated by XSLT is not present in the provided output XML, remove it from the XSLT.
                                        4.The order of elements in the XML generated by the XSLT should should be strictly same as the output XML.Refine it accordingly
                                        5.Focus only on:
                                            Differences or errors in formatting between the fields produced by the XSLT and the corresponding fields in the output XML.
                                            Missing or Extra Delimiters.
                                            Determine if any field produced by the XSLT is empty. If so, investigate the cause.
                                            Check for potential namespace issues in XPath.
                                        6.If discrepancies are found, refine and regenerate the XSLT 1.0, ensuring that the following two lines of code are added at the start: {startCode}.
                                        7.If no issues or refinements are needed, return an empty string.
                                        Important:
                                            Don't alter the Parent of each Xpath in the XSLT code. Consider to change only if there is a way to combine all under a single parent.
                                            Generate code without assumptions or hypothetical scenarios.
                                            Ignore all fields and elements not generated by the XSLT. Do not process or modify these.
                                            The focus should be exclusively on fields that the XSLT itself generates.
                                            Ensure that the regenerated XSLT contains only those fields directly involved in the transformation process.'''
                                        }
            ]
    print("inside refine_internal xslt")
    gpt_response = get_chat_completion(prompt,o3_mini_model_name)
    show_stats(gpt_response)
    complete_response = gpt_response.__str__()
    print(f"COMPLETE_RESPONSE: {complete_response}")
    response = gpt_response.choices[0].message.content
    print(f"RESPONSE: {response}")
    return (response,complete_response)

def convert_md_to_html(response):
    # Headers for the table
    headers = ["Field", "Input XPATH", "Output XPATH", "Complexity", "M/C/O", "Description"]

    # Remove the long dashes
    data_values = [val.strip() for val in response.split("|")]
    data_values.pop(0)
    data_values = [val for idx, val in enumerate(data_values, 1) if idx % 7 != 0]
    print(data_values)

    # Build the HTML table
    html_table = '<table data-table-width="1800" data-layout="full-width"><tr>'
    for header in headers:
        html_table += f"<th><p>{header}</p></th>"
    html_table += "</tr>"

    # Add rows to the table
    for i in range(12, len(data_values), 6):
        html_table += "<tr>"
        for j in range(6):
            value = data_values[i + j] if i + j < len(data_values) else ""
            html_table += f"<td><p>{value}</p></td>"
        html_table += "</tr>"

    html_table += "</table>"

    return html_table

def upload_spec(mapping_specifications):
    system_prompts = []
    if mapping_specifications is not None:
        instr_prompt = {'role': 'user', 'content': "Here are the specification :\n" + mapping_specifications}
        system_prompts.append(instr_prompt)
    return system_prompts

def update_specs(final_msg,fields_ref):
    if compare_text(final_msg,fields_ref):
        return
    else:
        ##UPdate specs
        print("MarkdownSpec : " , st.session_state.markdown_spec)
        system_prompts = upload_spec(st.session_state.markdown_spec)
        user_instruction_prompt = {"role":"user", "content": f'''The user instruction is to update the mapping specification with this update:{final_msg} and return the entire mapping document with the update. Give the updated document in this format :
                                                                | Field                              | Input XPATH                                                                                                                                                            
                                                                                                                                                                  | Output XPATH                   | Complexity   | M/C/O   | Description                                                                                                                                                                                                                   
                                                                                                        |
                                                                |:-----------------------------------|:------------------------------------------------------------------------------------------|:-------------------------------|:-------------|:--------|:---------------------------------------------------|
                                                                | Product ID                         |                                                                                                                                                                                        
                                                                                                                                                                                                                | product_id                     | S            | M       | Hardcode it to 12347nsaljscacnlaa                                                                                                                                                                                                             
                                                                                        |
                                                                | Coverage start date                | /InsuranceSmartShoppingRequest/insurancePlanSection/itineraryInfo/segmentDetails/flightDate/departureDate                                                                              
                                                                                                                                                                                                                | coverage_start_date            | S            | M       | The day on which coverage begins, Build it in this format :2021-10-01 '''}
        system_prompts.append(user_instruction_prompt)
        with st.spinner('Refining Specs....'):
            llm_response = get_chat_completion(system_prompts)
            print(llm_response)
            if llm_response:
                response = llm_response.choices[0].message.content
                print("response datatype : ",type(response))
                print("UPdated specsss:   ", response)

                refined_md,VectorDocument_ref= refine_and_display_markdown(response)
                st.session_state.updated_specs = refined_md
                html = convert_md_to_html(response)
                space, page_name = extract_space_and_page_name(st.session_state.url)
                page_name = page_name.replace("+", " ")
                st.session_state.space,st.session_state.page_name,st.session_state.html = space,page_name,html
                #publish_content(space, page_name, html)

def llm_process(context, message, input_xml, transformed_xml, main_xslt):
    print("Inside LLM Process")
    hidden_LLM_response,complete_LLM_response,bot_message = question_from_user(context, message, input_xml, transformed_xml)                                      
    LLM_xslt = hidden_LLM_response
    # Use a regular expression to capture the XSLT content
    xslt_code = re.search(r"(<xsl:stylesheet[^>]*>.*?</xsl:stylesheet>)", hidden_LLM_response, re.DOTALL)
    if not main_xslt: #If no XSLT has been generated yet, then use the current XSLT as main_xslt
        main_xslt = xslt_code.group(1)
    else: #Combining the current XSLT with already generated XSLTs
        hidden_LLM_response,complete_LLM_response = combine_xslt_2(xslt_code.group(1),main_xslt)
        xslt_code_comb = re.search(r"(<xsl:stylesheet[^>]*>.*?</xsl:stylesheet>)", hidden_LLM_response, re.DOTALL)
        main_xslt = xslt_code_comb.group(1)
    hidden_LLM_prompt,complete_LLM_response = refine_internal(main_xslt,transformed_xml)
    ref_xslt_code = re.findall(r"(<xsl:stylesheet[^>]*>.*?</xsl:stylesheet>)", hidden_LLM_prompt, re.DOTALL)
    if ref_xslt_code:
        main_xslt = ref_xslt_code[-1]
    return main_xslt

def process_user_response(message, chat_history, input_xml, transformed_xml, main_xslt, specs):
    print("-----------")
    print(message)
    print(chat_history)
    user_request = False
    bot_message = ""
    valid_format = False
    # If message contain START then resets all previous conversations
    # and then confirm if the input and output XMLs has been uploaded successfully

    # If bot_message is empty, 
    #    either the current message is START and the prerequisites are met OR we are in an ongoing conversations.
    #      Ongoing conversations can be of 2 types: 
    #      1. Its a conversation that is yet to engage LLM or has already to engaged LLM, i.e. chat_history beginning with START
    #      2. It's not a conversation that that is ready to engage LLM, i.e. chat_history not beginning with START
    #            So we ask the user to START 
    if not bot_message and message:
        # if we have chat history, we are in an ongoing conversation
        if message.strip().upper() == "START":
            chat_history = []
            bot_message = verify_prerequisite(input_xml, transformed_xml)
            print("found Start, to do: " + bot_message)
        print(f"Chat length: {len(chat_history)}")
        if len(chat_history):
            # As we reset history with every START, 
            # we can verify the presence of START message as the 1st message in hostory 
            if chat_history[0][0].strip().upper() == "START":
                # START is present, verifying the prerequisites again as they are multiple
                bot_message = verify_prerequisite(input_xml, transformed_xml)
                if not bot_message:
                    previous_message_from_bot = chat_history[-1][1]
                    print("Prev Msg from Bot: ", previous_message_from_bot)
                    
                    if previous_message_from_bot.find("UPLOAD INPUT XML") != -1 and  previous_message_from_bot.find("UPLOAD OUTPUT XML") != -1:
                        # relevant conversation has just started and all the prerequisites are met.
                        # So initiate conversation_with_LLM
                        bot_message = "Please provide Input & Output XMLs"

                        #previous_qna.extend(LLM_readable_questions)
                    elif message.strip().upper() == "YES":
                        bot_message = "Please provide the fields to be refined?"

                    elif message.strip().upper() == "NO":
                        bot_message = "Thank you. Please refresh the page to begin again"

                    elif previous_message_from_bot.find("Please provide the fields to be refined?") != -1:
                        bot_message = "What needs to be refined here?"

                    elif previous_message_from_bot.find("What needs to be refined here?") != -1:
                        chromadb.api.client.SharedSystemClient.clear_system_cache()
                        with st.spinner('Refining XSLT, Thanks for your patience'):
                            #document = chromadb_setup(specs)
                            #refine_check = chat_history[-4][1]
                            #if refine_check != 'What needs to be refined here?':
                            print(specs)
                            query_engine_llm = query_eng_setup(specs)
                            prev_user_resp = chat_history[-1][0]
                            fields_ref = get_answer_llm(query_engine_llm,prev_user_resp)
                            fields_ref_str = str(fields_ref)
                            print(fields_ref)
                            final_msg = prev_user_resp + "-" + message
                            #response = get_answer_llm(query_engine_llm,final_msg)
                            res = str(final_msg)
                            print(res)
                            whole_msg = f'''These are the fields to be refined: {prev_user_resp}. This is their previous mapping instruction: {fields_ref}. 
                                                Now please check this message from user: {res}. Now modify the specified field or fields in XSLT accordingly'''
                            print("whole msg: ", whole_msg)
                            hidden_LLM_response,complete_LLM_response,bot_message  =  refine_external(whole_msg, input_xml, transformed_xml, main_xslt,chat_history)
                            xslt_code = re.search(r"(<xsl:stylesheet[^>]*>.*?</xsl:stylesheet>)", hidden_LLM_response, re.DOTALL)
                            main_xslt = xslt_code.group(1)
                            bot_message = "Both XSLT and Specs have been refined. Any Corrections?"
                            update_specs(final_msg,fields_ref_str)
                            st.session_state.ask_yes_no = True
                            user_request = True 
                
                    elif previous_message_from_bot.find("Please provide the URL of the specs") != -1 or previous_message_from_bot.find("Provide Valid URL") != -1:
                        with st.spinner('Processing URL, Thanks for your patience'):
                            space, page_name = extract_space_and_page_name(message)
                            st.session_state.url = message
                            page_name = page_name.replace("+", " ")
                            if space and page_name:
                                html_content = get_body(space, page_name)
                                if html_content:
                                    #output_placeholder_html.markdown(html_content, unsafe_allow_html=True)
                                    csv_data,dataFrame = convert_html_to_csv(html_content)
                                    markdown_table = dataFrame.to_markdown(index=False)
                                    print("Markdown file : ", markdown_table)
                                    st.session_state.markdown_spec = markdown_table
                                    
                                    if markdown_table:
                                        refined_markdown_content,VectorDocument = refine_and_display_markdown(markdown_table)
                                    st.session_state.existing_specs = refined_markdown_content
                                    valid_format = True
                                    st.session_state.specs_file = VectorDocument

                                else:
                                    st.info("Please upload a valid URL.")
                            else:
                                st.error("Invalid URL format")
                        if valid_format:
                            print("User Response : " , message)
                            batch_size = 8
                            batch_size_c = 4
                            s_rows,c_rows =  row_extraction(dataFrame)
                            with st.spinner('Generating XSLT, Thanks for your patience'):
                                for i in range(0,len(c_rows),batch_size_c):

                                    context = c_rows.iloc[i:i + batch_size_c]
                                    print(f"context {i // batch_size_c + 1}:")
                                    context_fields = ",".join(map(str, context["Field"]))
                                    print(f"Map all the elements mentioned here :{context_fields}")
                                    if not context_fields:
                                        continue
                                    message = f"Map all the elements mentioned here :{context_fields}"
                                    print(context)                                    
                                    
                                    main_xslt = llm_process(context, message, input_xml, transformed_xml, main_xslt)
                                    
                                for i in range(0, len(s_rows), batch_size):    
                                                                                          
                                    context = s_rows.iloc[i:i + batch_size]
                                    print(f"context {i // batch_size + 1}:")
                                    context_fields = ",".join(map(str, context["Field"]))
                                    print(f"Map all the elements mentioned here :{context_fields}")
                                    if not context_fields:
                                        continue
                                    message = f"Map all the elements mentioned here :{context_fields}"
                                    print(context)
                                    main_xslt = llm_process(context, message, input_xml, transformed_xml, main_xslt)                             
                                bot_message = "XSLT for your requested field has been generated. Do you want to refine?"
                                st.session_state.ask_yes_no = True
                                user_request = True
                                st.session_state.existing_xslt = main_xslt
                        else:
                            bot_message = "Provide Valid URL"

                    else:
                        bot_message = "Please be specific"

                        
            # When START is not present we ask the user to type START to begin 
            else:
                bot_message = "Type START to begin..."

        else:
            print("No history block")     
            # If we are in this else block it means, relevant conversation has just started and all the prerequisites are met.
            # So initiate conversation_with_LLM
            bot_message = verify_prerequisite(input_xml, transformed_xml)
            xslt_code = ""
            if not bot_message and message.strip().upper() == "START":
                bot_message = "Please provide the URL of the specs"

            else:
                bot_message = "Type START to begin..."


    chat_history.append((message, bot_message))
    return user_request,bot_message, chat_history, main_xslt
