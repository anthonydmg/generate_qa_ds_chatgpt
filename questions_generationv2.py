import openai
import json
from dotenv import load_dotenv
import os
from utils import save_json, load_json, format_response_json, read_fragment_doc, list_json_to_txt, count_tokens
import glob
import tiktoken
import time
from tqdm import tqdm
from enum import Enum
import re
load_dotenv()

def set_openai_key():
    API_KEY = os.getenv("API_KEY")
    openai.api_key = API_KEY


class QuestionType(Enum):
    YES_OR_NOT_ANSWER = 1
    FACTOID = 2



def get_completion_from_messages(messages, model="gpt-3.5-turbo-1106", temperature=0):
    response = openai.chat.completions.create(
        model=model,
        messages=messages,
        #max_tokens = 0,
        temperature=temperature, # this is the degree of randomness of the model's output
    )
    return response.choices[0].message.content


def get_prompt_gen_questions(text, question_type, num_questions):
    if question_type == QuestionType.YES_OR_NOT_ANSWER:
        prompt = get_prompt_gen_yes_or_not_questions(text, num_questions)
        return prompt
    elif question_type == QuestionType.FACTOID:
        prompt = get_prompt_gen_factoid_questions(text, num_questions)
        return prompt



def get_prompt_gen_yes_or_not_questions_v3(reglamento, num_questions = 20):
    format_json = """{"preguntas": ["pregunta 1 generada", "pregunta 2 generada", ...]"""
    
    prompt = f"""
    Eres un asistente de IA especializado en matrículas, trámites y procedimientos académicos de la Facultad de Ciencias de la UNI. 
    Se te proporcionará un fragmento de texto con información sobre reglamentos y/o procedimientos académicos, delimitado por tres comillas invertidas.
    Genera al menos {num_questions} preguntas que cumplan con los siguientes criterios:
    - Respuestas directas de 'Sí' o 'No'.
    - No cite numerales de artículos en las preguntas.
    - No hables directamente del presente reglamento en las preguntas.
    - Enfócate en preguntas relevantes para alumnos, docentes o el público en general.
    - Asegúrese de que las preguntas puedan ser respondidas con un 'Sí' o 'No' basándose en la información proporcionada.

    Detecta y excluye de la lista final las preguntas que sigan la estructura de "¿El presente Reglamento establece...?" o "¿El presente Reglamento es de cumplimiento...?".     
    Finalmente, proporciona las preguntas en el siguiente formato JSON:
    {format_json}
    Fragmento de texto: ```{reglamento}```
    """
    return prompt

def get_prompt_gen_yes_or_not_questions_v4(reglamento, num_questions = 20):
    format_json = """{"preguntas": ["pregunta 1 generada", "pregunta 2 generada", ...]"""
    
    prompt = f"""
    Eres un asistente de IA especializado en matrículas, trámites y procedimientos académicos de la Facultad de Ciencias de la UNI. 
    Se te proporcionará información sobre reglamentos académicos delimitada por tres comillas invertidas. 
    Genera al menos {num_questions} preguntas que cumplan con los siguientes criterios:
     - Respuestas directas de 'Sí' o 'No'.
     - Evita citar numerales de artículos en las preguntas.
     - No menciones directamente el presente reglamento en las preguntas.
     - Enfócate en preguntas relevantes para alumnos, docentes o el público en general.
     - Asegúrate de que las preguntas puedan ser respondidas con un 'Sí' o 'No' basándose en la información proporcionada.
    Luego de generar las preguntas, detecta y excluye de la lista final las preguntas que sigan la estructura de "¿El presente Reglamento establece...?" o "¿El presente Reglamento es de cumplimiento...?". 
    Finalmente, proporciona la lista final de preguntas en el siguiente formato JSON : {format_json}. 
    Fragmento de texto: {reglamento}.
    """
    return prompt

def get_prompt_filter_questions(questions):
    format_json = """{"preguntas": ["pregunta 1 generada", "pregunta 2 generada", ...]"""
    list_preguntas = "\n- " + "\n- ".join(questions)
    prompt = f""" 
    Se te proporcionará una lista de preguntas.
    Filtra y elimina de la lista cualquier pregunta que contenga la palabra "reglamento"
    Finalmente, proporciona la lista final de preguntas en el siguiente formato JSON: {format_json}. 
    Preguntas: {list_preguntas}
    """
    return prompt

