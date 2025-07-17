import streamlit as st

def write_chat_message(role, message, spinner_with_message = None):
    if role == 'user':
        avatar = "😎"
    else:
        avatar = "🤖"

    if spinner_with_message:
        with st.chat_message(role, avatar=avatar):
            with st.spinner("spinner_with_message"):
                st.markdown(message)
    else:
        with st.chat_message(role, avatar=avatar):
            st.markdown(message)
    st.session_state.messages.append({"role": role, "content": message})

def add_to_prompts(prompt):
    st.session_state.prompts.append(prompt)
    if st.session_state.generator_agent is not None:
        st.session_state.generator_agent.add_message(prompt)

def add_to_messages(message):
    st.session_state.messages.append({"role": "user", "content": message})

def init_objects_into_session():
    session_defaults = {
        "messages": [],
        "prompts": [],
        "xslt": None,
        "generated_xslt": None,
        "existing_xslt": None,
        "updated_xslt": None,
        "updated_specs": None,
        "existing_specs": None,
        "source_xml": None,
        "target_xml": None,
        "llm_target_xml": None,
        "specs_file": None,
        "cook_books": None,
        "questions_map": {},
        "has_human_feedback": False,
        "generator_agent": None,
        "ask_yes_no": False,
        "user_response": None,
        "chat_history": [],
        "markdown_spec": None,
        "url":None,
        "current_xslt": None,
        "space":None,
        "page_name":None,
        "html":None,
        "gpt_model_used": None,
        "number_of_calls_to_llm": 0,
        "total_cost_per_tool": 0
    }

    for key, value in session_defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value
