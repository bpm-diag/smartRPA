import json
import csv
from typing import Any, List, Union

import google.generativeai as genai

import os

def csv_to_json(csvFilePath):
    jsonArray = []
      
    #read csv file
    with open(csvFilePath, encoding='utf-8') as csvf: 
        #load csv file data using csv library's dictionary reader
        csvReader = csv.DictReader(csvf,delimiter=';') 

        #convert each csv row into python dict
        for row in csvReader: 
            #add this python dict to json array
            jsonArray.append(row)
  
    return jsonArray

def remove_keys(item: Any, keys_to_remove: List[str]) -> Union[dict, list, Any]:
    """
    Recursively remove specified keys from a dictionary or list of dictionaries.

    Args:
        item (Any): The item to process (can be a dict, list, or any other type).
        keys_to_remove (List[str]): Keys that should be removed from the data.

    Returns:
        Union[dict, list, Any]: The cleaned item with specified keys removed.
    """
    if isinstance(item, dict):
        return {
            k: remove_keys(v, keys_to_remove)
            for k, v in item.items()
            if k not in keys_to_remove
        }
    elif isinstance(item, list):
        return [remove_keys(element, keys_to_remove) for element in item]
    else:
        return item

def read_json_file(file_path: str) -> Any:
    """
    Read and parse a JSON file.

    Args:
    file_path (str): Path to the JSON file.

    Returns:
    Any: Parsed JSON data.

    Raises:
    FileNotFoundError: If the specified file is not found.
    json.JSONDecodeError: If the file contains invalid JSON.
    """
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        raise FileNotFoundError(f"The file {file_path} was not found.")
    except json.JSONDecodeError:
        raise json.JSONDecodeError(f"The file {file_path} contains invalid JSON.")

def combine_header_and_data(UiLog: list) -> list:
    """
    Combine the provided header with data from another JSON file.

    Args:
    header_json (Dict[str, Any]): The header JSON structure.
    data_file_path (str): Path to the JSON file containing the data.
    output_file_path (str): Path where the combined JSON will be saved.

    Raises:
    FileNotFoundError: If the data file is not found.
    json.JSONDecodeError: If the data file contains invalid JSON.
    """
    # Read the semantic header file
    header = read_json_file(r"src/utils/LLM_semantic_header.json")

    # Ensure data is a list
    if not isinstance(UiLog, list):
        raise ValueError("Data file should contain a list of elements.")

    # Create the combined structure
    combined = {
        "header": header["header"],
        "data": {f"element_{i+1}": item for i, item in enumerate(UiLog)}
    }

    return combined

def extract_json_from_text(text: str) -> dict:
    """
    Extract a JSON object from a given text string.

    Args:
    text (str): The input text that may contain a JSON object.

    Returns:
    dict: The extracted JSON object, or an empty dict if no valid JSON is found.
    """
    # Find the first occurrence of an opening curly brace
    start = text.find('{')
    if start == -1:
        return {}  # No opening brace found

    # Initialize variables
    brace_count = 0
    in_quotes = False
    escape = False

    # Iterate through the string starting from the opening brace
    for i in range(start, len(text)):
        char = text[i]
        
        # Handle string literals
        if char == '"' and not escape:
            in_quotes = not in_quotes
        elif char == '\\' and not escape:
            escape = True
            continue
        
        if not in_quotes:
            if char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                
            if brace_count == 0:
                try:
                    return_text = text[start:i+1].replace("'", '"')
                    return json.loads(return_text)
                except json.JSONDecodeError:
                    # If it's not valid JSON, continue searching
                    continue
        
        escape = False

    # If we've reached this point, no valid JSON object was found
    return {}

def combine_elements(file1_data, file2_data):
  """
  Combines elements from two JSON files based on element names.

  Args:
      file1_data (dict): The data from the first JSON file.
      file2_data (dict): The data from the second JSON file.

  Returns:
      list: A list of combined elements.
  """

  combined_data = []
  for element_name, element_data in file2_data.items():
      if element_name in file1_data:
          combined_element = {
              "element_name": element_name,
              "data_from_file1": file1_data[element_name],
              "data_from_file2": element_data
          }
          combined_data.append(combined_element)

  return combined_data

### Gemini Stuff ###

def startModel():
    instruction_string = ('You are a domain expert in tagging User Interaction Logs (Recordings of mouse clicks, keystrokes, etc).'
                          'Each user interaction log is provided to you as JSON string/file.'
                          'The json has a header element containing a semantic description of each key an element can have.'
                          'After the header there can be one to many user activities. '
                          'Your task is to generate a semantic meaningfull, short tag for each activity in the UI log'
                          'based on the semantic header and the key value pairs per element.'
                          )
    
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        system_instruction=instruction_string
        )
    
    return model