def get_prompt_filter_questions_v1(questions):
    format_json = """{"preguntas": ["pregunta 1 generada", "pregunta 2 generada", ...]"""
    list_preguntas = "\n- ".join(questions)
    prompt = f""" 
    Se te proporcionará una lista de preguntas. 
    Filtra y elimina de la lista las preguntas que no cumplen con los siguientes criterios:
        - No deben mencionar directamente al reglamento.
        - No deben consultar sobre el objetivo o alcance del reglamento.
        - No deben preguntar directamente quiénes deben cumplir con el presente reglamento. 
    Finalmente, proporciona la lista final de preguntas en el siguiente formato JSON: {format_json}. 
    Preguntas: {list_preguntas}
    """
    return prompt

def get_prompt_gen_yes_or_not_questions(reglamento, num_questions = 20):
    format_json = """{"preguntas": ["pregunta 1 generada", "pregunta 2 generada", ...]"""
    
    prompt = f"""
Tu tarea es genera al menos  {num_questions} preguntas que tengan respuesta directas de 'Sí' o 'No', basadas en la información proporcionada sobre reglamentos académicos de la Facultad de Ciencias de la UNI (delimitada por tres comillas invertidas).
Antes de generar cada pregunta asegurate de cumplir con los siguientes criterios:
   - Las preguntas deben tener respuestas directas de 'Sí' o 'No' basándose en la información proporcionada.
   - Evita citar numerales de artículos en las preguntas.
   - No menciones o cites a tablas especificas en las preguntas.
   - No mencione directamente al reglamento en las preguntas.
   - Enfócate en preguntas relevantes para alumnos, docentes o el público en general que puedan ser respondidas con la información proporcionada.
Fragmento de texto: {reglamento}.
    """
    return prompt

# Me gusta al 85%
def get_prompt_gen_yes_or_not_questions_v3(reglamento, num_questions = 20):
    format_json = """{"preguntas": ["pregunta 1 generada", "pregunta 2 generada", ...]"""
    
    prompt = f"""
    Eres un asistente de IA especializado en matrículas, trámites y procedimientos académicos de la Facultad de Ciencias de la UNI. 
Se te proporcionará información sobre reglamentos académicos delimitada por tres comillas invertidas. 
Genera al menos {num_questions} preguntas que cumplan con los siguientes criterios:
   - Respuestas directas de 'Sí' o 'No'.
   - Evita citar numerales de artículos en las preguntas.
   - No mencione directamente al reglamento en las preguntas.
   - Enfócate en preguntas relevantes para alumnos, docentes o el público en general.
   - Asegúrate de que las preguntas puedan ser respondidas con un 'Sí' o 'No' basándose en la información proporcionada.

Finalmente, proporciona la lista final de preguntas en el siguiente formato JSON: {format_json}. 
Fragmento de texto: {reglamento}.
    """
    return prompt

def get_prompt_gen_yes_or_not_questions_v2(reglamento, num_questions = 20):
    format_json = """{"preguntas": ["pregunta 1 generada", "pregunta 2 generada", ...]"""
    
    prompt = f"""
    Eres un asistente de IA especializado en matrículas, trámites y procedimientos académicos de la Facultad de Ciencias de la UNI. 
    Se te proporcionará un fragmento de texto con información sobre reglamentos y/o procedimientos académicos, delimitado por tres comillas invertidas. 
    A continuación, los requisitos para generar preguntas:
    - Las preguntas deben tener respuestas directas de 'Sí' o 'No'.
    - No cite numerales de artículos en las preguntas.
    - No mencione directamente al presente reglamento en las preguntas.
    - Evite preguntas sobre que se establece en el presente reglamento, por ejemplo: ¿El presente reglamento establece ..?.
    - Enfóquese en preguntas relevantes para usuarios como alumnos, docentes o el público en general, que puedan responderse con la información proporcionada.
    - Asegúrese de que las preguntas puedan ser respondidas con un 'Sí' o 'No' basándose en la información proporcionada.
    - Genere al menos {num_questions} preguntas con una longitud máxima de 30 palabras.

    Finalmente, proporciona las preguntas en el siguiente formato JSON:
    {format_json}
    Fragmento de texto: ```{reglamento}```
    """
    return prompt
    
## probar la forma de chatgpt

