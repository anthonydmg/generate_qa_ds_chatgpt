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

#def +(reglamento, list_questions, q_type, max_size):
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

        progress_bar = tqdm(len(self.all_questions[0:34]), desc= "Generando Respuestas" )
        total_qa = 0
        for i, block_questions in enumerate(self.all_questions[0:34]):
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

            batch_size = 25
         
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
            #print("question_answer_pairs:", question_answer_pairs)
            answers_generated.append({
                "document": file_doc,
                "question_answer_pairs": question_answer_pairs,
                "type": q_type
            })
            #break
        
        save_json("./","answers_generated", answers_generated)
        
    def extract_questions_answers_from_response_regex(self, response):
        pattern = r'\d+\.-\s*(.*?)\s*Respuesta:\s*(.*?)(?=\d+\.-|$)'
        
        matches = re.findall(pattern, response, re.DOTALL)
        question_answer_pairs = [{"question": question, "answer": answer} for (question, answer) in matches]
        return question_answer_pairs
    
    def generate_answers(self, text, list_questions, len_questions, max_words = 50):
        #prompt = get_prompt_gen_answers(text, list_questions, q_type, max_words)
        prompt = get_prompt_gen_answers(text, list_questions, len_questions , max_words)
        messages =  [{'role':'user', 'content':prompt}]
        response = get_completion_from_messages(
            messages, 
            temperature=0,
            model="gpt-4-1106-preview"
            )
        print("response:", response)
        
        qa_pairs = self.extract_questions_answers_from_response_regex(response)
        print(f"len_questions={len_questions}, qa_pairs={len(qa_pairs)}")
        if abs(len_questions - len(qa_pairs)) > 1:
            print("Faltan preguntas")
            content = prompt + "\n" + response
            messages =  [{'role':'user', 'content':content}]
            response = get_completion_from_messages(
                messages, 
                temperature=0, 
                model="gpt-4-1106-preview"
            )
            print("response:", response)
            #print("Size output: " , count_tokens(encoding ,response))
            next_qa_pairs = self.extract_questions_answers_from_response_regex(response)
            print("Total de preguntas generadas:", len(next_qa_pairs))
            qa_pairs  = qa_pairs + next_qa_pairs
        
        # Utilizar expresiones regulares para eliminar el fragmento ```json`
        #texto_sin_fragmento_json = re.sub(r'```\s*json', '', response)
        
        # Utilizar expresiones regulares para eliminar el fragmento ```json`
        #texto_sin_fragmento_json = re.sub(r'```', '', texto_sin_fragmento_json)
        #texto_sin_fragmento_json = texto_sin_fragmento_json.strip()
        #resp_json = json.loads(texto_sin_fragmento_json)
        return qa_pairs

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

#     que, al hacer referencia al reglamento del cual proviene la información proporcionada, utilices únicamente su denominación completa y menciones explícitamente la afiliación con la Universidad Nacional de Ingeniería (UNI).
#         2. Si no puedes dar una respuesta completa con la información proporcionada, ofrece una respuesta parcial y complementa indicando de que tema especifico no posees informacion suficiente para ofrecer una respuesta completa.
    
def get_prompt_gen_answers(reglamento, list_questions, len_questions , max_size = 50):

    prompt = f"""
    Tu tarea es generar respuestas informativas y útiles para cada una de las {len_questions} preguntas listadas abajo, basado en la información sobre reglamentos de la Facultad de Ciencias de la Universidad Nacional de Ingeniería (delimitada por tres comillas invertidas).
    Antes de crear las respuestas, asegúrate estrictamente de cumplir cada uno de los siguientes criterios:
        1. Justifica detalladamente las razones de la respuesta basandote exclusivamente en la información proporcionada.
        2. Evita mencionar numerales de artículos que no mencionen al documento al que pertenecen en las respuestas; en su lugar, puedes referenciar directamente al reglamento donde pertenecen estos articulos.
        3. En las respuestas, abstente de hacer referencia directa al fragmento de texto proporcionado y, en su lugar, utiliza la denominación completa del reglamento correspondiente para respaldar tus argumentos.
        4. El reglamento correspondiente solo debe referenciarse con su denominación completa y haciendo referencia a la Universidad Nacional de Ingeniería (UNI) dentro de las respuestas.
        5. Suministra detalles complementarios pertinentes basados en la información proporcionada para enriquecer las respuestas a las preguntas.

    Finalmente, presenta cada una de las {len_questions} preguntas listadas abajo y sus respuestas de manera enumerada utilizando el guion punto como marcador de la siguente manera:
    
    1.- pregunta...
    Respuesta: ...
    2.- pregunta...
    Respuesta: ...

    Lista de preguntas:
    <<{list_questions}>>
    Fragmento del texto: ```{reglamento}```
    """
    return prompt

