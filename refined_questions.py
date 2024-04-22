from utils import load_json, get_completion_from_messages, list_json_to_txt, save_json
from dotenv import load_dotenv
import openai
import os
import re
import math
import time
def set_openai_key():
    API_KEY = os.getenv("API_KEY")
    openai.api_key = API_KEY

load_dotenv()

set_openai_key()


# Informacion: ```{context}```

def extract_questions_answers_from_response_regex(self, response):
        pattern = r'\d+\.-\s*(.*?)\s*Respuesta:\s*(.*?)(?=\d+\.-|\Z)'
        
        matches = re.findall(pattern, response, re.DOTALL)
        question_answer_pairs = [{"question": question, "answer": answer} for (question, answer) in matches]
        return question_answer_pairs


def get_prompt_gen_answers(questions):
    len_questions = len(questions)
    list_questions = list_json_to_txt(questions, numeric=True)
    prompt_gen_answers = f"""
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
Información: ```{context}```
"""
    return prompt_gen_answers

# Responde cada una de las siguientes consultas de manera clara, completa y consisa usando la informacion delimitada por tres comillas invertidas.
def get_prompt_identify_non_specific_questions_v1(questions_answers):
    prompt = f"""
    Identifica cuales de las siguientes preguntas son generales y amplias y no se centran en detalles específicos descrito en sus respuestas.    
    Preguntas y respuestas:
    {questions_answers}
    """
    return prompt

def get_prompt_identify_non_specific_questions(questions):
    list_questions = list_json_to_txt(questions)
    prompt = f"""
Tu tarea consiste en identificar cuáles preguntas de la siguiente lista carecen de precisión y no definen claramente qué información se está buscando. Para ello utiliza los siguientes criterios:
1. Considera preguntas con terminos demasiado amplios como "¿Qué sucede" como carentes de precisión y demansiado amplias.
2. No consideres la falta de claridad de terminos propios del contexto Facultad de Ciencias de La Universidad Nacional de Ingeniería como un criterio de falta de precision.
3. Enfocate en las preguntas que son demasiado amplias y no definen claramente qué información se está buscando.   

Lista de preguntas:
{list_questions}
Extrae de la lista anterior las preguntas que has identificado que carezcan de precisión o no definan claramente qué información se está buscando usando los criterior anteriormente menciondas y presentalas de la siguiente manera:
- Aqui la pregunta que carezcan de precisión o no definan claramente qué información se está buscando extraida literalmente de la lista anterior
Orden Original: Aqui el numero del orden de la pregunta en la lista original
...

"""
    return prompt

def get_prompt_identify_non_specific_questions_v3(questions):
    list_questions = list_json_to_txt(questions)
    prompt = f"""
Tu tarea consiste en identificar cuáles de las preguntas de la siguiente lista carecen de precisión y no definen claramente qué información se está buscando.
Considera las preguntas con terminos demasiado amplios como "¿Qué sucede" como carentes de precisión y demansiado amplias.

Lista de preguntas:
{list_questions}
Presenta la preguntas identificadas con su enumeracion original.
"""
    return prompt
# coherentes
def get_prompt_gen_answers_v3(questions, context):
    len_questions = len(questions)
    list_questions = list_json_to_txt(questions, numeric=True)
    prompt_gen_answers = f"""
Responde independientemente cada una las {len_questions} consultas de la lista, cumpliendo los siguientes criterios.
1. Analiza la informacion delimitada en tres comillas invertidas y provee respuestas basandote exclusivamente en lo descrito explicitamente en dicha informacion, sin suponer o inventar información ficticia.
2. Las respuestas deben ser caras, concisa y completas donde se justifiquen claramente las razones.
3. Mantén un tono informativo y explicativo apropiado para un Asistente de IA especializado en estos temas
4. Evita hacer referencia reglamentos especificos en las respuestas

Finalmente, presenta cada una de las {len_questions} preguntas listadas a continuación y sus respuestas de manera enumerada utilizando el punto-guión como marcador de la siguiente manera:

1.- Aquí la pregunta
Respuesta: Aquí la respuesta

2.- Aquí la pregunta
Respuesta: Aquí la respuesta

Lista de preguntas:
{list_questions}
Información: ```{context}```
"""
    return prompt_gen_answers