def get_prompt_gen_yes_or_not_questions_v1(reglamento, num_questions = 20):
    format_json = """{"preguntas": ["pregunta 1 generada", "pregunta 2 generada", ...]"""
    
    prompt = f"""
    Eres un asistente de IA especializado en temas de matriculas, tramites y procedimiendo academicos de la Facultad de Ciencias de la UNI
    Se te dará un texto delimitado por tres comillas invertidas tomado de un fragmento del reglamento de matricula. 
    A continuación se detallan los requisitos para generar preguntas que puedan surgir en una conversación con un usuario:
    - Las preguntas deben poder responderse directamente con un Sí ó No.
    - Evite mencionar directamente el reglamento en las preguntas.
    - Evite citar numerales de artículos en las preguntas.
    - Concéntrese en preguntas relevantes para usuarios como alumnos, docentes o el público en general, que puedan responderse con la información proporcionada. 
    - Asegurate que las preguntas puedan ser respondidas con un Sí ó No basándose en la información proveida.
    - Debe generar al menos {num_questions} preguntas que tengan como máximo 30 palabras de longitud.

    Finalmente, proporciona las preguntas en el siguiente formato JSON:
    {format_json}
    Fragmento del Reglamento: ```{reglamento}```
    """
    return prompt

def get_prompt_gen_factoid_questions_v4(reglamento, num_questions = 20):
    format_json = """{"preguntas": ["pregunta 1 generada", "pregunta 2 generada", ...]"""
    
    prompt = f"""
Eres un asistente de IA especializado en matrículas, trámites y procedimientos académicos de la Facultad de Ciencias de la UNI. 
Se te proporcionará información sobre reglamentos académicos delimitada por tres comillas invertidas. 
Genera al menos {num_questions} preguntas asegurándote que cumplan con los siguientes criterios:
    - No menciones numerales de artículos en las preguntas, por ejemplo, no utilices "¿En el Art. XXX del reglamento...?" o "¿... según el Art. XXX?" son ejemplos de preguntas que mencionan articulos.
    - No formule preguntas que requieran identificar artículos específicos del reglamento.
    - Enfócate en preguntas prácticas y relevantes para usuarios como alumnos, docentes o el público en general, que puedan responderse con la información proporcionada.

Asegúrate de que cada pregunta cumpla estrictamente con todos los criterios antes de generarlas.
Finalmente, proporciona las preguntas en el siguiente formato JSON: {format_json}
Fragmento de texto: ```{reglamento}```
    """
    return prompt


def get_prompt_gen_factoid_questions_v10(reglamento, num_questions = 20):
    format_json = """{"preguntas": ["pregunta 1 generada", "pregunta 2 generada", ...]"""
    
    prompt = f"""
Tu tarea es generar al menos {num_questions} preguntas basadas en la información proporcionada sobre reglamentos académicos (delimitada por tres comillas invertidas). 
Para ello sigue las siguientes instrucciones:
1. Para cada pregunta sigue los siguientes pasos:
    1.1. Antes de generar la pregunta usando la informacion proveida, piensa deteninamente en como explicar que la pregunta cumple cada uno de los siguientes criterios:
        a. Evita mencionar o citar numerales de artículos específicos en las preguntas.
        b. No formules preguntas que requieran identificar el numero de artículos específicos en el reglamento.
        c. No crees preguntas que mencionen directamente datos especificos.
        d. Concéntrate en preguntas prácticas y relevantes para usuarios como alumnos, docentes o el público en general, que puedan ser respondidas con la información proporcionada.
    1.2. Asegurate de generar la pregunta que cumple con todos los criterios anteriormente mencionados.
    1.3. Para cada criterio mencionado genera la explicacion de como la pregunta cumple con ese criterio. 
2. Muestra cada pregunta junto con las explicaciones generadas.
3. Finalmente, presenta las preguntas en el siguiente formato JSON: {format_json}

Fragmento de texto: ```{reglamento}```
    """
    return prompt


def get_prompt_gen_factoid_questions_v11(reglamento, num_questions = 20):
    format_json = """{"preguntas": ["pregunta 1 generada", "pregunta 2 generada", ...]"""
    
    prompt = f"""
Tu tarea es generar al menos {num_questions} preguntas basadas en la información proporcionada sobre reglamentos académicos (delimitada por tres comillas invertidas). 
Antes de crear una pregunta asegúrate de cumplir estrictamente cada uno de los siguientes criterios:
    1. Evita mencionar o citar numerales de artículos específicos en las preguntas.
    2. No formules preguntas que requieran identificar el numero de artículos específicos en el reglamento.
    3. No crees preguntas que mencionen directamente datos especificos.
    4. No elabores preguntas que consulten sobre el objetivo o alcance del reglamento.
    5. Concéntrate en preguntas prácticas y relevantes para usuarios como alumnos, docentes o el público en general, que puedan ser respondidas con la información proporcionada.

Finalmente, presenta las preguntas en el siguiente formato JSON: {format_json}
Fragmento de texto: ```{reglamento}```
    """
    return prompt

