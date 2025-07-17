import sys
import os
import json

sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))
from genie_core.hive import Agent
from genie_core.hive.repl import run_demo_loop
from genie_core.xml_processing.Filechunker import parse_xml_file_to_tree, select_tags, TreeNode
import streamlit as st
from pathlib import Path
from genie_core.hive.repl import run_gap_analyser
from genie_core.hive.types import Result 

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
    depth = TreeNode.calculate_subtree_depth(tree)
    custom_depth = depth/2
    tags = select_tags(tree, st.session_state.tags_to_select, custom_depth)
    # tags = select_tags(tree, st.session_state.tags_to_select, depth/2)
    result = Result(value=str(tags), agent=None, context_variables={})
    return result

def save_patterns():
    write_path = "/Users/nlepakshi/Documents/GitHub/genie/genie_core/config/patterns/patterns.json"
    with open(write_path, "w") as f:
        json.dump(st.session_state.tags_to_select, f, indent=4)

user_manager_agent = Agent(
    name="User Manager",
    model="gpt-4o",
    instructions="""You are a user interface agent that handles all interactions with the user. 
    Call this agent for general questions and when no other agent is correct for the user query.""",
    functions=[transfer_to_xml_chunker_agent],
)

xml_handler_agent = Agent(
    name="XML Handler",
    model="gpt-4o",
    instructions="You receive a file path from the user. Transfer the conversation to the relevant agent.",
    functions=[transfer_to_xml_chunker_agent],
)
xml_chunker_agent = Agent(
    name="XML Chunker",
    model="gpt-4o",
    instructions="""You chunk XML data into manageable pieces using the given tools and return the chunks.
                    Transfer the conversation to the next agent that extracts the patterns.
                 """,
    functions=[chunk_xml, transfer_to_pattern_extractor_agent]
)

current_dir = Path(__file__).resolve().parent
file_path = current_dir / "../../genie_core/config/prompts/generic/default_system_prompt_for_pattern_identification.md"
with file_path.open() as f:
        pattern_identifier_prompt = f.read()
pattern_identifier_prompt += "When all the patterns are identified, transfer the conversation to the relevant agent."

pattern_saver_agent = Agent(
    name="Pattern Saver",
    model="gpt-4o",
    instructions="You save extracted patterns into a file. Once the activity is done, ask the user for further instructions.",
    functions=[save_patterns, transfer_to_user_manager_agent]
)

pattern_extractor_agent = Agent(
    name="Pattern Extractor",
    model="gpt-4o",
    instructions=pattern_identifier_prompt,
    functions=[]
)

# if __name__ == "__main__":
#     # file_to_delete = "/Users/nlepakshi/Documents/GitHub/genie/genie_core/config/patterns/patterns.json"
#     # os.remove(file_to_delete)
    
#     temp_file_path = "/Users/nlepakshi/Documents/GitHub/genie/genie_core/config/test_data/xml_comparator/example2.xml"
#     run_gap_analyser(temp_file_path, xml_handler_agent)