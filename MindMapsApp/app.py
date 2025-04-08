import requests
from flask import Flask, request, render_template_string, render_template, session, jsonify, redirect
import openai
from rdflib import Graph
import os
import json
import re
from pydantic import BaseModel
from typing import List
from dotenv import load_dotenv
import PyPDF2
from docx import Document




load_dotenv()  # This loads the variables from the .env file into your environment

openai.api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)
app.secret_key = os.urandom(24)

class Node(BaseModel):
    id: str


class Link(BaseModel):
    source: str
    target: str
    label: str


class GraphClass(BaseModel):
    nodes: List[Node]
    links: List[Link]

def convert_to_json(graph: GraphClass) -> str:
    return json.dumps(graph.model_dump(), ensure_ascii=False, indent=2)

def get_gpt_response_pydantic(user_input):
    system_instruction = """
           You are a helpful assistant that generates valid JSON-LD mind maps.
           Only return the JSON structure, without any other text or explanation around it.
           Do not include any tags such as `json` or any other symbols. Just the raw JSON.
           """

    prompt = f"""
        Please generate a mind map on topic '{user_input}'. Ensure that links are only created to existing nodes. And that there is no node without a link"""


    response = openai.beta.chat.completions.parse(
        model="gpt-4o-mini-2024-07-18",
        messages=[
            {"role": "system", "content": system_instruction},  # Add dynamic system prompt here
            {"role": "user", "content": prompt},
        ],

        response_format=GraphClass

    )
    return response.choices[0].message.parsed


def get_gpt_response(prompt, temperature = 1.0, top_p = 1.0, system_instruction=""): #default values
    response = openai.chat.completions.create(
        model="gpt-4o-mini-2024-07-18",
        messages=[
            {"role": "system", "content": system_instruction},  # Add dynamic system prompt here
            {"role": "user", "content": prompt},
        ],
        temperature=temperature,
        top_p=top_p
    )
    return response.choices[0].message.content


def extract_main_entity(text):
    system_instruction = """
           You are a helpful assistant that identifies the main topic or entity from the text provided.
           Only return the identified entity, without any other text or explanation.
           No extra information, no elaborations, just the name of the main person, organization, event, or concept.
           If the text is asking for a mind map topic, return the entity following 'for a topic'.
           """

    prompt = f"""
    Please identify the most important person, organization, event, or concept mentioned in the following text.
    Return **only** the main entity without any explanation or extra details. For example: "Václav Havel" or "Microsoft"

    Text:
    {text}
    """
    temperature = 0.0  # Low randomness for deterministic response
    top_p = 0.0  # No diversity in sampling, strict response
    response = get_gpt_response(prompt, temperature, top_p, system_instruction)
    return response


def verify_jsonld(rdf_data):
    g = Graph()
    try:
        g.parse(data=rdf_data, format='json')
        print("RDF (JSON-LD) is valid.")
        return True
    except Exception as e:
        # Safely print the error message as a string to avoid invalid argument errors
        print(f"Exception:  {e}")
        return False

def verify_turtle(rdf_data):
    g = Graph()
    try:
        g.parse(data=rdf_data, format='turtle')
        print("RDF is valid.")
        return True
    except Exception as e:
        print(f"RDF is invalid: {e}")
        return False


