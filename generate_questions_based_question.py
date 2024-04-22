from utils import load_json, get_completion_from_messages, list_json_to_txt
from dotenv import load_dotenv
import openai
import os
import re
import math
def set_openai_key():
    API_KEY = os.getenv("API_KEY")
    openai.api_key = API_KEY

load_dotenv()

set_openai_key()

questions_topics = load_json("./refined_questions_generated.json")
# Informacion: ```{context}```

def generate_questions_based_questions_7_2(questions, context):
    list_questions = list_json_to_txt(questions, numeric=True)
    prompt = f"""
Tu tarea consiste en crear 12 preguntas únicas y específicas para cada una de las siguientes preguntas. Las preguntas generadas deben basarse en la información relacionada con la pregunta original, que esté explícitamente descrita y bien desarrollada dentro del texto delimitado por tres comillas invertidas. Es importante que las preguntas busquen de manera directa y específica obtener más detalles o información concreta sobre el tema o puntos relevantes mencionados en cada pregunta original, sin desviarse del mismo. Además, es esencial que las preguntas mantengan coherencia con los conceptos y contexto establecido en la información delimitada por tres comillas invertidas.
Evita mencionar tablas o articulos.

Lista de preguntas:
{list_questions}
Información: ```{context}```

Presenta las 12 preguntas únicas basadas en cada pregunta original de la siguiente manera:

Pregunta Original 1: [Aqui la pregunta original 1]
1. [Aquí la pregunta 1 basada en la primer pregunta original]
2. [Aquí la pregunta 2 basada en la primer pregunta original]
...
12. [Aquí la pregunta 12 basada en la primer pregunta original]

Pregunta Original 2: [Aqui la pregunta original 2]
1. [Aquí la pregunta 1 basada en la segunda pregunta original]
2. [Aquí la pregunta 2 basada en la segunda pregunta original]
...
12. [Aquí la pregunta 12 basada en la segunda pregunta original]

Pregunta Original 3: [Aqui la pregunta original 3]
1. [Aquí la pregunta 1 basada en la tercer pregunta original]
2. [Aquí la pregunta 2 basada en la tercer pregunta original]
...
12. [Aquí la pregunta 12 basada en la tercer pregunta original]
...
"""
    messages = [
    {"role": "user", "content": prompt}
    ]
    
    response = get_completion_from_messages(
        messages,
        #model="gpt-3.5-turbo-0613"
        #model="gpt-3.5-turbo-instruct",
        #chat=False
        )
    print("\nResponse:", response)

def generate_questions_based_questions_7_3(questions, context):
    list_questions = list_json_to_txt(questions, numeric=True)
    prompt = f"""Tu tarea consiste en generar 12 preguntas únicas y especificas para cada una de las siguientes preguntas, compliendo con los siguientes criterios.
1. Las preguntas generadas para cada pregunta deben basarse en la informacion relacionada con la pregunta original que este explicitamente descrita dentro de la informacion delimitada en tres comillas invertidas.
2. Las nuevas preguntas deben ser relevantes para estudiantes de la Facultad de Ciencias de la Univeridad Nacional de Ingenieria.
3. Es importante que las preguntas generadas busquen de manera directa y especifica obtener más detalles o información específica sobre el tema o puntos relevantes mencionados en cada pregunta original, sin desviarse del mismo
4. Es esencial que las preguntas generadas mantengan coherencia con los conceptos e información establecida en la texto delimitada por tres comillas invertidas.

Lista de preguntas:
{list_questions}
Información: ```{context}```

Presenta las 12 preguntas únicas basadas en cada pregunta original de la siguiente manera:

Pregunta Original 1: [Aqui la pregunta original 1]
1. [Aquí la pregunta 1 basada en la primer pregunta original]
2. [Aquí la pregunta 2 basada en la primer pregunta original]
...
12. [Aquí la pregunta 12 basada en la primer pregunta original]

Pregunta Original 2: [Aqui la pregunta original 2]
1. [Aquí la pregunta 1 basada en la segunda pregunta original]
2. [Aquí la pregunta 2 basada en la segunda pregunta original]
...
12. [Aquí la pregunta 12 basada en la segunda pregunta original]
...
"""
    messages = [
    {"role": "user", "content": prompt}
    ]
    
    response = get_completion_from_messages(
        messages,
        model="gpt-3.5-turbo-0613"
        #model="gpt-3.5-turbo-instruct",
        #chat=False
        )
    print("\nResponse:", response)
    
    return prompt

