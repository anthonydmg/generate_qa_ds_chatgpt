import glob
import json
from utils import format_response_json, list_json_to_txt, load_json, read_fragment_doc, save_json, count_tokens, get_completion_from_messages, set_openai_key
from tqdm import tqdm
from dotenv import load_dotenv
import math
import tiktoken
import time
from questions_generation import QuestionType
import os
import re

load_dotenv()

set_openai_key()

encoding = tiktoken.encoding_for_model('gpt-3.5-turbo')

#def get_prompt_gen_answers(reglamento, list_questions, q_type, max_size):
#    if q_type == QuestionType.YES_OR_NOT_ANSWER:
#        prompt = get_prompt_gen_answers(reglamento, list_questions, max_size)
#        return prompt
#    elif q_type == QuestionType.FACTOID:
#        prompt = get_prompt_gen_answers(reglamento, list_questions, max_size)
#        return prompt

    
class AnswerGenerator:
    def __init__(self, file_questions):
        self.file_questions = file_questions
        self.all_questions = load_json(self.file_questions)
    def run(self):
        answers_generated = []
        if os.path.exists("./answers_generated.json"):
            answers_generated = load_json("./answers_generated.json")

        #print("len(answers_generated):", len(answers_generated))
        progress_bar = tqdm(len(self.all_questions), desc= "Generando Respuestas" )
        total_qa = 0
        for i, block_questions in enumerate(self.all_questions):
            print("i:", i)
            if len(answers_generated) > i:
                total_qa = sum([len(ans["question_answer_pairs"]) for ans in answers_generated])
                progress_bar.update(1)
                continue

            questions = block_questions["questions"]
            file_doc = block_questions["document"]
            q_type = block_questions["type"]
            print("\nFile:", file_doc)
            text = read_fragment_doc(file_doc)
            num_tokens = count_tokens(encoding, text)

            if num_tokens < 1000:
                batch_size = 15
            elif num_tokens < 1500:
                batch_size = 10
            else:
                batch_size = 10

            num_batch = math.ceil(len(questions) / batch_size)

            question_answer_pairs = []
            try:
                for i in range(num_batch):
                    start = batch_size * i
                    if i + 1 < num_batch:
                        end = batch_size * (i + 1)
                        b_questions = questions[start:end]
                    else:
                        b_questions = questions[start:]
                    print("Total de preguntas:", len(b_questions))
                    list_questions = list_json_to_txt(b_questions)
                    #q_type_value = QuestionType[q_type.upper()]
                    qa = self.generate_answers(text, list_questions, len(b_questions) , 50)
                    total_qa += len(qa)
                    print("Total de pares de preguntas y respuestas: ", len(qa))
                    if abs(len(b_questions) - len(qa)) > 3:
                        print(f"El numero de preguntas y respuesta es diferente: preguntas={len(b_questions)}, pares={len(qa)}")
                        raise Exception("El numero de preguntas y respuestas es diferente")
                   
                    question_answer_pairs.extend(qa)

                    time.sleep(10)
                progress_bar.set_postfix({"total_preguntas": total_qa})

                progress_bar.update(1)
            except Exception as e:
                save_json("./", "answers_generated", answers_generated)
                raise Exception(e)
            print("question_answer_pairs:", question_answer_pairs)
            answers_generated.append({
                "document": file_doc,
                "question_answer_pairs": question_answer_pairs,
                "type": q_type
            })
            #break
        
        save_json("./","answers_generated", answers_generated)

    def generate_answers(self, text, list_questions, len_questions, max_words = 50):
        #prompt = get_prompt_gen_answers(text, list_questions, q_type, max_words)
        prompt = get_prompt_gen_answers(text, list_questions, len_questions , max_words)
        messages =  [{'role':'user', 'content':prompt}]
        response = get_completion_from_messages(messages, temperature=0)
        print("response:", response)
        # Utilizar expresiones regulares para eliminar el fragmento ```json`
        texto_sin_fragmento_json = re.sub(r'```\s*json', '', response)
        # Utilizar expresiones regulares para eliminar el fragmento ```json`
        texto_sin_fragmento_json = re.sub(r'```', '', texto_sin_fragmento_json)
        texto_sin_fragmento_json = texto_sin_fragmento_json.strip()
        resp_json = json.loads(texto_sin_fragmento_json)
        return resp_json

