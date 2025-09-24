import re
import json
import saxonche
from difflib import Differ
from pathlib import Path
import os

def apply_xslt(xslt, xml, logs, parameters=None):
    """
    Apply XSLT transformation to XML.
    
    Args:
    xslt (str): XSLT stylesheet
    xml (str): XML content
    logs (list): List to store log messages
    parameters (dict, optional): Parameters for XSLT transformation
    
    Returns:
    list: [transformed_xml, logs] or [None, logs] if an error occurs
    """
    if parameters is not None:
        xslt = replace_parameters(xslt, parameters) 

    try:
        processor = saxonche.PySaxonProcessor(license=False)
        document = processor.parse_xml(xml_text=xml)
        xslt30_processor = processor.new_xslt30_processor()
        compiled_xslt = xslt30_processor.compile_stylesheet(stylesheet_text=xslt)
        transformed_xml = compiled_xslt.transform_to_string(xdm_node=document) # Can pass parameters too
        return [transformed_xml, logs]
    except saxonche.PySaxonApiError as e:
        print(f"An error occurred during the XSLT transformation: {e}")
        logs.append(f"An error occurred during the XSLT transformation: {e}")
        return [None, logs]
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        logs.append(f"An unexpected error occurred: {e}")
        return [None, logs]


def save_generated_xslt(file_name, directory = None):
    """
    Save generated XSLT to a file.
    
    Args:
    file_name (str): Content of the XSLT to be saved
    
    Returns:
    str or None: The saved file_name if successful, None if an error occurs
    """
    try:
        if directory is None:
            directory = "../config/results/"
        if not os.path.exists(directory):
            os.makedirs(directory) 
        with open(f"{directory}/generated_xslt.xslt", "w") as f:
            f.write(file_name)
        return file_name
    except IOError as e:
        print(f"Error writing to file: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None
    

def save_generated_xml(file_name, directory = None):
    """
    Save generated XML to a file.
    
    Args:
    file_name (str): Content of the XML to be saved
    
    Returns:
    str or None: The saved file_name if successful, None if an error occurs
    """
    try:
        if directory is None:
            directory = "../config/results/"
        Path(directory).mkdir(parents=True, exist_ok=True)     
        with open("f${directory}/generated_xml.xml", "w") as f:
            f.write(file_name)
        return file_name
    except IOError as e:
        print(f"Error writing to file: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None

def has_observations(response_obj):
    """
    Check if the response object has any observations.
    
    Args:
    response_obj (dict): Response object containing observations
    
    Returns:
    bool: True if observations exist, False otherwise
    """
    if len(response_obj['observations']) > 0:
        return True
    else:
        return False

def consolidate_observations(response):
    """
    Consolidate observations from the response.
    
    Args:
    response (str): JSON string containing response data
    
    Returns:
    tuple: (bool, str) indicating if observations exist and formatted observations
    """
    print(f"In consolidate_observations::response = {response}")
    response_obj = json.loads(response)
    if has_observations(response_obj):
        formatted_observation = "Observations are:\n"
        for observation in response_obj['observations']:
            formatted_observation += observation['observation'] + "\n"
        return (True, formatted_observation)
    else:
        formatted_observation = "No observations"
        return (False, formatted_observation)
    
def copy(generated_xslt):
    """
    Copy the generated XSLT.
    
    Args:
    generated_xslt (str): XSLT content to be copied
    
    Returns:
    str: The input XSLT content
    """
    return generated_xslt

def get_parameters(uploaded_xslt):
    """
    Extract parameters from uploaded XSLT.
    
    Args:
    uploaded_xslt (str): Path to the uploaded XSLT file
    
    Returns:
    list: List of parameter names and their values
    """
    with open(uploaded_xslt, "r") as f:
        generated_xslt = f.read()

    generated_xslt = generated_xslt.split("\n")

    param_names = []
    parameter_lines = []
    for line in generated_xslt:
        if "xsl:param name" in line:
            split_line = re.split(r"(\"[^\"]*\")",  line)
            parameter_lines.append(split_line)
            param_names.append([split_line[1].split("\"")[1], split_line[3].split("\"")[1]])
    
    return param_names


def replace_parameters(generated_xslt, new_parameters):
    """
    Replace parameters in the generated XSLT with new values.
    
    Args:
    generated_xslt (str): XSLT content with parameters
    new_parameters (pandas.DataFrame): DataFrame containing new parameter values
    
    Returns:
    str: XSLT content with updated parameter values
    """
    generated_xslt_split = generated_xslt.split("\n")

    j = 0
    for i, line in enumerate(generated_xslt_split):
        if "xsl:param name" in line:
            new_param = new_parameters.loc[new_parameters.index == j, "Parameter Value"].item()
            split_line = re.split(r"(\"[^\"]*\")",  line)
            split_line[3] = f"\"{new_param}\""
            print(split_line)
            new_line = "".join(split_line)
            generated_xslt_split[i] = new_line
            j += 1
            
    return "\n".join(generated_xslt_split)

def read_xslt(xslt):
    """
    Read XSLT content from a file.
    
    Args:
    xslt (str): Path to the XSLT file
    
    Returns:
    str: Content of the XSLT file
    """
    with open(xslt, "r") as f:
        return f.read()

def diff_texts(text1, text2):
    """
    Compare two texts and return their differences.
    
    Args:
    text1 (str): First text for comparison
    text2 (str): Second text for comparison
    
    Returns:
    list: List of tuples containing (token, difference_type)
    """
    d = Differ()
    return [
        (token[2:], token[0] if token[0] != " " else None)
        for token in d.compare(text1, text2)
    ]    