def generate_questions_based_questions_7_1(questions, context):
    list_questions = list_json_to_txt(questions, numeric=True)
    prompt = f"""
Tu tarea consiste en generar 12 preguntas únicas y especificas para cada una de las siguientes preguntas, las preguntas generadas deben basarse en la informacion relacionada con la pregunta original que este explicitamente descrita dentro de la informacion delimitada en tres comillas invertidas y ser relevantes para estudiantes de la Facultad de Ciencias de la Univeridad Nacional de Ingenieria. Es importante que las preguntas busquen de manera directa y especifica obtener más detalles o información específica sobre el tema o puntos relevantes mencionados en cada pregunta original, sin desviarse del mismo. Además, es esencial que las preguntas mantengan coherencia con los conceptos y contexto establecido en la información delimitada por tres comillas invertidas.
Evita mencionar tablas o articulos.
Lista de preguntas:
{list_questions}
Información: ```{context}```

Presenta las 12 preguntas únicas basadas en cada pregunta original de la siguiente manera:

Pregunta Original 1: [Aqui la pregunta original 1]
1. [Aquí la pregunta 1 basada en la primer pregunta original]
2. [Aquí la pregunta 2 basada en la primer pregunta original]
...
12. [Aquí la pregunta 12 basada en la primer pregunta original]

Pregunta Original 2: [Aqui la pregunta original 2]
1. [Aquí la pregunta 1 basada en la segunda pregunta original]
2. [Aquí la pregunta 2 basada en la segunda pregunta original]
...
12. [Aquí la pregunta 12 basada en la segunda pregunta original]
...
"""
    messages = [
    {"role": "user", "content": prompt}
    ]
    
    response = get_completion_from_messages(
        messages,
        model="gpt-3.5-turbo-0613"
        #model="gpt-3.5-turbo-instruct",
        #chat=False
        )
    print("\nResponse:", response)

def generate_questions_based_questions_7(questions, context):
    list_questions = list_json_to_txt(questions, numeric=True)
    prompt = f"""

Tu tarea consiste en generar 12 preguntas únicas para cada una de las siguientes preguntas, las preguntas generdas deben basarse respectivamente en cada pregunta original y ser relevantes para estudiantes de la Facultad de Ciencias de la Univeridad Nacional de Ingenieria. Es importante que las preguntas busquen obtener más detalles o información específica sobre el tema o puntos relevantes mencionados en cada pregunta original, sin desviarse del mismo. Además, es esencial que las preguntas mantengan coherencia con los conceptos y contexto establecido en la información delimitada por tres comillas invertidas.

Lista de preguntas:
{list_questions}
Información: ```{context}```

Presenta las 12 preguntas únicas basadas en cada pregunta original de la siguiente manera:

Pregunta Original 1: [Aqui la pregunta original 1]
1. [Aquí la pregunta 1 basada en la primer pregunta orignal]
2. [Aquí la pregunta 2 basada en la primer pregunta orignal]
...
12. [Aquí la pregunta 12 basada la primer pregunta orignal]

Pregunta Original 2: [Aqui la pregunta original 2]
1. [Aquí la pregunta 1 basada en la primer pregunta orignal]
2. [Aquí la pregunta 2 basada en la primer pregunta orignal]
...
12. [Aquí la pregunta 12 basada la primer pregunta orignal]
...
"""
    messages = [
    {"role": "user", "content": prompt}
    ]
    
    response = get_completion_from_messages(
        messages,
        #model="gpt-3.5-turbo-0613"
        model="gpt-3.5-turbo-instruct",
        chat=False
        )
    print("\nResponse:", response)

