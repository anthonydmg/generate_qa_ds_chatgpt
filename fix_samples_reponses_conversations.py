
from glob import glob
from utils import load_json, save_json

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

conversational_dataset = []


def get_prompt_refine_answer(respuesta):
    prompt = f"""Corrige esta respuesta proporcionada por un asistente de AI para no mencionar "información proporcionada", manteniendo el sentido original de la respuesta.  Es preferible que en lugar menciones de manera cordial y pertinente que no tienes conocimento al respecto.

    Respuesta: {respuesta}"""
    return prompt



def refine_message_to_mencion_information(files):
    id = 0
    tab_updates = []
    for file_path in files:
        data = load_json(file_path)
        for conv_id_file, conv in enumerate(data):
            id +=1
            messages = conv["messages"]
            for i_m, m in enumerate(messages):
                if m["role"] == "assistant":
                    message = m["content"]
                    keywords = ["información proporcionada"]
                    if any(keyword in message.lower() for keyword in keywords):
                        print("\nConv id:", id)
                        print("message:", message) 
                        prompt_refine_answer = get_prompt_refine_answer(message)
                    

                        messages = [
                            {"role": "user", "content": prompt_refine_answer}]

                        new_answer = get_completion_from_messages(
                            messages,
                            model= "gpt-3.5-turbo-0613")

                        print("\nnew_answer:", new_answer)

                        tab_updates.append({
                            "conv_id_file": conv_id_file,
                            "conv_id": id - 1,
                            "message_id": i_m,
                            "original_message": message,
                            "new_message": new_answer.replace("Respuesta:", "").strip(),
                            "file_path": file_path
                        })
    return tab_updates

def refine_message_to_no_information(files):
    id = 0
    tab_updates = []
    for file_path in files:
        data = load_json(file_path)
        for conv_id_file, conv in enumerate(data):
            id +=1
            messages = conv["messages"]
            for i_m, m in enumerate(messages):
                if m["role"] == "assistant":
                    message = m["content"]
                    keywords = ["Lamentablemente"]
                    if any(keyword.lower() in message.lower() for keyword in keywords):
                        print("\nConv id:", id)
                        print("\nUser Message:", messages[i_m - 1]["content"])
                        print("\nAssistant Message:", message)
                        print() 

                    
    return tab_updates

refine_message_to_no_information(files)

# Lamentablemente, no tengo acceso a esa informaci\u00f3n

#tab_updates = refine_message_to_mencion_information(files)

#save_json("./updates_cache", "tab_updates", tab_updates)

#tab_updates = load_json("./updates_cache/tab_updates.json")

def updates_messages(tab_updates):
    for update_data in tab_updates:
        file_path = update_data["file_path"]
        print("file_path:", file_path)
        data = load_json(file_path)
        conv_id_file = update_data["conv_id_file"]
        print("conv_id_file:", conv_id_file)
        message_id = update_data["message_id"]
        print("message_id:", message_id)
        new_message = update_data["new_message"].replace("Respuesta:", "").strip()

        data[conv_id_file]["messages"][message_id]["content"] = new_message

        print("updated message:", data[conv_id_file]["messages"][message_id])

        directorio, archivo = os.path.split(file_path)

        save_json(directorio, archivo[:-5], data)

#updates_messages(tab_updates)