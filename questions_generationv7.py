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


def get_prompt_gen_yes_or_not_questions(reglamento, num_questions = 20):
    format_json = """{"preguntas": ["pregunta 1 generada", "pregunta 2 generada", ...]"""
    
    prompt = f"""
Tu tarea es genera al menos {num_questions} preguntas que tengan respuesta directas de 'Sí' o 'No', basadas en la información proporcionada sobre reglamentos académicos de la Facultad de Ciencias de la UNI (delimitada por tres comillas invertidas).
Antes de generar cada pregunta asegurate de cumplir con los siguientes criterios:
   - Las preguntas deben tener respuestas directas de 'Sí' o 'No' basándose en la información proporcionada.
   - Evita citar numerales de artículos en las preguntas.
   - No menciones o cites a tablas especificas en las preguntas.
   - No mencione directamente al reglamento en las preguntas.
   - Enfócate en preguntas relevantes para alumnos, docentes o el público en general que puedan ser respondidas con la información proporcionada.
   - Evita la repetición y asegúrate de crear preguntas únicas de diferentes temas relevantes para usuarios como alumnos, docentes o el público en general que puedan ser respondidas con la información proporcionada.

Finalmente, presenta las {num_questions} preguntas la siguiente manera:
1. pregunta...
2. pregunta...

Fragmento de texto: {reglamento}.
    """
    return prompt



def get_prompt_gen_factoid_questions_v2(reglamento, num_questions = 20):
    print(f"\nNumero de preguntas a crear {num_questions}\n")
    prompt = f"""
Tu tarea es generar al menos {num_questions} de preguntas únicas de diferentes temas relevantes para alumnos encontrados en información proporcionada sobre reglamentos académicos de la Facultad de Ciencias de la UNI (delimitada por tres comillas invertidas)
basadandote en la información proporcionada sobre reglamentos académicos de la Facultad de Ciencias de la UNI (delimitada por tres comillas invertidas). 
Antes de crear una pregunta asegúrate de cumplir estrictamente cada uno de los siguientes criterios:
    - Evita mencionar o citar numerales de artículos específicos en las preguntas.
    - No formules preguntas que requieran identificar el numero de artículos específicos en el reglamento.
    - No crees preguntas que mencionen directamente datos especificos.
    - Concéntrate en preguntas prácticas y relevantes para usuarios como alumnos, docentes o el público en general, que puedan ser respondidas con la información proporcionada.
    - Las preguntas deben fomentar respuestas extensas, basadas en la información proporcionada. 
    - Evita la repetición y asegúrate de crear preguntas únicas de diferentes temas relevantes para usuarios como alumnos, docentes o el público en general, que puedan ser respondidas con la información proporcionada.
 
Finalmente, presenta las {num_questions} preguntas la siguiente manera:
1. pregunta...
2. pregunta...
...

Fragmento de texto: ```{reglamento}```
    """
    return prompt
#     - Concéntrate en preguntas prácticas y relevantes para alumnos de la UNI.

#     - Evita la repetición y asegúrate de crear preguntas prácticas y únicas que aborden diferentes temas relevantes para los alumnos de la UNI, los cuales estén bien desarrollados y descritos en la información proporcionada (delimitada por tres comillas invertidas).

def get_prompt_gen_factoid_questions_v3(reglamento, num_questions = 20):
    print(f"\nNumero de preguntas a crear {num_questions}\n")
    prompt = f"""

Tu tarea consiste en generar al menos {num_questions} preguntas prácticas y únicas que aborden una variedad de temas relevantes para los estudiantes de la Facultad de Ciencias de la Universidad Nacional de Ingeniería, basándote en la información proporcionada (delimitada por tres comillas invertidas). Antes de formular cada pregunta, asegúrate de cumplir estrictamente con los siguientes criterios:
    - Las preguntas deben poder ser respondidas completamente utilizando únicamente la información proporcionada (delimitada por tres comillas invertidas).
    - Evita mencionar o citar artículos específicos.
    - Formula las preguntas sin hacer referencia explícita a ningún reglamento y evita especificar a qué reglamento o texto está relacionada la información.
    - Prioriza generar preguntas más generales y menos específicas.

Finalmente, presenta las {num_questions} preguntas de la siguiente manera:
1. pregunta...
2. pregunta...
...

Fragmento de texto: ```{reglamento}```
    """
    return prompt

def get_prompt_gen_factoid_questions_v4(reglamento, num_questions = 20):
    print(f"\nNumero de preguntas a crear {num_questions}\n")
    prompt = f"""

Tu tarea es generar al menos {num_questions} preguntas únicas que aborden diversos temas relevantes para los estudiantes de la Facultad de Ciencias de la Universidad Nacional de Ingenieria, basadas en la información proporcionada  (delimitada por tres comillas invertidas).
Antes de crear una pregunta asegúrate de cumplir estrictamente cada uno de los siguientes criterios:
    - Las preguntas deben poder ser respondida completamente utilizando únicamente la información proporcionada (delimitada por tres comillas invertidas).
    - Evita mencionar o citar artículos específicos en las preguntas.
    - Formula las preguntas sin hacer referencia explícita a ningún reglamento y evita especificar a qué reglamento está relacionada la información.
    - Prioriza preguntas mas generales y menos especificas.
    - Evita la repetición y asegúrate de crear preguntas prácticas y únicas de diferentes temas relevantes para alumnos de la UNI que esten bien desarrollados y descritos en la información proporcionada (delimitada por tres comillas invertidas).

Finalmente, presenta las {num_questions} preguntas de la siguiente manera:
1. pregunta...
2. pregunta...
...

Fragmento de texto: ```{reglamento}```
    """
    return prompt


def get_prompt_check_response(prompt, response):
    prompt = """ Analiza detalladamente el prompt proveido a continuancion y la respuesta generada el modelo e identifica que preguntas no cumplen con lo mencionado en el prompt
    Luego siguiendo detalladamente las intrucciones en el prompt genera nuevas preguntas para reemplazar las que no cumplen
    Actualiza las preguntas y muestralas.
    """