def generate_questions_based_questions_6(question, context):
    prompt = f"""
Tu tarea consiste en generar 8 preguntas únicas basadas en la pregunta delimitada por corchetes angulares. Ten en cuenta que las preguntas se presentan en el contexto de las normas, procedimientos o procesos de matrícula para estudiantes universitarios de la Facultad de Ciencias de la Universidad Nacional de Ingeniería. Es importante que las preguntas busquen obtener más detalles o información específica los puntos relevantes mencionados en la pregunta original, sin desviarse del mismo. Además, es esencial que las preguntas mantengan coherencia con los conceptos y contexto establecido en la información delimitada por tres comillas invertidas.

Pregunta: <{question}>
Información: {context}

Presenta las 8 preguntas basadas en la pregunta original de la siguiente manera:
1. [Aquí la pregunta 1]
2. [Aquí la pregunta 2]
...
"""
    messages = [
    {"role": "user", "content": prompt}
    ]
    
    response = get_completion_from_messages(
        messages,
        model="gpt-3.5-turbo-0613")
    print("\nResponse:", response)

def generate_questions_based_questions_5(question, context):
    prompt = f"""
Tu tarea consiste en generar 8 preguntas unicas basadas en la pregunta delimitada por corchetes angulares.
Ten en cuenta que las preguntas se presentan en el contexto de las normas, procedimientos o procesos de matrícula para estudiantes universitarios de la Facultad de Ciencias de la Universidad Nacional de Ingeniería.
Es importante que las las preguntas busquen obtener más detalles o información específica sobre el tema o puntos relevantes mencionado en la pregunta original, sin desviarse del mismo.
Es importante que las preguntas mantengan coherencia con los conceptos y contexto establecido en la informacion delimitado por tres comillas invertidas.
Pregunta: <{question}>
Informacion: ```{context}```
Presenta las 8 preguntas basadas en la pregunta orginal, de la siguiente manera:
1. [Aquí la pregunta 1]
2. [Aquí la pregunta 2]
...
"""     
    messages = [
    {"role": "user", "content": prompt}
    ]
    
    response = get_completion_from_messages(
        messages,
        model="gpt-3.5-turbo-0613")
    print("\nResponse:", response)

def generate_questions_based_questions_4(question, context):
    prompt = f"""
Tu tarea consiste en generar 8 preguntas unicas basadas en la pregunta delimitada por corchetes angulares.
Ten en cuenta que las preguntas se presentan en el contexto de las normas, procedimientos o procesos de matrícula para estudiantes universitarios de la Facultad de Ciencias de la Universidad Nacional de Ingeniería.
Asegurate que las preguntas cubran exclusivamente solo los puntos relevantes mencionado en la pregunta delimitada por corchetes angulares y que tenga sentido segun la informacion delimitado por tres comillas invertidas.

Pregunta: <{question}>
Informacion: ```{context}```

Presenta las 8 preguntas basadas en la pregunta orginal, de la siguiente manera:
1. [Aquí la pregunta 1]
2. [Aquí la pregunta 2]
...
"""     
    messages = [
    {"role": "user", "content": prompt}
    ]
    
    response = get_completion_from_messages(
        messages,
        model="gpt-3.5-turbo-0613")
    print("\nResponse:", response)

