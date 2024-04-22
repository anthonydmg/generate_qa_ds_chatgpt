from utils import load_json, get_completion_from_messages, list_json_to_txt, save_json
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


class DerivedQuestionsGenerator:
    def __init__(self, path_orignal_questions) -> None:
        self.original_questions_about_topics = load_json(path_orignal_questions) 
    
    
    def get_prompt_gen_based_questions_original(self, questions, context, num_questions = 8):
        list_questions = list_json_to_txt(questions)
        prompt = \
f"""Tu tarea consiste en generar {num_questions} preguntas únicas para cada una de las siguientes preguntas, las preguntas generadas deben basarse respectivamente en cada pregunta original y ser relevantes para estudiantes de la Facultad de Ciencias de la Univeridad Nacional de Ingenieria. Es importante que las preguntas busquen obtener más detalles o información específica sobre el tema o puntos relevantes mencionados en cada pregunta original, sin desviarse del mismo. Además, es esencial que las preguntas mantengan coherencia con los conceptos y contexto establecido en la información delimitada por tres comillas invertidas.

Lista de preguntas:
{list_questions}

Información: ```{context}```

Presenta las {num_questions} preguntas únicas basadas en cada pregunta original de la siguiente manera:

Pregunta Original 1: [Aqui la pregunta original 1]
1. [Aquí la pregunta 1 basada en la primer pregunta orignal]
2. [Aquí la pregunta 2 basada en la primer pregunta orignal]
...
{num_questions}. [Aquí la pregunta 8 basada la primer pregunta orignal]

Pregunta Original 2: [Aqui la pregunta original 2]
1. [Aquí la pregunta 1 basada en la segunda pregunta orignal]
2. [Aquí la pregunta 2 basada en la segunda pregunta orignal]
...
{num_questions}. [Aquí la pregunta 8 basada la segunda pregunta orignal]
..."""
        return prompt
# Los cuales deben
# con respecto al informacion y el contexto en las que se consultan
# _new
#     Los detalles o información específica sobre el tema o los puntos relevantes relacionados con la pregunta original, a los que se refiere la pregunta adicional, deben ser explícitamente descritos y bien desarrollados dentro de la información delimitada por tres comillas invertidas.
#   - Es importante que las preguntas se formulen de manera clara, completa y especifica
#    - Las preguntas deben ser relevantes para estudiantes de la Facultad de Ciencias de la Univeridad Nacional de Ingenieria.
#    - Las preguntas deben mentener coherencia con los conceptos y la informacion delimitada por tres comillas invertidas.
#""" sin desviarte de estos, para cada una de las siguientes preguntas.
#Considera los siguiente al formular las preguntas:
#    - Las preguntas adicionales deben buscar obtener más detalles o información específica sobre el tema o los puntos relevantes mencionados en la pregunta original, que se encuentren explícitamente descritos y desarrollados dentro de la información delimitada por tres comillas invertidas.
#    - Es importante que las preguntas adicionales para cada pregunta original se centren en el tema o los puntos relevantes mencionados en dicha pregunta sin desviarte de estos.
# """
# Es crucial que las preguntas adicionales se mantengan enfocadas en el tema mencionado en la pregunta original, se formulen de manera clara y específica, y sean relevantes o de interés para los estudiantes de la Facultad de Ciencias de la Universidad Nacional de Ingeniería.
# Es crucial que las preguntas adicionales se mantengan enfocadas en el tema mencionado en la pregunta original, se formulen de manera clara, específica, y sean relevantes o de interés para los estudiantes de la Facultad de Ciencias de la Universidad Nacional de Ingeniería.
    
    def get_prompt_gen_based_questions_only_question_1(self, question, context,  num_questions = 8):
        prompt = \
f"""
Tu tarea consiste en generar {num_questions} preguntas adicionales enfocadas en el exclusivamente en el tema mencionado en la pregunta delimitada por llaves angulares. Estas nuevas preguntas deben abordar detalles e información específica relacionada directamente con el tema de la pregunta original, los cuales deben estar explícitamente descritos y bien desarrollados dentro del texto delimitado por tres comillas invertidas.

Pregunta: <{question}>
Información: ```{context}```

Presenta las {num_questions} preguntas  de la siguiente manera:

1. [Aquí la pregunta 1 enfocada exclusivamente en el tema mencionado en la pregunta orignal]
2. [Aquí la pregunta 2 enfocada exclusivamente en el tema mencionado en la pregunta orignal]
...
"""
        return prompt
    
    #Es importante que las preguntas se formulen de manera clara y especifica con respecto al tema y contexto en las que se consultan.
