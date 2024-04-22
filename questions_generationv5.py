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


# Este es el ultimo
#Me gusta al 92.8 porciento
def get_prompt_gen_factoid_questions_v15(reglamento, num_questions = 20):
    print(f"\nNumero de preguntas a crear {num_questions}")
    prompt = f"""
Tu tarea es generar al menos {num_questions} preguntas basadas en la información proporcionada sobre reglamentos académicos de la Facultad de Ciencias de la UNI (delimitada por tres comillas invertidas). 
Antes de crear una pregunta asegúrate de cumplir estrictamente cada uno de los siguientes criterios:
    - Evita mencionar o citar numerales de artículos específicos en las preguntas.
    - No formules preguntas que requieran identificar el numero de artículos específicos en el reglamento.
    - No crees preguntas que mencionen directamente datos especificos.
    - Concéntrate en preguntas prácticas y relevantes para usuarios como alumnos, docentes o el público en general, que puedan ser respondidas con la información proporcionada.
Genera las {num_questions} preguntas y justifica para cada pregunta por que cumple con cada uno de los criterios mencionados anteriormente.
Fragmento de texto: ```{reglamento}```
    """
    return prompt

def get_prompt_gen_factoid_questions(reglamento, num_questions = 20):
    print(f"\nNumero de preguntas a crear {num_questions}")
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