def get_prompt_gen_factoid_questions_v12(reglamento, num_questions = 20):
    format_json = """{"preguntas": ["pregunta 1 generada", "pregunta 2 generada", ...]"""
    
    prompt = f"""
Tu tarea es generar al menos {num_questions} prácticas y relevantes para usuarios como alumnos, docentes o el público en general, que puedan ser respondidas con la información proporcionada sobre reglamentos académicos (delimitada por tres comillas invertidas).
Antes de crear cada pregunta piensa detenidamente y asegúrate de cumplir estrictamente cada uno de los siguientes criterios:
    1. Evita mencionar o citar numerales de artículos específicos en las preguntas.
    2. No formules preguntas que requieran identificar artículos específicos en el reglamento.
    3. No crees preguntas que mencionen directamente datos especificos.
    4. Concéntrate en preguntas prácticas y relevantes para usuarios como alumnos, docentes o el público en general, que puedan ser respondidas con la información proporcionada.
Finalmente, presenta las preguntas en el siguiente formato JSON: {format_json}
...

Fragmento de texto: ```{reglamento}```
"""
    return prompt

def get_prompt_gen_factoid_questions_v14(reglamento, num_questions = 20):
    format_json = """{"preguntas": ["pregunta 1 generada", "pregunta 2 generada", ...]"""
    
    prompt = f"""
Tu tarea es generar al menos {num_questions} preguntas prácticas y relevantes para usuarios como alumnos, docentes o el público en general, basadas en la información proporcionada sobre reglamentos académicos (delimitada por tres comillas invertidas). 
Antes de crear cada pregunta asegúrate de cumplir estrictamente cada uno de los siguientes criterios:
    1. No menciones numerales de artículos específicos en las preguntas.
    2. No formules preguntas que requieran identificar el numero de artículos específicos en el reglamento.
    3. No crees preguntas que mencionen directamente datos especificos.
    4. Concéntrate en preguntas prácticas y relevantes para usuarios como alumnos, docentes o el público en general, que puedan ser respondidas con la información proporcionada.
Fragmento de texto: ```{reglamento}```
    """
    return prompt
# Este es el ultimo
#Me gusta al 92.8 porciento
def get_prompt_gen_factoid_questions_v15(reglamento, num_questions = 20):
    print(f"\nNumero de preguntas a crear {num_questions}")
    prompt = f"""
Tu tarea es generar al menos {num_questions} preguntas basadas en la información proporcionada sobre reglamentos académicos de la Facultad de Ciencias de la UNI (delimitada por tres comillas invertidas). 
Antes de crear una pregunta asegúrate de cumplir estrictamente cada uno de los siguientes criterios:
    - Evita mencionar o citar numerales de artículos específicos en las preguntas.
    - No formules preguntas que requieran identificar el numero de artículos específicos en el reglamento.
    - No crees preguntas que mencionen directamente datos especificos.
    - Concéntrate en preguntas prácticas y relevantes para usuarios como alumnos, docentes o el público en general, que puedan ser respondidas con la información proporcionada.
Genera las {num_questions} preguntas y justifica para cada pregunta por que cumple con cada uno de los criterios mencionados anteriormente.
Fragmento de texto: ```{reglamento}```
    """
    return prompt

