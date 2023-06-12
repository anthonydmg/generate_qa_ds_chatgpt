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

class QuestionType(Enum):
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
        prompt = get_prompt_gen_yes_or_not_questions(text, num_questions)
        return prompt
    elif question_type == QuestionType.FACTOID:
        prompt = get_prompt_gen_factoid_questions(text, num_questions)
        return prompt



def get_prompt_gen_yes_or_not_questions(reglamento, num_questions = 20):
    format_json = """{"preguntas": ["pregunta 1 generada", "pregunta 2 generada", ...]"""
    
    prompt = f"""
    Tu tarea es generar {num_questions} preguntas que se puedan responder con un Sí ó No, a partir de la información en un fragmento del reglamento de una facultad universitaria.
    Asegúrate que las preguntas no excedan las 30 palabras.
    Utiliza el fragmento del reglamento de debajo, delimitado por tres comillas invertidas para generar las preguntas que se puedan responder con un Sí ó No en base a la información del fragmento del reglamento.
    Finalmente, proporciona las preguntas en el siguiente formato JSON:
    {format_json}
    Fragmento del Reglamento: ```{reglamento}```
    """
    return prompt
#  Asegúrate que las preguntas que se puedan responder con un Sí ó No en base a la información del fragmento del reglamento.
#  Asegúrate que las preguntas no excedan las 30 palabras. 
def get_prompt_gen_yes_or_not_questions_v1(reglamento, num_questions = 20):
    format_json = """{"preguntas": ["pregunta 1 generada", "pregunta 2 generada", ...]"""
    
    prompt = f"""
    Tu tarea es generar al menos {num_questions} preguntas que se puedan responder con un Sí ó No a partir de un fragmento del reglamento de una facultad universitaria. 
    Asegúrate que las preguntas se pueda responder directamente con un Sí ó No en base a la información del fragmento del reglamento.
    Las preguntas no deben superar las 25 palabras.
    Genera las preguntas para el reglamento de debajo, delimitado por tres comillas invertidas.
    Muestra las preguntas en el siguiente formato JSON:
    {format_json}
    Fragmento del Reglamento: ```{reglamento}```
    """
    return prompt

def get_prompt_gen_factoid_questions(reglamento, num_questions = 20):
    format_json = """{"preguntas": ["pregunta 1 generada", "pregunta 2 generada", ...]"""
    
    prompt = f"""Tu tarea es generar {num_questions} preguntas concisas y precisas basadas en un fragmento del reglamento de una facultad universitaria. 
    Asegúrate que las preguntas no excedan las 30 palabras.
    Utiliza el fragmento del reglamento de debajo, delimitado por tres comillas invertidas para generar las preguntas.
    Proporciona las preguntas en el siguiente formato JSON: {format_json}
    Fragmento del Reglamento: {reglamento}
    """
    return prompt

def get_prompt_gen_factoid_questions_v1(reglamento, num_questions = 20):
    format_json = """{"preguntas": ["pregunta 1 generada", "pregunta 2 generada", ...]"""
    
    prompt = f"""Tu tarea es generar {num_questions} preguntas concisas y precisas basadas en un fragmento del reglamento de una facultad universitaria. 
    Las preguntas deben tener un máximo de 50 palabras. 
    Proporciona las {num_questions} preguntas en formato JSON, utilizando el siguiente formato: {format_json}
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
    
    def run(self):
        questions_generated = []
        #for file_text in tqdm(glob.glob(f"{self.dir_documents}/*.txt"), desc= "Generando Preguntas"):
        documents = glob.glob(f"{self.dir_documents}/*.txt")
        documents.sort()
        print("Inicia Generación de preguntas...")
        #return
        for file_text in tqdm(documents, desc= "Documentos"):
            text = read_fragment_doc(file_text)
            num_tokens = count_tokens(encoding ,text)
            if num_tokens < 1000:
                num_questions = 20
            elif num_tokens < 1500:
                num_questions = 30
            else:
                num_questions = 40
            try:    
                ## Generar preguntas con respuesta de si o no
                for qt in self.questions_types:
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

#text = read_fragment_doc("documentos/reglamento_matricula/capitulo2_parte2.txt")

#prompt = get_prompt_gen_factoid_questions(text, num_questions = 40)
#print("prompt: ", prompt)
#messages =  [{'role':'user', 'content':prompt}]
#response = get_completion_from_messages(messages, temperature=0)
#resp_json = format_response_json(response)
#questions = resp_json["preguntas"] 
#print("questions: ",questions)
#print("questions: ",len(questions))
if __name__ == "__main__":
    questions_generator = QuestionGenerator(dir_documents = "./documentos/reglamento_matricula", 
                                        questions_types = [QuestionType.YES_OR_NOT_ANSWER, QuestionType.FACTOID])

    questions_generator.run()

#save_json("./", "questions_generated", questions_generated)
