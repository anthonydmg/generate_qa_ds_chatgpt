import openai
from dotenv import load_dotenv
import os 
from utils import get_completion_from_messages, list_json_to_txt, load_json, save_json
load_dotenv()

def set_openai_key():
    API_KEY = os.getenv("API_KEY")
    openai.api_key = API_KEY

set_openai_key()



questions =  [
            {
                "specific_topic": "Definici\u00f3n de convalidaci\u00f3n de asignaturas\n",
                "question": "\u00bfQu\u00e9 es la convalidaci\u00f3n de asignaturas seg\u00fan el reglamento de matr\u00edcula de la Universidad Nacional de Ingenier\u00eda?"
            },
            {
                "specific_topic": "Requisitos de contenido para convalidaci\u00f3n de asignaturas\n",
                "question": "\u00bfCu\u00e1l es el porcentaje m\u00ednimo de contenido que deben coincidir las asignaturas para que proceda la convalidaci\u00f3n?"
            },
            {
                "specific_topic": "Requisitos de cr\u00e9ditos para convalidaci\u00f3n de asignaturas\n",
                "question": "\u00bfCu\u00e1l es la diferencia m\u00e1xima de cr\u00e9ditos permitida entre las asignaturas a convalidar?"
            },
            {
                "specific_topic": "Decisi\u00f3n sobre convalidaci\u00f3n de asignaturas con mayor profundidad\n",
                "question": "\u00bfQui\u00e9n tiene la facultad de decidir sobre la convalidaci\u00f3n de una asignatura con mayor profundidad en el contenido?"
            },
            {
                "specific_topic": "Derecho a solicitar convalidaci\u00f3n de asignaturas\n",
                "question": "\u00bfEn qu\u00e9 casos tiene derecho un estudiante a solicitar la convalidaci\u00f3n de asignaturas?"
            },
            {
                "specific_topic": "Procedimiento de traslado interno\n",
                "question": "\u00bfQu\u00e9 es el traslado interno seg\u00fan el reglamento de matr\u00edcula de la Universidad Nacional de Ingenier\u00eda?"
            },
            {
                "specific_topic": "Procedimiento de traslado externo nacional o internacional\n",
                "question": "\u00bfQu\u00e9 es el traslado externo nacional o internacional seg\u00fan el reglamento de matr\u00edcula de la Universidad Nacional de Ingenier\u00eda?"
            },
            {
                "specific_topic": "Procedimiento de convenio internacional\n",
                "question": "\u00bfQu\u00e9 es el convenio internacional seg\u00fan el reglamento de matr\u00edcula de la Universidad Nacional de Ingenier\u00eda?"
            },
            {
                "specific_topic": "Procedimiento de graduados y titulados para segunda profesi\u00f3n\n",
                "question": "\u00bfQu\u00e9 es el procedimiento de graduados y titulados para segunda profesi\u00f3n seg\u00fan el reglamento de matr\u00edcula de la Universidad Nacional de Ingenier\u00eda?"
            },
            {
                "specific_topic": "Requisito de traducci\u00f3n oficial para asignaturas a convalidar en idiomas diferentes\n",
                "question": "\u00bfQu\u00e9 requisito se menciona para los certificados y s\u00edlabos de asignaturas a convalidar que est\u00e9n redactados en idiomas diferentes al espa\u00f1ol?"
            },
            {
                "specific_topic": "Refrendo de s\u00edlabos de asignaturas a convalidar\n",
                "question": "\u00bfQu\u00e9 entidad debe refrendar los s\u00edlabos de las asignaturas a convalidar en la especialidad de destino?"
            },
            {
                "specific_topic": "Reconocimiento de asignaturas mediante convalidaci\u00f3n\n",
                "question": "\u00bfQu\u00e9 es el acto acad\u00e9mico y administrativo mediante el cual la UNI reconoce como v\u00e1lidas las asignaturas de contenido similar y n\u00famero de cr\u00e9ditos igual o similar al de otro Plan de Estudios?"
            },
            {
                "specific_topic": "Procedimiento de convalidaci\u00f3n para estudiantes provenientes de otras universidades\n",
                "question": "\u00bfCu\u00e1l es el procedimiento para que un estudiante proveniente de una universidad nacional o extranjera pueda convalidar asignaturas en la UNI?"
            },
            {
                "specific_topic": "Requisitos para solicitar convalidaci\u00f3n de asignaturas\n",
                "question": "\u00bfQu\u00e9 requisitos acad\u00e9micos y administrativos debe cumplir un estudiante para solicitar la convalidaci\u00f3n de asignaturas?"
            },
            {
                "specific_topic": "Procedimiento para estudiantes de universidades extranjeras que desean continuar estudios en la UNI\n",
                "question": "\u00bfQu\u00e9 sucede si un estudiante desea continuar sus estudios en una especialidad que ofrece la UNI pero proviene de una universidad extranjera?"
            },
            {
                "specific_topic": "Procedimiento para graduados que desean seguir una segunda profesi\u00f3n en la UNI",
                "question": "\u00bfQu\u00e9 sucede si un estudiante desea seguir una segunda profesi\u00f3n en la UNI despu\u00e9s de haberse graduado en otra universidad?"
            }
        ]

