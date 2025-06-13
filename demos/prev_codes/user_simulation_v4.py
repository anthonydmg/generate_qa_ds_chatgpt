
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


def conversation_to_text(messages):
    txt = ""
    for m in messages:
        txt = txt + "\n" + m["role"] + ": "+ m["content"]
    return txt


propmpt_add = """
Responde de manera concisa y significativa, teniendo en cuenta el contexto del historial de diálogo en curso. Ten en cuenta tu objetivo principal de la conversación, que es obtener informacion o asesoria como estudiante universitario de la UNI
"""

question = "¡Hola!. Estoy buscando algo de orientación sobre el proceso de convalidación de asignaturas aquí en la Facultad de Ciencias de la UNI. He escuchado que hay ciertos criterios que deben cumplirse para que la convalidación proceda correctamente. ¿Podrías ayudarme con eso?"
respuesta = "Claro. Para que proceda la convalidación, los respectivos sílabos de las asignaturas a convalidar deben coincidir al menos en un 75% de su contenido y de horas dictadas."
prompt_user = """
Actua como un estudiante universitario de la Facultad de Ciencias de la Universidad Nacional de Ingenieria que estás buscando asesoría o información, 
por diversas razones.
Responde de manera concisa y significativa, teniendo en cuenta el contexto del historial de diálogo en curso. Ten en cuenta tu objetivo principal de la conversación, que es obtener informacion o asesoria como estudiante universitario de la UNI
"""

prompt_user_v2 =  """
Actua como un estudiante universitario de la Facultad de Ciencias de la Universidad Nacional de Ingeniería (UNI)  que esta buscando asesoría o información por lo que mantedras una conversacion conmingo donde consultes y tengas la intención de obtener diferente informacion que puedan ser inferida de los pares de preguntas y respuestas proporcionados  (delimitados por tres comillas invertidas).

Utiliza un tono semi formal apropiado para un estudiante universitario, evitando excesos en la formalidad. Responde de manera concisa y significativa, teniendo en cuenta el contexto del historial del diálogo en curso. Antes de plantear tus preguntas, considera exponer las razones, motivos o contexto que te llevan a buscar esta información o asesoría. Además, es preferible consultar un tema a la vez. Por ultimo, ten en cuenta tu objetivo principal de la conversación, que es obtener informacion o asesoria como estudiante universitario de la UNI.

Lista de pares de preguntas y respuesta: ```
1. ¿Cuál es el porcentaje mínimo de contenido que deben coincidir las asignaturas para que proceda la convalidación?
respuesta: Para que proceda la convalidación, los respectivos sílabos de las asignaturas a convalidar deben coincidir al menos en un 75% de su contenido y de horas dictadas.
2. ¿El plazo para las convalidaciones de traslados internos es de hasta cinco (05) días útiles desde la aprobación del Consejo de Facultad o autorización del Decano?
respuesta: Sí, el plazo para las convalidaciones de traslados internos es de hasta cinco (05) días útiles desde la aprobación del Consejo de Facultad o autorización del Decano, de acuerdo al reglamento de matrícula de la Facultad de Ciencias de la UNI.```

Comienza con la conversacion.
"""
messages =  [
#{"role": "system", "content": prompt_system},
{'role':'user', 'content': prompt_user_v2},
{"role": "assistant", "content": question},
{'role': 'user', 'content': respuesta}
]

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
