
from glob import glob
from utils import load_json, save_json
import re

from utils import count_num_tokens, get_completion_from_messages, load_json, save_json

import openai
import json
from dotenv import load_dotenv
import os


load_dotenv(override=True)

def set_openai_key():
    API_KEY = os.getenv("API_KEY")
    openai.api_key = API_KEY

set_openai_key()

path_directory = "./conversational_data"
files = glob(f"{path_directory}/conversations_simulated_*.json")
files.sort(key= lambda name: int(name[:-5].split("_")[-1]))

def get_range_from_filename(filename):
    numeros = re.findall(r'\d+', filename)
    range_file = [int(numeros[0]), int(numeros[1])]
    return range_file

tab_ranges = []
for file in files:
    name_file = os.path.basename(file)
    print(name_file)
    range_file = get_range_from_filename(name_file)
    tab_ranges.append(
        {"path_file": file,
        "range": range_file}
    )
    print(range_file)

def find_interseccion(rango1, rango2):

    # Calculamos la intersección entre los rangos
    inicio_interseccion = max(rango1[0], rango2[0])
    fin_interseccion = min(rango1[1], rango2[1])
    
    # Verificamos si la intersección es válida
    if inicio_interseccion <= fin_interseccion:
        return True, [inicio_interseccion, fin_interseccion]
    else:
        return False, []


tab_updates_conversations = []
original_files_to_update = [
    "conversations_simulated_70_to_79.json"
]
## encontrar intersecciones
for original_file in original_files_to_update:
    range_original_file = get_range_from_filename(original_file)
    original_data = load_json(os.path.join("./conversational_data", original_file))
    
    for range_row in tab_ranges[:-1]:
        range_current = range_row["range"]
        path_file = range_row["path_file"]
        path_directory, file_name = os.path.split(path_file)
        hay_interseccion, range_intersection = find_interseccion(range_original_file, range_current)

        if hay_interseccion and (file_name != original_file):
            new_data = load_json(path_file)
            min_inter, max_inter = range_intersection
            len_intersection = max_inter - min_inter + 1

            min_rang_original = range_original_file[0]
            if min_inter != max_inter:
                print(min_inter != max_inter)
                index_update = [i for i in range(min_inter - min_rang_original, max_inter - min_rang_original)]
            else:
                index_update = [range_intersection[0] - min_rang_original]
            
            tab_updates_conversations.append({
                "original_path_file": os.path.join(path_directory, original_file),
                "new_conversation_file": path_file,
                "index_update": index_update,
                "range_interseccion": range_intersection,
                "prev_conversations": [original_data[i] for i in  index_update],
                "new_conversations": new_data[:len_intersection]
            })

if len(tab_updates_conversations) > 0:
    print(f"\nNumero de actualizacion: {len(tab_updates_conversations)}")
    save_json("./updates_cache", "tab_updates_conversations", tab_updates_conversations)
else:
    print("\nNada que actualizar")
print()
## update tab

def print_conversations(conversations):
    messages = conversations["messages"]
    for m in messages:
        print(f'\n{m["role"]}: {m["content"]}')
def update_conversations(tab_updates_conversations):
    for update_data in tab_updates_conversations:
        original_path_file = update_data["original_path_file"]
        new_conversations = update_data["new_conversations"]
        index_update = update_data["index_update"]

        original_data = load_json(original_path_file)
        for i in range(len(index_update)):
            id_in_original = index_update[i]
            
            print(f"\noriginal_conversation[{id_in_original}]:\n")

            print_conversations(original_data[id_in_original])

            original_data[id_in_original] = new_conversations[i]

            print(f"\nnew_conversations[{id_in_original}]:\n")
            
            print_conversations(original_data[id_in_original])

        dir_path, filename = os.path.split(original_path_file)
        print(f"\nGuardando cambios de: {original_path_file}")
        save_json(dir_path, filename[:-5], original_data)

if len(tab_updates_conversations) > 0:
    update_conversations(tab_updates_conversations)
else:
    print("\nNada que actualizar")
print()


