import glob
from utils import format_response_json, list_json_to_txt, load_json, read_fragment_doc, save_json, count_tokens, get_completion_from_messages, set_openai_key
from tqdm import tqdm
from dotenv import load_dotenv
import math
import tiktoken
import time
from questions_generation import QuestionType
import os

load_dotenv()

set_openai_key()

encoding = tiktoken.encoding_for_model('gpt-3.5-turbo')

def get_prompt_gen_answers(reglamento, list_questions, q_type, max_size):
    if q_type == QuestionType.YES_OR_NOT_ANSWER:
        prompt = get_prompt_gen_answers_to_yes_or_not(reglamento, list_questions, max_size)
        return prompt
    elif q_type == QuestionType.FACTOID:
        prompt = get_prompt_gen_answers_to_factoid(reglamento, list_questions, max_size)
        return prompt

    
class AnswerGenerator:
    def __init__(self, file_questions):
        self.file_questions = file_questions
        self.all_questions = load_json(self.file_questions)
    def run(self):
        answers_generated = []
        if os.path.exists("./answers_generated.json"):
            answers_generated = load_json("./answers_generated.json")

        print("len(answers_generated):", len(answers_generated))
        for i, block_questions in tqdm(enumerate(self.all_questions), desc= "Generando Respuestas" ):
            print("i:", i)
            if len(answers_generated) > i:
                continue

            questions = block_questions["questions"]
            file_doc = block_questions["document"]
            q_type = block_questions["type"]
            print("\nFile:", file_doc)
            text = read_fragment_doc(file_doc)
            num_tokens = count_tokens(encoding, text)

            if num_tokens < 1000:
                batch_size = 20
            elif num_tokens < 1500:
                batch_size = 15
            else:
                batch_size = 10

            num_batch = math.ceil(len(questions) / batch_size)

            question_answer_pairs = []
            try:
                for i in range(num_batch):
                    start = batch_size * i
                    if i + 1 < num_batch:
                        end = batch_size * (i + 1)
                        list_questions = list_json_to_txt(questions[start:end])
                    else:
                        list_questions = list_json_to_txt(questions[start:])
                    q_type_value = QuestionType[q_type.upper()]
                    qa = self.generate_answers(text, list_questions, q_type_value, 50)
                    question_answer_pairs.extend(qa)

                    time.sleep(5)
            
            except Exception as e:
                save_json("./", "answers_generated", answers_generated)
                raise Exception(e)
                
            answers_generated.append({
                "document": file_doc,
                "question_answer_pairs": question_answer_pairs,
                "type": q_type
            })
            
        
        save_json("./","answers_generated", answers_generated)

    def generate_answers(self, text, list_questions, q_type, max_words = 50):
        prompt = get_prompt_gen_answers(text, list_questions, q_type, max_words)
        messages =  [{'role':'user', 'content':prompt}]
        response = get_completion_from_messages(messages, temperature=0)
        print("response:", response)
        resp_json = format_response_json(response)
        return resp_json
    
def get_prompt_gen_answers_to_yes_or_not(reglamento, list_questions, max_size = 50):
    format_json = """[{"pregunta": "pregunta 1", "respuesta" "respuesta para la pregunta 1"},...]"""

    prompt = f"""
    Imagina que eres un asistente virtual especializado en brindar información sobre la Facultad de Ciencias, incluyendo reglamentos, procedimientos, tramites académicos y cualquier información general relacionada.
    Proporciona las respuestas a una lista de preguntas utilizando la información de un fragmento del reglamento mas abajo.
    Asegúrate de ser elocuente y explicado al proporcionar la respuesta.
    Utiliza la información proporcionada por el fragmento del reglamento delimitado por tres comillas invertidas para inferir las respuestas a la lista de preguntas que se presenta más abajo.
    Asegúrate de que las respuestas no excedan {max_size} palabras.
    Finalmente, proporciona los pares de preguntas y respuestas solo en formato JSON, utilizando el siguiente formato:
    {format_json}
    Lista de preguntas:
    {list_questions}
    Fragmento del Reglamento: ```{reglamento}```
    """
    return prompt

## Funciona bien pero no se expresa elocuentemente
def get_prompt_gen_answers_to_yes_or_not_pred(reglamento, list_questions, max_size = 50):
    format_json = """[{"pregunta": "pregunta 1", "respuesta" "respuesta para la pregunta 1"},...]"""

    prompt = f"""
    Tu tarea consiste en generar respuestas a una lista de preguntas utilizando la información de un fragmento del reglamento de una facultad universitaria. 
    Utiliza la información proporcionada por el fragmento del reglamento delimitado por tres comillas invertidas para inferir las respuestas a la lista de preguntas que se presenta más abajo.
    Asegúrate de que las respuestas no excedan {max_size} palabras.
    Finalmente, proporciona los pares de preguntas y respuestas solo en formato JSON, utilizando el siguiente formato:
    {format_json}
    Lista de preguntas:
    {list_questions}
    Fragmento del Reglamento: ```{reglamento}```
    """
    return prompt
#    Proporciona las {num_questions} preguntas en formato JSON, utilizando el siguiente formato: {format_json}

def get_prompt_gen_answers_to_factoid(reglamento, list_questions, max_size = 50):
    format_json = """[{"pregunta": "pregunta 1", "respuesta" "respuesta para la pregunta 1"},...]"""

    prompt = f"""
    Tu tarea consiste en generar respuestas a una lista de preguntas utilizando un fragmento del reglamento de una facultad universitaria.
    Utiliza el fragmento del reglamento delimitado por tres comillas invertidas para inferir las respuestas la lista de preguntas que se presenta más abajo.
    Asegúrate de que las respuestas no excedan {max_size} palabras. 
    Finalmente, proporciona los pares de preguntas y respuestas solo en formato JSON, utilizando el siguiente formato:
    {format_json}
    Lista de preguntas:
    {list_questions}
    Fragmento del Reglamento: ```{reglamento}```
    """
    return prompt

answer_generator = AnswerGenerator(file_questions= "./questions_generated.json", )

answer_generator.run()
