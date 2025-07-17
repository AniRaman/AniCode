import sqlite3
import os
from dotenv import load_dotenv, find_dotenv
from openai import AzureOpenAI as OpenAIAzureOpenAI
import httpx
import re
import streamlit as st
import json
from pathlib import Path

def connect_to_db(db_name):
    """
    Connects to the SQLite database.
    
    Args:
        db_name (str): The name of the SQLite database file.
    
    Returns:
        sqlite3.Connection: SQLite connection object.\
    """
    os.chdir("/Users/nlepakshi/Documents/GitHub/genie/app/gap_analyser/data/")
    return sqlite3.connect(db_name)

def insert_data(conn, table_name, data):
    """
    Inserts data into the specified table.
    
    Args:
        conn (sqlite3.Connection): SQLite connection object.
        table_name (str): The name of the table to insert data into.
        data (list): List of tuples containing data to insert.
    """
    cursor = conn.cursor()
    cursor.executemany(f"INSERT INTO {table_name} VALUES (?, ?)", data)
    conn.commit()

def execute_query(conn, query, params=None):
    """
    Executes a query on the SQLite database.
    
    Args:
        conn (sqlite3.Connection): SQLite connection object.
        query (str): The SQL query to execute.
        params (tuple, optional): Parameters for parameterized queries. Defaults to None.
    
    Returns:
        list: Query results as a list of tuples.
    """
    cursor = conn.cursor()
    if params:
        cursor.execute(query, params)
    else:
        cursor.execute(query)
    return cursor.fetchall()

def run_query(db_name, query, params=None):
    """
    Connects to the SQLite database, executes a query, and fetches the results.
    
    Args:
        db_name (str): The name of the SQLite database file.
        query (str): The SQL query to execute.
        params (tuple, optional): Parameters for parameterized queries. Defaults to None.

    Returns:
        list: Query results as a list of tuples.
    """
    try:
        conn = connect_to_db(db_name)
        results = execute_query(conn, query, params)
        conn.commit()
        conn.close()
        return results
    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
        return None

def print_results(results):
    """
    Prints the query results.
    
    Args:
        results (list): Query results as a list of tuples.
    """
    if results:
        for row in results:
            print(row)

def search_in_database(element, selected_airlines):
    
    # Database name
    db_name = "api_analysis.db"
    
    # Example query
    # query = """
    #     SELECT a.api_name, pd.pattern_description, pd.pattern_prompt
    #     FROM api a
    #     JOIN api_section aps ON a.api_id = aps.api_id
    #     JOIN section_pattern_mapping spm ON aps.section_id = spm.section_id AND aps.api_id = spm.api_id
    #     JOIN pattern_details pd ON spm.pattern_id = pd.pattern_id
    #     WHERE aps.section_display_name = ? and a.api_name IN ({})
    #     GROUP BY a.api_name, pd.pattern_prompt
    # """.format(','.join('?' for _ in selected_airlines))
    
    query = """
        SELECT a.api_name, pd.pattern_description, pd.pattern_prompt
        FROM api a
        JOIN api_section aps ON a.api_id = aps.api_id
        JOIN section_pattern_mapping spm ON aps.section_id = spm.section_id AND aps.api_id = spm.api_id
        JOIN pattern_details pd ON spm.pattern_id = pd.pattern_id
        WHERE aps.section_display_name = ?
        GROUP BY a.api_name, pd.pattern_prompt
    """
    
    
    
    # Query parameter
    section_display_name = element    
    # Run the query
    # results = run_query(db_name, query, (section_display_name, *selected_airlines))
    results = run_query(db_name, query, (section_display_name,))

    
    # Print the results
    # print_results(results)
    return results;

def list_main_elements(xml_text):
    elements = set()
    elements_dict = {}
    pattern = re.compile(r"^\s*<([^/?!][^ >]*)[^>]*?>")
    
    for i, line in enumerate(xml_text.split("\n")):
        search = pattern.search(line)
        if search:
            element = search.group(1)
            elements.add(element)
            elements_dict[element] = [i]
    return elements
    