@app.route('/', methods=['GET', 'POST'])
def index():
    info_response = ""
    experiment_response = []
    if request.method == 'POST':
        user_input = request.form.get('user_input')
        mode = request.form.get('mode')

        # If the user input is empty, return an error message
        if not user_input:
            info_response = "Please enter some text!"
        else:
            try: # Sanitize user input before using it
                sanitized_input = sanitize_input(user_input)
                print(mode)
                if mode == "json":
                    # If in graph generation mode, generate a knowledge graph
                    #response_pydantic = get_gpt_response_pydantic(extract_main_entity(sanitized_input))
                    #info_response = convert_to_json(response_pydantic)
                    info_response = generate_json(extract_main_entity(sanitized_input))
                    verify_jsonld(info_response)
                    # Save the knowledge graph into a JSON file in the static folder
                    json_ld_response = json.loads(info_response)
                    static_folder = os.path.join(os.getcwd(), 'static')
                    file_path = os.path.join(static_folder, 'data.json')
                    with open(file_path, 'w') as json_file:
                        json.dump(json_ld_response, json_file)

                elif mode == "rag":
                    # Retrieve relevant information
                    retrieved_data = retrieve_information_from_api(extract_main_entity(sanitized_input))

                    # Then, generate the mind map using both the input and the retrieved data
                    info_response = generate_json_with_retrieval(sanitized_input, retrieved_data)

                    # Save the generated mind map to a JSON file
                    json_response = json.loads(info_response)
                    static_folder = os.path.join(os.getcwd(), 'static')
                    file_path = os.path.join(static_folder, 'data.json')
                    with open(file_path, 'w') as json_file:
                        json.dump(json_response, json_file)

                elif mode == "text":
                    # Then, generate the mind map using both the input and the retrieved data
                    info_response = generate_json_from_text(user_input)

                    # Optionally, save the generated mind map to a JSON file
                    json_response = json.loads(info_response)
                    static_folder = os.path.join(os.getcwd(), 'static')
                    file_path = os.path.join(static_folder, 'data.json')
                    with open(file_path, 'w') as json_file:
                        json.dump(json_response, json_file)

                elif mode == "turtle":
                    # Save the Turtle data into a .ttl file in the static folder
                    static_folder = os.path.join(os.getcwd(), 'static')
                    file_path = os.path.join(static_folder, 'turtle_data.ttl')

                    info_response = generate_turtle(user_input)
                    valid = verify_turtle(info_response)
                    if not valid:
                        fixed_response = fix_turtle(info_response)
                        was_fixed = verify_turtle(fixed_response)
                        if was_fixed:
                            print("RDF was fixed in second try")
                            info_response=fixed_response
                        else:
                            print("RDF wasn't fixed")
                            info_response="Invalid RDF data. Fix unsuccessful."

                    # Write the Turtle RDF data to the file
                    with open(file_path, 'w') as ttl_file:
                        ttl_file.write(info_response)
                elif mode == "experiment":
                    # If experimental mode, run the same prompt 10 times to check consistency
                    for _ in range(10):
                        response = generate_turtle(user_input)
                        valid = verify_turtle(response)
                        if not valid:
                            fixed_response = fix_turtle(response)
                            was_fixed=verify_turtle(fixed_response)
                            if was_fixed:
                                print("RDF was fixed in second try")
                                experiment_response.append(fixed_response)
                            else:
                                print("RDF wasn't fixed")
                        else:
                            experiment_response.append(response)
                else:
                    # If in chat mode, return a chat response
                    info_response = get_gpt_response(user_input)

                    # Save the response into a JSON file in the static folder
                    static_folder = os.path.join(os.getcwd(), 'static')
                    file_path = os.path.join(static_folder, 'data.json')
                    with open(file_path, 'w') as json_file:
                        json.dump({'response': info_response}, json_file)
            except ValueError as e:
                # Catch the ValueError from sanitize_input and display the error message
                info_response = str(e)

    return render_template('index.html', info_response=info_response)

def generate_mind_map(user_input):
    system_instruction = """
    You are a helpful assistant that generates valid JSON-LD mind maps.
    Only return the JSON-LD structure, without any other text or explanation around it.
    Do not include any tags such as `json` or any other symbols. Just the raw JSON-LD.
    """
    prompt = f"Generate a mind map in JSON-LD format on the topic '{user_input}', "

    temperature = 0.0
    top_p = 0.0
    response = get_gpt_response(prompt, temperature, top_p, system_instruction)
    return response