#Es crucial que las preguntas adicionales se mantengan enfocadas en el tema mencionado en la pregunta original y busquen obtener más detalles o información específica explícitamente descritos y desarrollados dentro de la información delimitada por tres comillas invertidas.

# y basadas en la informacion delimitada por llaves comillas invertidas.
#Dichas preguntas deben buscar obtener más detalles o información específica relacionada con la pregunta delimitada por llaves angulares que esten explícitamente descritos y desarrollados dentro de la información delimitada por tres comillas invertidas.
# Información: ```{context}```
    
    def generate_questions_based_one_question(self, question, context):
        prompt = f"""Tu tarea consiste en generar 12 preguntas únicas y especificas para la siguiente pregunta, compliendo con los siguientes criterios.
1. Las preguntas generadas deben basarse en la informacion relacionada con la pregunta original que este explicitamente descrita dentro de la informacion delimitada en tres comillas invertidas.
2. Las nuevas preguntas deben ser relevantes para estudiantes de la Facultad de Ciencias de la Univeridad Nacional de Ingenieria.
3. Es importante que las preguntas generadas busquen de manera directa y especifica obtener más detalles o información específica sobre el tema o puntos relevantes mencionados en la pregunta original, sin desviarse del mismo
4. Es esencial que las preguntas generadas mantengan coherencia con los conceptos e información establecida en la texto delimitada por tres comillas invertidas.

Pregunta:
{question}
Información: ```{context}```

Presenta las preguntas generadas para cada la pregunta original de la siguiente manera:

Pregunta Original: [Aqui la pregunta original]
1. [Aquí la pregunta 1 basada en la pregunta original]
2. [Aquí la pregunta 2 basada en la pregunta original]
...
12. [Aquí la pregunta 12 basada en la pregunta original]
"""
        return prompt
        
    def generate_questions_based_questions(self, questions, context):
        list_questions = list_json_to_txt(questions, numeric=True)
        num_original_questions = len(questions)
        prompt = f"""Tu tarea consiste en generar 12 preguntas únicas y especificas para cada una de las siguientes preguntas, compliendo con los siguientes criterios.
1. Las preguntas generadas para cada pregunta deben basarse en la informacion relacionada con la pregunta original que este explicitamente descrita dentro de la informacion delimitada en tres comillas invertidas.
2. Las nuevas preguntas deben ser relevantes para estudiantes de la Facultad de Ciencias de la Univeridad Nacional de Ingenieria.
3. Es importante que las preguntas generadas busquen de manera directa y especifica obtener más detalles o información específica sobre el tema o puntos relevantes mencionados en cada pregunta original, sin desviarse del mismo
4. Es esencial que las preguntas generadas mantengan coherencia con los conceptos, secuencia de eventos e información establecida en la texto delimitada por tres comillas invertidas.

Lista de preguntas:
{list_questions}
Información: ```{context}```

Presenta las preguntas generadas para cada una de las {num_original_questions} preguntas originales de la siguiente manera:

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
   
        return prompt
# 98.9%
    def generate_questions_based_questions_final(self, questions, context):
            list_questions = list_json_to_txt(questions, numeric=True)
            num_original_questions = len(questions)
            prompt = f"""Tu tarea consiste en generar 12 preguntas únicas y especificas para cada una de las siguientes preguntas, compliendo con los siguientes criterios.
    1. Las preguntas generadas para cada pregunta deben basarse en la informacion relacionada con la pregunta original que este explicitamente descrita dentro de la informacion delimitada en tres comillas invertidas.
    2. Las nuevas preguntas deben ser relevantes para estudiantes de la Facultad de Ciencias de la Univeridad Nacional de Ingenieria.
    3. Es importante que las preguntas generadas busquen de manera directa y especifica obtener más detalles o información específica sobre el tema o puntos relevantes mencionados en cada pregunta original, sin desviarse del mismo
    4. Es esencial que las preguntas generadas mantengan coherencia con los conceptos e información establecida en la texto delimitada por tres comillas invertidas.

    Lista de preguntas:
    {list_questions}
    Información: ```{context}```

    Presenta las preguntas generadas para cada una de las {num_original_questions} preguntas originales de la siguiente manera:

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
    
            return prompt

    def get_prompt_gen_based_questions(self, question, context,  num_questions = 8):
        prompt = \