def get_prompt_gen_factoid_questions_vF(reglamento, num_questions = 20):
    print(f"\nNumero de preguntas a crear {num_questions}\n")
    prompt = f"""
Tu tarea consiste en generar al menos {num_questions} preguntas prácticas y distintivas que aborden todos los temas relevantes para los estudiantes de la Facultad de Ciencias de la Universidad Nacional de Ingeniería que esten explícitamente descritos y bien desarrollados en la información proporcionada (delimitada por tres comillas invertidas), de modo que las preguntas puedan ser respondidas de manera sustancial y completa basándose únicamente en dicha información.

Evita generar preguntas que mencionen específicamente el reglamento. Prioriza preguntas que exploren los temas de manera más general y menos específica, abarcando áreas extensas bien desarrolladas y explícitamente descritas en la información proporcionada (delimitada por tres comillas invertidas).

Al presentar las {num_questions} preguntas, asegúrate de incluir una explicación de por qué cada pregunta cumple con los criterios mencionados anteriormente.

Utiliza el siguiente formato para presentar las preguntas:
1. pregunta...
    Explicación: [Aquí proporciona una breve explicación de por qué esta pregunta cumple con los criterios establecidos, destacando cómo aborda un tema relevante de manera general que este bien desarrollado y explícitamente descritas en la información proporcionada, sin hacer referencia explícita al reglamento.]
2. pregunta...
    Explicación: [De manera similar, proporciona una explicación de por qué esta pregunta también cumple con los criterios mencionados, destacando cómo aborda un tema relevante de manera general que este bien desarrollado y explícitamente descritas en la información proporcionada, sin hacer referencia explícita al reglamento.]
...

Fragmento de texto: ```{reglamento}```
    """

    return prompt


# Prioriza preguntas que exploren los temas de manera más general y menos específica.

def get_prompt_gen_factoid_questions_vg(reglamento, num_questions = 20):
    prompt = f"""
    Tu tarea consiste en identificar todos los temas y hechos relevantes para los estudiantes de la Facultad de Ciencias de la Universidad Nacional de Ingeniería descritos de información proporcionada (delimitada por tres comillas invertidas) y generar al menos {num_questions} preguntas relacionadas a esos temas, siguiento los siguientes pasos:
    Paso 1. Identifica todos los temas y hechos relevantes para los estudiantes de la Facultad de Ciencias de la Universidad Nacional de Ingeniería dentro de información proporcionada (delimitada por tres comillas invertidas). Los cuales deben estar explícitamente descritos y bien desarrollados en la información proporcionada (delimitada por tres comillas invertidas). 
    Paso 2. Genera preguntas que abarquen todos estos temas, de modo que las preguntas puedan ser respondidas de manera sustancial y completa basándose únicamente en dicha información. Evita generar preguntas que mencionen específicamente al reglamento o a numerales de articulos. 
    Paso 3. Presenta las preguntas con sus temas correspodientes y, asegúrate de incluir una explicación de por qué cada pregunta cumple con los criterios mencionados anteriormente..
    Utiliza el siguiente formato para presentar las preguntas:
        1. pregunta...
        Tema: [Aqui una nombre conciso y descriptivo del tema que trata la consulta]
        Explicación: [Aquí proporciona una breve explicación de por qué esta pregunta cumple con los criterios establecidos, destacando cómo aborda un tema relevante que este bien desarrollado y explícitamente descritas en la información proporcionada, sin hacer referencia explícita al reglamento a numerales de articulos.]
        
        2. pregunta...
        Tema: [Aqui una nombre conciso y descriptivo del tema que trata la consulta]
        Explicación: [De manera similar, proporciona una explicación de por qué esta pregunta también cumple con los criterios mencionados, destacando cómo aborda un tema relevante que este bien desarrollado y explícitamente descritas en la información proporcionada, sin hacer referencia explícita al reglamento a numerales de articulos.]

    Fragmento de texto: ```{reglamento}```
    """
    
    return prompt

def get_prompt_gen_factoid_questions_vf97_6(reglamento, num_questions = 20):
    print(f"\nNumero de preguntas a crear {num_questions}\n")
    prompt = f"""
Tu tarea consiste en identificar todos los temas o hechos relevantes para los estudiantes de la Facultad de Ciencias de la Universidad Nacional de Ingeniería que se describen en la información proporcionada (delimitada por tres comillas invertidas). Es esencial que estos temas o hechos estén explícitamente descritos y bien desarrollados en la información proporcionada.

Una vez identificados los temas y hechos, tu siguiente paso es generar al menos {num_questions} preguntas relacionadas con esos temas y hechos. Estas preguntas deben tener una respuesta sustancial y completa basándose únicamente en la información proporcionada.

Es importante evitar hacer mención específica al reglamento o algún artículo particular. Debes priorizar preguntas que exploren los temas de manera más general y menos específica.

Finalmente, presenta las {num_questions} preguntas junto con sus temas o hechos correspondientes. Asegúrate de incluir una explicación de por qué cada pregunta cumple con los criterios mencionados anteriormente.

Utiliza el siguiente formato para presentar las preguntas:

1. [Escribe aquí la pregunta]
Tema o Hecho: [Proporciona un nombre conciso y descriptivo del tema o hecho que trata la pregunta.]
Explicación: [Ofrece una breve explicación de por qué esta pregunta cumple con los criterios establecidos, destacando cómo aborda un tema relevante de manera general que está bien desarrollado y explícitamente descrito en la información proporcionada y puede responderse únicamente basándose en dicha información.]

2. [Escribe aquí la pregunta]
Tema o Hecho: [De manera similar, proporciona un nombre conciso y descriptivo del tema o hecho que trata la pregunta.]
Explicación: [De manera similar, proporciona una explicación de por qué esta pregunta también cumple con los criterios mencionados, destacando cómo aborda un tema relevante de manera general que está bien desarrollado y explícitamente descrito en la información proporcionada y puede responderse únicamente basándose en dicha información.]
...

Fragmento de texto: ```{reglamento}```

    """
    return prompt