def verify_and_confirm_airline(input_xml, selected_airlines):
    with st.spinner("Analyzing the API, please wait..."):
        sections = list_main_elements(input_xml)
        gap_analysis = {
            "sections": [],
            "matched_airlines": set()
        }

        for section in sections:
            row = search_in_database(section, selected_airlines)
            if row:
                section_data = {
                    "sectionName": section,
                    "rules": []
                }

                for item in row:
                    rule = {
                        "airline": item[0],
                        "verificationRule": item[1],
                        "matched": False,
                        "reason": ""
                    }

                    search_prompt = item[2]
                    response_obj_json = call_to_llm(input_xml, search_prompt)

                    confirmation = response_obj_json.get('confirmation')
                    rule["matched"] = confirmation == "YES"
                    if rule["matched"] == True:
                        gap_analysis["matched_airlines"].add(item[0])
                    rule["reason"] = response_obj_json.get('reason', "")

                    section_data["rules"].append(rule)

                gap_analysis["sections"].append(section_data)

        return gap_analysis


def call_to_llm(input_xml, search_prompt):
    current_dir = Path(__file__).resolve().parent
    prompts = []
    file_path = current_dir / "../config/prompts/generic/default_system_prompt_for_gap_analysis.txt"
    with file_path.open() as file:
        system_prompt = {"role":"system","content": file.read()}
    input_file_prompt = {"role": "user", "content": "Here is the input XML file." + "\n" + "```" + input_xml + "```" }
    additional_prompt = {"role": "user", "content": search_prompt }
    prompts.append(system_prompt)
    prompts.append(input_file_prompt)
    prompts.append(additional_prompt)
    model_name = "GPT4O"
    _ = load_dotenv(find_dotenv())
    deployment_model = os.getenv(f"{model_name}_MODEL_DEPLOYMENT_NAME")
    azure_endpoint = os.getenv(f"{model_name}_AZURE_OPENAI_ENDPOINT")
    api_key = os.getenv(f"{model_name}_AZURE_OPENAI_KEY")
    api_version = os.getenv(f"{model_name}_AZURE_API_VERSION")
    gpt_client = OpenAIAzureOpenAI(
                            azure_endpoint=azure_endpoint,
                            api_key=api_key,
                            api_version=api_version,
                            http_client=httpx.Client(verify=False)
                        )
    response = gpt_client.chat.completions.create(
                                model=deployment_model,
                                messages=prompts,
                                temperature=0,
                                top_p = 0.9,
                                )

                    # Assuming response.choices[0].message.content is a JSON string
    response_obj = response.choices[0].message.content
    response_obj = re.sub(r'[\x00-\x1F\x7F]', '', response_obj)
    # Parse the JSON string into a Python object
    response_obj_json = json.loads(response_obj)
    return response_obj_json


def print_table_data(db_name, table_name):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {table_name}")
    rows = cursor.fetchall()
    conn.close()
    print(f"Data from {table_name}:")
    for row in rows:
        print(row)

# Print data from relevant tables

                    
# if __name__ == "__main__":
#     print_table_data("api_analysis.db", "api")
#     print_table_data("api_analysis.db", "api_section")
#     print_table_data("api_analysis.db", "section_pattern_mapping")
#     print_table_data("api_analysis.db", "pattern_details")
    # current_dir = Path(__file__).resolve().parent
    # file_path = current_dir / "../config/prompts/generic/default_system_prompt_for_gap_analysis.txt"
    # with file_path.open() as file:
    #     prompt = file.read()
    # json_text = {
    #     "confirmation": "NO",
    #     "reason": "The XML does not contain a <PaxRefID> element inside the INF passenger's section. Therefore, it cannot be verified if the reference of an ADT passenger is correctly returned."
    # }
    # json_string = json.dumps(json_text)
    # # Load the JSON string into a Python object
    # response_obj_json = json.loads(json_string)
    # confirmation = response_obj_json.get('reason')
    
# if __name__ == "__main__":
#     with open("/Users/nlepakshi/Documents/GitHub/master/content-transformer-new/xslt_generator/main/gap_analyser/data/OVRS_LATAM_19_2_copy.xml","r") as file:
#         xml_file = file.read()
#     verify_and_confirm_airline(xml_file)

# /Users/nlepakshi/Documents/GitHub/master/content-transformer-new/xslt_generator/database/sql_db_utils.py
# /Users/nlepakshi/Documents/GitHub/master/content-transformer-new/xslt_generator/config/prompts/generic/default_system_prompt_for_gap_analysis.txt