def generate_questions_based_questions_3(question):
    prompt = f"""
Tu tarea consiste en generar 10 preguntas unicas basadas en pregunta delimitada por tres comillas invertidas.
Ten en cuenta que las preguntas se presentan en el contexto de las normas, procedimientos o procesos de matrícula para estudiantes universitarios de la Facultad de Ciencias de la Universidad Nacional de Ingeniería.
Asegurate que las preguntas cubran todos los puntos relevantes mencionado en la pregunta delimitada por tres comillas invertidas.

Pregunta: ```{question}```

Presenta las 10 preguntas basadas en la pregunta orginal, de la siguiente manera:
1. [Aquí la pregunta 1]
2. [Aquí la pregunta 2]
...
"""     
    messages = [
    {"role": "user", "content": prompt}
    ]
    
    response = get_completion_from_messages(
        messages,
        model="gpt-3.5-turbo-0613")
    print("\nResponse:", response)


def generate_questions_based_questions_1(question):
    prompt = f"""
Imagina que eres un estudiante universitario que necesita obtener información sobre la pregunta delimitada por tres comillas invertidas. 
Tu tarea es generar 8 formas únicas y originales de consultar esta pregunta. 
Evita repetir las mismas palabras en tus consultas para agregar variedad y creatividad.

La pregunta es: ```{question}```

Por favor, presenta tus 8 consultas de manera diferente y creativa, de la siguiente manera:

1. [Consulta Creativa 1]
2. [Consulta Creativa 2]
...
"""     
    messages = [
    {"role": "user", "content": prompt}
    ]
    
    response = get_completion_from_messages(
        messages,
        model="gpt-3.5-turbo-0613")
    print("\nResponse:", response)

def generate_questions_based_questions_1_2(question):
    prompt = f"""
Tu tarea es proponer 8 formas únicas en las que un estudiante universitario podría consultar la pregunta delimitada por tres comillas invertidas. Evita la repetición de palabras en las consultas. 
La pregunta es: {question}

Presenta las 8 maneras distintas de consulta de la siguiente manera:

1.[Consulta 1]
2.[Consulta 2]
"""     
    messages = [
    {"role": "user", "content": prompt}
    ]
    
    response = get_completion_from_messages(
        messages,
        model="gpt-3.5-turbo-0613")
    print("\nResponse:", response)
        
def generate_questions_based_questions_1_1(question):
    prompt = f"""
Tu tarea consiste en generar 8 maneras diferentes y únicas que un estudiante universitario podria usar para consultar la pregunta delimitada por tres comillas invertidas
Evita repetir las mismas palabras en las consultas
Pregunta: ```{question}```

Presenta las 8 maneras diferentes y únicas de consultar la pregunta, de la siguiente manera:
1. [Aquí la Forma 1 de consulta]
2. [Aquí la Forma 2 de consulta]
...
"""     
    messages = [
    {"role": "user", "content": prompt}
    ]
    
    response = get_completion_from_messages(
        messages,
        model="gpt-3.5-turbo-0613")
    print("\nResponse:", response)

def generate_questions_based_questions_1_prev(question):
    prompt = f"""
Tu tarea consiste en generar 10 maneras diferentes y únicas de consultar la pregunta delimitada por tres comillas invertidas, la cual se presenta en el contexto de las normas, procedimientos o procesos de matrícula de la Facultad de Ciencias de la Universidad Nacional de Ingeniería.
Prioriza utilizar la perspectiva de un estudiante universitario en búsqueda de información o asesoramiento.
Asegurate que cada manera de consultar se base estrictamente en lo descrito en la pregunta original

Pregunta: ```{question}```

Presenta las 10 maneras diferentes y únicas de consultar la pregunta, de la siguiente manera:
1. [Aquí la Forma 1 de consulta]
2. [Aquí la Forma 2 de consulta]
...
"""     
    messages = [
    {"role": "user", "content": prompt}
    ]
    
    response = get_completion_from_messages(
        messages,
        model="gpt-3.5-turbo-0613")
    print("\nResponse:", response)

