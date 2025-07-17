import json
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))
from genie_core.hive import Hive
import streamlit as st
import pandas as pd

def process_and_print_streaming_response(response):
    content = ""
    last_sender = ""

    for chunk in response:
        if "sender" in chunk:
            last_sender = chunk["sender"]

        if "content" in chunk and chunk["content"] is not None:
            if not content and last_sender:
                print(f"\033[94m{last_sender}:\033[0m", end=" ", flush=True)
                last_sender = ""
            print(chunk["content"], end="", flush=True)
            content += chunk["content"]
        if "tool_calls" in chunk and chunk["tool_calls"] is not None:
            for tool_call in chunk["tool_calls"]:
                f = tool_call["function"]
                name = f["name"]
                if not name:
                    continue
                print(f"\033[94m{last_sender}: \033[95m{name}\033[0m()")
        
        if "delim" in chunk and chunk["delim"] == "end" and content:
            print()  # End of response message
            content = ""
                        
        if "response" in chunk:
            return chunk["response"]


def pretty_print_messages(messages, agent) -> None:
    for message in messages:
        if message["role"] != "assistant":
            continue

        # st.markdown(f"{message['sender']}")

        # print response, if any
        if message["content"]:
            st.markdown(message["content"])

        # print tool calls in purple, if any
        tool_calls = message.get("tool_calls") or []
        if len(tool_calls) > 1:
            st.markdown("")
        for tool_call in tool_calls:
            f = tool_call["function"]
            name, args = f["name"], f["arguments"]
            arg_str = json.dumps(json.loads(args)).replace(":", "=")
            # st.markdown(f"{name}{arg_str[1:-1]}")
    st.write(f"agent ---- {agent.name}")

def get_response_from_agent(messages, agent_name):
    pattern_extractor_content = None

    for message in messages:
        if message['role'] == 'assistant' and message['sender'] == agent_name:
            pattern_extractor_content = message['content']
    
    try:
        pattern_extractor_content = json.loads(pattern_extractor_content)
    except:
        st.error("failed to parse pattern extractor content")
    
    for pattern in pattern_extractor_content:
        tag = pattern["pattern_path"]
        st.session_state.pattern_responses[tag] = [pattern["pattern_name"], pattern["pattern_description"], pattern['pattern_prompt'], False]
    
    data = []
    for tag, values in st.session_state.pattern_responses.items():
        pattern_name = values[0]
        pattern_description = values[1]
        pattern_prompt = values[2]
        is_verified = values[3]
        data.append([tag] + [pattern_name] + [pattern_description] + [pattern_prompt] )

    df = pd.DataFrame(data, columns=['XPATH', 'Name', 'Description', 'Pattern'])
    st.markdown(":blue[Here are the patterns identified for the given XML:]")
    st.dataframe(df)

def run_demo_loop(file_content, starting_agent, context_variables=None, stream=False, debug=True) -> None:
    pass

def run_gap_analyser(file_path, starting_agent, context_variables=None, debug=False
) -> None:
    client = Hive()

    messages = []
    agent = starting_agent    
    while True:
        if agent.name == "XML Handler":
            user_input = file_path
        if agent.name == "Pattern Extractor":
            break
        messages.append({"role": "user", "content": user_input})
        with st.spinner(":rainbow[Please wait while I spin-up my agents 🤖 to process the XML and extract patterns 📬]"):
            response = client.run(
                agent=agent,
                messages=messages,
                context_variables=context_variables or {},
                stream=False,
                debug=debug,
            )

        if response is not None:
            st.write(get_response_from_agent(response.messages, "Pattern Extractor"))

        messages.extend(response.messages)
        agent = response.agent
        
    