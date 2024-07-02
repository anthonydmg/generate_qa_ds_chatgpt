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

class AnswerGenerator:
    def __init__(self, file_questions):
        self.file_questions = file_questions
        self.all_questions = load_json(self.file_questions)
    def run(self):
        answers_generated = []
        if os.path.exists("./answers_generated.json"):
            answers_generated = load_json("./answers_generated.json")

        questions_topics_to_answers = self.all_questions[6:7]

        progress_bar = tqdm(len(questions_topics_to_answers), desc= "Generando Respuestas" )
        total_qa = 0
        
        for i, block_questions in enumerate(questions_topics_to_answers):
            print("i:", i)
            if len(answers_generated) > i:
                total_qa = sum([len(ans["question_answer_pairs"]) for ans in answers_generated])
                progress_bar.update(1)
                continue

            questions = block_questions["questions"]
            print("\nNumero de preguntas:", len(questions))
            source_context = block_questions["source_context"]
            q_type = block_questions["type"]
            general_topic = block_questions["topic"]
            text = block_questions["context"]

            print("\nFile:", source_context)
            #text = read_fragment_doc(file_doc)

            batch_size = 5
         
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
                   

                    #list_questions = [q["question"] for q in  b_questions]
                    text_questions = list_json_to_txt(b_questions, marcador = ".-")
                    
                    question_answers = self.generate_answers(text, text_questions, len(b_questions))

                    #answers = [ qa["answer"] for qa in question_answers]

                    index_to_mod = self.find_index_answers_with_mentions_articles(question_answers)

                    if len(index_to_mod) > 0:
                        answers = [question_answers[i_qa]["answer"] for i_qa in index_to_mod]
                        answers_mod = self.mod_texts_skip_mentions_articles(answers)
                        
                        for i_ans_mod, answer_mod in enumerate(answers_mod):
                            question_answers[index_to_mod[i_ans_mod]]["answer"] = answer_mod
         
                    #answers_mod = self.mod_texts_skip_mentions_articles(answers)

                    total_qa += len(question_answers)
                    print("Total de pares de preguntas y respuestas: ", len(question_answers))
                    
                    if abs(len(b_questions) - len(question_answers)) > 3:
                        print(f"El numero de preguntas y respuesta es diferente: preguntas={len(b_questions)}, pares={len(qa)}")
                        raise Exception("El numero de preguntas y respuestas es diferente")
                   
                        
                    question_answer_pairs.extend(question_answers)
                    time.sleep(10)

                progress_bar.set_postfix({"total_preguntas": total_qa})

                progress_bar.update(1)
            except Exception as e:
                save_json("./", "answers_generated", answers_generated)
                raise Exception(e)
            
            answers_generated.append({
                "source_context": source_context,
                "question_answer_pairs": question_answer_pairs,
                "type": q_type,
                "topic": general_topic,
                "context": text
            })
        
        save_json("./","answers_generated", answers_generated)
    
    def find_index_answers_with_mentions_articles(self, question_answers):
        index_to_mod = []
        
        for i_qa, qa_dict in enumerate(question_answers):
            answer = qa_dict["answer"]
            if "art." in answer.lower() or "artículo" in answer.lower():
                index_to_mod.append(i_qa)
        
        return index_to_mod

    def extract_questions_answers_from_response_regex(self, response):
        pattern = r'\d+\.-\s*(.*?)\s*Respuesta:\s*(.*?)(?=\d+\.-|\Z)'
        
        matches = re.findall(pattern, response, re.DOTALL)
        question_answer_pairs = [{"question": question, "answer": answer} for (question, answer) in matches]
        return question_answer_pairs
    
    
    def get_prompt_skip_mentions_information(self, textos):
        textos_list = list_json_to_txt(textos, marcador = ".-")
        prompt = f"""
        Tu tarea consiste en eliminar las partes del texto que menciones específicamente a artículos de reglamentos en los siguientes textos, sin alterar el sentido original de la información en ellos.            Es importante que no alteres las palabras originales de los textos.
        Preguntas: 
        {textos_list}
        Por favor, enumera las versiones modificadas de los textos para eliminar las referencias específicas a los numerales y artículos, manteniendo el mismo orden en que se proporcionaron los textos originales. 
        Utiliza el siguiente formato de enumeración con punto-guión:
            1.- Aqui el texto modificado
            2.- Aqui el texto modificado
            ...
            """
        return prompt
   
    def extract_texts_from_response_regex(self, response):
        patron = r'\d+\.-\s*(.*?)(?=\d+\.-|\Z)'
        preguntas = re.findall(patron, response, re.DOTALL)
        return preguntas
    
    def mod_texts_skip_mentions_articles(self, textos):
        prompt = self.get_prompt_skip_mentions_information(textos)
        print("\nReformurlando textos con mencion de articulos....\n")
        #print("\n\nprompt skip mentions articules:\n", prompt)
        messages =  [{'role':'user', 'content':prompt}]
        response = get_completion_from_messages(
            messages, 
            temperature=0,
            #model="gpt-3.5-turbo-0125" 
            #model= "gpt-4-1106-preview"
        )
        print("\nresponse:", response)
        print()
        textos_mod = self.extract_texts_from_response_regex(response)
        return textos_mod


    def generate_answers(self, text, list_questions, len_questions):
        prompt = get_prompt_gen_answers(text, list_questions, len_questions)
        #print("\n\nprompt:", prompt)
        messages =  [{'role':'user', 'content':prompt}]
        response = get_completion_from_messages(
            messages, 
            temperature=0,
           # model="gpt-4-1106-preview"
            model="gpt-3.5-turbo-0613"
            )
        
        print("\nresponse:", response)
        
        time.sleep(5)

        #messages =  [{'role':'user', 'content':prompt_verify}]
        #response_verify = get_completion_from_messages(
        #    messages, 
        #    temperature=0,
        #    model="gpt-3.5-turbo-0613"
        #    )
        
        #print("\nresponse_verify:", response_verify)
        
        qa_pairs = self.extract_questions_answers_from_response_regex(response)
        print(f"len_questions={len_questions}, qa_pairs={len(qa_pairs)}")
        if abs(len_questions - len(qa_pairs)) > 1:
            print("Faltan preguntas")
            content = prompt + "\n" + response
            messages =  [{'role':'user', 'content':content}]
            response = get_completion_from_messages(
                messages, 
                temperature=0, 
                #model="gpt-4-1106-preview"
            )
            print("response:", response)
            next_qa_pairs = self.extract_questions_answers_from_response_regex(response)
            print("Total de preguntas generadas:", len(next_qa_pairs))
            qa_pairs  = qa_pairs + next_qa_pairs
        
        return qa_pairs

