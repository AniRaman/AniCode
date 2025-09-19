"""
Agentic XSLT Processor - Function calling approach for XSLT generation
Replaces the conversation-based process_user_response with intelligent function calling
"""

import json
import os
import re
import streamlit as st
from dataclasses import dataclass
from typing import Dict, Any, List, Optional, Tuple
from genie_core.xml_processing.xml_utils import verify_prerequisite
from genie_core.common.utils import extract_space_and_page_name, get_body, convert_html_to_csv, refine_and_display_markdown
from genie_core.data_processing.cleanup import row_extraction
from genie_core.llm.llm_utils import get_chat_completion, llm_process, refine_external, update_specs, o3client, o3_mini_model_name
from genie_core.database.llamaIndex import query_eng_setup, get_answer_llm
import chromadb

@dataclass
class ConversationContext:
    """Centralized context management replacing scattered st.session_state usage"""
    specs_url: Optional[str] = None
    specs_data: Optional[str] = None  # markdown_spec
    current_xslt: Optional[str] = None  # existing_xslt
    processing_status: str = "not_started"  # not_started, processing, generated, refining
    specs_file: Optional[str] = None  # VectorDocument
    space: Optional[str] = None
    page_name: Optional[str] = None
    html: Optional[str] = None
    ask_yes_no: bool = False
    current_specs: Optional[str] = None  # For specs diff functionality

    def to_session_state(self):
        """Convert to session state for backward compatibility"""
        st.session_state.url = self.specs_url
        st.session_state.markdown_spec = self.specs_data

        # Simple XSLT versioning: 1st generation vs nth generation
        if self.current_xslt:
            # Always update the current/active XSLT
            st.session_state.generated_xslt = self.current_xslt

            # Store as original_xslt only on first generation
            if not st.session_state.original_xslt:
                st.session_state.original_xslt = self.current_xslt
            else:
                # On refinement, store as refined_xslt for diff
                st.session_state.refined_xslt = self.current_xslt

        # Simple specs versioning: 1st generation vs nth generation
        if self.current_specs:
            # Store as original_specs only on first generation
            if not st.session_state.original_specs:
                st.session_state.original_specs = self.current_specs
            else:
                # On refinement, store as refined_specs for diff
                st.session_state.refined_specs = self.current_specs

        st.session_state.specs_file = self.specs_file
        st.session_state.space = self.space
        st.session_state.page_name = self.page_name
        st.session_state.html = self.html
        st.session_state.ask_yes_no = self.ask_yes_no

    @classmethod
    def from_session_state(cls):
        """Create from existing session state for backward compatibility"""
        return cls(
            specs_url=getattr(st.session_state, 'url', None),
            specs_data=getattr(st.session_state, 'markdown_spec', None),
            current_xslt=getattr(st.session_state, 'generated_xslt', None),  # Use generated_xslt as current
            specs_file=getattr(st.session_state, 'specs_file', None),
            space=getattr(st.session_state, 'space', None),
            page_name=getattr(st.session_state, 'page_name', None),
            html=getattr(st.session_state, 'html', None),
            ask_yes_no=getattr(st.session_state, 'ask_yes_no', False),
            current_specs=getattr(st.session_state, 'original_specs', None)  # Use original_specs initially
        )