f"""
Tu tarea consiste en generar {num_questions} preguntas adicionales el tema o puntos relevantes mencionados en la pregunta delimitada por llaves angulares, que busquen obtener más detalles o información específica sobre estos, sin desviarse del mismo. Dichos detalles o informacion especifica deben estar explícitamente descritos y desarrollados dentro de la información delimitada por tres comillas invertidas.
Pregunta: <{question}>
Información: ```{context}```
"""
        return prompt

    # no esta mal pero aveces se va por el lado que no es
    def get_prompt_gen_based_questions_forma_sin_context(self, question, context,  num_questions = 8):
        prompt = \
f"""
Tu tarea consiste en generar {num_questions} preguntas adicionales basadas en la pregunta delimitada por llaves angulares.
Presenta las {num_questions} preguntas  de la siguiente manera:

Pregunta Original: [Aqui la pregunta original]
1. [Aquí la pregunta 1 basada en la pregunta orignal]
2. [Aquí la pregunta 2 basada en la pregunta orignal]
...
{num_questions}. [Aquí la pregunta {num_questions} basada en la pregunta orignal]

Pregunta: <{question}>

"""
        return prompt
    
    def get_prompt_gen_based_questions_forma6(self, question, context,  num_questions = 8):
        prompt = \
f"""
Tu tarea consiste en generar {num_questions} preguntas adicionales enfocadas exclusivamente en el tema mencionado en la pregunta delimitada por llaves angulares y basadas en la delimitada por llaves angulares.

Presenta las {num_questions} preguntas  de la siguiente manera:

Pregunta Original: [Aqui la pregunta original]
1. [Aquí la pregunta 1 enfocada exclusivamente en el tema mencionado en la pregunta orignal]
2. [Aquí la pregunta 2 enfocada exclusivamente en el tema mencionado en la pregunta orignal]
...
{num_questions}. [Aquí la pregunta {num_questions} enfocada exclusivamente en el tema mencionado en la pregunta orignal]

Pregunta: <{question}>
Información: ```{context}```
"""
        return prompt
    
    def get_prompt_gen_based_questions_only_question_3(self, question, context,  num_questions = 8):
        prompt = \
f"""
Tu tarea consiste en generar {num_questions} preguntas enfocadas exclusivamente en el tema mencionado en la pregunta delimitada por llaves angulares, siguiendo los siguientes pasos
Paso 1.  Determida el tema especifico tratado en la pregunta delimitada por por llaves angulares. Presentalo de la siguiemte manera:
        Tema de la pregunta original: [Aqui el tema de descrito de manera concisa]
Paso 2. Identifica todos los detalles e información específica explícitamente descritas y bien desarrollada dentro de la informacion delimitada por tres comillas invertidas relacionada al tema de la pregunta delimitada por llaves angulares. 
Paso 2.  Genera {num_questions} que aborden todos esos detalles e información específica relacionadas con el tema tratado en la pregunta delimitada por llaves angulares.
Paso 3.  Presenta las {num_questions} preguntas  de la siguiente manera:

Pregunta Original: [Aqui la pregunta original]
1. [Aquí la pregunta 1 enfocada en el tema mencionado en la pregunta orignal]
2. [Aquí la pregunta 2 enfocada en el tema mencionado en la pregunta orignal]
...
{num_questions}. [Aquí la pregunta {num_questions} enfocada en el tema mencionado en la pregunta orignal]

Pregunta: <{question}>
Información: ```{context}```
"""
        return prompt
    
    def get_prompt_gen_based_questions_only_question_2(self, question, context,  num_questions = 8):
        prompt = \