#     que, al hacer referencia al reglamento del cual proviene la información proporcionada, utilices únicamente su denominación completa y menciones explícitamente la afiliación con la Universidad Nacional de Ingeniería (UNI).
#         2. Si no puedes dar una respuesta completa con la información proporcionada, ofrece una respuesta parcial y complementa indicando de que tema especifico no posees informacion suficiente para ofrecer una respuesta completa.
#    2. Evita mencionar numerales de artículos que no mencionen al documento al que pertenecen en las respuestas; en su lugar, puedes referenciar directamente al reglamento donde pertenecen estos articulos.
#   2. En las respuestas, abstente de hacer referencia directa al fragmento de texto proporcionado y, en su lugar, utiliza la denominación completa del reglamento correspondiente para respaldar tus argumentos.
#   4. El reglamento correspondiente solo debe referenciarse con su denominación completa y haciendo referencia a la Universidad Nacional de Ingeniería (UNI) dentro de las respuestas.
      

# Me gusta al 96%
def get_prompt_gen_answers_v3(reglamento, list_questions, len_questions , max_size = 50):

    prompt = f"""
    Tu tarea consiste en generar respuestas informativas y útiles para cada una de las {len_questions} preguntas listadas abajo, basándote en la información proporcionada delimitada por tres comillas invertidas.

    Concéntrate en crear respuestas detalladas que justifiquen claramente las razones, utilizando exclusivamente la información proporcionada dentro de las comillas invertidas. Evita hacer referencia a reglamentos específicos y asegúrate de proporcionar detalles complementarios relevantes basados únicamente en dicha información para enriquecer las respuestas.

    Finalmente, presenta cada una de las {len_questions} preguntas listadas abajo y sus respuestas de manera enumerada utilizando el punto-guión como marcador de la siguiente manera:

    1.- Aqui la pregunata
    Respuesta: Aqui la respuesta

    2.- Aqui la pregunta
    Respuesta: Aqui la respuesta

    Lista de preguntas:
    {list_questions}

    Información: ```{reglamento}```
    """
    return prompt

