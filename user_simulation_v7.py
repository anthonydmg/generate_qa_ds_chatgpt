
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

questions = [
    "¡Hola!. Estoy buscando algo de orientación sobre el proceso de convalidación de asignaturas aquí en la Facultad de Ciencias de la UNI. He escuchado que hay ciertos criterios que deben cumplirse para que la convalidación proceda correctamente. ¿Podrías ayudarme con eso?",
    "Estoy considerando cambiar de carrera y me gustaría saber si algunas de las asignaturas que ya cursé pueden convalidarse en la nueva carrera que deseo estudiar. ¿Cuál es el porcentaje mínimo de contenido que deben coincidir las asignaturas para que proceda la convalidación en la nueva carrera?",
    "Me acaban de informar que mi traslado interno ya ha sido aprobado. Y quisiera saber hasta cuando se puede realizar la convalidacion de asignaturas."
    ]

respuesta = "Claro. Para que proceda la convalidación, los respectivos sílabos de las asignaturas a convalidar deben coincidir al menos en un 75% de su contenido y de horas dictadas."

prompt_system_user =  """
Eres un estudiante universitario de la Facultad de Ciencias de Ciencias de la Universidad Nacional de Ingeniería (UNI) que tiene la intención de obtener informacion sobre diferentes temas. Dicha informacion debe poder ser inferida de los pares de preguntas y respuestas proporcionados  (delimitados por tres comillas invertidas).
Deberas responder a los mensajes asegurandote de cumplir con los siguientes criterios.
Criterio 1. Utiliza un tono semi formal apropiado para un estudiante universitario, evitando declaraciones excesivamente educadas.
Criterio 2. Antes de saltar a otro tema considera consultar mas al respecto teniendo en cuenta el contexto del historial del diálogo en curso.

Lista de pares de preguntas y respuesta: ```
1. ¿Cuál es el porcentaje mínimo de contenido que deben coincidir las asignaturas para que proceda la convalidación?
respuesta: Para que proceda la convalidación, los respectivos sílabos de las asignaturas a convalidar deben coincidir al menos en un 75% de su contenido y de horas dictadas.
2. ¿El plazo para las convalidaciones de traslados internos es de hasta cinco (05) días útiles desde la aprobación del Consejo de Facultad o autorización del Decano?
respuesta: Sí, el plazo para las convalidaciones de traslados internos es de hasta cinco (05) días útiles desde la aprobación del Consejo de Facultad o autorización del Decano, de acuerdo al reglamento de matrícula de la Facultad de Ciencias de la UNI.```
"""

prompt_system_user_v2 =  """
Eres un estudiante universitario de la Facultad de Ciencias de Ciencias de la Universidad Nacional de Ingeniería (UNI) que tiene la intención de obtener informacion sobre diferentes temas. Dicha informacion debe poder ser inferida de los pares de preguntas y respuestas proporcionados  (delimitados por tres comillas invertidas).
Deberas responder a los mensajes asegurandote de cumplir con los siguientes criterios.
Criterio 1. Utiliza un tono semi formal apropiado para un estudiante universitario, evitando declaraciones excesivamente educadas.
Criterio 2. Antes de mencionar tu consultar, cosidera exponer las razones, motivos o contexto que te llevan a buscar esta información o asesoría.
Criterio 3. Responde de manera concisa y significativa, teniendo en cuenta el contexto del historial del diálogo en curso. 
Criterio 4. Es preferible consultar un tema a la vez.

Lista de pares de preguntas y respuesta: ```
1. ¿Cuál es el porcentaje mínimo de contenido que deben coincidir las asignaturas para que proceda la convalidación?
respuesta: Para que proceda la convalidación, los respectivos sílabos de las asignaturas a convalidar deben coincidir al menos en un 75% de su contenido y de horas dictadas.
2. ¿El plazo para las convalidaciones de traslados internos es de hasta cinco (05) días útiles desde la aprobación del Consejo de Facultad o autorización del Decano?
respuesta: Sí, el plazo para las convalidaciones de traslados internos es de hasta cinco (05) días útiles desde la aprobación del Consejo de Facultad o autorización del Decano, de acuerdo al reglamento de matrícula de la Facultad de Ciencias de la UNI.```
"""