f"""
Tu tarea consiste en generar {num_questions} preguntas enfocadas en el exclusivamente en el tema mencionado en la pregunta delimitada por llaves angulares, siguiendo los siguientes pasos
Paso 1.  Identifica todos los detalles e información específica explícitamente descritas y bien desarrollada dentro de la informacion delimitada por tres comillas invertidas relacionada al tema de la pregunta delimitada por llaves angulares.
Paso 2.  Genera {num_questions} que aborden todos esos detalles e información específica relacinadas con la pregunta delimitada  por llaves angulares.
Paso 3.  Presenta las {num_questions} preguntas  de la siguiente manera:

Pregunta Original: [Aqui la pregunta original]
1. [Aquí la pregunta 1  enfocada en el tema mencionado en la pregunta orignal]
2. [Aquí la pregunta 2  enfocada en el tema mencionado en la pregunta orignal]
...

Pregunta: <{question}>
Información: ```{context}```
"""
        return prompt
    

    def get_prompt_gen_based_questions_forma6(self, questions, context, num_questions = 8):
        list_questions = list_json_to_txt(questions)
        prompt = \
f"""
Tu tarea consiste en generar {num_questions} preguntas adicionales para cada pregunta de la lista, enfocándote en el tema mencionado en la pregunta original y evitando desviaciones, siguiendo los siguientes pasos para cada pregunta de la lista.
Paso 1. Identifica toda los detalles e información específica explícitamente descritas y bien desarrollada dentro de la informacion delimitada por tres comillas invertidas relacionada al tema de la pregunta original.
Paso 2. Genera {num_questions} que aborden todos esos detalles e información específica
Paso 3. Presenta las {num_questions} preguntas adicionales de cada pregunta original de la siguiente manera:

Pregunta Original 1: [Aqui la pregunta original]
1. [Aquí la pregunta 1 adicional enfocada en el tema mencionado en la pregunta orignal]
2. [Aquí la pregunta 2 adicional enfocada en el tema mencionado en la pregunta orignal]
...

Pregunta Original 2: [Aqui la pregunta original]
1. [Aquí la pregunta 1 adicional enfocada en el tema mencionado en la pregunta orignal]
2. [Aquí la pregunta 2 adicional enfocada en el tema mencionado en la pregunta orignal]
...

Pregunta Original 3: [Aqui la pregunta original]
1. [Aquí la pregunta 1 adicional enfocada en el tema mencionado en la pregunta orignal]
2. [Aquí la pregunta 2 adicional enfocada en el tema mencionado en la pregunta orignal]
...

Lista de preguntas
{list_questions}

Información: ```{context}```
"""
        return prompt
    
    def get_prompt_gen_based_questions_forma5(self, questions, context, num_questions = 8):
        list_questions = list_json_to_txt(questions)
        prompt = \
f"""
Tu tarea consiste en generar {num_questions} preguntas adicionales para cada pregunta de la lista, enfocándote en el tema mencionado en la pregunta original y evitando desviaciones. Estas nuevas preguntas deben consultar sobre detalles o solicitar información específica explícitamente descritas y bien desarrollada dentro de la informacion delimitada por tres comillas invertidas relacionadas al tema de la pregunta original.

Lista de preguntas
{list_questions}

Información: ```{context}```

Presenta las {num_questions} preguntas adicionales de cada pregunta original de la siguiente manera:

Pregunta Original 1: [Aqui la pregunta original 1]
1. [Aquí la pregunta 1 adicional enfocada en el tema mencionado en la primer pregunta orignal]
2. [Aquí la pregunta 2 adicional enfocada en el tema mencionado en la primer pregunta orignal]
...
{num_questions}. [Aquí la pregunta {num_questions} adicional correspondiente la primer pregunta orignal]

Pregunta Original 2: [Aqui la pregunta original 2]
1. [Aquí la pregunta 1 adicional enfocada en el tema mencionado en la segunda pregunta orignal]
2. [Aquí la pregunta 2 adicional enfocada en el tema mencionado en la segunda pregunta orignal]
...
{num_questions}. [Aquí la pregunta {num_questions} adicional enfocada en el tema mencionado en la segunda pregunta orignal]
...

Pregunta Original 3: [Aqui la pregunta original 3]
1. [Aquí la pregunta 1 adicional enfocada en el tema mencionado en la tercera pregunta orignal]
2. [Aquí la pregunta 2 adicional enfocada en el tema mencionado en la tercera pregunta orignal]
...
{num_questions}. [Aquí la pregunta {num_questions} adicional enfocada en el tema mencionado en la tercera pregunta orignal]
...
"""
        return prompt
    
    def get_prompt_gen_based_questions_forma4(self, questions, context, num_questions = 8):
        list_questions = list_json_to_txt(questions)
        prompt = \