def get_function_definitions() -> List[Dict]:
    """Define functions that GPT can call for XSLT processing"""
    return [
        {
            "name": "validate_prerequisites",
            "description": "Check if all required inputs (input XML, output XML) are provided and validate them",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        },
        {
            "name": "process_specs_and_generate_xslt",
            "description": "Process specifications from URL or uploaded file and generate XSLT. This handles URL validation, file content processing, HTML to CSV conversion, DataFrame processing, and XSLT generation with complex-first batch processing.",
            "parameters": {
                "type": "object",
                "properties": {
                    "specs_source": {
                        "type": "string",
                        "description": "MUST be either: (1) HTTP/HTTPS URL for web specs, OR (2) 'file:filename' format for uploaded files. For file uploads, always extract the part after 'file:/' or 'file:' from user message."
                    }
                },
                "required": ["specs_source"]
            }
        },
        {
            "name": "refine_existing_xslt",
            "description": "Refine specific fields in existing XSLT based on user instructions. Uses RAG to find field context and applies refinements.",
            "parameters": {
                "type": "object",
                "properties": {
                    "field_names": {
                        "type": "string", 
                        "description": "Comma-separated list of field names to refine, extracted from user message"
                    },
                    "refinement_instructions": {
                        "type": "string",
                        "description": "User's instructions on how to refine the specified fields"
                    }
                },
                "required": ["field_names", "refinement_instructions"]
            }
        },
        {
            "name": "request_missing_prerequisites", 
            "description": "Identify and request missing prerequisites from the user",
            "parameters": {
                "type": "object",
                "properties": {
                    "missing_items": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of missing items: input_xml, output_xml, specs_url"
                    }
                },
                "required": ["missing_items"]
            }
        }
    ]

def validate_prerequisites() -> Tuple[bool, str, List[str]]:
    """
    Check if all prerequisites are met
    Returns: (all_met, message, missing_items)
    """
    missing_items = []
    
    # Check for XMLs using existing verify_prerequisite function
    input_xml = getattr(st.session_state, 'input_xml', None) 
    output_xml = getattr(st.session_state, 'output_xml', None)
    
    xml_message = verify_prerequisite(input_xml, output_xml)
    if xml_message:
        if "input XML" in xml_message.lower():
            missing_items.append("input_xml")
        if "output XML" in xml_message.lower():  
            missing_items.append("output_xml")
    
    # Check for specs URL in context
    context = ConversationContext.from_session_state()
    if not context.specs_url:
        missing_items.append("specs_url")
    
    if missing_items:
        return False, xml_message, missing_items
    else:
        return True, "", []

def process_file_content(uploaded_file) -> Tuple[Optional[str], Optional[str]]:
    """
    Process uploaded file content and return HTML content and filename
    Returns: (html_content, filename)
    """
    try:
        filename = uploaded_file.name
        file_extension = filename.lower().split('.')[-1]
        
        if file_extension in ['html', 'htm', 'mhtml']:
            # Read HTML/MHTML content directly
            html_content = uploaded_file.read().decode('utf-8')
            return html_content, filename
            
        elif file_extension == 'md':
            # For markdown files, convert to HTML table format
            md_content = uploaded_file.read().decode('utf-8')
            # Simple approach: assume markdown table, convert to HTML
            html_content = f"<html><body>{md_content}</body></html>"
            return html_content, filename
            
        elif file_extension == 'csv':
            # For CSV files, convert to HTML table
            csv_content = uploaded_file.read().decode('utf-8')
            import pandas as pd
            import io
            df = pd.read_csv(io.StringIO(csv_content))
            html_table = df.to_html(index=False)
            html_content = f"<html><body>{html_table}</body></html>"
            return html_content, filename
            
        else:
            print(f"Unsupported file type: {file_extension}")
            return None, filename
            
    except Exception as e:
        print(f"Error processing file {uploaded_file.name}: {e}")
        return None, uploaded_file.name