def get_prompt_gen_answers_v4(questions, context):
    len_questions = len(questions)
    list_questions = list_json_to_txt(questions, numeric=True)
    prompt_gen_answers = f"""
Responde independientemente cada una las {len_questions} consultas de la lista, cumpliendo los siguientes criterios.
1. Para las preguntas que no esten explícitamente respondida en la información delimitada por tres comillas invertidas, describe en la respuesta la informacion mas proxima relacionada con la pregunta que este explicitamente descrita en dicha informacion.
2. Para las demas preguntas que si esten explícitamente respondidas en la información delimitada por tres comillas responde responde de manera clara, concisa y completas donde se justifiquen claramente las razones bsandote en dicha informacion.
3. Mantén un tono informativo y explicativo apropiado para un Asistente de IA especializado en estos temas
4. Evita hacer referencia reglamentos especificos en las respuestas

Finalmente, presenta cada una de las {len_questions} preguntas listadas a continuación y sus respuestas de manera enumerada utilizando el punto-guión como marcador de la siguiente manera:

1.- Aquí la pregunta
Respuesta: Aquí la respuesta

2.- Aquí la pregunta
Respuesta: Aquí la respuesta

Lista de preguntas:
{list_questions}
Información: ```{context}```
"""
    return prompt_gen_answers

def get_prompt_gen_answers_v2(questions, context):
    len_questions = len(questions)
    list_questions = list_json_to_txt(questions, numeric=True)
    prompt_gen_answers = f"""
Responde independientemente cada una las {len_questions} consultas de la lista de manera clara, concisa y completa justificando claramente las razones inferiendo la respuesta de la información delimitada entre tres comillas invertidas. Mantén un tono informativo y explicativo apropiado para un Asistente de IA especializado en estos temas. Evita hacer referencia reglamentos especificos en las respuestas.

Finalmente, presenta cada una de las {len_questions} preguntas listadas a continuación y sus respuestas de manera enumerada utilizando el punto-guión como marcador de la siguiente manera:

1.- Aquí la pregunta
Respuesta: Aquí la respuesta

2.- Aquí la pregunta
Respuesta: Aquí la respuesta

Lista de preguntas:
{list_questions}
Información: ```{context}```
"""
    return prompt_gen_answers

def identify_non_specific_questions(questions):
    prompt_identify_non_specific_questions = get_prompt_identify_non_specific_questions(
    questions=questions)

    print("prompt_identify_non_specific_questions:", prompt_identify_non_specific_questions)
    messages = [
    {"role": "user", "content": prompt_identify_non_specific_questions}
    ]

    response = get_completion_from_messages(
        messages,
        model="gpt-3.5-turbo-0613"
        #model="gpt-3.5-turbo-instruct",
        #chat=False
        )
    print("\nPreguntas Identificadas:\n", response)
    
    # Expresión regular para extraer números
    original_orders = re.findall(r'\b\d+\b', response)
    original_orders = [ int(order) for order in original_orders]
    # Expresión regular para extraer preguntas
    patron_pregunta = r'\d+\.\s(¿[^\?]+?\?)'
    non_specific_questions = re.findall(r'- (¿[^\?]+?\?)', response, re.DOTALL)

    #non_specific_questions = extract_questions_from_response_regex(response)
    return non_specific_questions, original_orders
 