f"""
Tu tarea consiste en generar {num_questions} preguntas adicionales para cada pregunta de la lista que busquen obtener más detalles o información específica sobre el tema o los puntos relevantes mencionados en la pregunta original. Estos detalles o información específica deben estar explícitamente descritos y desarrollados dentro de la información delimitada por tres comillas invertidas.
Es crucial que las preguntas adicionales se mantengan enfocadas en el tema mencionado en la pregunta original y obtener más detalles o información específica explícitamente descritos y desarrollados dentro de la información delimitada por tres comillas invertidas.

Lista de preguntas
{list_questions}

Información: ```{context}```

Presenta las {num_questions} preguntas adicionales de cada pregunta original de la siguiente manera:

Pregunta Original 1: [Aqui la pregunta original 1]
1. [Aquí la pregunta 1 adicional enfocada en el tema mencionado en la primer pregunta orignal]
2. [Aquí la pregunta 2 adicional enfocada en el tema mencionado en la primer pregunta orignal]
...
{num_questions}. [Aquí la pregunta {num_questions} adicional correspondiente la primer pregunta orignal]

Pregunta Original 2: [Aqui la pregunta original 2]
1. [Aquí la pregunta 1 adicional enfocada en el tema mencionado en la segunda pregunta orignal]
2. [Aquí la pregunta 2 adicional enfocada en el tema mencionado en la segunda pregunta orignal]
...
{num_questions}. [Aquí la pregunta {num_questions} adicional enfocada en el tema mencionado en la segunda pregunta orignal]
...

Pregunta Original 3: [Aqui la pregunta original 3]
1. [Aquí la pregunta 1 adicional enfocada en el tema mencionado en la tercera pregunta orignal]
2. [Aquí la pregunta 2 adicional enfocada en el tema mencionado en la tercera pregunta orignal]
...
{num_questions}. [Aquí la pregunta {num_questions} adicional enfocada en el tema mencionado en la tercera pregunta orignal]
...
"""
        return prompt

    
    def get_prompt_gen_based_questions_forma4(self, questions, context, num_questions = 8):
        list_questions = list_json_to_txt(questions)
        prompt = \
f"""
Tu tarea consiste en generar {num_questions} preguntas adicionales que busquen obtener más detalles o información específica sobre el tema o los puntos relevantes mencionados en la pregunta original, que se encuentren explícitamente descritos y desarrollados dentro de la información delimitada por tres comillas invertidas, para cada una de las siguientes preguntas.
Es importante que las preguntas adicionales para cada pregunta de la lista de abajo no se desvien y se enfoquen en el tema mencionado en la pregunta original.
Es importante que las preguntas se formulen de manera clara, directa, completa y especifica y deben ser relevantes para estudiantes de la Facultad de Ciencias de la Univeridad Nacional de Ingenieria.

Lista de preguntas:
{list_questions}

Información: ```{context}```

Presenta las {num_questions} preguntas adicionales de cada pregunta original de la siguiente manera:

Pregunta Original 1: [Aqui la pregunta original 1]
1. [Aquí la pregunta 1 adicional enfocada en el tema de la primer pregunta orignal]
2. [Aquí la pregunta 2 adicional enfocada en el tema de la primer pregunta orignal]
...
{num_questions}. [Aquí la pregunta {num_questions} adicional correspondiente la primer pregunta orignal]

Pregunta Original 2: [Aqui la pregunta original 2]
1. [Aquí la pregunta 1 adicional enfocada en el tema de la segunda pregunta orignal]
2. [Aquí la pregunta 2 adicional enfocada en el tema de la segunda pregunta orignal]
...
{num_questions}. [Aquí la pregunta {num_questions} adicional enfocada en el tema de la segunda pregunta orignal]
...

Pregunta Original 3: [Aqui la pregunta original 3]
1. [Aquí la pregunta 1 adicional enfocada en el tema de la tercera pregunta orignal]
2. [Aquí la pregunta 2 adicional enfocada en el tema de la tercera pregunta orignal]
...
{num_questions}. [Aquí la pregunta {num_questions} adicional enfocada en el tema de la tercera pregunta orignal]
...

"""
        return prompt
    
    def get_prompt_gen_based_questions_forma3(self, questions, context, num_questions = 8):
        list_questions = list_json_to_txt(questions)
        prompt = \