def get_prompt_skip_mentions_information(preguntas):
    #preguntas_text = list_json_to_txt(preguntas)
    prompt = f"""
        Tu tarea consiste en omitir menciones específicas al reglamento en las siguientes preguntas, sin afectar el sentido original de las preguntas.
        Es importante que no alteres las palabras originales de las preguntas.
        Preguntas: 
        1. ¿Quiénes son partícipes de la Matrícula Condicionada según el reglamento?
        2. ¿Qué deben priorizar los estudiantes al momento de decidir su matrícula según el reglamento?
        3. ¿Qué recomendación se da para la reincorporación como rezagado según el reglamento?
    
    Por favor, enumera las preguntas modificadas en el mismo orden proporcionado
        """
    return prompt
import re

def extract_questions_from_response_regex(response):
        patron = r'\d+\.\s(¿[^\?]+?\?)'
        preguntas = re.findall(patron, response)
        return preguntas


def mod_questions_skip_mentions_information(preguntas):
    prompt = get_prompt_skip_mentions_information(preguntas)
    messages =  [{'role':'user', 'content':prompt}]
    response = get_completion_from_messages(
        messages, 
        temperature=0,
        model="gpt-3.5-turbo-0125" 
        #model= "gpt-4-1106-preview"
    )
    print("response:",response)
    questions_mod = extract_questions_from_response_regex(response)
    return questions_mod

def find_questions_with_mentions_information(questions):
    questions_to_mod = []
    
    for i_q, question_dict in enumerate(questions):
        question = question_dict["question"]
        if "reglamento" in question.lower() or "información proporcionada" in question.lower():
            questions_to_mod.append({"question": question, "index": i_q})
    
    return questions_to_mod

questions_to_mod = find_questions_with_mentions_information(questions)
print("questions_to_mod:", questions_to_mod)

if len(questions_to_mod) > 0:
    questions_content = [ q["question"] for q in questions_to_mod]
    mod_questions_skip_mentions_information(questions_content)


""" questions_generated = load_json("./questions_generated_liked_98_5%_pp3.json")


for q in questions_generated:
    questions_orignal = q["questions"]
    questions_to_mod = find_questions_with_mentions_information(questions_orignal)

    if len(questions_to_mod) > 0:
        questions_content = [ q["question"] for q in questions_to_mod]
        questions_mod = mod_questions_skip_mentions_information(questions_content)
        ## Replace questions
        for i_q_mod, q_to_mod in enumerate(questions_to_mod):
            print("\norignal",questions_orignal[q_to_mod["index"]]["question"])
            print("\nmod:",questions_mod[i_q_mod])
            print()
            questions_orignal[q_to_mod["index"]]["question"] = questions_mod[i_q_mod]
        
        q["questions"] = questions_orignal

save_json("./", "questions_generated_liked_98_5%_pp3_mod.json", questions_generated) """