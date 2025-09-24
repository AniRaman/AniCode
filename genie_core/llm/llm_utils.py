import os
import json
import pandas as pd
import streamlit as st
import re
import textwrap
from collections import Counter
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

import sys
# Open the file once at the top of your main script
log_file = open("full_output_log.txt", "w", encoding="utf-8")
sys.stdout = log_file  # Redirect all print output globally

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

def get_chat_completion_with_stop(input_messages, model_name=o3_mini_model_name):
    try:
        print(f"Model Used: {o3_mini_model_name}")
        response = o3client.chat.completions.create(
            model=model_name,
            messages=input_messages,
            stop=["<!-- END OF FRAGMENT -->"]
            )
        return response
    except Exception as e:
        print(f"Error in get_chat_completion: {e.__cause__}")
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
    
    # Extract original stylesheet tag to preserve it exactly
    original_stylesheet_match = re.search(r'<xsl:stylesheet[^>]*>', xslt_content)
    original_stylesheet_tag = original_stylesheet_match.group(0) if original_stylesheet_match else None
    
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

        # 2) deterministic rules (always run, no caching - they're fast to recompute)
        ruled_text, rule_actions, placeholder_map = rule_based_refine(chunk_text)
        print("Inside Rules finder")
        if rule_actions:
            # If deterministic merge_attr_loops applied, skip LLM – fully refined already
            if any(a.get('op') == 'merge_attr_loops' for a in rule_actions):
                print("merge_attr_loops applied – skipping LLM call")
                # Replace placeholders since we're skipping LLM
                from .refine_cache import replace_placeholders
                final_result = replace_placeholders(ruled_text, placeholder_map) if placeholder_map else ruled_text
                print("Ruled text inside merge_attr_loops: ", final_result)
                return final_result
        else:
            ruled_text = chunk_text  # unchanged

        # 3) LLM refinement – single template
        def extract_template_body(xslt_chunk: str) -> str:
            # Match everything inside <xsl:template ...>...</xsl:template>
            match = re.search(r"<xsl:template[^>]*>(.*?)</xsl:template>", xslt_chunk, re.DOTALL)
            if match:
                inner_content = match.group(1).strip()
                return inner_content
            return xslt_chunk.strip()
            
        refined_inner = extract_template_body(ruled_text) 
        ruled_text_with_marker = refined_inner + "\n" + "<!-- END OF FRAGMENT -->"
        print("Before LLM XSLT : ", ruled_text_with_marker)
        print("Inside LLM")
        prompts = [
        {
            "role": "system",
            "content": (
            "You are an expert in XSLT 1.0. Simplify incomplete XSLT fragments using @* with name() filters. "
            "Do not add, remove, or close any tags. Leave any partially shown elements exactly as-is—assume they belong to surrounding context. "
            "Always avoid repetition, avoid completing missing parts, and return only raw XML without markdown or commentary. "
            "Stop exactly at the end marker <!-- END OF FRAGMENT -->."
            )
        },
        {
            "role": "user",
            "content": f"""
        CRITICAL INSTRUCTIONS:
        1. Simplify this XSLT fragment as much as possible with efficient XPath and XSLT 1.0 syntax.
        2. Apply any needed transformations (substring, boolean, number) inline.
        3. Use attribute wildcards (@*) and name() filters when applicable.
        4. Do not add template wrappers or closing tags—keep it incomplete exactly as given.
        5. Return only the refined chunk without commentary or markdown.

        {ruled_text_with_marker}
        """
        }
        ]

        gpt_response = get_chat_completion_with_stop(prompts,o3_mini_model_name)
        llm_out = gpt_response.choices[0].message.content.strip()
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
            
            # Replace placeholders in LLM result
            from .refine_cache import replace_placeholders
            final_result = replace_placeholders(refined_llm, placeholder_map) if placeholder_map else refined_llm
            return final_result
            
        except Exception as e:
            print(f"Error computing diff actions: {e}")
            # Fallback to passthrough if diff fails
            cache_actions(fp, [{"op": "llm_passthrough", "refined": refined_llm}])
            
            # Replace placeholders in LLM result
            from .refine_cache import replace_placeholders
            final_result = replace_placeholders(refined_llm, placeholder_map) if placeholder_map else refined_llm
            return final_result

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
        """Process each chunk with placeholders and replace sequentially."""
        m = re.search(r'(<xsl:template[^>]*>)([\s\S]*?)(</xsl:template>)', tmpl_text)
        if not m:
            return _process_chunk(tmpl_text)
        open_tag, body, close_tag = m.groups()
        
        # Create well-formed XML chunks from body
        chunks = _create_well_formed_chunks(body, char_budget)
        
        def format_xslt_chunk(chunk_text):
            """Format XSLT chunk with proper line breaks and indentation."""
            # Add newlines after closing tags
            formatted = re.sub(r'>(<[^/][^>]*>)', r'>\n\1', chunk_text)
            # Add newlines before closing tags if they're immediately after content
            formatted = re.sub(r'>([^<\n]+)</([^>]+)>', r'>\n\1\n</\2>', formatted)
            # Add newlines after self-closing tags
            formatted = re.sub(r'/>(<[^>]*>)', r'/>\n\1', formatted)
            # Clean up multiple newlines
            formatted = re.sub(r'\n\s*\n', r'\n', formatted)
            # Add basic indentation
            lines = formatted.split('\n')
            indent_level = 0
            formatted_lines = []
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                # Decrease indent for closing tags
                if line.startswith('</'):
                    indent_level = max(0, indent_level - 1)
                # Add indentation
                formatted_lines.append('\t' * indent_level + line)
                # Increase indent for opening tags (but not self-closing)
                if line.startswith('<') and not line.startswith('</') and not line.endswith('/>'):
                    indent_level += 1
            return '\n'.join(formatted_lines)

        # Step 1: Replace all chunks with placeholders
        current_template = tmpl_text
        
        # Format the entire template consistently
        current_template = format_xslt_chunk(current_template)
        current_template = "\n".join(line.strip() for line in current_template.splitlines() if line.strip())

        for i, chunk in enumerate(chunks):
            placeholder = f"<Chunk{i+1}/>"
            # Format the chunk properly
            chunk = format_xslt_chunk(chunk)
            chunk = "\n".join(line.strip() for line in chunk.splitlines() if line.strip())
            # if i == 0:
            #     with open("first_chunk_formatted.txt", "w", encoding="utf-8") as file:
            #         file.write(chunk) 
            current_template = current_template.replace(chunk, placeholder, 1)
            print(f"DEBUG: Replaced chunk {i+1} with {placeholder}")
        
        # Step 2: Process each chunk and replace its placeholder
        for i, chunk in enumerate(chunks):
            placeholder = f"<Chunk{i+1}/>"
            print(f"DEBUG: Processing chunk {i+1}/{len(chunks)} - input length: {len(chunk)}")
            
            # Process this chunk
            seg_text = f"{open_tag}{chunk}{close_tag}"
            refined_seg = _process_chunk(seg_text)
            print(f"DEBUG: Chunk {i+1} refined length: {len(refined_seg)}")
            
            # Extract inner content from refined result
            refined_inner = _extract_inner_content_from_refined(refined_seg, open_tag, close_tag, chunk, i+1)
            
            # Validate chunk structure and fix tag discrepancies
            print(f"DEBUG: Chunk {i+1} - Validating structural tags")
            refined_inner = _validate_chunk_structure(chunk, refined_inner)
            # Format the refined content consistently
            refined_inner = format_xslt_chunk(refined_inner)
            refined_inner = "\n".join(line.strip() for line in refined_inner.splitlines() if line.strip())
            # Replace placeholder with refined content
            if placeholder in current_template:
                current_template = current_template.replace(placeholder, refined_inner, 1)            
                print(f"DEBUG: Chunk {i+1} - Successfully replaced {placeholder} with refined content")
            else:
                print(f"DEBUG: Chunk {i+1} - ERROR: {placeholder} not found in template!")
            
            # Check for optimizations
            union_count = refined_inner.count('|')
            if union_count > 0:
                print(f"DEBUG: Chunk {i+1} - Contains {union_count} union operators - optimization preserved!")
        
        print(f"DEBUG: Final template length: {len(current_template)}")
        print(f"DEBUG: Final template union count: {current_template.count('|')}")
        return current_template
    
    def _extract_inner_content_from_refined(refined_seg: str, open_tag: str, close_tag: str, original_chunk: str, chunk_num: int) -> str:
        """Extract inner content from refined template by simply removing the template wrapper."""
        
        # Simple regex to extract everything between template tags
        pattern = r'<xsl:template[^>]*>(.*)</xsl:template>'
        match = re.search(pattern, refined_seg, re.DOTALL)
        
        if match:
            inner = match.group(1)
            print(f"DEBUG: Chunk {chunk_num} - Extracted inner content ({len(inner)} chars)")
            return inner
        else:
            print(f"DEBUG: Chunk {chunk_num} - Could not extract inner content, using original chunk")
            return refined_seg
    
    def _extract_structural_tag_names(content: str) -> list:
        """Extract non-XSL tag names in order (opening and closing)."""
        import re
        tag_list = []
        
        # Find all tags that don't start with xsl:
        for match in re.finditer(r'<(/?(?!xsl:)\w+)[^>]*>', content):
            tag_name = match.group(1)
            if tag_name.startswith('/'):
                tag_list.append('/' + tag_name[1:])  # closing tag like "/TaxAmount"
            else:
                tag_list.append(tag_name)  # opening tag like "TaxAmount"
        
        return tag_list

    def _validate_chunk_structure(input_chunk: str, refined_chunk: str) -> str:
        """Compare structural tags and fix discrepancies."""
        input_tags = _extract_structural_tag_names(input_chunk)
        output_tags = _extract_structural_tag_names(refined_chunk)
        print("Validating chunk structure")
        print(f"Input tags: {input_tags}")
        print(f"Output tags: {output_tags}")
        
        if input_tags == output_tags:
            print("Tag lists match perfectly")
            return refined_chunk
        elif len(output_tags) < len(input_tags):
            print("Output has fewer tags than input - applying XML validation logic")
            
            # Count element tags (non-XSLT tags) in input vs output
            input_tag_count = len(input_tags)
            output_tag_count = len(output_tags)
            tag_difference = abs(output_tag_count - input_tag_count)
            
            print(f"Tag count difference: {tag_difference} (input: {input_tag_count}, output: {output_tag_count})")
            
            # If difference is odd, fall back to original chunk
            if tag_difference % 2 == 1:
                print("Odd tag difference detected - falling back to original chunk")
                return input_chunk
            
            # For even differences, validate that different tags form complete pairs
            if tag_difference > 0:
                # Check if all different tags have proper opening/closing pairs
                if _validate_tag_pairs(input_tags, output_tags):
                    print("Even tag difference with proper pairs - using refined chunk")
                    return refined_chunk
                else:
                    print("Tag pairs not properly matched - falling back to original chunk")
                    return input_chunk
            
            # No difference in count but content differs - validate pairs
            if not _validate_tag_pairs_content(input_tags, output_tags):
                print("Tag pairing validation failed - falling back to original chunk")
                return input_chunk
            
            # All validation passed for fewer tags case
            return refined_chunk
        else:
            print("Output has extra tags - fixing discrepancies")
            return _fix_tag_discrepancies(refined_chunk, input_tags, output_tags)

    def _fix_tag_discrepancies(refined_chunk: str, input_tags: list, output_tags: list) -> str:
        """Remove extra tags from refined chunk until it matches input structure."""
        current_content = refined_chunk
        
        # Find extra tags in output that aren't in input
        extra_tags = []
        for tag in output_tags:
            if tag not in input_tags:
                extra_tags.append(tag)
        
        print(f"Extra tags found in output: {extra_tags}")
        
        # Remove each extra tag
        for extra_tag in extra_tags:
            print(f"Removing extra tag: {extra_tag}")
            
            if extra_tag.startswith('/'):
                # It's a closing tag, extract the tag name
                tag_name = extra_tag[1:]  # Remove the '/'
            else:
                # It's an opening tag
                tag_name = extra_tag
            
            # Apply the removal logic
            current_content = _remove_first_complete_tag_block(current_content, tag_name)
        
        print("Content after llm xslt repair : ", current_content)
        return current_content

    def _remove_first_complete_tag_block(content: str, tag_name: str) -> str:
        """Remove first duplicate closing tag and all closing tags until next opening tag."""
        import re
        
        print(f"Removing first duplicate closing tag {tag_name} and subsequent closing tags")
        
        lines = content.split('\n')
        closing_pattern = f'</{tag_name}>'
        
        # Find the first occurrence of the duplicate closing tag
        first_closing_line = -1
        for i, line in enumerate(lines):
            if closing_pattern in line:
                first_closing_line = i
                print(f"Found first closing {tag_name} at line {i + 1}: {line.strip()[:100]}")
                break
        
        if first_closing_line >= 0:
            # Starting from this closing tag, remove all closing tags until we find an opening tag
            lines_to_remove = []
            
            for i in range(first_closing_line, len(lines)):
                line = lines[i].strip()
                
                # Check if this line contains an opening tag (but not self-closing)
                if re.search(r'<[^/!][^>]*[^/]>', line) and not line.startswith('</'):
                    print(f"Found opening tag at line {i + 1}, stopping removal: {line[:100]}")
                    break
                
                # Check if this line contains a closing tag
                if re.search(r'</[^>]+>', line):
                    lines_to_remove.append(i)
                    print(f"Marking closing tag for removal at line {i + 1}: {line[:100]}")
            
            # Remove the marked lines (in reverse order to maintain indices)
            for line_idx in reversed(lines_to_remove):
                print(f"Removing line {line_idx + 1}: {lines[line_idx].strip()[:100]}")
                lines.pop(line_idx)
            
            print(f"Removed {len(lines_to_remove)} closing tag lines")
            return '\n'.join(lines)
        else:
            print(f"Could not find first closing {tag_name}")
            return content

    def _validate_tag_pairs(input_tags: list, output_tags: list) -> bool:
        """Validate that different tags between input and output form complete opening/closing pairs."""
        import re
        
        # Find tags that are different between input and output
        input_set = set(input_tags)
        output_set = set(output_tags)
        
        different_tags = (input_set - output_set) | (output_set - input_set)
        
        if not different_tags:
            return True  # No differences, validation passes
        
        print(f"Different tags to validate: {different_tags}")
        
        # For each different tag, check if it has a matching opening/closing pair
        for tag in different_tags:
            if tag.startswith('/'):
                # This is a closing tag, find its opening counterpart
                opening_tag = tag[1:]  # Remove the '/'
                if opening_tag not in different_tags:
                    print(f"Closing tag {tag} has no matching opening tag in differences")
                    return False
            else:
                # This is an opening tag, find its closing counterpart  
                closing_tag = '/' + tag
                if closing_tag not in different_tags:
                    print(f"Opening tag {tag} has no matching closing tag in differences")
                    return False
        
        print("All different tags have proper opening/closing pairs")
        return True
    
    def _validate_tag_pairs_content(input_tags: list, output_tags: list) -> bool:
        """Validate that tag pairs are properly matched in content ordering."""
        # Create dictionaries to count opening and closing tags
        input_pairs = _count_tag_pairs(input_tags)
        output_pairs = _count_tag_pairs(output_tags)
        
        # Check if all tag pairs are balanced in both input and output
        for tag_name, counts in input_pairs.items():
            if counts['open'] != counts['close']:
                print(f"Input has unbalanced tag pairs for {tag_name}: {counts['open']} open, {counts['close']} close")
                return False
        
        for tag_name, counts in output_pairs.items():
            if counts['open'] != counts['close']:
                print(f"Output has unbalanced tag pairs for {tag_name}: {counts['open']} open, {counts['close']} close")
                return False
        
        print("All tag pairs are properly balanced")
        return True
    
    def _count_tag_pairs(tags: list) -> dict:
        """Count opening and closing tags for each tag name."""
        pairs = {}
        
        for tag in tags:
            if tag.startswith('/'):
                # Closing tag
                tag_name = tag[1:]
                if tag_name not in pairs:
                    pairs[tag_name] = {'open': 0, 'close': 0}
                pairs[tag_name]['close'] += 1
            else:
                # Opening tag
                if tag not in pairs:
                    pairs[tag] = {'open': 0, 'close': 0}
                pairs[tag]['open'] += 1
        
        return pairs

    # --- iterate templates in document order ---

    for t in templates:
        original = t["text"]
        print(f"DEBUG: Processing template {t['id'][:50]}... ({len(original)} chars, budget: {char_budget})")
        if len(original) <= char_budget:
            print("Inside ProcessChunk")
            refined = _process_chunk(original)
        else:
            print("Inside ProcessLargeTemplate")
            refined = _process_large_template(original)

        try:
            with open("debug_xslt_fragment.xml", "w", encoding="utf-8") as f:
                f.write(refined)
            
            # Handle both complete templates and body-only content
            if not refined.strip().startswith('<xsl:template'):
                print(f"DEBUG: Refined content is body-only, reconstructing template")
                
                # Extract namespace declarations from original stylesheet tag
                import re
                if original_stylesheet_tag:
                    xmlns_pattern = r'xmlns:?[^=]*="[^"]*"'
                    xmlns_matches = re.findall(xmlns_pattern, original_stylesheet_tag)
                    namespace_attrs = ' '.join(xmlns_matches)
                else:
                    # Fallback to basic namespaces if stylesheet tag not found
                    namespace_attrs = 'xmlns:xsl="http://www.w3.org/1999/XSL/Transform"'
                
                # Parse refined content with namespace context (like _create_well_formed_chunks)
                temp_wrapper = f'<temp {namespace_attrs}>{refined}</temp>'
                temp_root = etree.fromstring(temp_wrapper.encode())
                
                # Create new template element with original attributes
                original_template_attrs = dict(t["elem"].attrib)
                new_elem = etree.Element("{http://www.w3.org/1999/XSL/Transform}template", original_template_attrs)
                
                # Move all parsed children from temp wrapper to template
                for child in temp_root:
                    new_elem.append(child)
                    
                print(f"DEBUG: Reconstructed template with {len(list(new_elem))} children")
            else:
                # Complete template - parse normally
                new_elem = etree.fromstring(refined.encode())
            
            t["elem"].getparent().replace(t["elem"], new_elem)
            print(f"[SUCCESS] Successfully replaced template {t['id'][:50]}... with refined version")
        except Exception as e:
            print(f"[ERROR] Failed to replace template {t['id'][:50]}... Error: {e}")
            print(f"[ERROR] Refined content (first 200 chars): {refined[:200]}...")
            print(f"[ERROR] Keeping original template for {t['id'][:50]}...")

    final_xslt = etree.tostring(tree, encoding="unicode", pretty_print=True)
    
    # Preserve the original stylesheet tag exactly as provided in input
    if original_stylesheet_tag:
        # Replace the generated stylesheet tag with the original one
        final_xslt = re.sub(r'<xsl:stylesheet[^>]*>', original_stylesheet_tag, final_xslt, count=1)
        print(f"DEBUG: Preserved original stylesheet tag: {original_stylesheet_tag}")
    
    st.session_state.generated_xslt = final_xslt
           
    print("Inside 9")
    return

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



# Backward compatibility wrapper for agentic approach
def process_user_response(message, chat_history, input_xml, transformed_xml, main_xslt, specs):
    """
    XSLT processing using agentic approach with intelligent function calling
    """
    print("Using AGENTIC approach for XSLT processing")
    from genie_core.llm.agentic_xslt_processor import process_user_request_agentic
    return process_user_request_agentic(
        message, chat_history, input_xml, transformed_xml, main_xslt, specs
    )