def get_prompt_gen_factoid_questions(reglamento, num_questions = 20):
    print(f"\nNumero de preguntas a crear {num_questions}")
    prompt = f"""
Tu tarea es generar al menos {num_questions} preguntas, basadandote en la información proporcionada sobre reglamentos académicos de la Facultad de Ciencias de la UNI (delimitada por tres comillas invertidas). 
Antes de crear una pregunta asegúrate de cumplir estrictamente cada uno de los siguientes criterios:
    - Evita mencionar o citar numerales de artículos específicos en las preguntas.
    - No formules preguntas que requieran identificar el numero de artículos específicos en el reglamento.
    - No crees preguntas que mencionen directamente datos especificos.
    - Concéntrate en preguntas prácticas y relevantes para usuarios como alumnos, docentes o el público en general, que puedan ser respondidas con la información proporcionada.
    - Las preguntas deben fomentar respuestas extensas, respaldadas por la información brindada. 
    - Evita la repetición y asegúrate de crear preguntas únicas de diferentes temas relevantes para usuarios como alumnos, docentes o el público en general,
Genera las {num_questions} preguntas y justifica para cada pregunta por que cumple con cada uno de los criterios mencionados anteriormente.
Fragmento de texto: ```{reglamento}```
    """
    return prompt

#Me gusta al 92.5 porciento
def get_prompt_gen_factoid_questions_v14(reglamento, num_questions = 20):
    
    prompt = f"""
Tu tarea es generar al menos {num_questions} preguntas basadas en la información proporcionada sobre reglamentos académicos (delimitada por tres comillas invertidas). 
Antes de crear una pregunta asegúrate de cumplir estrictamente cada uno de los siguientes criterios:
    - Evita mencionar o citar numerales de artículos específicos en las preguntas.
    - No formules preguntas que requieran identificar el numero de artículos específicos en el reglamento.
    - No crees preguntas que mencionen directamente datos especificos.
    - Concéntrate en preguntas prácticas y relevantes para usuarios como alumnos, docentes o el público en general, que puedan ser respondidas con la información proporcionada.
Genera cada pregunta justificando por que cumple con cada uno de los criterios mencionados anteriormente.
Fragmento de texto: ```{reglamento}```
    """
    return prompt


# Me gusta el 92 por ciento
def get_prompt_gen_factoid_questions_v13(reglamento, num_questions = 20):
    format_json = """{"preguntas": ["pregunta 1 generada", "pregunta 2 generada", ...]"""
    
    prompt = f"""
Genera al menos {num_questions} preguntas basadas en la información proporcionada sobre reglamentos académicos (delimitada por tres comillas invertidas). 
Antes de crear una pregunta asegúrate de cumplir estrictamente cada uno de los siguientes criterios:
    - Evita mencionar o citar numerales de artículos específicos en las preguntas.
    - No formules preguntas que requieran identificar el numero de artículos específicos en el reglamento.
    - No crees preguntas que mencionen directamente datos especificos.
    - Concéntrate en preguntas prácticas y relevantes para usuarios como alumnos, docentes o el público en general, que puedan ser respondidas con la información proporcionada.
Luego presenta cada pregunta y explica de manera concisa a continuacion de cada pregunta por que cumplen con cada uno de los criterios mencionados.
Finalmente, presenta las preguntas en el siguiente formato JSON: {format_json}
Fragmento de texto: ```{reglamento}```
    """
    return prompt

## Me gusta al 90 por ciento

def get_prompt_gen_factoid_questions_v8(reglamento, num_questions = 20):
    format_json = """{"preguntas": ["pregunta 1 generada", "pregunta 2 generada", ...]"""
    
    prompt = f"""
Genera al menos {num_questions} preguntas basadas en la información proporcionada sobre reglamentos académicos (delimitada por tres comillas invertidas). 
Antes de crear una pregunta asegúrate de cumplir estrictamente cada uno de los siguientes criterios:
    - Evita mencionar o citar numerales de artículos específicos en las preguntas.
    - No formules preguntas que requieran identificar el numero de artículos específicos en el reglamento.
    - No crees preguntas que mencionen directamente al reglamento.
    - Concéntrate en preguntas prácticas y relevantes para usuarios como alumnos, docentes o el público en general, que puedan ser respondidas con la información proporcionada.
Luego presenta cada pregunta y explica de manera concisa a continuacion de cada pregunta por que cumplen con cada uno de los criterios mencionados.
Finalmente, presenta las preguntas en el siguiente formato JSON: {format_json}
Fragmento de texto: ```{reglamento}```
    """
    return prompt


