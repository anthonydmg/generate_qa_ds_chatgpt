import pandas as pd
import ast
from scipy import spatial
import os
import pandas as pd
import openai
from utils import get_completion_from_messages
import time

from dotenv import load_dotenv
def set_openai_key():
    API_KEY = os.getenv("API_KEY")
    openai.api_key = API_KEY

load_dotenv()

set_openai_key()

GPT_MODEL = "gpt-3.5-turbo"
EMBEDDING_MODEL = "text-embedding-3-small"


prompt_v2 = """Dado el historial de chat y la última pregunta del usuario que podría hacer referencia al contexto en el historial de chat proporcionados delimitadas por tres comillas invertidas, formule una pregunta independiente que pueda entenderse sin el historial de chat. No responda la pregunta, simplemente reformúlela si es necesario y, en caso contrario, devuélvala tal como está.
            
            historial del chat: ```
                user:¿Un estudiante puede matricularse en un curso y su pre requisito?
                assistant:Un estudiante puede matricularse en un curso y su prerequisito en el mismo ciclo académico si es un "estudiante en posibilidad de egresar", es decir, le faltan como máximo treinta créditos para completar su Plan de Estudios y graduarse. Deben comunicarse con su escuela profesional para solicitar la matrícula en el curso y su prerequisito, siendo evaluada y aprobada por el director de la escuela correspondiente.```
            
            última pregunta del usuario: ```¿Qué pasos debo seguir para comunicarme con mi escuela profesional y solicitar ese tramite?```"""

history_chat = ""
prompt = f"""Dado el historial del chat proporcionado entre tres comillas invertidas y el ultimo mensaje del usuario, que podría hacer referencia al contexto en el historial del chat, reformule el mensaje de manera que incluya todo el contexto necesario para que pueda entenderse en su totalidad sin necesidad del contexto del historial del chat. No responda el mensaje, simplemente reformúlela si es necesario y, en caso contrario, devuélvala tal como está.

historial del chat: {history_chat}```"""


last_user_message = "¡Genial! Gracias por la información. ¿Puedes decirme cuáles son los pasos específicos que debo seguir para solicitar la evaluación y aprobación por el director de la escuela correspondiente?"

prompt_3 = f"""Dado el historial del chat proporcionado entre tres comillas invertidas y la ultima pregunta del usuario, reformula la pregunta de manera que incluya todo el contexto necesario para que pueda entenderse en su totalidad sin necesidad del historial del chat. Si el mensaje ya es claro y no requiere reformulación, devuélvelo tal como está. No respondas el mensaje, solo reformúlalo si es necesario.

Historial del chat: {history_chat}

Último mensaje del usuario: {last_user_message}
"""

prompt_5 = f"""Dado el historial del chat proporcionado entre tres comillas invertidas, reformula el ultimo mensaje del usuario
Historial del chat: {history_chat}
"""

prompt_4 = f"""Dado el historial del chat proporcionado entre tres comillas invertidas, reformula el ultimo mensaje del usuario de manera que incluya todo el contexto necesario para que pueda entenderse en su totalidad sin necesidad del historial del chat. Si el mensaje ya es claro y no requiere reformulación, devuélvelo tal como está. No respondas el mensaje, solo reformúlalo si es necesario.
Historial del chat: {history_chat}
"""
#3. Si el mensaje y las preguntas ya son claros y no requieren reformulación ni agregar contexto adicional, devuélvelo tal como está.

prompt_6 = f"""Dado el historial del chat proporcionado entre tres comillas invertidas, reformula el ultimo mensaje si fuiese necesario, cumpliendo con los siguiente criterios:
1. Si el último mensaje del usuario contiene preguntas, reformula dichas preguntas para que incluyan todo el contexto necesario, de modo que puedan entenderse sin necesidad de revisar el historial del chat.
2. Si no hay preguntas en el último mensaje del usuario, devuélvelo tal como está.
3. Presenta el mensaje de la siguiente manera:
    user: Aqui el mensaje tal como está o el mensaje reformulado que incluye todo el contexto necesario, de modo que puedan entenderse sin necesidad de revisar el historial del chat
No respondas el mensaje, solo reformúlalo si es necesario.

Historial del chat: ```{history_chat}```
"""
## Paso 2. Si el último mensaje del usuario contiene preguntas, reformula dichas preguntas para que incluyan todo el contexto necesario, de modo que puedan entenderse sin necesidad de revisar el historial del chat.
#Paso 3. Presenta el ultimo mensaje del usuario reformulado o el original si no se requiere reformulacion de la siguiente manera:
#    user: Aqui el mensaje tal como está o el mensaje reformulado que incluye todo el contexto necesario, de modo que puedan entenderse sin necesidad de revisar el historial del chat
#No respondas el mensaje, solo reformúlalo si es necesario.