def get_prompt_gen_answers_vf3(reglamento, list_questions, len_questions , max_size = 50):

    prompt = f"""
    Tu tarea es generar respuestas informativas y útiles para cada una de las {len_questions} preguntas listadas abajo, basado en la información sobre reglamentos de la Facultad de Ciencias de la Universidad Nacional de Ingeniería (delimitada por tres comillas invertidas).
    Antes de crear las respuestas, asegúrate estrictamente de cumplir cada uno de los siguientes criterios:
        1. Indica claramente que no posees información para responder a la pregunta si esta no tiene respuesta basada en la información proporcionada.
        2. Para las preguntas que sí tengan respuesta, justifica detalladamente las razones de la respuesta basada en la información proporcionada.
        3. Evita mencionar numerales de artículos que no mencionen al documento al que pertenecen en las respuestas; en su lugar, puedes referenciar directamente al reglamento donde pertenecen estos articulos.
        4. El reglamento solo debe referenciarse con su denominación completa y haciendo referencia a la Universidad Nacional de Ingeniería (UNI) dentro de las respuestas.
        5. Suministra detalles complementarios pertinentes basados en la información proporcionada para enriquecer las respuestas a las preguntas.

    Finalmente, presenta cada una de las {len_questions} preguntas listadas abajo y sus respuestas en el siguiente formato:
    
    1. pregunta...
    Respuesta: ....
    2. pregunta...
    Respuesta: ...
    
    Lista de preguntas:
    <<{list_questions}>>
    Fragmento del texto: ```{reglamento}```
    """
    return prompt

def get_prompt_gen_answers_vf2(reglamento, list_questions, len_questions , max_size = 50):
    format_json = """[{"pregunta": "contenido de la pregunta 1", "respuesta": "respuesta para la pregunta 1"}, ...]"""

    prompt = f"""
    Tu tarea es generar respuestas informativas y útiles para cada una de las {len_questions} preguntas listadas abajo, basado en la información sobre reglamentos de la Facultad de Ciencias de la Universidad Nacional de Ingeniería (delimitada por tres comillas invertidas).
    Antes de crear las respuestas, asegúrate estrictamente de cumplir cada uno de los siguientes criterios:
        1. Indica claramente que no posees información para responder a la pregunta si esta no tiene respuesta basada en la información proporcionada.
        2. Para las preguntas que sí tengan respuesta, justifica detalladamente las razones de la respuesta basada en la información proporcionada.
        3. Evita mencionar numerales de artículos que no mencionen al documento al que pertenecen en las respuestas; en su lugar, puedes referencia directamente al reglamento 
        de matrícula de la Facultad de Ciencias de la UNI.
        4. El reglamento solo debe referenciarse de manera completa como el reglamento de matrícula de la Facultad de Ciencias de la UNI dentro de las respuestas.
        5. Suministra detalles complementarios pertinentes basados en la información proporcionada para enriquecer las respuestas a las preguntas.

    Finalmente, presenta cada una de las {len_questions} preguntas listadas abajo y sus respuestas en el siguiente formato:
    
    1. pregunta...
    Respuesta: ....
    2. pregunta...
    Respuesta: ...
    
    Lista de preguntas:
    <<{list_questions}>>
    Fragmento del texto: ```{reglamento}```
    """
    return prompt

def get_prompt_gen_answers_vf(reglamento, list_questions, len_questions , max_size = 50):
    format_json = """[{"pregunta": "contenido de la pregunta 1", "respuesta": "respuesta para la pregunta 1"}, ...]"""

    prompt = f"""
    Tu tarea es generar respuestas informativas y útiles para cada una de las {len_questions} preguntas listadas abajo, basado en la información sobre reglamentos de la Facultad de Ciencias de la Universidad Nacional de Ingeniería (delimitada por tres comillas invertidas).
    Antes de crear las respuestas, asegúrate estrictamente de cumplir cada uno de los siguientes criterios:
        1. Indica claramente que no posees información para responder a la pregunta si esta no tiene respuesta basada en la información proporcionada.
        2. Para las preguntas que sí tengan respuesta, justifica detalladamente las razones de la respuesta basada en la información proporcionada.
        3. Evita mencionar numerales de artículos que no mencionen al documento al que pertenecen en las respuestas; en su lugar, puedes referencia directamente al reglamento de matrícula de la Facultad de Ciencias de la UNI.
        4. El reglamento solo debe referenciarse de manera completa como el reglamento de matrícula de la Facultad de Ciencias de la UNI dentro de las respuestas.
        5. Suministra detalles complementarios pertinentes basados en la información proporcionada para enriquecer las respuestas a las preguntas.

    Finalmente, presenta cada una de las {len_questions} preguntas listadas abajo y sus respuestas en el siguiente formato JSON:
    {format_json}
    Lista de preguntas:
    <<{list_questions}>>
    Fragmento del texto: ```{reglamento}```
    """
    return prompt

answer_generator = AnswerGenerator(file_questions= "./questions_generated_gpt4-turbo.json", )

answer_generator.run()