# Me gusta al 97%
def get_prompt_gen_answers_v5(reglamento, list_questions, len_questions , max_size = 50):

    prompt = f"""
    Tu tarea consiste en generar respuestas informativas y útiles para cada una de las {len_questions} preguntas listadas abajo, basándote en la información proporcionada delimitada por tres comillas invertidas.

    Concéntrate en crear respuestas informativas y detalladas que justifiquen claramente las razones, utilizando exclusivamente la información proporcionada dentro de las comillas invertidas. Evita hacer referencia a reglamentos específicos y asegúrate de proporcionar detalles complementarios relevantes basados únicamente en dicha información para enriquecer las respuestas.

    Finalmente, presenta cada una de las {len_questions} preguntas listadas abajo y sus respuestas de manera enumerada utilizando el punto-guión como marcador de la siguiente manera:

    1.- Aqui la pregunata
    Respuesta: Aqui la respuesta

    2.- Aqui la pregunta
    Respuesta: Aqui la respuesta

    Lista de preguntas:
    {list_questions}

    Información: ```{reglamento}```
    """
    return prompt
#     Asegúrate de que al mencionar tablas, incluyas la fuente o el documento reglamentario de donde provienen, especificando su nombre completo.
# y asegúrate de proporcionar detalles complementarios relevantes basados únicamente en dicha información para enriquecer las respuestas.
#     Se prefiere que generes respuestas extensas que proporcionen la mayor cantidad de información y detalles útiles, las cuales pueden incluir tablas obtenidas de la información delimitada por tres comillas invertidas.
#     Asegúrate de que al mencionar tablas en las respuestas, incluyas en la misma mención la fuente o el documento reglamentario de donde provienen, especificando su nombre completo.

def get_prompt_gen_answers_vf(reglamento, list_questions, len_questions):

    prompt = f"""
    Tu tarea consiste en generar respuestas informativas y útiles para cada una de las {len_questions} preguntas listadas abajo, basándote en la información proporcionada delimitada por tres comillas invertidas.

    Concéntrate en crear respuestas informativas, completas y detalladas que justifiquen claramente las razones, basandote exclusivamente la información proporcionada dentro de las comillas invertidas, sin añadir información ficticia. 
    
    Asegurate de generar respuestas suficientemente extensas que incluyan todo la información y detalles útiles, las cuales pueden incluir información relevante extraidas de las tablas de la información delimitada por tres comillas invertidas.

    Finalmente, presenta cada una de las {len_questions} preguntas listadas abajo y sus respuestas de manera enumerada utilizando el punto-guión como marcador de la siguiente manera:

    1.- Aqui la pregunata
    Respuesta: Aqui la respuesta

    2.- Aqui la pregunta
    Respuesta: Aqui la respuesta

    Lista de preguntas:
    {list_questions}

    Información: ```{reglamento}```
    """
    return prompt

# Asegurate de generar respuestas lo suficientemente extensas que incluyan toda la información y detalles útiles, los cuales pueden extraerse de las tablas de la información delimitada entre tres comillas invertidas. 

#Es importante ser específico al mencionar los reglamentos utilizando su nombre completo cada vez que se haga referencia a ellos y evitar mencionar artículos específicos en las respuestas. 

#Además, utiliza un tono informativo y explicativo para generar las respuestas.

