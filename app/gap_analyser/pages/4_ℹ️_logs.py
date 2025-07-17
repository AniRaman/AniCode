import streamlit as st
prompts = []
for prompt in st.session_state.prompts:
    prompts.append(prompt)

st.write(prompts)  # Display the prompts