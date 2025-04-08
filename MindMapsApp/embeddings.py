import openai
import os
import json

from dotenv import load_dotenv



load_dotenv()  # This loads the variables from the .env file into your environment

openai.api_key = os.getenv("OPENAI_API_KEY")


# Function to generate embeddings from a text file
def generate_embedding_from_file(text_file_path):
    with open(text_file_path, 'r') as file:
        text_data = file.read()

    # Get the embedding from OpenAI API (small model)
    response = openai.embeddings.create(
        model="text-embedding-3-small",  # Small model for cost-effectiveness
        input=text_data
    )

    # Extract the embedding vector from the response object
    embedding = response.data[0].embedding
    return embedding


# Function to process all text files in the Strings folder and save embeddings
def process_text_files(input_folder, output_file):
    embeddings_list = []

    # Get the list of all text files in the folder
    files = [f for f in os.listdir(input_folder) if f.endswith('.txt')]

    for file_name in files:
        # Construct the full path of each text file
        text_file_path = os.path.join(input_folder, file_name)

        # Generate the embedding for this text file
        embedding = generate_embedding_from_file(text_file_path)

        # Save the embedding with the corresponding file name
        embeddings_list.append({
            "file_name": file_name,
            "embedding": embedding
        })

    # Save all embeddings to a JSON file
    with open(output_file, 'w') as output:
        json.dump(embeddings_list, output)

    print(f"Embeddings saved to {output_file}")


# Example usage:
input_folder = 'evaluation/Strings/rag_london'  # Folder containing the text files
output_file = 'evaluation/embeddings/rag_london/rag_london.json'  # File to store the embeddings

# Process the text files and save the embeddings
process_text_files(input_folder, output_file)