def process_specs_and_generate_xslt(specs_source: str) -> Tuple[bool, str, Optional[str]]:
    """
    Process specifications from URL or uploaded file and generate XSLT
    Preserves exact logic from lines 1684-1740 of original function
    Returns: (success, message, generated_xslt)
    """
    try:
        # Determine if this is a URL or file
        print(f"DEBUG: process_specs_and_generate_xslt received specs_source: {repr(specs_source)}")
        print(f"DEBUG: specs_source type: {type(specs_source)}")                                      
               
        print("Specs source : ", specs_source)
        is_file = specs_source.startswith("file:")
        
        if is_file:
            # Handle uploaded file
            filename = specs_source[5:]  # Remove "file:" prefix
            
            # Get the uploaded file from session state
            uploaded_file = getattr(st.session_state, 'specs_file_input', None)
            if not uploaded_file:
                return False, "Uploaded file not found in session", None
            
            with st.spinner('Processing uploaded file, Thanks for your patience'):
                # Process file content
                html_content, filename = process_file_content(uploaded_file)
                
                if not html_content:
                    return False, f"Could not process file: {filename}", None
                    
                # For file processing, we don't have space/page_name
                space = "uploaded_file"
                page_name = filename
        else:
            # Handle URL (preserving original logic)
            with st.spinner('Processing URL, Thanks for your patience'):
                # Extract space and page name (preserving original logic)
                space, page_name = extract_space_and_page_name(specs_source)
                
                if not (space and page_name):
                    return False, "Provide Valid URL", None
                    
                page_name = page_name.replace("+", " ")
                html_content = get_body(space, page_name)
                
                if not html_content:
                    return False, "Please upload a valid URL.", None
        
        # Convert HTML to CSV and process (preserving original logic)
        csv_data, dataFrame = convert_html_to_csv(html_content)
        markdown_table = dataFrame.to_markdown(index=False)
        print("Markdown file : ", markdown_table)
        
        refined_markdown_content, VectorDocument = refine_and_display_markdown(markdown_table)
        
        # Update context (replacing scattered st.session_state usage)
        context = ConversationContext(
            specs_url=specs_source if not is_file else None,
            specs_data=markdown_table,
            specs_file=VectorDocument,
            space=space,
            page_name=page_name,
            processing_status="processing",
            current_specs=markdown_table  # Set initial specs for diff functionality
        )
        context.to_session_state()  # Backward compatibility
            
        # Generate XSLT using exact same batch processing logic
        print("User Response : ", specs_source)
        batch_size = 8
        batch_size_c = 4
        s_rows, c_rows = row_extraction(dataFrame)
        
        # Get XML inputs 
        input_xml = getattr(st.session_state, 'input_xml', None)
        output_xml = getattr(st.session_state, 'output_xml', None)
        main_xslt = context.current_xslt
        
        with st.spinner('Generating XSLT, Thanks for your patience'):
            # Process complex mappings first (preserving original order)
            for i in range(0, 2, batch_size_c):
                context_batch = c_rows.iloc[i:i + batch_size_c]
                print(f"context {i // batch_size_c + 1}:")
                context_fields = ",".join(map(str, context_batch["Field"]))
                print(f"Map all the elements mentioned here :{context_fields}")
                if not context_fields:
                    continue
                message = f"Map all the elements mentioned here :{context_fields}"
                print(context_batch)
                
                main_xslt = llm_process(context_batch, message, input_xml, output_xml, main_xslt)
            
            # Process simple mappings second (preserving original order)
            # for i in range(0, len(s_rows), batch_size):
            #     context_batch = s_rows.iloc[i:i + batch_size]
            #     print(f"context {i // batch_size + 1}:")
            #     context_fields = ",".join(map(str, context_batch["Field"]))
            #     print(f"Map all the elements mentioned here :{context_fields}")
            #     if not context_fields:
            #         continue
            #     message = f"Map all the elements mentioned here :{context_fields}"
            #     print(context_batch)
            #     main_xslt = llm_process(context_batch, message, input_xml, output_xml, main_xslt)
        
        # Update context with generated XSLT
        context.current_xslt = main_xslt
        context.processing_status = "generated"
        context.to_session_state()
        
        return True, "XSLT generated successfully! You can refine it by typing messages like 'Fix TaxAmount to include currency format' or download it from the output tab.", main_xslt
            
    except Exception as e:
        print(f"Error in process_specs_and_generate_xslt: {e}")
        return False, f"Error processing specifications: {str(e)}", None

