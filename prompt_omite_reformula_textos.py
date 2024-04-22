import openai
from dotenv import load_dotenv
import os 
from utils import get_completion_from_messages, list_json_to_txt, load_json, save_json
load_dotenv()

def set_openai_key():
    API_KEY = os.getenv("API_KEY")
    openai.api_key = API_KEY

set_openai_key()

question_anwers =  [
            {
                "question": "\u00bfCu\u00e1l es el n\u00famero m\u00ednimo de cr\u00e9ditos que los estudiantes de la Facultad de Ciencias de la Universidad Nacional de Ingenier\u00eda deben matricularse por semestre para conservar su condici\u00f3n de estudiante regular?",
                "answer": "El n\u00famero m\u00ednimo de cr\u00e9ditos que los estudiantes de la Facultad de Ciencias de la Universidad Nacional de Ingenier\u00eda deben matricularse por semestre para conservar su condici\u00f3n de estudiante regular es de doce (12) cr\u00e9ditos, seg\u00fan el numeral 99.8 del Art. 99 del REGLAMENTO DE MATR\u00cdCULA PARA ESTUDIANTES DE ANTEGRADO DE LA UNIVERSIDAD NACIONAL DE INGENIER\u00cdA.\n\n",
                "specific_topic": "Requisitos de Cr\u00e9ditos para Estudiante Regular\n\n"
            },
            {
                "question": "\u00bfQu\u00e9 excepci\u00f3n se establece para los estudiantes que les falten menos cr\u00e9ditos para culminar su carrera en cuanto a la cantidad m\u00ednima de cr\u00e9ditos a matricular por semestre para conservar su condici\u00f3n de estudiante regular?",
                "answer": "La excepci\u00f3n establecida para los estudiantes que les falten menos cr\u00e9ditos para culminar su carrera es que no tienen que matricularse en el n\u00famero m\u00ednimo de doce (12) cr\u00e9ditos por semestre para conservar su condici\u00f3n de estudiante regular, seg\u00fan el numeral 99.8 del Art. 99 del REGLAMENTO DE MATR\u00cdCULA PARA ESTUDIANTES DE ANTEGRADO DE LA UNIVERSIDAD NACIONAL DE INGENIER\u00cdA.",
                "specific_topic": "Condiciones de Estudiante Regular"
            }
        ]

def get_prompt_skip_mentions_information(textos):
    textos_list = list_json_to_txt(textos)
    print("\nOriginal:\n", textos_list)
    print()
    prompt = f"""
        Tu tarea consiste en omitir las referencias específicas a los numerales y artículos en los siguientes textos, sin alterar el sentido original de la información en ellos.
        Es importante que no alteres las palabras originales de los textos.
        Preguntas: 
        {textos_list}
        Por favor, enumera las versiones modificadas de los textos para eliminar las referencias específicas a los numerales y artículos, manteniendo el mismo orden en que se proporcionaron los textos originales. 
        Utiliza el siguiente formato de enumeración con punto-guión:
            1.- Aqui el texto modificado
            2.- Aqui el texto modificado
            ...
        """
    return prompt
import re

def extract_texts_from_response_regex(response):
        patron = r'\d+\.-\s*(.*?)(?=\d+\.-|\Z)'
        preguntas = re.findall(patron, response, re.DOTALL)
        return preguntas


def mod_texts_skip_mentions_articles(textos):
    prompt = get_prompt_skip_mentions_information(textos)
    print("\n\nprompt:", prompt)
    messages =  [{'role':'user', 'content':prompt}]
    response = get_completion_from_messages(
        messages, 
        temperature=0,
        model="gpt-3.5-turbo-0125" 
        #model= "gpt-4-1106-preview"
    )
    print("response:",response)
    textos_mod = extract_texts_from_response_regex(response)
    return textos_mod

def find_index_answers_with_mentions_articles(question_answers):
    index_to_mod = []
    
    for i_qa, qa_dict in enumerate(question_answers):
        answer = qa_dict["answer"]
        if "Art." in answer.lower():
             index_to_mod.append(i_qa)
    
    return index_to_mod

index_to_mod = find_index_answers_with_mentions_articles(question_anwers)

if len(index_to_mod) > 0:
    answers = [question_anwers[i_qa]["answer"] for i_qa in index_to_mod]
    answers_mod = mod_texts_skip_mentions_articles(answers)
    
    for i_ans_mod, answer_mod in enumerate(answers_mod):
        question_anwers[index_to_mod[i_ans_mod]]["answer"] = answer_mod
         
         