def generate_refined_questions(questions, context, select_non_specific_questions = True):
    if select_non_specific_questions:
        non_specific_questions, original_orders = identify_non_specific_questions(questions)
    else:
        non_specific_questions = questions
    #print("non_specific_questions:", non_specific_questions)
    batch_size = 5
    num_batch = math.ceil(len(non_specific_questions)/ batch_size)
    refined_questions = []
    for i in range(num_batch):
        print("-"*15 + f"-batch-{i}" + "-"*15)
        print()
        start = batch_size * i
        end = min(len(non_specific_questions),  batch_size * (i+1))     
        b_non_specific_questions = non_specific_questions[start:end]
        #print("b_non_specific_questions:", b_non_specific_questions)
        prompt_gen_answers = get_prompt_gen_answers_v4(b_non_specific_questions, context)
        #print("prompt_gen_answers:", prompt_gen_answers)
        messages = [
        {"role": "user", "content": prompt_gen_answers}
        ]
        
        questions_anwers_text = get_completion_from_messages(
            messages,
            model="gpt-3.5-turbo-0613"
            #model="gpt-3.5-turbo-instruct",
            #chat=False
            )
        print("\nRespuestas Generadas:\n", questions_anwers_text)

        prompt_refine_questions = f"""
        Refina de manera pertinente las siguientes preguntas para enfocarlas en el tema específico descrito en sus respuestas, eliminando cualquier ambigüedad. Reformula las preguntas solo en caso de que no sean lo suficientemente específicas y no estén enfocadas en el tema específico descrito en sus respuestas, evitando mencionar tablas en las preguntas.

        Lista de preguntas:
        {questions_anwers_text}
        Presenta las preguntas refinadas de las siguiente manera:
        1. [Aqui la pregunta 1 refinada para enfocarse en el tema específico descrito en su respuesta]
        2. [Aqui la pregunta 2 refinada para enfocarse en el tema específico descrito en su respuesta]
        ...
        """

        messages = [
        {"role": "user", "content": prompt_refine_questions}
        ]
        
        response = get_completion_from_messages(
            messages,
            model="gpt-3.5-turbo-0613"
            #model="gpt-3.5-turbo-instruct",
            #chat=False
        )

        print("\nPreguntas reformuladas:\n", response)
        b_refined_questions = extract_questions_from_response_regex(response)
        refined_questions.extend(b_refined_questions)
    
    # Actualizar preguntas:
    if select_non_specific_questions:
        updated_questions = questions.copy()
        #print("non_specific_questions:", non_specific_questions)
        #print("questions:", questions)
        for i, non_spec_question in enumerate(non_specific_questions):
            if non_spec_question.strip() not in questions:
                j = original_orders[i]
                updated_questions[j] = refined_questions[i]
                print("Pregunta identifica no encontrada literalmente")
                continue
            
            for j in range(len(questions)):
                if  non_spec_question.strip() in questions[j]:
                    updated_questions[j] = refined_questions[i]
                    break
    else:
        updated_questions = refined_questions
                  
    return updated_questions

def extract_questions_from_response_regex(response):
        patron = r'\d+\.\s(¿[^\?]+?\?)'
        preguntas = re.findall(patron, response)
        return preguntas

questions_topics = load_json("./additional_questions.json")

f1 = open("./questions_generated.txt", 'w')
f2 = open("./refined_questions_generated.txt", 'w')
refined_questions_generated = questions_topics.copy()

for i_q, questions_about_topic in enumerate(questions_topics):
    print()
    print("-"*15 + "-"*15)
    questions = questions_about_topic["additional_questions"]
    print("\nOriginal questions:")
    print(list_json_to_txt(questions))
    f1.writelines([
        "-"*15 + "-"*15, 
        "\n", 
        questions_about_topic["topic"], 
        "\n",
        questions_about_topic["original_question"], 
        "\n", 
        list_json_to_txt(questions)])
    #questions = questions[8:]
    context = questions_about_topic["context"]
    
    updated_questions = generate_refined_questions(questions, context, select_non_specific_questions= False)
    print("\nRefined questions:")
    print(list_json_to_txt(updated_questions))

    refined_questions_generated[i_q]["questions"] = updated_questions

    f2.writelines([
        "-"*15 + "-"*15, 
        "\n", 
        questions_about_topic["topic"], 
        "\n",
        questions_about_topic["original_question"], 
        "\n", 
        list_json_to_txt(updated_questions)])
    time.sleep(4)
    break

f1.close()
f2.close()
save_json("./","refined_questions_generated",refined_questions_generated)
    
    