# _vf97_5
def get_prompt_gen_factoid_questions_vf97_5(reglamento, num_questions = 20):
    print(f"\nNumero de preguntas a crear {num_questions}\n")
    prompt = f"""
Tu tarea consiste en identificar todos los temas o hechos relevantes para los estudiantes de la Facultad de Ciencias de la Universidad Nacional de Ingeniería que se describen en la información proporcionada (delimitada por tres comillas invertidas). Estos temas deben estar explícitamente descritos y bien desarrollados en la información proporcionada.

Una vez identificados los temas y hechos, tu siguiente paso es generar al menos {num_questions} preguntas relacionadas con esos temas y hechos, las cuales deben tener un respuesta sustancial y completa basándose únicamente en la información proporcionada. 

Es importante evitar hacer mención específica al reglamento o algún artículo particular, priorizando preguntas que exploren los temas de manera más general y menos específica.

Finalmente, presenta las {num_questions} preguntas junto con sus temas o hechos correspondientes. Asegúrate de incluir una explicación de por qué cada pregunta cumple con los criterios mencionados anteriormente.

Utiliza el siguiente formato para presentar las preguntas:

1. Aqui proporciona la pregunta
    Aqui Tema o Hecho: [Aquí proporciona un nombre conciso y descriptivo del tema o hecho que trata la pregunta.]
    Explicación: [Proporciona una breve explicación de por qué esta pregunta cumple con los criterios establecidos, destacando cómo aborda un tema relevante de manera general que está bien desarrollado y explícitamente descrito en la información proporcionada y que puede responderse basandose unicamente en dicha informacion]
2.  Aqui proporciona la pregunta
    Aqui Tema o Hecho: [De manera similar, proporciona un nombre conciso y descriptivo del tema o hecho que trata la pregunta.]
    Explicación: [De manera similar, proporciona una explicación de por qué esta pregunta también cumple con los criterios mencionados, destacando cómo aborda un tema relevante de manera general que está bien desarrollado y explícitamente descrito en la información proporcionada y que puede responderse basandose unicamente en dicha informacion]
...

Fragmento de texto: ```{reglamento}```

    """
    return prompt

# _vf97_4

def get_prompt_gen_factoid_questions_vf97_4(reglamento, num_questions = 20):
    print(f"\nNumero de preguntas a crear {num_questions}\n")
    prompt = f"""
Tu tarea consiste en identificar todos los temas relevantes para los estudiantes de la Facultad de Ciencias de la Universidad Nacional de Ingeniería que se describen en la información proporcionada (delimitada por tres comillas invertidas). Estos temas deben estar explícitamente descritos y bien desarrollados en la información proporcionada.

Una vez identificados los temas, tu siguiente paso es generar al menos {num_questions} preguntas relacionadas con esos temas que puedan ser respondidas de manera sustancial y completa basándose únicamente en la información proporcionada. 

Asegurate de no mencionar específicamente el reglamento o algún artículo específico, y prioriza que las preguntas exploren los temas de manera más general y menos específica.

Finalmente, presenta las {num_questions} preguntas junto con sus temas correspondientes. Asegúrate de incluir una explicación de por qué cada pregunta cumple con los criterios mencionados anteriormente.

Utiliza el siguiente formato para presentar las preguntas:

1. Aqui proporciona la pregunta
    Tema: [Aquí proporciona un nombre conciso y descriptivo del tema que trata la pregunta.]
    Explicación: [Proporciona una breve explicación de por qué esta pregunta cumple con los criterios establecidos, destacando cómo aborda un tema relevante de manera general que está bien desarrollado y explícitamente descrito en la información proporcionada y que puede responderse basandose unicamente en dicha informacion, ademas de no hacer referencia explícita al reglamento.]
2.  Aqui proporciona la pregunta
    Tema: [De manera similar, proporciona un nombre conciso y descriptivo del tema que trata la pregunta.]
    Explicación: [De manera similar, proporciona una explicación de por qué esta pregunta también cumple con los criterios mencionados, destacando cómo aborda un tema relevante de manera general que está bien desarrollado y explícitamente descrito en la información proporcionada y que puede responderse basandose unicamente en dicha informacion, ademas de no sin hacer referencia explícita al reglamento.]
...

Fragmento de texto: ```{reglamento}```

    """
    return prompt

# Me gusta al 97 porciento

# _vf97_3

def get_prompt_gen_factoid_questions_vf97_3(reglamento, num_questions = 20):
    print(f"\nNumero de preguntas a crear {num_questions}\n")
    prompt = f"""
Tu tarea consiste en identificar todos los temas relevantes para los estudiantes de la Facultad de Ciencias de la Universidad Nacional de Ingeniería que se describen en la información proporcionada (delimitada por tres comillas invertidas). Estos temas deben estar explícitamente descritos y bien desarrollados en la información proporcionada.

Una vez identificados los temas, tu siguiente paso es generar al menos {num_questions} preguntas relacionadas con esos temas que puedan ser respondidas de manera sustancial y completa basándose únicamente en la información proporcionada. 

Asegurate de no mencionar específicamente el reglamento o algún artículo específico, y prioriza que las preguntas exploren los temas de manera más general y menos específica.

Finalmente, presenta las {num_questions} preguntas junto con sus temas correspondientes. Asegúrate de incluir una explicación de por qué cada pregunta cumple con los criterios mencionados anteriormente.

Utiliza el siguiente formato para presentar las preguntas:

1. Aqui proporciona la pregunta
    Tema: [Aquí proporciona un nombre conciso y descriptivo del tema que trata la pregunta.]
    Explicación: [Proporciona una breve explicación de por qué esta pregunta cumple con los criterios establecidos, destacando cómo aborda un tema relevante de manera general que está bien desarrollado y explícitamente descrito en la información proporcionada y que puede responderse basandose unicamente en dicha informacion, ademas de no hacer referencia explícita al reglamento.]
2.  Aqui proporciona la pregunta
    Tema: [De manera similar, proporciona un nombre conciso y descriptivo del tema que trata la pregunta.]
    Explicación: [De manera similar, proporciona una explicación de por qué esta pregunta también cumple con los criterios mencionados, destacando cómo aborda un tema relevante de manera general que está bien desarrollado y explícitamente descrito en la información proporcionada y que puede responderse basandose unicamente en dicha informacion, ademas de no sin hacer referencia explícita al reglamento.]
...

Fragmento de texto: ```{reglamento}```

    """
    return prompt


