
from questions_generation import get_completion_from_messages

import openai
import json
from dotenv import load_dotenv
import os

import re
load_dotenv()

def set_openai_key():
    API_KEY = os.getenv("API_KEY")
    openai.api_key = API_KEY

set_openai_key()

prompt_system = """Eres un estudiante universitario de la Facultad de Ciencias de la Universidad Nacional de Ingenieria.
que estás buscando asesoría o información relevante para las siguientes preguntas, por diversas razones::
Preguntas:
    1. ¿Cuál es la fecha límite para solicitar el retiro parcial de asignaturas?
    2. ¿Cuáles son los motivos válidos para solicitar el retiro total de asignaturas?"
"""

conversation_messages = [{
    "role": "human", 
    'content': "Hasta cuando puedo solicitar el retiro de cursos?"},
    {"role": 'assistant',
    "content": "El retiro parcial se puede realizar hasta la quinta semana despues de inicio de clases."}]


def conversation_to_text(messages):
    txt = ""
    for m in messages:
        txt = txt + "\n" + m["role"] + ": "+ m["content"]
    return txt

conversation_txt = conversation_to_text(conversation_messages)
prompt_user = f""""
"Continúa la siguiente conversación proveendo solo el siguiente mensaje. Ten en cuenta el contexto proporcionado y tu rol como estudiante universitario de la UNI buscando asesoría o informacion:

Conversación:
{conversation_txt}

Por favor, usa el siguiente formato para proveer  el siguiente mensaje de la siguiente conversación ."
Human: Aqui el mensaje...
"""

print("prompt_user:", prompt_user)


while True:
    messages =  [
    {"role": "system", "content": prompt_system},
    {'role':'user', 'content': prompt_user}]
    
    response = get_completion_from_messages(messages)
    print("\nChatgpt:", response)
    message = input("Ingresa Mensaje:")
    only_message = message.replace("Human:", "").strip()
    conversation_messages.extend([
        {'role': 'human', "content": only_message},
        {'role': 'assistant', "content": message}
    ])

   
    conversation_txt = conversation_to_text(conversation_messages)

    prompt_user = f""""
Continua la siguiente conversacion teniendo en consideracion el contexto de la conversacion y tu rol como estudiante que busca asesoria o informacion:
Conversacion:
{conversation_txt}
"""

    print("\Yo:", message)