def generate_json_zero(user_input):
    system_instruction = """
           You are a helpful assistant that generates valid JSON mind maps.
           Only return the JSON structure, without any other text or explanation around it.
           Do not include any tags such as `json` or any other symbols. Just the raw JSON-LD.
           """
    prompt = f"""
        Please generate a mind map on topic '{user_input}', in the JSON format specified below.

        The output should have two arrays:
        - "nodes": an array of objects where each object has an "id" field. Aim for 9 nodes in a mindmap
        - "links": an array of objects where each object has "source", "target", and "label" fields.
        """
    temperature = 1.0
    top_p = 1.0
    response = get_gpt_response(prompt, temperature, top_p, system_instruction)
    return response

def generate_json(user_input):
    system_instruction = """
       You are a helpful assistant that generates valid JSON mind maps.
       Only return the JSON structure, without any other text or explanation around it.
       Do not include any tags such as `json` or any other symbols. Just the raw JSON.
       """
    prompt = f"""
    Please generate a mind map on topic '{user_input}', in the JSON format specified below.

    The output should have two arrays:
    - "nodes": an array of objects where each object has an "id" field. Aim for 9 nodes in a mindmap
    - "links": an array of objects where each object has "source", "target", and "label" fields.

    For example:

    {{
      "nodes": [
        {{ "id": "Václav Havel" }},
        {{ "id": "Playwright" }},
        {{ "id": "Czech" }}
      ],
      "links": [
        {{ "source": "Václav Havel", "target": "Playwright", "label": "hasOccupation" }},
        {{ "source": "Václav Havel", "target": "Czech", "label": "hasNationality" }}
      ]
    }}
    """
    temperature = 0.0
    top_p = 0.0
    response = get_gpt_response(prompt, temperature, top_p, system_instruction)
    return response

def generate_turtle(user_input):
    system_instruction = """
    You are a helpful assistant that generates VALID Turtle mind maps.
    Only return the Turtle structure, without any other text or explanation around it.
    Do not include any tags such as `Turtle` or any other symbols. Just the raw Turtle.
    """
    prompt = f"Generate a mind map in Turtle format on the topic '{user_input}', " \

    temperature = 0.0
    top_p = 0.0
    response = get_gpt_response(prompt, temperature, top_p, system_instruction)
    return response


def fix_turtle(invalid_turtle):
    system_instruction = """
        You are a helpful assistant that corrects invalid Turtle RDF statements.
        Your task is to fix the invalid Turtle RDF input and return the corrected version.
        Do not include any tags such as `Turtle` or any other symbols. Just the raw Turtle.
    """
    prompt = f"""
    The following is an invalid Turtle RDF statement:

    {invalid_turtle}

    Your task is to fix the errors and return the corrected version. 
    The most common mistake is using "()", remove them.
    """

    temperature = 0.0
    top_p = 0.0
    response = get_gpt_response(prompt, temperature, top_p, system_instruction)
    return response

@app.route('/visualize')
def visualize():
    return render_template('visualization.html')
@app.route('/test')
def test():
    return render_template('index.html')


@app.route('/latest_map')
def latest_map():
    file_path = 'static/data.json'

    try:
        # Open and load the JSON data from the file
        with open(file_path, 'r') as file:
            json_data = json.load(file)

            transformed_data = {
                "nodes": json_data.get("nodes", []),
                "links": json_data.get("links", [])
            }
    except FileNotFoundError:
        # Handle the case where the file is not found
        return render_template('error.html', message="The JSON file was not found.")
    except json.JSONDecodeError:
        # Handle the case where JSON is malformed
        return render_template('error.html', message="The JSON file is malformed.")

    return render_template('latest_map.html', json_map=transformed_data)


@app.route('/expand_node', methods=['GET', 'POST'])
def process_enrichment():
    if request.method == 'POST':
        # Retrieve the concept (node id) from the form data
        concept = request.form.get('selected_node')

    if concept:
        print(f"Selected concept: {concept}")
    else:
        print("No concept selected.")

    file_path = 'static/data.json'
    with open(file_path, 'r') as file:
        json_data = json.load(file)
    expansion_response = expand_mindmap(json_data, concept)

    verify_jsonld(expansion_response)
    # Save the knowledge graph into a JSON file in the static folder
    json_response = json.loads(expansion_response)
    static_folder = os.path.join(os.getcwd(), 'static')
    file_path = os.path.join(static_folder, 'data.json')
    with open(file_path, 'w') as json_file:
        json.dump(json_response, json_file)

    return render_template('visualization.html')  # You can render the template or return another response