prompt_ai_assistant = """
Eres un asistente de AI especializado en temas de matricula, procedimientos, tramites academicos de la Facultad de Ciencias.
Deberas responder a los mensajes asegurandote de cumplir con los siguientes criterios.
    1. Debes brindar respuestas informativas y útiles a las preguntas del usuario al inferir la información exclusivamente de los pares de preguntas y respuestas proporcionados dentro de las comillas invertidas, sin añadir información ficticia.
    2. Evita proporcionar informacion que no haya sido inferida de los pares de preguntas y respuestas proporcionados dentro de las comillas invertidas
    3. Manten un tono cordial y empático en sus interacciones.
    4. En caso sea sumamente necesario puedes usar la siguiente informacion adicional de la Facultad de Ciencias para complementar alguna respuesta:
        - La facultad de ciencias cuenta con pagina web.
        - En la sección de Matrícula y Procedimientos (dentro de Aera) de la pagina web de la facultad se publica:
            * Manuales/diagramas de diferentes procesos de matricula, procedimientos y tramites academicos.
            * El calendario académico
            * Modelos para solicitudes de diferentes procesos academicos.
        - Las vacantes disponibles de los cursos a matriculase se visualizan en la plataforma de intranet-alumno (DIRCE)

    5. Solo en caso no sea posible proveer una respuesta completa con la información proporcionada o se mencione problemas con procesos de matricula sugiere consultar con la oficina del Area de Estadistica y Registros Academicos de la Facultad de ciencias (AERA).

Lista de pares de preguntas y respuesta: ```
1. ¿Cuál es el porcentaje mínimo de contenido que deben coincidir las asignaturas para que proceda la convalidación?
respuesta: Para que proceda la convalidación, los respectivos sílabos de las asignaturas a convalidar deben coincidir al menos en un 75% de su contenido y de horas dictadas.
2. ¿El plazo para las convalidaciones de traslados internos es de hasta cinco (05) días útiles desde la aprobación del Consejo de Facultad o autorización del Decano?
respuesta: Sí, el plazo para las convalidaciones de traslados internos es de hasta cinco (05) días útiles desde la aprobación del Consejo de Facultad o autorización del Decano, de acuerdo al reglamento de matrícula de la Facultad de Ciencias de la UNI.```
"""

for i ,question in enumerate(questions[0:2]):
    print(f"\n\nConversacion {i + 1}.......................................................\n\n")
    messages_to_assitant_ai = [
    {'role': "system", 'content': prompt_ai_assistant},
    {"role": "user", "content": question}
    ]

    messages_to_user_ai =  [
    {'role':'system', 'content': prompt_system_user},
    {'role': 'user', 'content': propmpt_add},
    {"role": "assistant", "content": question},
    #{'role': 'user', 'content': respuesta}
    ]

    print(conversation_to_text(messages_to_user_ai[:1] + messages_to_assitant_ai[1:2]))

    for i in range(3):

        response_ai = get_completion_from_messages(messages_to_assitant_ai)
        print("\nAssitant:", response_ai)
        #message_input = input("Ingresa Mensaje:")
        
        messages_to_assitant_ai.extend([
            {"role": "assistant", "content": response_ai},
        ])

        messages_to_user_ai.extend([
            {"role": "user", "content": response_ai},
        ])

        response_user_ai = get_completion_from_messages(messages_to_user_ai)
        
        messages_to_assitant_ai.extend([
            {"role": "user", "content": response_user_ai},
        ])

        messages_to_user_ai.extend([
            {"role": "assistant", "content": response_user_ai},
        ])

        print("\nUser:", response_user_ai)

#print("messages_to_user_ai:", messages_to_user_ai)
