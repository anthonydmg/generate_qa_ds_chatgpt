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
load_dotenv()

def set_openai_key():
    API_KEY = os.getenv("API_KEY")
    openai.api_key = API_KEY


class QuestionType(Enum):
    YES_OR_NOT_ANSWER = 1
    FACTOID = 2



def get_completion_from_messages(messages, model="gpt-3.5-turbo-0613", temperature=0):
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
    Eres un asistente de IA especializado en matrículas, trámites y procedimientos académicos de la Facultad de Ciencias de la UNI. 
    Se te proporcionará un fragmento del reglamento de matrícula delimitado por tres comillas invertidas. 
    A continuación, los requisitos para generar preguntas:
    - Las preguntas deben tener respuestas directas de 'Sí' o 'No'.
    - Evite mencionar directamente el presente reglamento en las preguntas.
    - No cite numerales de artículos en las preguntas.
    - Enfóquese en preguntas relevantes para usuarios como alumnos, docentes o el público en general, que puedan responderse con la información proporcionada.
    - Asegúrese de que las preguntas puedan ser respondidas con un 'Sí' o 'No' basándose en la información proporcionada.
    - Genere al menos {num_questions} preguntas con una longitud máxima de 30 palabras.

    Finalmente, proporciona las preguntas en el siguiente formato JSON:
    {format_json}
    Fragmento del Reglamento: ```{reglamento}```
    """
    return prompt

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

def get_prompt_gen_factoid_questions(reglamento, num_questions = 20):
    format_json = """{"preguntas": ["pregunta 1 generada", "pregunta 2 generada", ...]"""
    
    prompt = f"""
   Eres un asistente de IA especializado en matrículas, trámites y procedimientos académicos de la Facultad de Ciencias de la UNI. 
   Se te proporcionará un fragmento del reglamento de matrícula entre tres comillas invertidas. 
   A continuación, los requisitos para generar preguntas:   
    - Evite mencionar directamente el reglamento en las preguntas.
    - No formule preguntas que requieran identificar artículos específicos del reglamento.
    - Evite citar numerales de artículos en las preguntas.
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
    
    prompt = f"""Eres un asistente de IA especializado en temas de matriculas, tramites y procedimiendo academicos de la Facultad de Ciencias de la UNI
    Se te dará un texto tomado de un fragmento del reglamento de matricula. 
    A continuación se detallan los requisitos para generar preguntas que puedan surgir en una conversación con un usuario:
    - Las preguntas deben tener respuesta en el fragmenteo de texto proviedo.
    - Evite citar al reglamento o numerales de articulos en las preguntas. Concéntrese en hacer preguntas que un usuario como un alumno, docente o publico en general puedan tener y que puedan ser respondididas con la informacion proveida.
    - Asegúrese de que las preguntas sean preguntas concisas y precisas.
    - Debe generar al menos {num_questions} preguntas que tengan como máximo 30 palabras de longitud.

    Proporciona las preguntas en el siguiente formato JSON: {format_json}
    Fragmento del Reglamento: {reglamento}
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
        #return
        for file_text in tqdm(documents[0:1] + documents[3:4], desc= "Documentos"):
            text = read_fragment_doc(file_text)
            num_tokens = count_tokens(encoding ,text)
 
            try:    
                ## Generar preguntas con respuesta de si o no
                for qt in self.questions_types:
                    num_questions = self.get_num_questions(qt, num_tokens)
                    questions = self.generate_questions(text, qt, num_questions = num_questions)
                    questions_generated.append({"document": file_text, "type":  QuestionType(qt).name.lower(), "questions": questions})
                    time.sleep(5)
                ## 
            except Exception as e:
                save_json("./", "questions_generated", questions_generated)
                raise Exception(e)
            time.sleep(5)
        save_json("./", "questions_generated", questions_generated)


    def generate_questions(self, text, question_type, num_questions = 30):
        prompt = get_prompt_gen_questions(text, question_type, num_questions)
        messages =  [{'role':'user', 'content':prompt}]
        response = get_completion_from_messages(messages, temperature=0)
        print("response:", response)
        resp_json = format_response_json(response)
        questions = resp_json["preguntas"]
        return questions

if __name__ == "__main__":
    questions_generator = QuestionGenerator(dir_documents = "./documentos/reglamento_matricula", 
                                        questions_types = [QuestionType.YES_OR_NOT_ANSWER, QuestionType.FACTOID])

    questions_generator.run()

#save_json("./", "questions_generated", questions_generated)
