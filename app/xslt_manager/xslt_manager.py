import streamlit as st
import re
# st.set_page_config(
#     page_title="XSLT Generator",
#     page_icon="👋",
# )
def main():
    st.write("# Welcome to GENIE, GENerative IntEgrator! 👋")

    st.sidebar.success("Select an operation above.")

    st.markdown(
        """
        ### 🤖 Generate XSLT with AI
        Leverage the power of our advanced language model to generate custom XSLT files based on your input XML data and transformation requirements. AI’s Got Your Back 😉
        ### 🛠️ Update XSLT with AI
        New requirements? No worries! Just Plug Them In with the existing XSLT, and watch the updated XSLT appear instantly.
        ### 🎨 Refine XSLT with AI
        Smarter, Faster, Better, Let AI Optimize Your XSLT!
    """
    )

try:
    main()
except ModuleNotFoundError as e:
    pattern = r"\'(.*)\'"
    module_name = re.search(pattern, str(e)).group(1)
    st.exception(f"ModuleNotFoundError: please install the required module by running pip install {module_name}\n ({e})")