def get_prompt_gen_answers_v2(reglamento, list_questions, max_size = 50):
    format_json = """[{"pregunta": "pregunta 1", "respuesta" "respuesta para la pregunta 1"},...]"""

    prompt = f"""
    Tu tarea es generar respuestas informativas y utiles a las preguntas listadas abajo, basado en la informacion sobre reglamentos de la Facultad de Ciencias de la Universidad Nacional de Ingenieria (delimitada por tres comillas invertidas).
    Antes de crear las respuestas asegúrate de cumplir estrictamente cada uno de los siguientes criterios:
        1. Reponde a las preguntas que no tengan respuesta en la informacion proveida indicado que no posees informacion para poder responder a dicha pregunta.
        2. Para las pregunta que si tengan respuesta justifica de manera detallada las razones de la respuesta basada en la informacion proveida.
            
    Finalmente, proporciona los pares de preguntas y respuestas solo en formato JSON, utilizando el siguiente formato:
    {format_json}
    Lista de preguntas:
    {list_questions}
    Fragmento del texto: ```{reglamento}```
    """
    return prompt


def get_prompt_gen_answers(reglamento, list_questions, len_questions , max_size = 50):
    format_json = """[{"pregunta": "contenido de la pregunta 1", "respuesta": "respuesta para la pregunta 1"}, ...]"""

    prompt = f"""
    Tu tarea es generar respuestas informativas y útiles para cada una de las {len_questions} preguntas listadas abajo, basado en la información sobre reglamentos de la Facultad de Ciencias de la Universidad Nacional de Ingeniería (delimitada por tres comillas invertidas).
    Antes de crear las respuestas, asegúrate estrictamente de cumplir cada uno de los siguientes criterios:
        1. Indica claramente que no posees información para responder a la pregunta si esta no tiene respuesta basada en la información proporcionada.
        2. Para las preguntas que sí tengan respuesta, justifica detalladamente las razones de la respuesta basada en la información proporcionada.
        3. Proporciona información complementaria en las respuestas que sea útil basado en las preguntas.
        4. Evita mencionar numerales de artículos que no mencionen al documento al que pertenecen en las respuestas; en su lugar, puedes referencia directamente al reglamento de matrícula de la Facultad de Ciencias de la UNI.
        5. El reglamento solo debe referenciarse de manera completa como el reglamento de matrícula de la Facultad de Ciencias de la UNI dentro de las respuestas.
    Finalmente, presenta cada una de las {len_questions} preguntas listadas abajo y sus respuestas en el siguiente formato JSON:
    {format_json}
    Lista de preguntas:
    <<{list_questions}>>
    Fragmento del texto: ```{reglamento}```
    """
    return prompt

def get_prompt_gen_answers_to_yes_or_not(reglamento, list_questions, max_size = 50):
    format_json = """[{"pregunta": "pregunta 1", "respuesta" "respuesta para la pregunta 1"},...]"""

    prompt = f"""
    Tu tarea es generar respuestas informativas y utiles a las preguntas listadas abajo, basado en la informacion sobre reglamentos de la Facultad de Ciencias de la Universidad Nacional de Ingenieria (delimitada por tres comillas invertidas).
    Antes de crear las respuestas asegúrate de cumplir estrictamente cada uno de los siguientes criterios:
        1. Reponde a las preguntas que no tengan respuesta en la informacion proveida indicado que no posees informacion para poder responder a dicha pregunta.
        2. Para las pregunta que si tengan respuesta justifica de manera detallada las razones de la respuesta basada en la informacion proveida.
            
    Finalmente, proporciona los pares de preguntas y respuestas solo en formato JSON, utilizando el siguiente formato:
    {format_json}
    Lista de preguntas:
    {list_questions}
    Fragmento del texto: ```{reglamento}```
    """
    return prompt

def get_prompt_gen_answers_to_factoid(reglamento, list_questions, max_size = 50):
    format_json = """[{"pregunta": "pregunta 1", "respuesta" "respuesta para la pregunta 1"},...]"""

    prompt = f"""
    Tu tarea es generar respuestas informativas y utiles a las preguntas listadas abajo, basado en la informacion sobre reglamentos de la Facultad de Ciencias de la Universidad Nacional de Ingenieria (delimitada por tres comillas invertidas).
    Antes de crear las respuestas asegúrate de cumplir estrictamente cada uno de los siguientes criterios:
        1. Reponde a las preguntas que no tengan respuesta en la informacion proveida indicado que no posees informacion para poder responder a dicha pregunta.
        2. Para las pregunta que si tengan respuesta justifica de manera detallada las razones de la respuesta basada en la informacion proveida.
    Finalmente, proporciona los pares de preguntas y respuestas solo en formato JSON, utilizando el siguiente formato:
    {format_json}
    Lista de preguntas:
    {list_questions}
    Fragmento del texto: ```{reglamento}```
    """
    return prompt

answer_generator = AnswerGenerator(file_questions= "./questions_generated.json", )

answer_generator.run()
