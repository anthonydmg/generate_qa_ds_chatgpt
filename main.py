import openai
import json
from dotenv import load_dotenv
import os
from utils import save_json, load_json, format_response_json, read_fragment_doc, list_json_to_txt
import glob
import tiktoken

load_dotenv()
class QuestionType:
    YES_OR_NOT_ANSWER = 1
    FACTOID = 2

def set_openai_key():
    API_KEY = os.getenv("API_KEY")
    openai.api_key = API_KEY

def get_completion_from_messages(messages, model="gpt-3.5-turbo-0301", temperature=0):
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        #max_tokens = 0,
        temperature=temperature, # this is the degree of randomness of the model's output
    )
    return response.choices[0].message["content"]


def get_prompt_gen_questions(text, question_type, num_questions):
    if question_type == QuestionType.YES_OR_NOT_ANSWER:
        format_json = """{"preguntas": ["pregunta 1 generada", "pregunta 2 generada", ...]"""
        
        prompt = f"""
        Tu tarea es generar al menos {num_questions} preguntas que se puedan responder con un Sí ó No a partir de un fragmento del reglamento de una facultad universitaria. 
        Asegúrate que las preguntas se pueda responder directamente con un Sí ó No en base a la informacion del fragmento del reglamento.
        Las preguntas no deben superar las 25 palabras.
        Genera las preguntas para el reglamento de debajo, delimitado por tres comillas invertidas.
        Muestra las preguntas en el siguiente formato JSON:
        {format_json}
        Fragmento del Reglamento: ```{text}```
        """
        return prompt
    elif question_type == QuestionType.FACTOID:
        format_json = """{"preguntas": ["pregunta 1 generada", "pregunta 2 generada", ...]"""
        
        prompt = f"""
        Tu tarea es generar al menos {num_questions} preguntas que se puedan responder con un Sí ó No a partir de un fragmento del reglamento de una facultad universitaria. 
        Asegúrate que las preguntas se pueda responder directamente con un Sí ó No en base a la informacion del fragmento del reglamento.
        Las preguntas no deben superar las 25 palabras.
        Genera las preguntas para el reglamento de debajo, delimitado por tres comillas invertidas.
        Muestra las preguntas en el siguiente formato JSON:
        {format_json}
        Fragmento del Reglamento: ```{text}```
        """
        return prompt

def generate_questions(text, question_type, num_questions = 30):
    prompt = get_prompt_gen_questions(text, question_type, num_questions)
    messages =  [{'role':'user', 'content':prompt}]
    response = get_completion_from_messages(messages, temperature=0)
    resp_json = format_response_json(response)
    questions = resp_json["preguntas"]
    return questions

def get_prompt_gen_questions_type_1(reglamento, num_questions = 20):
    format_json = """{"preguntas": ["pregunta 1 generada", "pregunta 2 generada", ...]"""
    
    prompt = f"""
    Tu tarea es generar al menos {num_questions} preguntas que se puedan responder con un Sí ó No a partir de un fragmento del reglamento de una facultad universitaria. 
    Asegúrate que las preguntas se pueda responder directamente con un Sí ó No en base a la informacion del fragmento del reglamento.
    Las preguntas no deben superar las 25 palabras.
    Genera las preguntas para el reglamento de debajo, delimitado por tres comillas invertidas.
    Muestra las preguntas en el siguiente formato JSON:
    {format_json}
    Fragmento del Reglamento: ```{reglamento}```
    """
    return prompt

def get_prompt_gen_answer_type_1(reglamento, list_questions, max_size = 50):
    format_json = """{"respuestas": ["respuesta para la pregunta 1", "respuesta para la pregunta 2", ...]"""

    prompt = f"""
    Tu tarea consiste en generar respuestas a una lista de preguntas utilizando un fragmento del reglamento de una facultad universitaria. 
    Asegúrate de inferir las respuestas basándote en la información proporcionada en el fragmento del reglamento que se muestra debajo. 
    Asegúrate de generar respuestas coherentes para las preguntas.
    Genera las respuestas para la lista de preguntas que se presenta más abajo, utilizando el fragmento del reglamento delimitado por tres comillas invertidas. 
    Finalmente, muestra las respuestas en siguiente formato JSON:
    {format_json}
    Lista de preguntas:
    {list_questions}
    Fragmento del Reglamento: ```{reglamento}```
    """
    return prompt