def generate_questions_based_questions_1_v1(question):
    prompt = f"""
Tu tarea consiste en generar 10 consultas distintas y únicas basado en la pregunta delimitada por tres comillas invertidas
Prioriza utilizar la perspectiva de un estudiante en búsqueda de información o asesoramiento.

Pregunta: ```{question}```

Presenta las 10 consultas distintas y únicas, de la siguiente manera:
1. [Aquí la Forma 1 de consulta]
2. [Aquí la Forma 2 de consulta]
...
"""     
    messages = [
    {"role": "user", "content": prompt}
    ]
    
    response = get_completion_from_messages(messages)
    print("\nResponse:", response)


def generate_questions_based_questions_2_v2(question):
    prompt = f"""
Tu tarea consiste en generar cinco consultas distintas y únicas que un estudiante universitario podría utilizar para obtener información o asesoramiento basando en la pregunta a continuación. Prioriza utilizar la perspectiva de un estudiante en búsqueda de información o asesoramiento.
pregunta: {question}
Presenta las 10 formas diferentes y únicas de consultarla, de la siguiente manera:
1. [Aquí la Forma 1 de consulta]
2. [Aquí la Forma 2 de consulta]
...
"""      
    messages = [
    {"role": "user", "content": prompt}
    ]
    
    response = get_completion_from_messages(messages)
    print("\nResponse:", response)




def generate_questions_based_questions_2_v1(question):
    prompt = f"""
Tu tarea es basado en la pregunta a continuacion, es generar 6 maneras distintas y unicas de consultar dicha pregunta inventando situaciones o contexto unicos en un donde un estudiante universitario desee obtener dicha información o asesoramiento.
Prioriza utilizar la perspectiva de un estudiante de faculta de ciencias de la universidad nacional de ingenieria en búsqueda de información o asesoramiento y el cual describe su situacion o contexto al momento de manistar su consulta.
Asegurate que las situaciones y contextos esten estrictamente realacionado con lo descrito en la pregunta original ademas que tengan sentido en el contexto de la Facultad de Ciencias de la Universidad Nacional de Ingenieria.
Pregunta: {question}

Presenta las 6 formas diferentes y únicas de consultar la pregunta, junto con las situaciones o contextos unicos, de la siguiente manera:
1. Situacion: [Aqui una breve descripcion de las situacion o contexto del estudiante]
Pregunta: [Aqui la pregunta formulada desde la perspectiva del estudiante el cual expone su situacion o contexto y su consulta dentro del mismo mensaje]
2. Situacion: [Aqui una breve descripcion de las situacion o contexto del estudiante]
Pregunta: [Aqui la pregunta formulada desde la perspectiva del estudiante el cual expone su situacion o contexto y su consulta dentro del mismo mensaje]
...
"""      
    messages = [
    {"role": "user", "content": prompt}
    ]
    
    response = get_completion_from_messages(messages)
    print("\nResponse:", response)

def generate_questions_based_questions_2_v3(question):
    prompt = f"""
Tu tarea es generar 6 maneras distintas y únicas de consultar la pregunta delimitada entre tres comillas invertidas, la cual se presenta en el contexto de las normas, procedimientos o procesos de matrícula de la Facultad de Ciencias de la Universidad Nacional de Ingeniería. Para ello, inventa situaciones o contextos únicos donde un estudiante universitario desee obtener dicha información o asesoramiento.
Asegurate que las situaciones y contextos esten estrictamente realacionado con lo descrito en la pregunta original ademas que tengan sentido en el contexto de las normas, procedimientos o procesos de matrícula de la Facultad de Ciencias de la Universidad Nacional de Ingenieria.

Pregunta: ```{question}```

Presenta las 6 formas diferentes y únicas de consultar la pregunta, junto con las situaciones o contextos unicos, de la siguiente manera:
1. Situacion: [Aqui una breve descripcion de las situacion o contexto del estudiante]
Pregunta: [Aqui la pregunta formulada desde la perspectiva del estudiante el cual expone su situacion o contexto y su consulta dentro del mismo mensaje]
2. Situacion: [Aqui una breve descripcion de las situacion o contexto del estudiante]
Pregunta: [Aqui la pregunta formulada desde la perspectiva del estudiante el cual expone su situacion o contexto y su consulta dentro del mismo mensaje]
...
"""      
    messages = [
    {"role": "user", "content": prompt}
    ]
    
    response = get_completion_from_messages(messages)
    print("\nResponse:", response)


