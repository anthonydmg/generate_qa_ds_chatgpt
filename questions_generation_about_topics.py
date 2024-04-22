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

load_dotenv(override=True)

def set_openai_key():
    API_KEY = os.getenv("API_KEY")
    print("API_KEY:", API_KEY)
    openai.api_key = API_KEY

def get_completion_from_messages(messages, model="gpt-3.5-turbo-1106", temperature=0):
    response = openai.chat.completions.create(
        model=model,
        messages=messages,
        #max_tokens = 0,
        temperature=temperature, # this is the degree of randomness of the model's output
    )
    return response.choices[0].message.content



# Prioriza preguntas que exploren los temas de manera más general y menos específica.

# _origin
def get_prompt_gen_questions_origin(text, num_questions = 20):
    print(f"\nNumero de preguntas a crear {num_questions}\n")
    prompt = f"""
Tu tarea consiste en analizar detalladamente toda la informacion delimitada por tres comillas invertidas y sintetizar toda la informacion relevante para estudiantes de la UNI en {num_questions} preguntas informativas, completas y relevantes para los estudiantes.
Es importante que las preguntan abarquen temas extensos y bien desarrolados en la informacion delimitada por tres comillas invertidas y eviten mencionar tablas o articulos especificos.
Presenta las {num_questions} preguntas, para ello utiliza el siguiente formato:

1. [Aqui la pregunta]
2. [Aqui la pregunta]
...

Informacion: ```{text}```
    """
    return prompt
# _forma2
# Evita mencionar articulos en las preguntas
# En importante que las preguntas abarquen todos los conceptos, hechos y puntos que sean relevantes para estudiantes y esten explícitamente descritos y bien desarrollados en la información delimitada por tres comillas invertidas.
# Es importante que las preguntas se formulen de manera clara y completa con respecto al tema o contexto sobre el que se formulan.

def get_prompt_gen_questions(text, num_questions = 20):
    prompt = f"""
Genera una {num_questions} preguntas relevantes para los estudiantes de la Facultad de Ciencias de la UNI, basadas en la información delimitada por tres comillas invertidas, que puedan ayudar a clarificar dudas comunes y a promover un mejor entendimiento de las reglas y procesos en la institución educativa.
Es importante que las preguntas se formulen de manera clara, completa y especifica con respecto al informacion y el contexto en las que se consultan, evitando cualquier ambigüedad.
Ademas, es esencial que las preguntas abarquen todos los conceptos, hechos y puntos que sean relevantes para estudiantes y esten explícitamente descritos y bien desarrollados en la información delimitada por tres comillas invertidas.
Asegúrate de no utilizar la primera persona del estudianta para formular las preguntas.

Presenta las {num_questions} preguntas de la siguiente manera:

1. [Aqui la pregunta]
2. [Aqui la pregunta]
...

Informacion: ```{text}```
"""
    return prompt

def get_prompt_gen_questions_origin(text, num_questions = 20):
    print(f"\nNumero de preguntas a crear {num_questions}\n")
    prompt = f"""
Tu tarea consiste en generar {num_questions} preguntas completas y relevantes para estudiantes de la UNI, basandote en la informacion delimitada por tres comillas.
En importante que las preguntas abarquen todos los conceptos, hechos y puntos que sean relevantes para estudiantes y esten explícitamente descritos y bien desarrollados en la información delimitada por tres comillas invertidas.
Evita mencionar articulos en las preguntas
Presenta las {num_questions} preguntas, para ello utiliza el siguiente formato:

1. [Aqui la pregunta]
2. [Aqui la pregunta]
...

Informacion: ```{text}```
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


set_openai_key()

encoding = tiktoken.encoding_for_model('gpt-3.5-turbo')

class QuestionGenerator:
    def __init__(self, 
                 topics_data):
        
        self.topics_data = load_json(topics_data)
        
    
    def get_num_questions(self, num_tokens):
        #60
        num_questions = int(round((num_tokens - 10) / 120))

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
            #model="gpt-3.5-turbo-0613" 
            #model= "gpt-4-1106-preview"
        )

        questions_mod = self.extract_questions_from_response_regex(response)
        return questions_mod

    def run(self):
        
        total_subtopics = len(self.topics_data)

        print(f"{total_subtopics} temas encontrados...")
        
        topics_selected = self.topics_data[0:5]

        questions_generated = []
        
        progress_bar = tqdm(range(len(topics_selected)), desc= "Temas")
        total_questions = 0
        for topic in topics_selected:
            num_tokens = count_tokens(encoding, text = topic["content"])
            print("\nNumero de tokens:", num_tokens)
            context_text = topic["topic"] + "\n" + topic["content"]
            print()
            try:    
              
                num_questions = self.get_num_questions(num_tokens)
                
                questions = self.generate_questions(context_text, num_questions = num_questions)
                
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
                progress_bar.update(1)

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

    def generate_questions(self, text, num_questions = 30):
        prompt = get_prompt_gen_questions(text, num_questions)
        #print("prompt:", prompt)
        #print("Size input: " , count_tokens(encoding ,prompt))
 
        messages =  [{'role':'user', 'content':prompt}]
        response = get_completion_from_messages(
            messages, 
            temperature=0,
            #model="gpt-3.5-turbo-0613"
            #model="gpt-3.5-turbo-0125" 
            #model= "gpt-4-1106-preview"
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
    questions_generator = QuestionGenerator(topics_data= "./topics_finals.json")
 
    questions_generator.run()

#save_json("./", "questions_generated", questions_generated)
