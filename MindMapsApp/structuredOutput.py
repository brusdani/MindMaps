import os

import openai
from pydantic import BaseModel
from typing import List
import json

from dotenv import load_dotenv



load_dotenv()  # This loads the variables from the .env file into your environment

openai.api_key = os.getenv("OPENAI_API_KEY")

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
        Please generate a mind map on topic '{user_input}'"""


    response = openai.beta.chat.completions.parse(
        model="gpt-4o-mini-2024-07-18",
        messages=[
            {"role": "system", "content": system_instruction},  # Add dynamic system prompt here
            {"role": "user", "content": prompt},
        ],

        response_format=GraphClass

    )
    return response.choices[0].message.parsed

user_input = "Large Language Models"
response_pydantic = get_gpt_response_pydantic(user_input)
result = convert_to_json(response_pydantic)
json_result = json.loads(result)


static_folder = os.path.join(os.getcwd(), 'static')
file_path = os.path.join(static_folder, 'structured.json')
with open(file_path, 'w') as json_file:
    json.dump(json_result, json_file)