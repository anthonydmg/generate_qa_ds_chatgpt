import pandas as pd
import ast
from scipy import spatial
import os
import pandas as pd
import openai
from utils import get_completion_from_messages

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

history_chat = """
user: ¿Un estudiante puede matricularse en un curso y su pre requisito?
assistant: Los estudiantes en posibilidad de egresar pueden matricularse en un curso y su prerequisito en el mismo ciclo. Deben comunicarse con su escuela profesional para solicitar la evaluación y aprobación por el director de la escuela correspondiente. Este beneficio aplica a aquellos alumnos que les falten como máximo treinta créditos para completar su Plan de Estudios y graduarse de la Universidad. Es importante cumplir con esta condición para poder matricularse en un curso y su prerequisito en el mismo ciclo académico.
user: ¡Genial! Gracias por la información. ¿Puedes decirme cuáles son los pasos específicos que debo seguir para solicitar la evaluación y aprobación por el director de la escuela correspondiente?   
"""
prompt = f"""Dado el historial del chat proporcionado entre tres comillas invertidas y el ultimo mensaje del usuario, que podría hacer referencia al contexto en el historial del chat, reformule el mensaje de manera que incluya todo el contexto necesario para que pueda entenderse en su totalidad sin necesidad del contexto del historial del chat. No responda el mensaje, simplemente reformúlela si es necesario y, en caso contrario, devuélvala tal como está.

historial del chat: {history_chat}```"""


history_chat = """
user: ¿Un estudiante puede matricularse en un curso y su pre requisito?
assistant: Los estudiantes en posibilidad de egresar pueden matricularse en un curso y su prerequisito en el mismo ciclo. Deben comunicarse con su escuela profesional para solicitar la evaluación y aprobación por el director de la escuela correspondiente. Este beneficio aplica a aquellos alumnos que les falten como máximo treinta créditos para completar su Plan de Estudios y graduarse de la Universidad. Es importante cumplir con esta condición para poder matricularse en un curso y su prerequisito en el mismo ciclo académico.
"""

last_user_message = "¡Genial! Gracias por la información. ¿Puedes decirme cuáles son los pasos específicos que debo seguir para solicitar la evaluación y aprobación por el director de la escuela correspondiente?"

prompt_3 = f"""Dado el historial del chat proporcionado entre tres comillas invertidas y la ultima pregunta del usuario, reformula la pregunta de manera que incluya todo el contexto necesario para que pueda entenderse en su totalidad sin necesidad del historial del chat. Si el mensaje ya es claro y no requiere reformulación, devuélvelo tal como está. No respondas el mensaje, solo reformúlalo si es necesario.

Historial del chat: {history_chat}

Último mensaje del usuario: {last_user_message}
"""

messages = [{"role": "user", "content": prompt_3}]

response  = get_completion_from_messages(
    messages=messages,
    model="gpt-3.5-turbo-0125")

print("response:", response)