def get_prompt_gen_factoid_questions(reglamento, num_questions = 20):
    print(f"\nNumero de preguntas a crear {num_questions}\n")
    prompt = f"""
Tu tarea consiste en analizar detalladamente toda la informacion delimitada por tres comillas invertidas y sintetizar toda la informacion relevante para estudiantes de la UNI en {num_questions} preguntas informativas, completas y relevantes para los estudiantes.
Es importante que las preguntan abarquen temas extensos y bien desarrolados en la informacion delimitada por tres comillas invertidas y eviten mencionar tablas o articulos especificos.
Presenta las {num_questions} preguntas, para ello utiliza el siguiente formato:

1. [Aqui la pregunta]
2. [Aqui la pregunta]
...

Informacion: ```{reglamento}```
    """
    return prompt

def get_prompt_gen_factoid_questions_vf98_5_v2(reglamento, num_questions = 20):
    print(f"\nNumero de preguntas a crear {num_questions}\n")
    prompt = f"""
Tu tarea consiste en generar {num_questions} preguntas significativas, detalladas y relevantes para estudiantes de la UNI que abarquen de manera completa todos los temas, conceptos y hechos explícitamente descritos y bien desarrollados en la información delimitada por tres comillas invertidas y relevantes para los estudiantes de la Facultad de Ciencias de la Universidad Nacional de Ingeniería.
Es importante que no formules preguntas que consulten sobre articulos especificos y evites repetir las mismas consultas.
Evitar mencionar tablas en las preguntas.
Presenta las {num_questions} preguntas, para ello utiliza el siguiente formato para presentar las preguntas:

1. [Aqui la pregunta sobre un tema, concepto o hecho relevante para estudiantes de la UNI, la cual refleja y detalla adecuadamente el contexto en las que se plantea]
2. [Aqui la pregunta sobre un tema, concepto o hecho relevante para estudiantes de la UNI, la cual refleja y detalla adecuadamente el contexto en las que se plantea]
...

Informacion: ```{reglamento}```
    """
    return prompt

def get_prompt_gen_factoid_questions_vf98_5(reglamento, num_questions = 20):
    print(f"\nNumero de preguntas a crear {num_questions}\n")
    prompt = f"""
Tu tarea consiste en identificar todos los temas, conceptos y hechos relevantes para los estudiantes de la Facultad de Ciencias de la Universidad Nacional de Ingeniería descritos en la información proporcionada (delimitada por tres comillas invertidas) y generar preguntas que abarquen de manera completa dichos temas, conceptos y hechos, siguiendo estos pasos:

Paso 1: Identifica todos los temas, conceptos y hechos relevantes para los estudiantes de la Facultad de Ciencias de la Universidad Nacional de Ingeniería dentro de la información proporcionada (delimitada por tres comillas invertidas). Estos deben estar explícitamente descritos y bien desarrollados en la información proporcionada.

Paso 2: Genera {num_questions} preguntas significativas y relevantes para estudiantes de la UNI que aborden de manera completa todos estos temas, conceptos y hechos explícitamente descritos y bien desarrollados en la información delimitada por tres comillas invertidas, sin hacer mención a articulos especificos o al reglamento en las preguntas. Es importante que no formules preguntas que consulten sobre articulos especificos y evites repetir las mismas consultas.
Es importante que las preguntas reflejen y detallen adecuadamente el contexto en las que se plantea, asi como tambien tengan sentido segun lo información delimitada por tres comillas invertidas.

Paso 3: Presenta las {num_questions} preguntas con sus temas correspondientes.

Utiliza el siguiente formato para presentar las preguntas:

1. [Aqui la pregunta sobre un tema, concepto o hecho relevante para estudiantes de la UNI, la cual refleja y detalla adecuadamente el contexto en las que se plantea]
   Tema o Hecho: [Aquí un nombre conciso y descriptivo del tema, concepto o hecho que esta explícitamente descrito y bien desarrollados en la información delimitada por tres comillas invertidas el cual aborda la pregunta]
2. [Aqui la pregunta sobre un tema, concepto o hecho relevante para estudiantes de la UNI, la cual refleja y detalla adecuadamente el contexto en las que se plantea]
   Tema o Hecho: [Aquí un nombre conciso y descriptivo del tema, concepto o hecho que esta explícitamente descrito y bien desarrollados en la información delimitada por tres comillas invertidas el cual aborda la pregunta]
...

Informacion: ```{reglamento}```
    """
    return prompt

def get_prompt_gen_factoid_questions_prev_98(reglamento, num_questions = 20):
    print(f"\nNumero de preguntas a crear {num_questions}\n")
    prompt = f"""
Tu tarea consiste en identificar todos los temas y hechos relevantes para los estudiantes de la Facultad de Ciencias de la Universidad Nacional de Ingeniería descritos en la información proporcionada (delimitada por tres comillas invertidas) y generar preguntas que abarquen de manera completa dichos temas y hechos, siguiendo estos pasos:

Paso 1: Identifica todos los temas y hechos relevantes para los estudiantes de la Facultad de Ciencias de la Universidad Nacional de Ingeniería dentro de la información proporcionada (delimitada por tres comillas invertidas). Estos deben estar explícitamente descritos y bien desarrollados en la información proporcionada.

Paso 2: Genera {num_questions} preguntas que aborden de manera completa todos estos temas y hechos explícitamente descritos y bien desarrollados en la información delimitada por tres comillas invertidas, sin hacer mención a articulos especificos o al reglamento en las preguntas. Es importante que no formules preguntas que consulten sobre articulos especificos y evites repetir las mismas consultas.

Paso 3: Presenta las {num_questions} preguntas con sus temas correspondientes.

Utiliza el siguiente formato para presentar las preguntas:

1. [Aqui la pregunta]
   Tema o Hecho: [Aquí un nombre conciso y descriptivo del tema o hecho que aborda la pregunta]
2. [Aqui la pregunta]
   Tema o Hecho: [Aquí un nombre conciso y descriptivo del tema o hecho que aborda la pregunta]
...

Informacion: {reglamento}
    """
    return prompt