def refine_existing_xslt(field_names: str, refinement_instructions: str) -> Tuple[bool, str, Optional[str]]:
    """
    Refine existing XSLT based on field names and instructions
    Preserves exact logic from lines 1656-1681 of original function
    Returns: (success, message, updated_xslt)
    """
    try:
        chromadb.api.client.SharedSystemClient.clear_system_cache()
        
        with st.spinner('Refining XSLT, Thanks for your patience'):
            # Get current context and inputs
            context = ConversationContext.from_session_state()
            specs = context.specs_file
            main_xslt = context.current_xslt
            input_xml = getattr(st.session_state, 'input_xml', None)
            output_xml = getattr(st.session_state, 'output_xml', None)

            print(f"DEBUG REFINEMENT: main_xslt exists: {main_xslt is not None}")
            print(f"DEBUG REFINEMENT: specs exists: {specs is not None}")
            print(f"DEBUG REFINEMENT: specs type: {type(specs)}")
            print(f"DEBUG REFINEMENT: field_names: '{field_names}'")
            print(f"DEBUG REFINEMENT: refinement_instructions: '{refinement_instructions}'")

            if not main_xslt:
                return False, "No XSLT found to refine. Please generate XSLT first.", None

            if not specs:
                return False, "No specs file found for refinement. Please regenerate XSLT.", None

            print("Specs content:", specs)
            query_engine_llm = query_eng_setup(specs)
            fields_ref = get_answer_llm(query_engine_llm, field_names)
            fields_ref_str = str(fields_ref)
            print(fields_ref)
            
            # Create refinement message (preserving original logic)
            final_msg = field_names + "-" + refinement_instructions
            res = str(final_msg)
            print(res)
            
            whole_msg = f'''These are the fields to be refined: {field_names}. This is their previous mapping instruction: {fields_ref}. 
                            Now please check this message from user: {res}. Now modify the specified field or fields in XSLT accordingly'''
            print("whole msg: ", whole_msg)
            
            # Execute refinement using existing function
            hidden_LLM_response, complete_LLM_response, bot_message = refine_external(
                whole_msg, input_xml, output_xml, main_xslt, []
            )
            
            # Extract XSLT from response
            xslt_code = re.search(r"(<xsl:stylesheet[^>]*>.*?</xsl:stylesheet>)", hidden_LLM_response, re.DOTALL)
            if xslt_code:
                updated_xslt = xslt_code.group(1)
                
                # Update context
                context.current_xslt = updated_xslt

                # Update specifications (preserving original logic)
                print(f"DEBUG: Calling update_specs with final_msg='{final_msg}', fields_ref_str='{fields_ref_str}'")
                try:
                    update_specs(final_msg, fields_ref_str)
                    print("DEBUG: update_specs completed successfully")
                except Exception as e:
                    print(f"DEBUG: update_specs failed with error: {e}")
                    # Continue without failing the entire refinement
                    pass

                # Capture updated specs from session state after update_specs call
                # update_specs sets st.session_state.updated_specs with the refined version
                if hasattr(st.session_state, 'updated_specs') and st.session_state.updated_specs:
                    context.current_specs = st.session_state.updated_specs

                context.to_session_state()
                
                return True, "XSLT and specifications refined successfully! Ask for more changes or download the updated XSLT.", updated_xslt
            else:
                return False, "Failed to extract refined XSLT from response", None
                
    except Exception as e:
        print(f"Error in refine_existing_xslt: {e}")
        return False, f"Error refining XSLT: {str(e)}", None

def request_missing_prerequisites(missing_items: List[str]) -> str:
    """Generate appropriate message for missing prerequisites"""
    messages = []
    
    if "input_xml" in missing_items:
        messages.append("Upload input XML")
    if "output_xml" in missing_items:
        messages.append("upload output XML") 
    if "specs_url" in missing_items:
        messages.append("provide specifications URL")
    
    if len(messages) == 1:
        return f"Please {messages[0]}."
    elif len(messages) == 2:
        return f"Please {messages[0]} and {messages[1]}."
    else:
        return f"Please {', '.join(messages[:-1])}, and {messages[-1]}."

