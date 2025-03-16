import requests
from flask import Flask, request, render_template_string, render_template, session, jsonify
import openai
from rdflib import Graph
from markupsafe import escape
import os
import json
import re
from dotenv import load_dotenv

load_dotenv()  # This loads the variables from the .env file into your environment

openai.api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)
app.secret_key = os.urandom(24)

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
        g.parse(data=rdf_data, format='json-ld')
        print("RDF (JSON-LD) is valid.")
        return True
    except Exception as e:
        print(f"RDF (JSON-LD) is invalid: {e}")
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
                if mode == "entity":
                    print("entity")
                    info_response = extract_main_entity(user_input)
                elif mode == "json_ld":
                    # If in graph generation mode, generate a knowledge graph
                    info_response = generate_json(sanitized_input)
                    verify_jsonld(info_response)
                    # Save the knowledge graph into a JSON file in the static folder
                    json_ld_response = json.loads(info_response)
                    static_folder = os.path.join(os.getcwd(), 'static')
                    file_path = os.path.join(static_folder, 'data.json')
                    with open(file_path, 'w') as json_file:
                        json.dump(json_ld_response, json_file)

                elif mode == "rag":
                    # First, retrieve relevant information
                    retrieved_data = retrieve_information_from_api(sanitized_input)

                    # Then, generate the mind map using both the input and the retrieved data
                    info_response = generate_json_with_retrieval(sanitized_input, retrieved_data)

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
                elif mode == "evaluation":
                    for i in range(5):
                        # If in graph generation mode, generate a knowledge graph
                        info_response = generate_json(user_input)
                        verify_jsonld(info_response)

                        # Save the knowledge graph into a JSON file in the /evaluation folder
                        json_ld_response = json.loads(info_response)

                        # Create the evaluation folder if it doesn't exist
                        evaluation_folder = os.path.join(os.getcwd(), 'evaluation')
                        if not os.path.exists(evaluation_folder):
                            os.makedirs(evaluation_folder)

                        file_name = f"boat{i + 1}.json"
                        file_path = os.path.join(evaluation_folder, file_name)

                        # Save the JSON data into the file
                        with open(file_path, 'w') as json_file:
                            json.dump(json_ld_response, json_file)

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

def generate_knowledge_graph(user_input):
    system_instruction = """
    You are a helpful assistant that generates valid JSON-LD mind maps.
    Only return the JSON-LD structure, without any other text or explanation around it.
    Do not include any tags such as `json` or any other symbols. Just the raw JSON-LD.
    """
    prompt = f"Generate a mind map in JSON-LD format on the topic '{user_input}', " \
            #"but please make sure that the structure is flat with only one level of nesting allowed. For example, include relationships or linked entities in an array or simple objects, but avoid deeply nested structures."
             #"but do NOT include nested objects or arrays. " \
             #"Each entity and its properties should be flat, with NO hierarchical relationships."
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

    # List of common prompt injection patterns or keywords
    banned_phrases = [
        "inject", "instruction", "terminate", "exit", "end", "cancel",
        "deliberate", "if you are", "you are a", "let's think step by step",
        "please follow", "become", "act as", "pretend", "ignore previous instructions"
    ]

    # Check if any banned phrases are present
    for phrase in banned_phrases:
        if phrase.lower() in user_input.lower():
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
    temperature = 1.0
    top_p = 1.0
    response = get_gpt_response(prompt, temperature, top_p, system_instruction)
    return response

if __name__ == '__main__':
    app.run(debug=True)