def generate_questions_based_questions_2(question, answer=""):
    prompt = f"""

Tu tarea es generar 6 maneras distintas y únicas de consultar la pregunta delimitada entre tres comillas invertidas, la cual se presenta en el contexto de las normas, procedimientos o procesos de matrícula de la Facultad de Ciencias de la Universidad Nacional de Ingeniería. Para ello, inventa situaciones o contextos únicos donde un estudiante universitario desee obtener dicha información o asesoramiento. Asegúrate de que las situaciones y contextos estén estrictamente relacionados y tengan sentido con lo descrito en la pregunta original y su respuesta.
Pregunta: ```{question}```
Respuesta: ```{answer}```

Presenta las 6 formas diferentes y únicas de consultar la pregunta, junto con las situaciones o contextos unicos, de la siguiente manera:
1. Situacion: [Aqui una breve descripcion de las situacion o contexto del estudiante]
Pregunta: [Aqui la pregunta formulada desde la perspectiva del estudiante el cual expone su situacion o contexto y su consulta dentro del mismo mensaje]
2. Situacion: [Aqui una breve descripcion de las situacion o contexto del estudiante]
Pregunta: [Aqui la pregunta formulada desde la perspectiva del estudiante el cual expone su situacion o contexto y su consulta dentro del mismo mensaje]
...
"""      
    messages = [
    {"role": "user", "content": prompt}
    ]
    
    response = get_completion_from_messages(
        messages,
        model="gpt-3.5-turbo-0613")
    print("\nResponse:", response)

def extracts_questions_basades(texto):
    # Expresión regular para dividir el texto en bloques de preguntas para cada pregunta orignal
    patron_bloque = r"(Pregunta Original \d+:.*?)((?=Pregunta Original \d+:)|$)"
    # Buscar todos los bloques de preguntas en el texto
    bloques_preguntas = re.findall(patron_bloque, texto, re.DOTALL)

    # Iterar sobre cada bloque de preguntas
    groups_related_questions = []
    for bloque in bloques_preguntas :
        titulo, preguntas_texto = bloque
        #print(f"\nGrupo {i}: {titulo.strip()}")
        
        # Expresión regular para encontrar las preguntas dentro del bloque
        patron_pregunta = r"\d+\.\s(.*?)\?"
        
        # Buscar todas las preguntas dentro del bloque
        preguntas = re.findall(patron_pregunta, preguntas_texto, re.DOTALL)
        
        groups_related_questions.append(preguntas)
        
    return groups_related_questions   

for questions_about_topic in questions_topics[:1]:
    #question_answer_pairs = questions_about_topic["question_answer_pairs"][0:3]
    #questions = [qt["question"] for qt in question_answer_pairs]
    context = questions_about_topic["context"]
    questions = questions_about_topic["questions"][0:3]
    generate_questions_based_questions_7_3(questions, context)

    for qa in questions[0:3]:
        print("\nquestion:", qa)
        #print("\nanswer:", qa["answer"])
        #generate_questions_based_questions_2(qa["question"], qa["answer"])
        #generate_questions_based_questions_6(qa["question"], context
        #
    questions = questions_about_topic["questions"][3:6]
    generate_questions_based_questions_7_3(questions, context)

    for qa in questions[3:6]:
        print("\nquestion:", qa)                                     
    
    questions = questions_about_topic["questions"][6:9]
    generate_questions_based_questions_7_3(questions, context)

    for qa in questions[6:9]:
        print("\nquestion:", qa) 
    