def get_prompt_gen_factoid_questions_v7(reglamento, num_questions = 20):
    format_json = """{"preguntas": ["pregunta 1 generada", "pregunta 2 generada", ...]"""
    
    prompt = f"""
Genera al menos {num_questions} preguntas basadas en la información proporcionada sobre reglamentos académicos (delimitada por tres comillas invertidas). 
Asegúrate de que cada pregunta cumpla con los siguientes criterios:
    - Evita mencionar o citar numerales de artículos específicos en las preguntas.
    - No formules preguntas que requieran identificar el numero de artículos específicos en el reglamento.
    - Concéntrate en preguntas prácticas y relevantes para usuarios como alumnos, docentes o el público en general, que puedan ser respondidas con la información proporcionada.
Asegurate de no generar preguntas que no cumplan estos criterios.
Finalmente, presenta las preguntas en el siguiente formato JSON: {format_json}
Fragmento de texto: ```{reglamento}```
    """
    return prompt


def get_prompt_gen_factoid_questions_v6(reglamento, num_questions = 20):
    format_json = """{"preguntas": ["pregunta 1 generada", "pregunta 2 generada", ...]"""
    
    prompt = f"""
Se te proporcionará información sobre reglamentos académicos delimitada por tres comillas invertidas. 
Genera al menos {num_questions} preguntas asegurándote que cumplan con los siguientes criterios:
    - Las preguntas no deben mencionar o citar numerales de articulos.
    - No formule preguntas que requieran identificar artículos específicos del reglamento.
    - Enfócate en preguntas prácticas y relevantes para usuarios como alumnos, docentes o el público en general, que puedan responderse con la información proporcionada.

Asegúrate de que cada pregunta cumpla estrictamente con todos los criterios antes de generarlas.
Finalmente, proporciona las preguntas en el siguiente formato JSON: {format_json}
Fragmento de texto: ```{reglamento}```
    """
    return prompt

def get_prompt_gen_factoid_questions_v5(reglamento, num_questions = 20):
    format_json = """{"preguntas": ["pregunta 1 generada", "pregunta 2 generada", ...]"""
    
    prompt = f"""
Se te proporcionará información sobre reglamentos académicos delimitada por tres comillas invertidas. 
Genera al menos {num_questions} preguntas asegurándote que cumplan con los siguientes criterios:
    - No menciones numerales de artículos en las preguntas, por ejemplo, no crees preguntas como: "¿En el Art. XXX del reglamento...?" o "¿... según el Art. XXX?".
    - No formule preguntas que requieran identificar artículos específicos del reglamento.
    - Enfócate en preguntas prácticas y relevantes para usuarios como alumnos, docentes o el público en general, que puedan responderse con la información proporcionada.

Asegúrate de que cada pregunta cumpla estrictamente con todos los criterios antes de generarlas.
Finalmente, proporciona las preguntas en el siguiente formato JSON: {format_json}
Fragmento de texto: ```{reglamento}```
    """
    return prompt

def get_prompt_gen_factoid_questions_f1(reglamento, num_questions = 20):
    format_json = """{"preguntas": ["pregunta 1 generada", "pregunta 2 generada", ...]"""
    
    prompt = f"""
   
Entiendo que es crucial cumplir con la condición de concentrarse en preguntas relevantes para usuarios como alumnos, docentes o el público en general, que puedan responderse con la información proporcionada. Intentemos mejorar la instrucción para enfocarnos aún más en este aspecto:

plaintext
Copy code
Eres un asistente de IA especializado en matrículas, trámites y procedimientos académicos de la Facultad de Ciencias de la UNI. 
Se te proporcionará información sobre reglamentos académicos delimitada por tres comillas invertidas. 
Genera al menos {num_questions} preguntas asegurándote que cumplan con los siguientes criterios:
    - No menciones numerales de artículos en las preguntas, por ejemplo, no menciones directamente "¿En el Art. 102 del reglamento...?" o "¿... según el Art. 25?".
    - Enfócate en preguntas prácticas y relevantes para usuarios como alumnos, docentes o el público en general, que puedan responderse con la información proporcionada.

Asegúrate de que cada pregunta cumpla estrictamente con todos los criterios antes de generarlas.
Finalmente, proporciona las preguntas en el siguiente formato JSON: {format_json}
Fragmento de texto: ```{reglamento}```
    """
    return prompt

