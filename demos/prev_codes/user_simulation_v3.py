
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
que estás buscando asesoría o información relevante para las siguientes preguntas, por diversas razones:
Preguntas:
    1. ¿Cuál es la fecha límite para solicitar el retiro parcial de asignaturas?
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


propmpt_add = """
Responde de manera concisa y significativa, teniendo en cuenta el contexto del historial de diálogo en curso. Ten en cuenta tu objetivo principal de la conversación, que es obtener informacion o asesoria como estudiante universitario de la UNI
"""

question = "Hasta cuando puedo solicitar el retiro de cursos?"
respuesta = "El retiro parcial puede ser relizadao solo hasta la quinta semana de clases."
prompt_user = """
Actua como un estudiante universitario de la Facultad de Ciencias de la Universidad Nacional de Ingenieria que estás buscando asesoría o información, por diversas razones.
Responde de manera concisa y significativa, teniendo en cuenta el contexto del historial de diálogo en curso. Ten en cuenta tu objetivo principal de la conversación, que es obtener informacion o asesoria como estudiante universitario de la UNI
"""

messages =  [
{"role": "system", "content": prompt_system},
{'role':'user', 'content': prompt_user},
{"role": "assistant", "content": question},
{'role': 'user', 'content': respuesta}]

print(conversation_to_text(messages))
while True:

    response = get_completion_from_messages(messages)
    print("\nChatgpt:", response)
    message_input = input("Ingresa Mensaje:")
    messages.extend([
        {"role": "assistant", "content": response},
        {'role':'user', 'content': message_input}
    ])
    print("\Yo:", message_input)