f"""
Tu tarea consiste en generar {num_questions} preguntas adicionales para obtener más detalles o información específica sobre el tema o los puntos relevantes mencionados en la pregunta original, sin desviarte de estos, para cada una de las siguientes preguntas.
Es importante que los detalles o información específica esten explícitamente descritos y bien desarrollados en la información delimitada por tres comillas invertidas.
Es importante que las preguntas se formulen de manera clara, completa y especifica y deben ser relevantes para estudiantes de la Facultad de Ciencias de la Univeridad Nacional de Ingenieria.
Además, es esencial que todas las preguntas mantengan coherencia con los conceptos y la informacion delimitada por tres comillas invertidas.

Lista de preguntas:
{list_questions}

Información: ```{context}```

Presenta las {num_questions} preguntas adicionales de cada pregunta original de la siguiente manera:

Pregunta Original 1: [Aqui la pregunta original 1]
1. [Aquí la pregunta 1 adicional correspondiente a la primer pregunta orignal]
2. [Aquí la pregunta 2 adicional correspondiente a la primer pregunta orignal]
...
{num_questions}. [Aquí la pregunta {num_questions} adicional correspondiente la primer pregunta orignal]

Pregunta Original 2: [Aqui la pregunta original 2]
1. [Aquí la pregunta 1 adicional correspondiente a la segunda pregunta orignal]
2. [Aquí la pregunta 2 adicional correspondiente a la segunda pregunta orignal]
...
{num_questions}. [Aquí la pregunta {num_questions} adicional correspondiente la segunda pregunta orignal]
...

Pregunta Original 3: [Aqui la pregunta original 3]
1. [Aquí la pregunta 1 adicional correspondiente a la tercera pregunta orignal]
2. [Aquí la pregunta 2 adicional correspondiente a la tercera pregunta orignal]
...
{num_questions}. [Aquí la pregunta {num_questions} adicional correspondiente a la tercera pregunta orignal]
...

"""
        return prompt
         
    def get_prompt_gen_based_questions_new2(self, questions, context, num_questions = 8):
        list_questions = list_json_to_txt(questions)
        prompt = \
