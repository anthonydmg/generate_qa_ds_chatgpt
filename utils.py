import json

def save_json(path, filename, data):
    with open(f"{path}/{filename}.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data


def format_response_json(response):
    resp_json = json.loads(response.strip())
    return resp_json

def read_fragment_doc(path):
    with open(path) as f:
        text = f.read()
        return text

def list_json_to_txt(elements, numeric = True):
    text = ''
    for i ,e in enumerate(elements):
        text += str(i + 1) + ". " + e + "\n"
    return text