def get_prompt_gen_factoid_questions_prev_vf(reglamento, num_questions = 20):
    print(f"\nNumero de preguntas a crear {num_questions}\n")
    prompt = f"""
Tu tarea consiste en identificar todos los temas y hechos relevantes para los estudiantes de la Facultad de Ciencias de la Universidad Nacional de Ingeniería descritos en el fragmento de información proporcionada (delimitada por tres comillas invertidas) y generar preguntas que abarquen de manera completa dichos temas y hechos, siguiendo estos pasos:

Paso 1: Identifica todos los temas y hechos relevantes para los estudiantes de la Facultad de Ciencias de la Universidad Nacional de Ingeniería dentro del fragmento de información proporcionada (delimitada por tres comillas invertidas). Estos deben estar explícitamente descritos y bien desarrollados en la información proporcionada.

Paso 2: Genera {num_questions} preguntas que aborden de manera completa todos estos temas y hechos explícitamente descritos y bien desarrollados en el fragmento de información delimitada por tres comillas invertidas, sin hacer mención a articulos especificos o al reglamento en las preguntas. Es importante que no formules preguntas que consulten sobre articulos especificos y evites repetir las mismas consultas.

Paso 3: Presenta las {num_questions} preguntas con sus temas correspondientes.

Utiliza el siguiente formato para presentar las preguntas:

1. [Aqui la pregunta]
   Tema o Hecho: [Aquí un nombre conciso y descriptivo del tema o hecho que aborda la pregunta]
2. [Aqui la pregunta]
   Tema o Hecho: [Aquí un nombre conciso y descriptivo del tema o hecho que aborda la pregunta]
...

Fragmento de texto: {reglamento}
    """
    return prompt


def get_prompt_gen_factoid_questions_vf98_3(reglamento, num_questions = 20):
    print(f"\nNumero de preguntas a crear {num_questions}\n")
    prompt = f"""
Tu tarea consiste en identificar todos los temas y hechos relevantes para los estudiantes de la Facultad de Ciencias de la Universidad Nacional de Ingeniería descritos en la de información proporcionada (delimitada por tres comillas invertidas) y generar preguntas que de manera completa abarquen todos estos temas y hechos, siguiendo los siguientes pasos:

Paso 1. Identifica todos los temas y hechos relevantes para los estudiantes de la Facultad de Ciencias de la Universidad Nacional de Ingeniería dentro de la información proporcionada (delimitada por tres comillas invertidas). Los cuales deben estar explícitamente descritos y bien desarrollados en la información proporcionada (delimitada por tres comillas invertidas).

Paso 2. Genera {num_questions} preguntas que de manera completa abarquen todos estos temas y hechos que estan explícitamente descritos y bien desarrollados en información delimitada por tres comillas invertidas.

Paso 3. Presenta las {num_questions} preguntas con sus temas correspodientes 

Utiliza el siguiente formato para presentar las preguntas:
1. pregunta...
    Tema o Hecho: [Aqui una nombre conciso y descriptivo del tema o hecho que trata la consulta]
2. pregunta...
    Tema o Hecho: [Aqui una nombre conciso y descriptivo del tema o hecho que trata la consulta]
...

Fragmento de texto: ```{reglamento}```
    """
    return prompt

def get_prompt_gen_factoid_questions_vf98_2(reglamento, num_questions = 20):
    print(f"\nNumero de preguntas a crear {num_questions}\n")
    prompt = f"""
Tu tarea consiste en identificar todos los temas y hechos relevantes para los estudiantes de la Facultad de Ciencias de la Universidad Nacional de Ingeniería descritos en la de información proporcionada (delimitada por tres comillas invertidas) y generar al menos {num_questions} preguntas relacionadas a esos temas, siguiento los siguientes pasos:

Paso 1. Identifica todos los temas y hechos relevantes para los estudiantes de la Facultad de Ciencias de la Universidad Nacional de Ingeniería dentro de la información proporcionada (delimitada por tres comillas invertidas). Los cuales deben estar explícitamente descritos y bien desarrollados en la información proporcionada (delimitada por tres comillas invertidas), 

Paso 2. Genera preguntas que abarquen todos estos temas y hechos, de modo que las preguntas tengan una respuesta sustancial y completa basándose únicamente en la información delimitada por tres comillas invertidas. Es importante que las preguntas eviten mencionar reglamentos o algun artículo especifico. Ademas, prioriza que las preguntas exploren los temas de manera más general y menos específica, que abarquen areas extensas en la informacion proporcionda pero sin perder el contexto de la tematica tratada.

Paso 3. Presenta las {num_questions} preguntas con sus temas correspodientes y, asegúrate de incluir una explicación de por qué cada pregunta cumple con los criterios mencionados anteriormente.

Utiliza el siguiente formato para presentar las preguntas:
1. pregunta...
    Tema o Hecho: [Aqui una nombre conciso y descriptivo del tema o hecho que trata la consulta]
    Explicación: [Brinda una breve explicación sobre por qué esta pregunta satisface los criterios establecidos, enfatizando cómo aborda un tema o hecho relevante de manera general que está claramente desarrollado y explícitamente descrito en la información proporcionada. Además, destaca como esta pregunta tiene una respuesta sustancial y completa basándose únicamente esa información.]
2. pregunta...
    Tema o Hecho: [Aqui una nombre conciso y descriptivo del tema o hecho que trata la consulta]
    Explicación: [De manera similar, proporciona una explicación de por qué esta pregunta también cumple con los criterios mencionados, enfatizando cómo aborda un tema o hecho relevante de manera general que está claramente desarrollado y explícitamente descrito en la información proporcionada. Además, destaca como esta pregunta tiene una respuesta sustancial y completa basándose únicamente esa información.]
...

Fragmento de texto: ```{reglamento}```
    """
    return prompt

