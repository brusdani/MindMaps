import openai
import os

from dotenv import load_dotenv

load_dotenv()  # This loads the variables from the .env file into your environment
openai.api_key = os.getenv("OPENAI_API_KEY")


# Define the function to generate mind maps
def generate_mind_map(user_input):
    return {
        "type": "function",
        "name": "generate_mind_map",
        "parameters": {
            "topic": user_input
        }
    }

# Function to execute OpenAI request
def get_openai_response(user_input):
    system_instruction = """
       You are a helpful assistant that generates valid JSON-LD mind maps.
       Your response should contain the following:
       - "nodes": an array of objects, each with an "id" field representing a concept or entity in the mind map (e.g., a person, place, or idea).
       - "links": an array of objects where each object has "source", "target", and "label" fields, representing relationships between nodes (e.g., "hasOccupation", "isLocatedIn").
       Only return the raw JSON-LD without any additional text or explanation.
    """

    # Correct function schema format
    response = openai.chat.completions.create(
        model="gpt-4o-mini-2024-07-18",  # Or the model you prefer (e.g., GPT-3.5)
        messages=[{
            "role": "system",
            "content": system_instruction
        }, {
            "role": "user",
            "content": f"Please generate a mind map on the topic: {user_input}"
        }],
        functions=[{
            "name": "generate_mind_map",
            "description": "Generates a JSON-LD formatted mind map based on the given topic",
            "parameters": {
                "type": "object",  # JSON Schema type for parameters
                "properties": {
                    "topic": {
                        "type": "string"  # Correct schema for the "topic" parameter
                    }
                },
                "required": ["topic"]  # Ensure the "topic" parameter is required
            }
        }],
        function_call="auto"
    )

    return response.choices[0].message.function_call.arguments



response_format = {
  "system_instruction": "You are a helpful assistant that generates valid JSON-LD mind maps.\nOnly return the JSON-LD structure, without any other text or explanation around it.\nDo not include any tags such as `json` or any other symbols. Just the raw JSON-LD.",
  "prompt": "Please generate a mind map on topic '{user_input}', in the JSON format specified below.\n\nThe output should have two arrays:\n- \"nodes\": an array of objects where each object has an \"id\" field. Aim for 9 nodes in a mindmap\n- \"links\": an array of objects where each object has \"source\", \"target\", and \"label\" fields.\n\nFor example:\n\n{{\n  \"nodes\": [\n    {{ \"id\": \"Václav Havel\" }},\n    {{ \"id\": \"Playwright\" }},\n    {{ \"id\": \"Czech\" }}\n  ],\n  \"links\": [\n    {{ \"source\": \"Václav Havel\", \"target\": \"Playwright\", \"label\": \"hasOccupation\" }},\n    {{ \"source\": \"Václav Havel\", \"target\": \"Czech\", \"label\": \"hasNationality\" }}\n  ]\n}}",
  "input_parameters": [
    {
      "name": "user_input",
      "description": "The topic for which the mind map should be generated.",
      "type": "string"
    }
  ],
  "output_format": {
    "type": "JSON",
    "description": "A JSON structure representing a mind map.",
    "schema": {
      "type": "object",
      "properties": {
        "nodes": {
          "type": "array",
          "description": "An array of node objects.",
          "items": {
            "type": "object",
            "properties": {
              "id": {
                "type": "string",
                "description": "The unique identifier for the node."
              }
            },
            "required": [
              "id"
            ]
          }
        },
        "links": {
          "type": "array",
          "description": "An array of link objects representing the connections between nodes.",
          "items": {
            "type": "object",
            "properties": {
              "source": {
                "type": "string",
                "description": "The id of the source node."
              },
              "target": {
                "type": "string",
                "description": "The id of the target node."
              },
              "label": {
                "type": "string",
                "description": "The label describing the relationship between the source and target nodes."
              }
            },
            "required": [
              "source",
              "target",
              "label"
            ]
          }
        }
      },
      "required": [
        "nodes",
        "links"
      ]
    },
    "constraints": [
      "The output should only contain the JSON structure, without any surrounding text or explanations.",
      "No tags such as `json` or any other symbols should be included.",
      "The mind map should aim for approximately 9 nodes.",
      "The `id` field in the `nodes` array should be a string representing the node's name or concept.",
      "The `source` and `target` fields in the `links` array should correspond to the `id` values in the `nodes` array.",
      "The `label` field in the `links` array should describe the relationship between the connected nodes (e.g., 'isA', 'partOf', 'relatedTo')."
    ]
  },
  "examples": [
    {
      "input": {
        "user_input": "Artificial Intelligence"
      },
      "output": {
        "nodes": [
          { "id": "Artificial Intelligence" },
          { "id": "Machine Learning" },
          { "id": "Deep Learning" },
          { "id": "Neural Networks" },
          { "id": "Robotics" },
          { "id": "Natural Language Processing" },
          { "id": "Computer Vision" },
          { "id": "Expert Systems" },
          { "id": "Data Science" }
        ],
        "links": [
          { "source": "Artificial Intelligence", "target": "Machine Learning", "label": "isA" },
          { "source": "Machine Learning", "target": "Deep Learning", "label": "isA" },
          { "source": "Deep Learning", "target": "Neural Networks", "label": "uses" },
          { "source": "Artificial Intelligence", "target": "Robotics", "label": "appliedTo" },
          { "source": "Artificial Intelligence", "target": "Natural Language Processing", "label": "areaOf" },
          { "source": "Artificial Intelligence", "target": "Computer Vision", "label": "areaOf" },
          { "source": "Artificial Intelligence", "target": "Expert Systems", "label": "historicalApproach" },
          { "source": "Artificial Intelligence", "target": "Data Science", "label": "relatedTo" }
        ]
      }
    }
  ]
}
# Example usage
user_input = "Václav Havel"
mind_map_json = get_openai_response(user_input)
print(mind_map_json)