def expand_mindmap(jsonData, concept):
        retrieved_data = retrieve_information_from_api(concept)

        system_instruction = """
               You are a helpful assistant that generates valid JSON mind maps.
               Only return the JSON structure, without any other text or explanation around it.
               Do not include any tags such as `json` or any other symbols. Just the raw JSON-LD.
               """
        prompt = f"""
        I have a JSON file representing a graph of nodes and links. Here is the JSON data: 
        {jsonData}
        Enhance this JSON data by adding 3 new nodes and links related to the concept '{concept}'. 
        Use the following additional relevant information from Wikipedia to help enrich the mind map:
        {retrieved_data}
        
        Specifically Try to keep the context of intial data:
        - Relevant details about the **person**, **place**, **event**, or **movie**.
        - Examples of new nodes could be related to:
            - **For people**: Profession, birth date, notable works, etc.
            - **For places**: Country, population, important landmarks, etc.
            - **For events**: Date, location, significant participants, etc.
            - **For movies**: Director, filming date, main villain, box office, etc
        - Ensure that new nodes and relationships are added to the existing graph without removing or duplicating existing information.
        - Maintain the same JSON format, including the original data and newly added nodes.
        - Ensure that new nodes and relationships are added only for the selected concept and linked directly to it.

        
        Please provide the enhanced JSON data with these additions while maintaining the original format and return complete data, including the initial data.
        """
        temperature = 1.0
        top_p = 1.0
        response = get_gpt_response(prompt, temperature, top_p, system_instruction)
        return response


def sanitize_input(user_input):
    word_count = len(user_input.split())
    if word_count > 250:
        raise ValueError("Input is too long. Please limit your input to 250 words.")

    # List of common prompt injection patterns or keywords
    banned_phrases = [
        "inject", "instruction", "terminate", "exit", "cancel",
        "deliberate", "if you are", "you are a", "let's think step by step",
        "please follow", "become", "act as", "pretend", "ignore previous instructions"
    ]

    # Check if any banned phrases are present
    for phrase in banned_phrases:
        if phrase.lower() in user_input.lower():
            print(phrase)
            raise ValueError("Input contains prohibited phrases.")

    # Optionally: Further sanitize input by removing excess spaces or special characters (e.g., `<>`)
    sanitized_input = re.sub(r'[<>`"\'\;\|]', '', user_input).strip()

    return sanitized_input

def retrieve_information_from_api(topic):
    # Use a Wikipedia API or similar service to retrieve information about the topic
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{topic.replace(' ', '_')}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        return data.get('extract', '')  # Return the text summary of the topic
    else:
        return "No relevant data found."

def generate_json_with_retrieval(user_input,retrieval_data):
    system_instruction = """
       You are a helpful assistant that generates valid JSON mind maps.
       Only return the JSON structure, without any other text or explanation around it.
       Do not include any tags such as `json` or any other symbols. Just the raw JSON.
       """
    prompt = f"""
    Please generate a mind map on topic '{user_input}', in the JSON format specified below.

    The output should have two arrays:
    - "nodes": an array of objects where each object has an "id" field. Aim for 9 nodes in a mindmap
    - "links": an array of objects where each object has "source", "target", and "label" fields.

    For example:

    {{
      "nodes": [
        {{ "id": "Václav Havel" }},
        {{ "id": "Playwright" }},
        {{ "id": "Czech" }}
      ],
      "links": [
        {{ "source": "Václav Havel", "target": "Playwright", "label": "hasOccupation" }},
        {{ "source": "Václav Havel", "target": "Czech", "label": "hasNationality" }}
      ]
    }}
    - Ensure that links are only created to nodes that EXIST
     Here is some additional relevant information to help you create a more accurate mind map:
    {retrieval_data}
    """
    temperature = 0.0
    top_p = 0.0
    response = get_gpt_response(prompt, temperature, top_p, system_instruction)
    return response

