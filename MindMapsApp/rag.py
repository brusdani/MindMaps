import requests


def retrieve_information_from_api(topic):
    # Use a Wikipedia API or similar service to retrieve information about the topic
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{topic.replace(' ', '_')}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        return data.get('extract', '')  # Return the text summary of the topic
    else:
        return "No relevant data found."

topic = "Václav Havel"

result = retrieve_information_from_api(topic)
print(result)