def get_prompt_gen_factoid_questions_vf98(reglamento, num_questions = 20):
    print(f"\nNumero de preguntas a crear {num_questions}\n")
    prompt = f"""
Tu tarea consiste en identificar todos los temas relevantes para los estudiantes de la Facultad de Ciencias de la Universidad Nacional de Ingeniería descritos en la de información proporcionada (delimitada por tres comillas invertidas) y generar al menos {num_questions} preguntas relacionadas a esos temas, siguiento los siguientes pasos:

Paso 1. Identifica todos los temas relevantes para los estudiantes de la Facultad de Ciencias de la Universidad Nacional de Ingeniería dentro de la información proporcionada (delimitada por tres comillas invertidas). Los cuales deben estar explícitamente descritos y bien desarrollados en la información proporcionada (delimitada por tres comillas invertidas), 

Paso 2. Genera preguntas que abarquen todos estos temas, de modo que las preguntas tengan una respuesta sustancial y completa basándose únicamente en la información proporcionada (delimitada por tres comillas invertidas). Evita generar preguntas que mencionen específicamente el reglamento o algun artículo especifico y prioriza que las preguntas exploren los temas de manera más general y menos específica pero sin perder el contexto de la tematica tratada.

Paso 3. Presenta las {num_questions} preguntas con sus temas correspodientes y, asegúrate de incluir una explicación de por qué cada pregunta cumple con los criterios mencionados anteriormente.

Utiliza el siguiente formato para presentar las preguntas:
1. pregunta...
    Tema: [Aqui una nombre conciso y descriptivo del tema que trata la consulta]
    Explicación: [Brinda una breve explicación sobre por qué esta pregunta satisface los criterios establecidos, enfatizando cómo aborda un tema relevante de manera general que está claramente desarrollado y explícitamente descrito en la información delimitada por tres comillas invertidas. Además, destaca como esta pregunta tiene una respuesta sustancial y completa basándose únicamente esa información.]
2. pregunta...
    Tema: [Aqui una nombre conciso y descriptivo del tema que trata la consulta]
    Explicación: [De manera similar, proporciona una explicación de por qué esta pregunta también cumple con los criterios mencionados, enfatizando cómo aborda un tema relevante de manera general que está claramente desarrollado y explícitamente descrito en la información delimitada por tres comillas invertidas. Además, destaca como esta pregunta tiene una respuesta sustancial y completa basándose únicamente esa información.]
...

Fragmento de texto: ```{reglamento}```
    """
    return prompt




def get_prompt_gen_factoid_questions_vf97_2(reglamento, num_questions = 20):
    print(f"\nNumero de preguntas a crear {num_questions}\n")
    prompt = f"""
Tu tarea consiste en identificar todos los temas relevantes para los estudiantes de la Facultad de Ciencias de la Universidad Nacional de Ingeniería descritos en la de información proporcionada (delimitada por tres comillas invertidas) y generar al menos {num_questions} preguntas relacionadas a esos temas, siguiento los siguientes pasos:

Paso 1. Identifica todos los temas relevantes para los estudiantes de la Facultad de Ciencias de la Universidad Nacional de Ingeniería dentro de la información proporcionada (delimitada por tres comillas invertidas). Los cuales deben estar explícitamente descritos y bien desarrollados en la información proporcionada (delimitada por tres comillas invertidas), 

Paso 2. Genera preguntas que abarquen todos estos temas, de modo que asegures que las preguntas puedan ser respondidas de manera sustancial y completa basándose únicamente en la información proporcionada (delimitada por tres comillas invertidas). Evita generar preguntas que mencionen específicamente el reglamento o algun artículo especifico y prioriza que las preguntas exploren los temas de manera más general y menos específica.

Paso 3. Presenta las {num_questions} preguntas con sus temas correspodientes y, asegúrate de incluir una explicación de por qué cada pregunta cumple con los criterios mencionados anteriormente.

Utiliza el siguiente formato para presentar las preguntas:
1. pregunta...
    Tema: [Aqui una nombre conciso y descriptivo del tema que trata la consulta]
    Explicación: [Aquí proporciona una breve explicación de por qué esta pregunta cumple con los criterios establecidos, destacando cómo aborda un tema relevante de manera general que este bien desarrollado y explícitamente descritas en la información proporcionada, sin hacer referencia explícita al reglamento.]
2. pregunta...
    Tema: [Aqui una nombre conciso y descriptivo del tema que trata la consulta]
    Explicación: [De manera similar, proporciona una explicación de por qué esta pregunta también cumple con los criterios mencionados, destacando cómo aborda un tema relevante de manera general que este bien desarrollado y explícitamente descritas en la información proporcionada, sin hacer referencia explícita al reglamento.]
...

Fragmento de texto: ```{reglamento}```
    """
    return prompt

# Me gusta al 97 porciento

def get_prompt_gen_factoid_questions_vf97(reglamento, num_questions = 20):
    print(f"\nNumero de preguntas a crear {num_questions}\n")
    prompt = f"""
Tu tarea consiste en identificar todos los temas relevantes para los estudiantes de la Facultad de Ciencias de la Universidad Nacional de Ingeniería dentro de información proporcionada (delimitada por tres comillas invertidas) y generar al menos {num_questions} preguntas relacionadas a esos temas, siguiento los siguientes pasos:

Paso 1. Identifica todos los temas relevantes para los estudiantes de la Facultad de Ciencias de la Universidad Nacional de Ingeniería dentro de información proporcionada (delimitada por tres comillas invertidas). Los cuales deben estar explícitamente descritos y bien desarrollados en la información proporcionada (delimitada por tres comillas invertidas), 

Paso 2. Genera al menos {num_questions} sobre estos temas, de modo que las preguntas puedan ser respondidas de manera sustancial y completa basándose únicamente en dicha información. Evita generar preguntas que mencionen específicamente el reglamento. Prioriza preguntas que exploren los temas de manera más general y menos específica.

Paso 3. Presenta las {num_questions} preguntas con sus temas correspodientes y , asegúrate de incluir una explicación de por qué cada pregunta cumple con los criterios mencionados anteriormente.

Utiliza el siguiente formato para presentar las preguntas:
1. pregunta...
    Tema: [Aqui una nombre conciso y descriptivo del tema que trata la consulta]
    Explicación: [Aquí proporciona una breve explicación de por qué esta pregunta cumple con los criterios establecidos, destacando cómo aborda un tema relevante de manera general que este bien desarrollado y explícitamente descritas en la información proporcionada, sin hacer referencia explícita al reglamento.]
2. pregunta...
    Tema: [Aqui una nombre conciso y descriptivo del tema que trata la consulta]
    Explicación: [De manera similar, proporciona una explicación de por qué esta pregunta también cumple con los criterios mencionados, destacando cómo aborda un tema relevante de manera general que este bien desarrollado y explícitamente descritas en la información proporcionada, sin hacer referencia explícita al reglamento.]
...

Fragmento de texto: ```{reglamento}```
    """
    return prompt