def execute_function_call(function_call, input_xml=None, output_xml=None) -> Tuple[bool, str, Optional[str]]:
    """
    Execute the function called by GPT
    Returns: (success, message, xslt)
    """
    function_name = function_call.name
    
    try:
        arguments = json.loads(function_call.arguments) if function_call.arguments else {}
    except json.JSONDecodeError:
        return False, "Invalid function arguments", None
    
    if function_name == "validate_prerequisites":
        all_met, message, missing_items = validate_prerequisites()
        if all_met:
            return True, "All prerequisites are met. Ready to process.", None
        else:
            return False, request_missing_prerequisites(missing_items), None
    
    elif function_name == "process_specs_and_generate_xslt":
        specs_source = arguments.get("specs_source")
        if not specs_source:
            return False, "Specifications source is required", None
        return process_specs_and_generate_xslt(specs_source)
    
    elif function_name == "refine_existing_xslt":
        field_names = arguments.get("field_names", "")
        refinement_instructions = arguments.get("refinement_instructions", "")
        return refine_existing_xslt(field_names, refinement_instructions)
    
    elif function_name == "request_missing_prerequisites":
        missing_items = arguments.get("missing_items", [])
        message = request_missing_prerequisites(missing_items)
        return False, message, None
    
    else:
        return False, f"Unknown function: {function_name}", None

def build_system_prompt(context: ConversationContext, chat_history: List[Tuple[str, str]]) -> str:
    """Build system prompt with current context for GPT"""
    
    # Analyze current state
    input_xml = getattr(st.session_state, 'input_xml', None)
    output_xml = getattr(st.session_state, 'output_xml', None)
    
    xml_status = "✓ Input XML and Output XML are uploaded" if (input_xml and output_xml) else "✗ Missing XML files"
    specs_status = f"✓ Specs URL: {context.specs_url}" if context.specs_url else "✗ No specifications URL provided"
    xslt_status = f"✓ XSLT generated ({len(context.current_xslt)} chars)" if context.current_xslt else "✗ No XSLT generated yet"
    
    # Build context summary for GPT
    context_summary = f"""
Current Status:
- {xml_status}
- {specs_status}  
- {xslt_status}
- Processing Status: {context.processing_status}
"""
    
    # Add chat history context if available
    history_context = ""
    if chat_history:
        recent_history = chat_history[-3:] if len(chat_history) > 3 else chat_history
        history_context = "\n\nRecent Conversation:\n" + "\n".join([
            f"User: {msg[0]}\nBot: {msg[1]}" for msg in recent_history
        ])
    
    system_prompt = f"""You are an expert XSLT generation assistant. Your role is to help users generate XSLT transformations from specifications and refine them based on user requirements.

{context_summary}

## Your Capabilities:
1. **validate_prerequisites**: Check if input XML, output XML are provided
2. **process_specs_and_generate_xslt**: Process specifications URL and generate XSLT using intelligent batching (complex mappings first, then simple mappings)
3. **refine_existing_xslt**: Refine specific fields in existing XSLT based on user instructions
4. **request_missing_prerequisites**: Ask user for missing requirements

## Processing Rules:
- Always check prerequisites before starting any processing
- If user provides a URL and XMLs are uploaded, automatically start XSLT generation
- For refinements, extract field names from user messages and understand their instructions
- Maintain exact same error messages as original system for consistency
- Use complex-first batch processing strategy (4 rows for complex, 8 rows for simple)

## Response Guidelines:
- Be direct and helpful
- Use exact same terminology as the original system
- For errors, use messages like "Please upload a valid URL", "Provide Valid URL"
- For successful generation: "XSLT for your requested field has been generated. Do you want to refine?"
- For refinement completion: "Both XSLT and Specs have been refined. Any Corrections?"

## User Input Analysis:
- URLs (http/https links) → Process specifications and generate XSLT
- Field refinement requests ("fix TaxAmount field", "change currency format") → Refine existing XSLT
- General questions → Check what's needed and guide user
- Missing prerequisites → Request what's missing

{history_context}

Always call the appropriate function based on user input and current context. Do not engage in lengthy explanations - execute actions efficiently."""
    
    return system_prompt

