import openai
import json
from dotenv import load_dotenv
import os
from utils import save_json, load_json, format_response_json, read_fragment_doc, list_json_to_txt
import glob
import tiktoken
import time
from tqdm import tqdm

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
        prompt = get_prompt_gen_yes_or_not_questions(text, num_questions)
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

def get_prompt_gen_yes_or_not_questions(reglamento, num_questions = 20):
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
    
    prompt = f"""Tu tarea es generar {num_questions} preguntas que busquen obtener información precisa y objetiva dentro de las disposiciones y normas en un reglamento de una facultad universitaria.
    Genera las {num_questions} preguntas a partir del fragmento del reglamento debajo, delimitado por tres comillas invertidas.
    Muestra las {num_questions} preguntas el siguiente formato JSON:
    {format_json}
    Fragmento del Reglamento: ```{reglamento}```
    """
    return prompt

## Las preguntas deben tener un máximo de 50 palabras.
def count_tokens(encoding, text): 
    return len(encoding.encode(text))

set_openai_key()

encoding = tiktoken.encoding_for_model('gpt-3.5-turbo')

class QuestionGenerator:
    def __init__(self, dir_documents, questions_types):
        self.dir_documents = dir_documents
        self.questions_types = questions_types
    
    def run(self):
        questions_generated = []
        print(self.dir_documents)
        for file_text in tqdm(glob.glob(f"{self.dir_documents}/*.txt"), desc= "Generando Preguntas"):
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
                questions = generate_questions(text, QuestionType.YES_OR_NOT_ANSWER, num_questions = num_questions)
                print("questions:", questions)
                questions_generated.append({"document": file_text, "type": "yes_or_not_answer", "questions": questions})
                ## 

            except Exception as e:
                save_json("./", "questions_generated", questions_generated)
                print("Error:", e)
            time.sleep(5)
            break
        save_json("./", "questions_generated", questions_generated)

text = read_fragment_doc("documentos/reglamento_matricula/capitulo2_parte2.txt")

prompt = get_prompt_gen_factoid_questions(text, num_questions = 40)
print("prompt: ", prompt)
messages =  [{'role':'user', 'content':prompt}]
response = get_completion_from_messages(messages, temperature=0)
resp_json = format_response_json(response)
questions = resp_json["preguntas"]
print("questions: ",questions)
print("questions: ",len(questions))
#questions_generator = QuestionGenerator(dir_documents = "./documentos/reglamento_matricula", questions_types = [QuestionType.YES_OR_NOT_ANSWER])

#questions_generator.run()

#save_json("./", "questions_generated", questions_generated)