def get_prompt_gen_factoid_questions_v2(reglamento, num_questions = 20):
    format_json = """{"preguntas": ["pregunta 1 generada", "pregunta 2 generada", ...]"""
    
    prompt = f"""
    Eres un asistente de IA especializado en matrículas, trámites y procedimientos académicos de la Facultad de Ciencias de la UNI. 
    Se te proporcionará un fragmento del reglamento de matrícula entre tres comillas invertidas. 
    A continuación, los requisitos para generar preguntas:  
        - Evite citar numerales de artículos en las preguntas. 
        - Evite mencionar directamente el reglamento en las preguntas.
        - No formule preguntas que requieran identificar artículos específicos del reglamento.
        - Concéntrese en preguntas relevantes para usuarios como alumnos, docentes o el público en general, que puedan responderse con la información proporcionada.
        - Debe generar al menos {num_questions} preguntas que tengan como máximo 30 palabras de longitud.

    Finalmente, proporciona las preguntas en el siguiente formato JSON:
    {format_json}
    Fragmento del Reglamento: ```{reglamento}```
    """
    return prompt


def get_prompt_gen_factoid_questions_v1(reglamento, num_questions = 20):
    format_json = """{"preguntas": ["pregunta 1 generada", "pregunta 2 generada", ...]"""
    
    prompt = f"""
    Eres un asistente de IA especializado en temas de matriculas, tramites y procedimiendo academicos de la Facultad de Ciencias de la UNI
    Se te dará un texto delimitado por tres comillas invertidas tomado de un fragmento del reglamento de matricula. 
    A continuación se detallan los requisitos para generar preguntas que puedan surgir en una conversación con un usuario:
    - Evite hacer referencia al reglamento en las preguntas.
    - Absténgase de formular preguntas que requieran identificar cual artículo específicos del reglamento establece alguna norma.
    - No cite numerales de artículos en las preguntas.
    - Concéntrese en hacer preguntas que un usuario como un alumno, docente o publico en general puedan tener y que puedan ser respondididas con la informacion proveida.
    - Debe generar al menos {num_questions} preguntas que tengan como máximo 30 palabras de longitud.

    Finalmente, proporciona las preguntas en el siguiente formato JSON:
    {format_json}
    Fragmento del Reglamento: ```{reglamento}```
    """
    return prompt

def get_prompt_gen_factoid_questions_v1(reglamento, num_questions = 20):
    format_json = """{"preguntas": ["pregunta 1 generada", "pregunta 2 generada", ...]"""
    
    prompt = f"""Eres un asistente de IA especializado en matrículas, trámites y procedimientos académicos de la Facultad de Ciencias de la UNI. Se te brindará información sobre reglamentos académicos delimitada por tres comillas invertidas.
Genera al menos {num_questions} preguntas que cumplan con los siguientes criterios:
Respuestas directas de 'Sí' o 'No'.
Evita citar numerales de artículos en las preguntas.
No menciones directamente el presente reglamento en las preguntas.
Enfócate en preguntas relevantes para alumnos, docentes o el público en general.
Asegúrate de que las preguntas puedan ser respondidas con un 'Sí' o 'No' basándose en la información proporcionada.
Detecta y excluye de la lista final las preguntas que mencionen al reglamento".
Finalmente, presenta la lista final de preguntas en el siguiente formato JSON: {format_json}. Fragmento de texto: {reglamento}.
    """
    return prompt

## Las preguntas deben tener un máximo de 50 palabras.

set_openai_key()

encoding = tiktoken.encoding_for_model('gpt-3.5-turbo')