#     manteniendo consistencia con la información proporcionada entre tres comillas invertidas 
# elementos particulares, como 
def get_prompt_gen_answers(reglamento, list_questions, len_questions):

    prompt = f"""
    Tu tarea consiste en proporcionar respuestas informativas, completas y útiles para cada una de las {len_questions} preguntas que se presentan a continuación. Asegúrate de basarte en la información proporcionada entre tres comillas invertidas para responder de manera clara y con un tono informativo y explicativo apropiado para un Asistente de IA especializado en estos temas.

    Para cumplir con esto, sigue estas pautas:

    - Responde cada pregunta de manera clara, concisa y completa justificando claramente las razones.
    - Usa un tono profesional y objetivo en tus respuestas.
    - Asegúrate de cubrir todos los puntos relevantes de cada pregunta.
    - Utiliza ejemplos o detalles específicos cuando sea necesario para una mejor comprensión.
    - Asegurate de especificar claramente la procedencia de tablas mencionados en las respuestas.
    - Evita mencionar articulos o incisos específicos
    
    Finalmente, presenta cada una de las {len_questions} preguntas listadas a continuación y sus respuestas de manera enumerada utilizando el punto-guión como marcador de la siguiente manera:

    1.- Aquí la pregunta
    Respuesta: Aquí la respuesta

    2.- Aquí la pregunta
    Respuesta: Aquí la respuesta
    Lista de preguntas:
    {list_questions}

    Información: ```{reglamento}```"""

    return prompt

def get_prompt_gen_answers_vf_prev2(reglamento, list_questions, len_questions):

    prompt = f"""
    Tu tarea consiste en proporcionar respuestas informativas, completas y útiles para cada una de las {len_questions} preguntas listadas a continuación, basándote en la información proporcionada entre tres comillas invertidas.

    Es importante que respondas las preguntas de manera clara con un tono informativo y explicativo de un Asistente de IA especializado dichos temas.
    
Finalmente, presenta cada una de las {len_questions} preguntas listadas a continuación y sus respuestas de manera enumerada utilizando el punto-guión como marcador de la siguiente manera:

1.- Aquí la pregunta
Respuesta: Aquí la respuesta

2.- Aquí la pregunta
Respuesta: Aquí la respuesta

Lista de preguntas:
{list_questions}

Información: {reglamento}"
    """
    return prompt

answer_generator = AnswerGenerator(
    file_questions = "./questions_generated_topics_finals.json")

answer_generator.run()

prompt = """Tu tarea consiste en eliminar las partes del texto que menciones específicamente a artículos de reglamentos en los siguientes textos, sin alterar el sentido original de la información en ellos.
            Es importante que no alteres las palabras originales de los textos.
            Preguntas: 
            1.- En la primera matrícula de un estudiante nuevo ingresante al primer ciclo, el alumno será matriculado en todas las asignaturas correspondientes al primer ciclo según el plan de estudios de su especialidad o carrera universitaria. Esto se establece en el Reglamento de Matrícula para Estudiantes de Pregrado de la Universidad Nacional de Ingeniería, Capítulo VI, Artículo 57°, inciso a.


2.- Si un estudiante en posibilidad de egresar no ha completado los créditos por prácticas pre-profesionales, se le permitirá matricularse hasta en treinta (30) créditos, siempre que dentro de este creditaje no exista una asignatura desaprobada dos (02) veces y no le falte la asignación de los créditos por prácticas pre-profesionales. Si le faltase esta asignación, los créditos se descontarán de los 30 créditos permitidos. Esto se establece en el Reglamento de Matrícula para Estudiantes de Pregrado de la Universidad Nacional de Ingeniería, Capítulo VI, Artículo 60°.

            Por favor, enumera las versiones modificadas de los textos para eliminar las referencias específicas a los numerales y artículos, manteniendo el mismo orden en que se proporcionaron los textos originales. 
            Utiliza el siguiente formato de enumeración con punto-guión:
                1.- Aqui el texto modificado
                2.- Aqui el texto modificado
                ...
                """

#messages =  [{'role':'user', 'content':prompt}]
#response = get_completion_from_messages(
#    messages, 
#    temperature=0,
    #model="gpt-3.5-turbo-0613"
#    )

#print("\nresponse:", response)