## esta es la buena
def get_prompt_gen_answers_type_1_v1(reglamento, list_questions, max_size = 50):
    format_json = """[{"pregunta": "pregunta 1", "respuesta" "respuesta para la pregunta 1"},...]"""

    prompt = f"""
    Tu tarea consiste en generar respuestas a una lista de preguntas utilizando un fragmento del reglamento de una facultad universitaria. 
    Asegúrate de inferir las respuestas basándote en la información proporcionada en el fragmento del reglamento que se muestra debajo. 
    Genera las respuestas para la lista de preguntas que se presenta más abajo, utilizando el fragmento del reglamento delimitado por tres comillas invertidas. 
    Finalmente, muestra los pares de preguntas y respuestas en siguiente formato JSON:
    {format_json}
    Lista de preguntas:
    {list_questions}
    Fragmento del Reglamento: ```{reglamento}```
    """
    return prompt
#  Asegúrate de generar respuestas coherentes para las preguntas.
#   La respuesta a cada pregunta deben tener un máximo de {max_size} palabras.
# 
#     responder adec    uadamente a las preguntas en base a información precisa y objetiva dentro del fragmento del reglamento debajo.

#def generate_questions(prompt, num_questions):
#    messages =  [{'role':'user', 'content':prompt}]
#    response = get_completion_from_messages(messages, temperature=0)
#    resp_json = format_response_json(response)
#    questions = resp_json["preguntas"]
#    return questions

def count_tokens(encoding, text): 
    return len(encoding.encode(text))


set_openai_key()
encoding = tiktoken.encoding_for_model('gpt-3.5-turbo')

for file_text in glob.glob("./documentos/reglamento_matricula/*.txt"):
    text = read_fragment_doc(file_text)
    num_tokens = count_tokens(encoding ,text)
    
    print("File:", file_text)
    print("Num Tokens:", num_tokens)
    
    if num_tokens < 1000:
        num_questions = 20
    elif num_tokens < 1500:
        num_questions = 30
    else:
        num_questions = 40

    #questions = generate_questions(text, QuestionType.YES_OR_NOT_ANSWER, num_questions = num_questions)
    file_questions = file_text.split("/")[-1][:-4] + "_yes_not_questions"
    print(file_questions)
    #save_json("./questions/yes_not_answer/", file_questions, questions)
    break
    

#print(file_list)










## Generacion de las preguntas
#dir_path = "./textos"
#file_name = "capituloII_part2.txt"
#path_file_txt = f"{dir_path}/{file_name}"

#text = read_fragment_doc(path_file_txt)
#prompt = get_prompt_gen_questions_type_1(text, 30)
#questions = generete_questions(prompt, 30)

#questions = load_json("./questions/capituloII_part2_quetions.json")

#text_questions = list_json_to_txt(questions[:10])

#print(text_questions)
#prompt = get_prompt_gen_answer_type_1_v1(text, text_questions, max_size = 80)

#messages =  [{'role':'user', 'content':prompt}]
#response = get_completion_from_messages(messages, temperature=0)
#print(response)
#resp_json = format_response_json(response)
#save_json("./questions", file_name[:-4] + "_qa", resp_json)

#answers = resp_json["respuestas"]
#print("\n\n\n", list_json_to_txt(answers))
#save_json("./questions", file_name[:-4] + "_quetions", questions)

#save_questions()

#format_json = """{"preguntas": ["pregunta 1 generada", "pregunta 2 generada", ...]"""


#messages =  [{'role':'user', 'content':prompt}]

#prompt = f""" 
#TU tareas es siguir las siguientes instrucciones:
#    - Analiza el fragmento del reglamento de matrícula debajo, delimitado con tres comillas invertidas e identifica los procedimientos, tramites o solicitudes descritos en el fragmento.
#    - Selecciona solo los procedimientos, tramites o solicitudes que puedan ser solicitados por alumnos y muestralos en una lista numerica
#Fragmento del reglamento de matrícula: ```{text}```"""

#response = get_completion_from_messages(messages, temperature=0)

#resp_json = format_response_json(response)
#questions = resp_json["preguntas"]
#print(response)