class QuestionGenerator:
    def __init__(self, dir_documents, questions_types):
        self.dir_documents = dir_documents
        self.questions_types = questions_types
    
    def get_num_questions(self, question_type, num_tokens):
        if question_type == QuestionType.YES_OR_NOT_ANSWER:
            if num_tokens < 500:
                num_questions = 10
            elif num_tokens < 1000:
                num_questions = 20
            elif num_tokens < 1500:
                num_questions = 30
            else:
                num_questions = 40

        elif question_type == QuestionType.FACTOID:
            if num_tokens < 500:
                num_questions = 10
            elif num_tokens < 1000:
                num_questions = 25
            elif num_tokens < 1500:
                num_questions = 35
            else:
                num_questions = 45

        return num_questions

    def run(self):
        questions_generated = []
        #for file_text in tqdm(glob.glob(f"{self.dir_documents}/*.txt"), desc= "Generando Preguntas"):
        documents = glob.glob(f"{self.dir_documents}/*.txt")
        documents.sort()
        print("Inicia Generación de preguntas...")
        
        progress_bar = tqdm(range(len(documents[3:4])), desc= "Documentos")
        total_questions = 0
        for file_text in documents[3:4]:
            text = read_fragment_doc(file_text)
            num_tokens = count_tokens(encoding ,text)
 
            try:    
                ## Generar preguntas con respuesta de si o no
              
                for qt in self.questions_types:
                    num_questions = self.get_num_questions(qt, num_tokens)
                    questions = self.generate_questions(text, qt, num_questions = num_questions)
                    #if abs(num_questions - len(questions)) > 3:
                    #    print(f"El numero de preguntas solicitadas y generados son diferentes: solcitadas preguntas={num_questions}, generadas preguntas={len(questions)}")
                    #    raise Exception("El numero de preguntas solicitadas y generados son diferentes")
                                
                    questions = self.filter_questions(questions)
                    total_questions += len(questions)
                    #print("\nFinal Questions:", questions)
                    questions_generated.append({"document": file_text, "type":  QuestionType(qt).name.lower(), "questions": questions})
                    time.sleep(10)
                    progress_bar.set_postfix({"total_preguntas": total_questions})
                    progress_bar.update(1 / len(self.questions_types))

                #progress_bar.set_postfix({"total_preguntas": total_questions})
                #progress_bar.update(1)
                    
                ## 
            except Exception as e:
                save_json("./", "questions_generated", questions_generated)
                raise Exception(e)
            
           
            time.sleep(5)
        #print(f"\nUn total de {len(questions_generated)} han sido generdas")
        save_json("./", "questions_generated", questions_generated)


    def format_response_to_json(self, response_questions):
        format_json = """{"preguntas": ["pregunta 1 generada", "pregunta 2 generada", ...]}"""

        prompt = f"""
        Tu tarea es proporcionar la lista de preguntas de abajo delimitada por tres comillas invertidas en el siguente formato: {format_json} 
        Asegúrate de copiar cada una de las preguntas sin su enumeración en el formato indicado anteriormente y no omitas ninguna pregunta.
        Lista de preguntas: 
        ```{response_questions}```
        """
        messages =  [{'role':'user', 'content':prompt}]
        #print("format_response_to_json prompt: ", prompt)
        response = get_completion_from_messages(messages, temperature=0)
        #print("format_response_to_json response:", response)
        resp_json = format_response_json(response)
        print("resp_json:", resp_json)
        return resp_json

    def filter_questions(self, questions):
        questions = [ q for q in questions if "presente reglamento" not in q.lower() ]
        return questions

    def extract_questions_from_response(self, response):
        resp_json = self.format_response_to_json(response)
        #print("resp_json:", resp_json)
        questions = resp_json["preguntas"]
        return questions
    
    def extract_questions_from_response_regex(self, response):
        patron = r'\d+\.\s(¿[^\?]+?\?)'
        preguntas = re.findall(patron, response)
        return preguntas


    def generate_questions(self, text, question_type, num_questions = 30):
        prompt = get_prompt_gen_questions(text, question_type, num_questions)
        #print("prompt:", prompt)
        messages =  [{'role':'user', 'content':prompt}]
        response = get_completion_from_messages(messages, temperature=0, model= "gpt-4-1106-preview")
        print("response:", response)
        questions = self.extract_questions_from_response_regex(response)
        print("Total de preguntas generadas:", len(questions))
        if abs(num_questions - len(questions)) > 3:
            print("Faltan preguntas")
            content = prompt + "\n" + response
            messages =  [{'role':'user', 'content':content}]
            response = get_completion_from_messages(messages, temperature=0, model="gpt-4-1106-preview")
            next_questions = self.extract_questions_from_response_regex(response)
            print("Total de preguntas generadas:", len(next_questions))
            questions  = questions + next_questions
        print("Total de preguntas extraidas:", len(questions))
        #print("response:", response)
        #resp_json = format_response_json(response)
        #questions = resp_json["preguntas"]
        return questions
    
    #def filter_questions(self, questions):
    #    prompt = get_prompt_filter_questions(questions)
    #    messages =  [{'role':'user', 'content':prompt}]
    #    response = get_completion_from_messages(messages, temperature=0)
    #    resp_json = format_response_json(response)
    #    questions = resp_json["preguntas"]
    #    return questions

if __name__ == "__main__":
    questions_generator = QuestionGenerator(dir_documents = "./documentos/reglamento_matricula", 
                                        questions_types = [#QuestionType.YES_OR_NOT_ANSWER, 
                                                           QuestionType.FACTOID])
 
    questions_generator.run()

#save_json("./", "questions_generated", questions_generated)
