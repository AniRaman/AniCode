import json
import chromadb
from chromadb.utils import embedding_functions
import streamlit as st
from typing import List
from dotenv import load_dotenv, find_dotenv
from genie_core.database.configure_llama_chroma_database import DatabaseConfigurator
from genie_core.common.user_interaction import add_to_prompts, add_to_messages, write_chat_message
from genie_core.data_processing.cleanup import cleanup_process
from llama_index.core import Document

DEFAULT_DIR = "../../config/prompts/NDC"
configurator = None 

_ = load_dotenv(find_dotenv())

def chromadb_setup(specs):

    # Let's assume the column containing text is named "content"
    # You can concatenate other columns if needed
    documents = []
    df2 = cleanup_process(specs)
    df2.loc[:, 'Field'] = df2['Field'].fillna(df2['Output XPATH'].apply(lambda x: x.split('@')[1] if '@' in x else x))
    df_final = df2.dropna(subset=['Field', 'Description'], how='all')
    df_final['Field']
    for index, row in df_final.iterrows():
        # content = row['Description']  # Extract content column (modify as needed)
        # You could combine multiple columns like this:
        content = (f"Field:{row['Field']};Input XPATH:{row['Input XPATH']};Output XPATH:{row['Output XPATH']};Description:{row['Description']}")
        # Convert the row's content into a Document object
        documents.append(Document(id_=row['Field'],text=content))
    
    return documents

def load_qna_from_file(file_path):
    """
    Loads question-answer pairs from a JSON file.
    
    Args:
    file_path (str): Path to the JSON file containing QnA data.
    
    Returns:
    tuple: Two lists containing questions and answers respectively, or (None, None) if an error occurs.
    """
    with open(file_path, 'r') as file:
        qna_data = json.load(file)
    qa_pairs = qna_data
    questions = [pair['question'] for pair in qa_pairs]
    answers = [pair['answer'] for pair in qa_pairs]
    return questions, answers


# Function to configure the ChromaDB database
def configure_database(qna_file):
    """
    Configures and initializes the ChromaDB database with QnA data.
    
    Args:
    qna_file (str): Path to the file containing QnA data.
    
    Returns:
    chromadb.Collection: Configured ChromaDB collection, or None if an error occurs.
    """
    try:
        questions, answers = load_qna_from_file(qna_file)
        ids = ["q" + str(i) for i in range(1, len(questions) + 1)]

        chroma_client = chromadb.PersistentClient(
            path="./chromaDB")
        chroma_client.reset()
        default_ef = embedding_functions.DefaultEmbeddingFunction()
        collection = chroma_client.get_or_create_collection(name="ndc_qna_collection_nevio", embedding_function=default_ef)

        collection.add(documents=questions, metadatas=[{"answer": answer} for answer in answers], ids=ids)
        return collection
    except Exception as e:
        print(f"Error configuring the database: {e}")
        return None

def get_answer_from_db(query_text, collection, threshold=0.5, top_n=2):
    """
    Retrieves an answer from the database based on the query text.
    
    Args:
    query_text (str): The question to search for.
    collection (chromadb.Collection): The ChromaDB collection to query.
    threshold (float): Similarity threshold for exact matches.
    top_n (int): Number of top results to consider.
    
    Returns:
    str: The answer to the query, or an empty string if no match is found.
    """
    try:
        results = collection.query(query_texts=[query_text], n_results=top_n)
        
        if results and results['distances']:
            closest_matches = []
            for i, distance in enumerate(results['distances'][0]):
                if distance <= 1:  # Only consider matches with distance <= 1
                    closest_matches.append(results['metadatas'][0][i]['answer'])
                else:
                    break  # Stop if distance exceeds 1
            
            if closest_matches:
                if results['distances'][0][0] <= threshold:
                    return closest_matches[0]  # Return the best match if it meets the threshold
                else:
                    return "\n\n".join(closest_matches)  # Return all matches within distance 1
            else:
                print("No matching results found within the specified threshold.")
                return ""
        else:
            print("No matching results found.")
            return ""
    except Exception as e:
        print(f"Error querying the database: {e}")
        return ""

def query_db_for_answers(questions:List[str], question_map, human_feedback_list, ndc_qna_collection):
    """
    Queries the database for answers to a list of questions.
    
    Args:
    questions (List[str]): List of questions to query.
    question_map (dict): Map to track question frequency.
    human_feedback_list (list): List to store questions requiring human feedback.
    ndc_qna_collection (chromadb.Collection): The ChromaDB collection to query.
    
    Returns:
    tuple: Lists of answers, updated human feedback list, and updated question map.
    """
    qna_list = []
    if questions:
        for question in questions:
            if question not in question_map:
                question_map[question] = 0 # doesn't exist
            else:
                question_map[question] = question_map[question] + 1 # already existing, so incrementing
        
        num_count = 1
        if len(questions) > 0:
            for question in questions: #parse the question received
                for ques, count in question_map.items(): # for each question, get its count
                    if ques == question:
                        if count < 2: # if its the question asked and its asked less than 3 times
                            answer = get_answer_from_db(question, ndc_qna_collection) # get the answer
                            answer = str(num_count) + "." + answer
                            qna_list.append(answer) # append to the answer list
                            num_count += 1
                        else:
                            print(f"This question - {question} - has already been asked and got irrevant answer or no answer, will be asked for human feedback.")
                            human_feedback_list.append(question)
    return qna_list, human_feedback_list, question_map


## Testing
# Path to the QnA file
qna_file = '../../config/data/specs_qna_1.json'

###Testing
# Configure the database
# ndc_qna_collection = configure_database(qna_file)

# if ndc_qna_collection:
#     print(get_answer_from_db("How should the 'FareBasisCode' and 'FareRule' elements be mapped from the input XML to the output XML?", ndc_qna_collection))

def parse_questions_and_retreive_answers(human_readable_questions):
    human_readable_questions_chat_message = ""
    human_readable_to_llm = ""  
    retreived_answers_list = ""
    retreive_answers_list_llm = ""

    if human_readable_questions is not None:
        write_chat_message("assistant", """:blue[In order to generate the XSLT completely, please provide 
                           answers to the following questions to ensure we have all the necessary information.\n]""")
        
        if len(human_readable_questions) > 0:
            for index, question in enumerate(human_readable_questions):
                human_readable_questions_chat_message += f"{index + 1}. {question}\n"
                human_readable_to_llm += question + "\n"
            
            write_chat_message("assistant", human_readable_questions_chat_message)
            add_to_messages(human_readable_questions_chat_message)
            write_chat_message("assistant", ":orange[Searching specifications for answers, please wait!!]\n")
            add_to_prompts({"role":"assistant", "content": human_readable_to_llm})
            # add_to_messages(human_readable_to_llm)
            
            for index, question in enumerate(human_readable_questions):
                if question not in st.session_state.questions_map:
                    st.session_state.questions_map[question] = 0
                else:
                    st.session_state.questions_map[question] += 1
                
                answer = retreive_answers(question)
                retreived_answers_list += answer + "\n"
                retreive_answers_list_llm += answer + "\n"
            
            write_chat_message("assistant", "Here are the answers: \n \n" + retreived_answers_list)
            add_to_prompts({"role":"user", "content": retreive_answers_list_llm})
            add_to_messages(retreived_answers_list)

@st.cache_data
def retreive_answers(question, directory = DEFAULT_DIR):
    global configurator
    answers_list = ""
    
    if configurator is None:
        configurator = DatabaseConfigurator(directory)
    
    answers_list += configurator.get_answer_from_db(question)
    answers_list += "\n"
    return answers_list