# Set up a folder for uploaded files
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['ALLOWED_EXTENSIONS'] = {'pdf', 'docx'}
MAX_WORDS = 250

# Function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


# Route for uploading files
@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # Check if a file is part of the request
        if 'file' not in request.files:
            return render_template('upload.html', error="No file part")

        file = request.files['file']

        # If the user doesn't select a file
        if file.filename == '':
            return render_template('upload.html', error="No selected file")

        # Check if the file has an allowed extension
        if file and allowed_file(file.filename):
            # Save the file locally
            filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filename)

            # Extract text from the uploaded file
            try:
                extracted_text = extract_text_from_file(filename)
                #sanitized_text = sanitize_input(extracted_text)
                mind_map_text = generate_json_from_text(extracted_text)
                mind_map_json = json.loads(mind_map_text)
                static_folder = os.path.join(os.getcwd(), 'static')
                file_path = os.path.join(static_folder, 'data.json')
                with open(file_path, 'w') as json_file:
                    json.dump(mind_map_json, json_file)

                # Return success message with the mind map JSON
                return render_template('upload.html', success=f'File uploaded successfully: {filename}',
                                       mind_map=mind_map_json)
            except ValueError as e:
                return render_template('upload.html', error=str(e))
            except Exception as e:
                return render_template('upload.html', error=f"Error processing the file: {str(e)}")
        else:
            return render_template('upload.html', error="Invalid file type. Only .pdf and .docx files are allowed.")

    return render_template('upload.html')

def extract_pdf_text(pdf_path):
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
    return text


# Function to extract text from a DOCX file
def extract_docx_text(docx_path):
    doc = Document(docx_path)
    text = ""
    for paragraph in doc.paragraphs:
        text += paragraph.text + '\n'
    return text


# Function to handle file type and extract text


def extract_text_from_file(file_path):
    _, extension = os.path.splitext(file_path.lower())

    if extension == '.pdf':
        text = extract_pdf_text(file_path)
    elif extension == '.docx':
        text = extract_docx_text(file_path)
    else:
        raise ValueError("Unsupported file type")
        # Count words in the extracted text
    word_count = len(text.split())

    # Check if the word count exceeds the limit
    if word_count > MAX_WORDS:
        raise ValueError(
            f"Document is too long. It contains {word_count} words, which exceeds the limit of {MAX_WORDS} words.")

    return text

def generate_json_from_text(text):
    system_instruction = """
       You are a helpful assistant that generates valid JSON mind maps.
       Only return the JSON structure, without any other text or explanation around it.
       Do not include any tags such as `json` or any other symbols. Just the raw JSON.
       """
    prompt = f"""
        Please generate a mind map from the following text: '{text}', in the JSON format specified below.
        Please ensure that all the links are only created to **existing** nodes. Do not create any links to non-existent or new nodes.
        Also make sure that the generated mindmap is in the same language as the original text.
        
        The output should have two arrays:
        - "nodes": an array of objects where each object has an "id" field. Aim for 9 nodes in a mind map.
        - "links": an array of objects where each object has "source", "target", and "label" fields.

        Make sure the following:
        - Links should only reference nodes that are already defined in the "nodes" array.
        - If a link references a non-existent node, it should not be created.

        Example format:
        {{
          "nodes": [
            {{ "id": "Václav Havel" }},
            {{ "id": "Playwright" }},
            {{ "id": "Czech" }}
          ],
          "links": [
            {{ "source": "Václav Havel", "target": "Playwright", "label": "hasOccupation" }},
            {{ "source": "Václav Havel", "target": "Czech", "label": "hasNationality" }}
          ]
        }}
    """

    temperature = 1.0
    top_p = 1.0
    response = get_gpt_response(prompt, temperature, top_p, system_instruction)
    return response



if __name__ == '__main__':
    app.run(debug=True)