# me gusta al 96% 
def get_prompt_gen_factoid_questions_vf96(reglamento, num_questions = 20):
    print(f"\nNumero de preguntas a crear {num_questions}\n")
    prompt = f"""
Tu tarea consiste en generar al menos {num_questions} preguntas prácticas y distintivas que aborden una variedad de temas relevantes para los estudiantes de la Facultad de Ciencias de la Universidad Nacional de Ingeniería. Estos temas deben estar explícitamente descritos y bien desarrollados en la información proporcionada (delimitada por tres comillas invertidas), de modo que las preguntas puedan ser respondidas de manera sustancial y completa basándose únicamente en dicha información.

Evita generar preguntas que mencionen específicamente el reglamento. Prioriza preguntas que exploren los temas de manera más general y menos específica, abarcando áreas extensas bien desarrolladas y explícitamente descritas en la información proporcionada (delimitada por tres comillas invertidas).

Al presentar las {num_questions} preguntas, asegúrate de incluir una explicación de por qué cada pregunta cumple con los criterios mencionados anteriormente.

Utiliza el siguiente formato para presentar las preguntas:
1. pregunta...
    Explicación: [Aquí proporciona una breve explicación de por qué esta pregunta cumple con los criterios establecidos, destacando cómo aborda un tema relevante de manera general que este bien desarrollado y explícitamente descritas en la información proporcionada, sin hacer referencia explícita al reglamento.]
2. pregunta...
    Explicación: [De manera similar, proporciona una explicación de por qué esta pregunta también cumple con los criterios mencionados, destacando cómo aborda un tema relevante de manera general que este bien desarrollado y explícitamente descritas en la información proporcionada, sin hacer referencia explícita al reglamento.]
...

Fragmento de texto: ```{reglamento}```
    """
    return prompt

def get_prompt_gen_factoid_questions_v6(reglamento, num_questions = 20):
    print(f"\nNumero de preguntas a crear {num_questions}\n")
    prompt = f"""

Tu tarea es generar al menos {num_questions} preguntas practicas y únicas que aborden diversos temas relevantes para los estudiantes de la Facultad de Ciencias de la Universidad Nacional de Ingenieria, que se encuentren explicitamente descritos y bien desarralos  en la información proporcionada  (delimitada por tres comillas invertidas) de manera que las pueden ser respondidos de manera sustancial y completa  basandose únicamente en la información proporcionada (delimitada por tres comillas invertidas).
Prioriza generar preguntas más generales y menos específicas que abarquen temas extensos bien desarrollados y explicitamente descritos en la informacion proporcionada.
Ademas asegurate que las preguntas tengan una respuesta sustancial y completa basandose únicamente en la información proporcionada (delimitada por tres comillas invertidas).

Finalmente, presenta las {num_questions} preguntas de la siguiente manera:
1. pregunta...
2. pregunta...
...

Fragmento de texto: ```{reglamento}```
    """
    return prompt

def get_prompt_gen_factoid_questions_v2(reglamento, num_questions = 20):
    print(f"\nNumero de preguntas a crear {num_questions}\n")
    prompt = f"""
Tu tarea es generar al menos {num_questions} de preguntas, basadandote en la información proporcionada sobre reglamentos académicos de la Facultad de Ciencias de la UNI (delimitada por tres comillas invertidas).
Antes de crear una pregunta asegúrate de cumplir estrictamente cada uno de los siguientes criterios:
    - Evita mencionar o citar numerales de artículos específicos en las preguntas.
    - No formules preguntas que requieran identificar el numero de artículos específicos en el reglamento.
    - No crees preguntas que mencionen directamente datos especificos.
    - Concéntrate en preguntas prácticas y relevantes para usuarios como alumnos, docentes o el público en general, que puedan ser respondidas con la información proporcionada.
    - Las preguntas deben fomentar respuestas extensas, basadas en la información proporcionada. 
    - Evita la repetición y asegúrate de crear preguntas únicas de diferentes temas relevantes para usuarios como alumnos, docentes o el público en general, que puedan ser respondidas con la información proporcionada.

Finalmente, presenta las {num_questions} preguntas la siguiente manera:
1. pregunta...
2. pregunta...
...

Fragmento de texto: ```{reglamento}```
    """
    return prompt



set_openai_key()

encoding = tiktoken.encoding_for_model('gpt-3.5-turbo')