lasts_messages = [
    "¡Genial! Gracias por la información.", 
    "¡Genial! Gracias por la información. ¿Puedes decirme cuáles son los pasos específicos que debo seguir para solicitar la evaluación y aprobación por el director de la escuela correspondiente?",
    "Gracial por la informacion",
    "Gracias, entonces como puedo contactarme con esa oficina",
    "Entiendo, entonces como puedo solicitar la evalucion y aprovacion",
    "Gracias por esa informacion"
    ]

for last in lasts_messages:
    history_chat = """
    user: ¿Un estudiante puede matricularse en un curso y su pre requisito?
    assistant: Los estudiantes en posibilidad de egresar pueden matricularse en un curso y su prerequisito en el mismo ciclo. Deben comunicarse con su escuela profesional para solicitar la evaluación y aprobación por el director de la escuela correspondiente. Este beneficio aplica a aquellos alumnos que les falten como máximo treinta créditos para completar su Plan de Estudios y graduarse de la Universidad. Es importante cumplir con esta condición para poder matricularse en un curso y su prerequisito en el mismo ciclo académico."""

    last_user_message = last

    #last_user_message = "¡Genial! Gracias por la información. ¿Puedes decirme cuáles son los pasos específicos que debo seguir para solicitar la evaluación y aprobación por el director de la escuela correspondiente?"

    prompt_7 = f"""
    Dado el historial del chat proporcionado entre tres comillas invertidas, reformula el ultimo mensaje si fuiese necesario, siguiendo los siguiente pasos:
    Paso 1. Identifica si el ultimo mensaje del usuario contiene preguntas, en caso no contenga preguntas no es necesario reformúlarlo, devuelve el mensaje tal y como esta.
    Paso 2. Si el último mensaje del usuario contiene preguntas, reformula dichas preguntas para que incluyan todo el contexto necesario, de modo que puedan entenderse sin necesidad de revisar el historial del chat.

    Historial del chat: ```{history_chat}```
    """

    prompt_8 = f"""Dado el historial del chat proporcionado entre tres comillas invertidas, reformula el último mensaje del usuario si es necesario, siguiendo estos pasos:

    Paso 1. Identifica si el último mensaje del usuario contiene preguntas. Si no contiene preguntas, no es necesario reformularlo y debes devolver el mensaje tal como está.
    Paso 2. Si el último mensaje del usuario contiene preguntas, reformula dichas preguntas para que incluyan todo el contexto necesario, de modo que puedan entenderse sin necesidad de revisar el historial del chat.

    Historial del chat: ```{history_chat}```
    Último mensaje del usuario: ```{last_user_message}```"""



    prompt_10 = f"""Dado el historial del chat proporcionado entre tres comillas invertidas, reformula el último mensaje del usuario si es necesario, siguiendo estos pasos:

Paso 1: Identifica si el último mensaje del usuario contiene preguntas (ya sean implícitas o explícitas). Menciónalo de la siguiente manera: Contiene Preguntas: Sí o Contiene Preguntas: No.
Paso 2: Luego, según sea el caso, realiza lo siguiente:
    - Si no contiene preguntas, devuelve el mensaje tal como está sin reformular.
    - Si contiene preguntas, reformula dichas preguntas para que incluyan todo el contexto necesario, de modo que puedan entenderse sin necesidad de revisar el historial del chat. Proporciona el mensaje reformulado de la siguente manera: Reformulacion: Mensaje reformulado

Historial del chat: ```{history_chat}```
Último mensaje del usuario: ```{last_user_message}```"""

    prompt_9 = f"""Dado el historial del chat proporcionado entre tres comillas invertidas y el último mensaje del usuario, reformula cualquier pregunta contenida en el último mensaje del usuario para que incluya todo el contexto necesario y pueda entenderse de forma independiente, sin necesidad de revisar el historial del chat. Si el último mensaje del usuario no contiene preguntas, devuelve el mismo mensaje sin reformular.

Historial del chat: {history_chat}
Último mensaje del usuario: {last_user_message}```"""

    messages = [{"role": "user", "content": prompt_10}]

    response  = get_completion_from_messages(
        messages=messages,
        model="gpt-3.5-turbo-0125")

    print("response:", response)
    time.sleep(10)
