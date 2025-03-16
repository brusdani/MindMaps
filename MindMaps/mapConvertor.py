import json
import os


# Function to convert JSON data into text
def json_to_text(json_data):
    text_representation = ""

    # Add nodes to the text
    text_representation += " ".join([node['id'] for node in json_data['nodes']]) + ". "

    # Add links to the text
    for link in json_data['links']:
        text_representation += f"{link['source']} {link['label']} {link['target']}. "

    return text_representation


# Function to read JSON files, convert them to text, and save as .txt files
def process_json_files(input_folder, output_folder):
    # Get list of JSON files in the input folder
    files = [f for f in os.listdir(input_folder) if f.endswith('.json')]

    for file_name in files:
        # Construct full path of the JSON file
        json_path = os.path.join(input_folder, file_name)

        # Open and load JSON data
        with open(json_path, 'r') as file:
            json_data = json.load(file)

        # Convert the JSON data into text
        text_representation = json_to_text(json_data)

        # Save the text to a new .txt file in the output folder
        text_file_name = file_name.replace('.json', '.txt')
        text_path = os.path.join(output_folder, text_file_name)

        with open(text_path, 'w') as text_file:
            text_file.write(text_representation)

        print(f"Processed {file_name} and saved to {text_file_name}")


# Example usage:
# Set the correct folder paths based on your structure
#input_folder_havel = 'evaluation/maps/havel'  # Folder containing Václav Havel JSON files
#input_folder_churchill = 'evaluation/maps/churchill'  # Folder containing Churchill JSON files
input_folder_eiffel = 'evaluation/assignment/maps/goldStandart'  # Folder containing Churchill JSON files
output_folder = 'evaluation/assignment/strings/goldStandart'  # Folder to store the generated text files

# Make sure the output folder exists
os.makedirs(output_folder, exist_ok=True)

# Process the JSON files from both Havel and Churchill folders
#process_json_files(input_folder_havel, output_folder)
#process_json_files(input_folder_churchill, output_folder)
process_json_files(input_folder_eiffel,output_folder)