class QuestionGenerator:
    def __init__(self, 
                 topics_data, 
                 questions_types):
        
        self.topics_data = load_json(topics_data)
        self.questions_types = questions_types
        
    
    def get_num_questions(self, question_type, num_tokens):
        if question_type == QuestionType.YES_OR_NOT_ANSWER:
            
            if num_tokens < 200:
                num_questions = 2
            elif num_tokens < 350:
                num_questions = 4
            elif num_tokens < 500:
                num_questions = 8
            elif num_tokens < 1000:
                num_questions = 16
            elif num_tokens < 1500:
                num_questions = 24
            elif num_tokens < 2000:
                num_questions = 32
            elif num_tokens < 2500:
                num_questions = 40
            else:
                num_questions = 48

        elif question_type == QuestionType.FACTOID:
            num_questions = int(round((num_tokens - 10) / 60))

        return num_questions
    
    def get_num_questions_prev(self, question_type, num_tokens):
        if question_type == QuestionType.YES_OR_NOT_ANSWER:
            
            if num_tokens < 200:
                num_questions = 2
            elif num_tokens < 350:
                num_questions = 4
            elif num_tokens < 500:
                num_questions = 8
            elif num_tokens < 1000:
                num_questions = 16
            elif num_tokens < 1500:
                num_questions = 24
            elif num_tokens < 2000:
                num_questions = 32
            elif num_tokens < 2500:
                num_questions = 40
            else:
                num_questions = 48

        elif question_type == QuestionType.FACTOID:
            if num_tokens < 200:
                num_questions = 2
            elif num_tokens < 350:
                num_questions = 5
            elif num_tokens < 500:
                num_questions = 8
            elif num_tokens < 800:
                num_questions = 12
            elif num_tokens < 1000:
                num_questions = 16
            elif num_tokens < 1500:
                num_questions = 24
            elif num_tokens < 2000:
                num_questions = 32
            elif num_tokens < 2500:
                num_questions = 40
            else: 
                num_questions = 48

        return num_questions
    

    def find_questions_with_mentions_information(self, questions):
        questions_to_mod = []
        keywords = ["reglamento", 
                    "información proporcionada", 
                    "estatuto de la uni", 
                    "tabla", 
                    "artículo",
                    "art."]

        for i_q, question in enumerate(questions):
            #question = question_dict["question"]
            if any(keyword in question.lower() for keyword in keywords):
                questions_to_mod.append({"question": question, "index": i_q})
        
        return questions_to_mod
    
    

    def get_prompt_skip_mentions_information(self, preguntas):
        preguntas_text = list_json_to_txt(preguntas)
        prompt = f"""
            Tu tarea consiste en omitir menciones específicas al reglamento, a articulos o a tablas en las siguientes preguntas, sin afectar el sentido original de las preguntas.
            Es importante que no alteres las palabras originales de las preguntas.
            Preguntas: 
            {preguntas_text}

            Por favor, enumera las preguntas modificadas en el mismo orden proporcionado
            """
        return prompt
    
    def mod_questions_skip_mentions_information(self, preguntas):
        prompt = self.get_prompt_skip_mentions_information(preguntas)
        messages =  [{'role':'user', 'content':prompt}]
        response = get_completion_from_messages(
            messages, 
            temperature=0,
            model="gpt-3.5-turbo-0613" 
            #model= "gpt-4-1106-preview"
        )

        questions_mod = self.extract_questions_from_response_regex(response)
        return questions_mod

    #def refine_questions(self, questions):
    #    prompt = 

    def run(self):
        
        total_subtopics = len(self.topics_data)

        print(f"{total_subtopics} subtemas encontrados...")
        
        topics_selected = self.topics_data[0:1]

        questions_generated = []
        
        progress_bar = tqdm(range(len(topics_selected)), desc= "Sub Temas")
        total_questions = 0
        for topic in topics_selected:
            num_tokens = count_tokens(encoding, text = topic["content"])
            print("\nNumero de tokens:", num_tokens)
            context_text = topic["topic"] + "\n" + topic["content"]
            print()
            try:    
              
                for qt in self.questions_types:
                    num_questions = self.get_num_questions(qt, num_tokens)
                    
                    questions = self.generate_questions_answers(context_text, qt, num_questions = num_questions)
                    
                    ## Modificar preguntas que mencionen al reglamento
                    questions_to_mod = self.find_questions_with_mentions_information(questions)

                    if len(questions_to_mod) > 0:
                        questions_content = [ q["question"] for q in questions_to_mod]
                        questions_mod = self.mod_questions_skip_mentions_information(questions_content)
                        ## Replace questions
                        for i_q_mod, q_to_mod in enumerate(questions_to_mod):
                            print("\norignal:",questions[q_to_mod["index"]])
                            print("\nmod:",questions_mod[i_q_mod])
                            print()
                            questions[q_to_mod["index"]] = questions_mod[i_q_mod]
                        
                    print()
                    
                    total_questions += len(questions)
                    
                    questions_generated.append({
                        "context": context_text,
                        "topic": topic["topic"],
                        "source_context": topic["source"], 
                        "questions": questions
                        })
                    
                    time.sleep(10)
                    progress_bar.set_postfix({"total_preguntas": total_questions})
                    progress_bar.update(1 / len(self.questions_types))

            except Exception as e:
                save_json("./", "questions_generated", questions_generated)
                raise Exception(e)
            time.sleep(5)
        
        save_json("./", "questions_generated", questions_generated)    
           
    def extract_questions_from_response_regex(self, response):
        patron = r'\d+\.\s(¿[^\?]+?\?)'
        preguntas = re.findall(patron, response)
        return preguntas

    def extract_questions_topic_from_response_regex(self, response):
        pattern = r'\d+\.\s(¿[^\?]+?\?)\s*Tema[^\:]*:\s*(.*?)(?=\d+\.|\Z)'
        matches = re.findall(pattern, response, re.DOTALL)
        question_topics = [{"specific_topic": topic, "question": question} for (question, topic) in matches]
        return question_topics

    def generate_questions_answers(self, text, question_type, num_questions = 30):
        prompt = get_prompt_gen_questions(text, question_type, num_questions)
        print("prompt:", prompt)
        #print("Size input: " , count_tokens(encoding ,prompt))
 
        messages =  [{'role':'user', 'content':prompt}]
        response = get_completion_from_messages(
            messages, 
            temperature=0,
            #model="gpt-3.5-turbo-0613"
            #model="gpt-3.5-turbo-0125" 
            model= "gpt-4-1106-preview"
        )

        print("response:", response)
        print("Size output: " , count_tokens(encoding ,response))
 
        questions = self.extract_questions_from_response_regex(response)
        #print("Total de preguntas generadas:", len(questions))
        if abs(num_questions - len(questions)) > 0:
            print("\nFaltan preguntas\n")
            content = prompt + "\n" + response
            messages =  [{'role':'user', 'content':content}]
            response = get_completion_from_messages(
                messages, 
                temperature=0,
                #model="gpt-3.5-turbo-0613"
                #model="gpt-3.5-turbo-0125"  
                #model="gpt-4-1106-preview"
            )
            print("response:", response)
            next_questions = self.extract_questions_topic_from_response_regex(response)
            print("Total de preguntas generadas:", len(next_questions))
            questions  = questions + next_questions
        #print("Total de preguntas extraidas:", len(questions))

        return questions
    
if __name__ == "__main__":
    questions_generator = QuestionGenerator(topics_data= "./topics_finals.json", 
                                        questions_types = [#QuestionType.YES_OR_NOT_ANSWER, 
                                                           QuestionType.FACTOID])
 
    questions_generator.run()

#save_json("./", "questions_generated", questions_generated)