def get_prompt_gen_factoid_questions(reglamento, num_questions = 20):
    print(f"\nNumero de preguntas a crear {num_questions}")
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
            if num_tokens < 300:
                num_questions = 4
            if num_tokens < 500:
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
            if num_tokens < 300:
                num_questions = 5
            if num_tokens < 500:
                num_questions = 10
            elif num_tokens < 1000:
                num_questions = 20
            elif num_tokens < 1500:
                num_questions = 30
            elif num_tokens < 2000:
                num_questions = 40
            elif num_tokens < 2500:
                num_questions = 50
            else: 
                num_questions = 60

        return num_questions

    def run(self):
        questions_generated = []
        #documents = glob.glob(f"{self.dir_documents}/*/*.txt")
        #documents.sort()
        #print("documents:", documents)
        
        total_subtopics = len(self.topics_data)
        print(f"{total_subtopics} subtemas encontrados...")
        # unir subtemas con menos de 200 temas
        # self.join_subtopics_with_few_content
        
        subtopics_few_content_idx = []

        context_subtopics = []
        for idx ,subtopic in enumerate(self.topics_data):
            num_tokens = count_tokens(encoding, text = subtopic["content"])
            print("num_tokens:", num_tokens)
            
            if num_tokens <= 200:
                subtopics_few_content_idx.append(idx)
            
            
            context_text = subtopic["subtopic"] + "\n" + subtopic["content"]
            
            context_subtopics.append({
                "context": context_text,
                "subtopic": subtopic["subtopic"],
                "topic": subtopic["topic"],
                "source": subtopic["source"]
                })
        
        join_subtopics = lambda s1, s2: { 
                "context": s1["context"] + s2["context"], 
                "subtopic": [s1["subtopic"], s2["subtopic"]],
                "topic": [s1["topic"],s2["topic"]],
                "source": [s1["source"],s2["source"]]  
                }
        
        print("subtopics_few_content_idx:", subtopics_few_content_idx)
        
        new_content_subtopics = []

        for idx in subtopics_few_content_idx:
            
            subtopic = context_subtopics[idx]
            if idx == 0:
                 context_subtopics[idx] = join_subtopics(subtopic, context_subtopics[idx + 1])
                 context_subtopics =  context_subtopics[:idx + 1] +  context_subtopics[idx + 2:]
            elif idx == total_subtopics - 1:
                 context_subtopics[idx] = join_subtopics(context_subtopics[idx - 1], subtopic)
                 context_subtopics =  context_subtopics[:idx -1] +  context_subtopics[idx:]
            elif subtopic["topic"]!= context_subtopics[idx + 1]["topic"]:
                context_subtopics[idx] = join_subtopics(context_subtopics[idx - 1], subtopic)
                context_subtopics =  context_subtopics[:idx -1] +  context_subtopics[idx:]
            elif subtopic["topic"]!= context_subtopics[idx - 1]["topic"]:
                context_subtopics[idx] = join_subtopics(subtopic, context_subtopics[idx + 1])
                context_subtopics =  context_subtopics[:idx + 1] +  context_subtopics[idx + 2:]
            else:
                if count_tokens(encoding, context_subtopics[idx - 1]["context"]) < count_tokens(encoding, context_subtopics[idx + 1]["context"]):
                    context_subtopics[idx] = join_subtopics(context_subtopics[idx - 1], subtopic)
                    context_subtopics =  context_subtopics[:idx -1] +  context_subtopics[idx:]
                else:
                    context_subtopics[idx] = join_subtopics(subtopic, context_subtopics[idx + 1])
                    context_subtopics =  context_subtopics[:idx + 1] +  context_subtopics[idx + 2:]

        save_json("./", "context_subtopics", context_subtopics)
        


    def format_response_to_json(self, response_questions):
        format_json = """{"preguntas": ["pregunta 1 generada", "pregunta 2 generada", ...]}"""

        prompt = f"""
        Tu tarea es proporcionar la lista de preguntas de abajo delimitada por tres comillas invertidas en el siguente formato: {format_json} 
        Asegúrate de copiar cada una de las preguntas sin su enumeración en el formato indicado anteriormente y no omitas ninguna pregunta.
        Lista de preguntas: 
        ```{response_questions}```
        """
        messages =  [{'role':'user', 'content':prompt}]
        response = get_completion_from_messages(messages, temperature=0)
        resp_json = format_response_json(response)
        print("resp_json:", resp_json)
        return resp_json

    def filter_questions(self, questions):
        questions = [ q for q in questions if "presente reglamento" not in q.lower() ]
        return questions

    def extract_questions_from_response(self, response):
        resp_json = self.format_response_to_json(response)
        questions = resp_json["preguntas"]
        return questions
    
    def extract_questions_from_response_regex(self, response):
        patron = r'\d+\.\s(¿[^\?]+?\?)'
        preguntas = re.findall(patron, response)
        return preguntas

    def extract_questions_answers_from_response_regex(self, response):
        pattern = r'\d+\.\s*(.*?)\s*Respuesta:\s*(.*?)(?=\d+\.|\Z)'
        matches = re.findall(pattern, response, re.DOTALL)
        question_answer_pairs = [{"question": question, "answer": answer} for (question, answer) in matches]
        return question_answer_pairs

    def generate_questions_answers(self, text, question_type, num_questions = 30):
        prompt = get_prompt_gen_questions(text, question_type, num_questions)
        #print("Size input: " , count_tokens(encoding ,prompt))
 
        messages =  [{'role':'user', 'content':prompt}]
        response = get_completion_from_messages(
            messages, 
            temperature=0, 
            model= "gpt-4-1106-preview"
        )
        print("response:", response)
        #print("Size output: " , count_tokens(encoding ,response))
 
        questions = self.extract_questions_from_response_regex(response)
        print("Total de preguntas generadas:", len(questions))
        if abs(num_questions - len(questions)) > 3:
            print("Faltan preguntas")
            content = prompt + "\n" + response
            messages =  [{'role':'user', 'content':content}]
            response = get_completion_from_messages(
                messages, 
                temperature=0, 
                #model="gpt-4-1106-preview"
            )
            print("response:", response)
            next_questions = self.extract_questions_from_response_regex(response)
            print("Total de preguntas generadas:", len(next_questions))
            questions  = questions + next_questions
        print("Total de preguntas extraidas:", len(questions))

        return questions
    
if __name__ == "__main__":
    questions_generator = QuestionGenerator(topics_data= "./topics_selected.json", 
                                        questions_types = [QuestionType.YES_OR_NOT_ANSWER, 
                                                           QuestionType.FACTOID])
 
    questions_generator.run()

#save_json("./", "questions_generated", questions_generated)