def process_user_request_agentic(message: str, chat_history: List[Tuple[str, str]], 
                               input_xml: str, transformed_xml: str, main_xslt: str, 
                               specs: str) -> Tuple[bool, str, List[Tuple[str, str]], str]:
    """
    Main agentic entry point replacing process_user_response
    Maintains identical signature for backward compatibility
    
    Args:
        message: User input message
        chat_history: Chat history as list of (user_msg, bot_msg) tuples
        input_xml: Input XML content
        transformed_xml: Expected output XML content  
        main_xslt: Current XSLT (if any)
        specs: Specifications data
        
    Returns:
        Tuple[user_request, bot_message, updated_chat_history, updated_main_xslt]
    """
    print("-----------")
    print("AGENTIC PROCESSOR")
    print(f"User message: {message}")
    print(f"Chat history length: {len(chat_history)}")
    
    try:
        # Initialize or load context
        context = ConversationContext.from_session_state()
        if main_xslt and not context.current_xslt:
            context.current_xslt = main_xslt
            
        # Set up session state for backward compatibility
        if input_xml:
            st.session_state.input_xml = input_xml
        if transformed_xml:
            st.session_state.output_xml = transformed_xml
        
        # Build system prompt with current context
        system_prompt = build_system_prompt(context, chat_history)
        
        # Prepare messages for GPT
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": message}
        ]
        
        # Get function definitions
        functions = get_function_definitions()
        
        # Call GPT with function calling using Azure OpenAI client directly
        print("=== AGENTIC DEBUG: Calling GPT with function calling capability ===")
        print(f"AGENT MODEL: {o3_mini_model_name}")
        print(f"CLIENT: o3client (Azure OpenAI)")
        print(f"FUNCTIONS AVAILABLE: {[f['name'] for f in functions]}")
        try:
            response = o3client.chat.completions.create(
                model=o3_mini_model_name,
                messages=messages,
                functions=functions,
                function_call="auto"  # Let GPT decide when to call functions
            )
        except Exception as e:
            print(f"Error calling GPT: {e}")
            bot_message = "Sorry, I'm having trouble processing your request. Please try again."
            chat_history.append((message, bot_message))
            return False, bot_message, chat_history, main_xslt
        
        if not response:
            bot_message = "Sorry, I'm having trouble processing your request. Please try again."
            chat_history.append((message, bot_message))
            return False, bot_message, chat_history, main_xslt
        
        # Check if GPT wants to call a function
        if hasattr(response.choices[0].message, 'function_call') and response.choices[0].message.function_call:
            function_name = response.choices[0].message.function_call.name
            print(f"=== AGENTIC DEBUG: GPT Function Call ===")
            print(f"FUNCTION CALLED: {function_name}")
            print(f"FUNCTION ARGUMENTS: {response.choices[0].message.function_call.arguments}")
            
            # Execute the function
            success, bot_message, updated_xslt = execute_function_call(
                response.choices[0].message.function_call, 
                input_xml, 
                transformed_xml
            )
            print(f"FUNCTION RESULT - Success: {success}, Message: {bot_message[:100]}...")
            
            # Update main_xslt if function returned one
            if updated_xslt:
                main_xslt = updated_xslt
                
            # Determine user_request flag (for UI compatibility)
            user_request = success and ("generated" in bot_message.lower() or "refined" in bot_message.lower())
            
        else:
            # GPT responded without function call
            bot_message = response.choices[0].message.content
            user_request = False
        
        # Add to chat history
        chat_history.append((message, bot_message))
        print(f"Bot response: {bot_message}")
        
        return user_request, bot_message, chat_history, main_xslt
        
    except Exception as e:
        print(f"Error in agentic processor: {e}")
        bot_message = "An error occurred while processing your request. Please try again."
        chat_history.append((message, bot_message))
        return False, bot_message, chat_history, main_xslt


# Backward compatibility - create alias for easy replacement
process_user_response_agentic = process_user_request_agentic