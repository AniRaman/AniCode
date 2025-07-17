import sys
import os
import json

sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))
from genie_core.hive import Agent
from genie_core.hive.repl import run_demo_loop
from genie_core.xml_processing.Filechunker import parse_xml_file_to_tree, select_tags
import streamlit as st
from pathlib import Path

if 'tags_to_select' not in st.session_state:
    st.session_state.tags_to_select = {}

if 'patterns' not in st.session_state:
    st.session_state.patterns = {}

def transfer_to_user_manager_agent():
    """Transfer XML data to the User Manager agent."""
    return user_manager_agent
    
def transfer_to_xml_chunker_agent():
    """Transfer XML data to the XML Chunker agent."""
    return xml_chunker_agent

def transfer_to_pattern_extractor_agent():
    """Transfer XML data to the Pattern Extractor agent."""
    return pattern_extractor_agent

def transfer_to_pattern_saver_agent():
    """Transfer XML data to the Pattern Saver agent."""
    return pattern_saver_agent

def chunk_xml(file):
    tree = parse_xml_file_to_tree(file)
    return select_tags(tree, st.session_state.tags_to_select, 5)

def save_patterns():
    write_path = "/Users/nlepakshi/Documents/GitHub/genie/genie_core/config/patterns/patterns.json"
    with open(write_path, "w") as f:
        json.dump(st.session_state.tags_to_select, f, indent=4)

user_manager_agent = Agent(
    name="User Manager Agent",
    model="gpt-4o",
    instructions="You manage the user's requests and transfer the conversation to the relevant Agent.",
    functions=[transfer_to_xml_chunker_agent],
)

xml_handler_agent = Agent(
    name="XML Handler Agent",
    model="gpt-4o",
    instructions="You receive a file path from the user.",
    functions=[transfer_to_xml_chunker_agent],
)
xml_chunker_agent = Agent(
    name="XML Chunker Agent",
    model="gpt-4o",
    instructions="""You chunk XML data into manageable pieces using the given tools and return the chunks. 
                    Once the XML is chunked, next step is to extract the patterns for each chunk. 
                    Transfer the conversation to the relevant Agent.
                 """,
    functions=[chunk_xml, transfer_to_pattern_extractor_agent]
)

current_dir = Path(__file__).resolve().parent
file_path = current_dir / "../../config/prompts/generic/default_system_prompt_for_pattern_identification.md"
with file_path.open() as f:
        pattern_identifier_prompt = f.read()
pattern_identifier_prompt += "When all the patterns are extracted, transfer the conversation to the Pattern Saver Agent."

pattern_extractor_agent = Agent(
    name="Pattern Extractor Agent",
    model="gpt-4o",
    instructions=pattern_identifier_prompt,
    functions=[transfer_to_pattern_saver_agent]
)
pattern_saver_agent = Agent(
    name="Pattern Saver Agent",
    model="gpt-4o",
    instructions="You save extracted patterns into a file. Once the activity is done, ask the user for further instructions.",
    functions=[save_patterns, transfer_to_user_manager_agent]
)

if __name__ == "__main__":
    run_demo_loop(xml_handler_agent)