f"""
Tu tarea consiste en generar {num_questions} preguntas basadas en la pregunta original para cada una de las siguientes preguntas. 
Es importante que las preguntas sean relevantes para estudiantes de la Facultad de Ciencias de la Univeridad Nacional de Ingenieria y busquen obtener más detalles o información específica sobre el tema o puntos relevantes mencionados en cada pregunta original, sin desviarse del mismo. 
Además, es esencial que todas las preguntas mantengan coherencia con los conceptos y la informacion delimitada por tres comillas invertidas.

Lista de preguntas:
{list_questions}

Información: ```{context}```

Presenta las {num_questions} preguntas basadas en cada pregunta original de la siguiente manera:

Pregunta Original 1: [Aqui la pregunta original 1]
1. [Aquí la pregunta 1 basada en la primer pregunta orignal]
2. [Aquí la pregunta 2 basada en la primer pregunta orignal]
...
{num_questions}. [Aquí la pregunta {num_questions} basada la primer pregunta orignal]

Pregunta Original 2: [Aqui la pregunta original 2]
1. [Aquí la pregunta 1 basada en la segunda pregunta orignal]
2. [Aquí la pregunta 2 basada en la segunda pregunta orignal]
...
{num_questions}. [Aquí la pregunta {num_questions} basada la segunda pregunta orignal]
..."""
        return prompt

    def get_prompt_gen_reformulated_questions(self, question):
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
        return prompt

    def extracts_questions_basades(self, texto):
        # Expresión regular para dividir el texto en bloques de preguntas para cada pregunta orignal
        patron_bloque = r"(Pregunta Original \d+:\s+[^\[].*?)((?=Pregunta Original \d+:)|$)"
        # Buscar todos los bloques de preguntas en el texto
        bloques_preguntas = re.findall(patron_bloque, texto, re.DOTALL)

        # Iterar sobre cada bloque de preguntas
        groups_related_questions = []
        for bloque in bloques_preguntas :
            block_texto, _ = bloque
            # pregunta_original = re.search(r'Pregunta Original \d+: (.+?)\n', block_texto).group(1)
            # Expresión regular para encontrar las preguntas dentro del bloque
            patron_pregunta = r'\d+\.\s(¿[^\?]+?\?)'
            
            # Buscar todas las preguntas dentro del bloque
            preguntas = re.findall(patron_pregunta, block_texto, re.DOTALL)
            
            groups_related_questions.append(preguntas)
        return groups_related_questions

    def generate_based_questions(self, questions, context):
        batch_size = 3
        num_questions = len(questions[:4])
        num_batch = math.ceil(num_questions / 3)
        
        new_related_questions = []

        for i in range(num_batch):
            print(f"\nLote {i+1}\n")
            start = i * batch_size
            end = min(num_questions, start + batch_size)
            b_questions = questions[start:end]
            if len(b_questions) > 1:
                prompt = self.generate_questions_based_questions(
                    b_questions, 
                    context, 
                    )
                
                messages = [
                {"role": "user", "content": prompt}
                ]
                
                response = get_completion_from_messages(
                    messages,
                    model="gpt-3.5-turbo-0613"
                    )
                
                print("\nresponse:", response)
                groups_related_questions = self.extracts_questions_basades(response)
            else:
                prompt = self.generate_questions_based_questions(
                    b_questions + [questions[start - 1]], 
                    context, 
                    )
                
                messages = [
                {"role": "user", "content": prompt}
                ]
                
                response = get_completion_from_messages(
                    messages,
                    model="gpt-3.5-turbo-0613"
                    )
                
                print("\nresponse:", response)
                groups_related_questions = self.extracts_questions_basades(response)
                groups_related_questions = groups_related_questions[:1]
               
                
            #print("\ngroups_related_questions:", groups_related_questions)
            if len(groups_related_questions) != len(b_questions):
                raise Exception("Fatan generar preguntas basadas")

            for original_question, related_questions in zip(b_questions, groups_related_questions):
                new_related_questions.append({
                    "original_question": original_question,
                    "context": context,
                    "additional_questions": related_questions
                })
            
        return new_related_questions
    
    def extract_questions_by_list(self, texto):
        patron_pregunta = r'\d+\.\s(¿[^\?]+?\?)'

        # Buscar todas las preguntas en el texto
        preguntas = re.findall(patron_pregunta, texto, re.DOTALL)
        return preguntas

    def generate_reformulated_questions(self, questions):
        reformulated_questions = []
        
        for orignal_question in questions:
            prompt = self.get_prompt_gen_reformulated_questions(orignal_question)
            messages = [
            {"role": "user", "content": prompt}
            ]
            
            response = get_completion_from_messages(
                messages,
                model="gpt-3.5-turbo-0613")
            
            rephrased_questions_by_question = self.extract_questions_by_list(response)
            reformulated_questions.append({
                "orignal_question": orignal_question,
                "rephrased_questions": rephrased_questions_by_question
            })

        return reformulated_questions
            
       
    def run(self):
        all_additional_questions = []
        for questions_about_topic in self.original_questions_about_topics[:2]:
            #question_answer_pairs = questions_about_topic["question_answer_pairs"]
            context = questions_about_topic["context"]
            questions = questions_about_topic["questions"]
            topic = questions_about_topic["topic"]
            #questions = [qt["question"] for qt in question_answer_pairs]
            new_related_questions = self.generate_based_questions(questions, context)
            for adds_questions in new_related_questions:
                adds_questions['topic'] = topic
            
            all_additional_questions.extend(new_related_questions)
        
        save_json("./", "additional_questions", all_additional_questions)


derivedQuestionsGenerator = DerivedQuestionsGenerator(path_orignal_questions= "./questions_generated.json")

derivedQuestionsGenerator.run()

    