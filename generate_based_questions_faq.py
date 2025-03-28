from utils import get_completion_from_messages, set_openai_key, read_fragment_doc, count_num_tokens, list_json_to_txt, save_json
import os
import re
from dotenv import load_dotenv

load_dotenv()

set_openai_key()

def extract_faqs(text):
    pattern_block = r"Tema: (.+?)Pregunta: (.+?)Respuesta:(.+?)(?=Tema: |$)"
    bloques = re.findall(pattern_block, text, re.DOTALL)
    faq_json = []
    for bloq in bloques:
        tema = bloq[0].strip()
        pregunta = bloq[1].strip()
        respuesta = bloq[2].strip()

        faq_json.append({
            "question": pregunta,
            "answer": respuesta,
            "topic": tema,
            "num_tokens_answers": count_num_tokens(respuesta) 
        })
    return faq_json
## Utiliza la información proporcionada en las preguntas y sus respuestas para generar preguntas relevantes y que requieran razonamiento en algunos casos.

## esta bueno pero solo falta un poco
# presenten una variedad de enfoques en la formulación de las preguntas. Asegúrate de que las nuevas preguntas
#  Varía tanto la persona gramatical (primera persona y tercera persona) como el nivel de formalidad del lenguaje (formal, semiformal o informal)
# Instrucción 2. Utiliza una amplia variedad de enfoques en la formulación de las preguntas, como preguntas condicionales, de inferencia, de comparación, de causa y efecto, de definición, etc.
# Utiliza una amplia variedad de enfoques en la formulación de las preguntas, como preguntas condicionales, de inferencia, de comparación, de causa y efecto, de definición, etc.

def get_prompt_gen_questions_based_faq_vff(faqs, num_questions = 40):
    questions_answer_list = list_json_to_txt(faqs)
    print()
    prompt = f"""
Utilizando las preguntas y respuestas proporcionadas, genera una lista de {num_questions} preguntas únicas que abarquen diferentes niveles de complejidad y cubran tanto puntos generales o amplios hasta detalles específicos. Cada pregunta debe tener una respuesta dentro de la información proporcionada. Sigue estas instrucciones:
Instrucciones:

Instrucción 1. Lee cuidadosamente las preguntas y respuestas proporcionadas para comprender completamente el contexto.
Instrucción 2. Genera preguntas utilizando una amplia variedad de enfoques en la formulación de las preguntas, como preguntas condicionales, de inferencia, de comparación, de causa y efecto, de definición, etc, que aborden tanto aspectos generales o amplios como detalles específicos.  Asegurate que cada pregunta sea única y pueda ser respondida empleando unicamente la información en las respuestas de las preguntas proporcionadas entre tres comillas invertidas. 
Instrucción 3. Presenta las {num_questions} preguntas generadas de la siguiente manera:
1. [Aquí va la primera pregunta]
2. [Aquí va la segunda pregunta]
...
Preguntas y Respuestas:```
{questions_answer_list}```
"""
    return prompt

def get_prompt_2_gen_questions_based_faq(faqs, num_questions = 40):
    questions_answer_list = list_json_to_txt(faqs)
    print()
    prompt = f"""
Utilizando las preguntas y respuestas proporcionadas, genera una lista de {num_questions} preguntas únicas que abarquen diferentes niveles de complejidad y cubran tanto puntos generales o amplios hasta detalles específicos. Cada pregunta debe tener una respuesta dentro de la información proporcionada. Sigue estas instrucciones:
Instrucciones:

Instrucción 1. Lee cuidadosamente las preguntas y respuestas proporcionadas para comprender completamente el contexto.
Instrucción 2. Genera utilizando una amplia variedad de enfoques en la formulación de las preguntas, como preguntas condicionales, de inferencia, de comparación, de causa y efecto, de definición, etc. y asegurandote que cada pregunta sea única y pueda ser respondida empleando unicamente la información en las respuestas de las preguntas proporcionadas entre tres comillas invertidas. 
Instrucción 3. Presenta las {num_questions} preguntas generadas de la siguiente manera:
1. [Aquí va la primera pregunta]
2. [Aquí va la segunda pregunta]
...
Preguntas y Respuestas:```
{questions_answer_list}```
"""
    return prompt
# abarquen diferentes niveles de complejidad y 
def get_prompt_1_gen_questions_based_faq(faqs, num_questions = 40):
    questions_answer_list = list_json_to_txt(faqs)
    print()
    prompt = f"""
Utilizando las preguntas y respuestas proporcionadas, genera una lista de {num_questions} preguntas únicas que cubran tanto puntos generales o amplios hasta detalles específicos. Cada pregunta debe tener una respuesta dentro de la información proporcionada. Sigue estas instrucciones:
Instrucciones:

Instrucción 1. Lee cuidadosamente las preguntas y respuestas proporcionadas para comprender completamente el contexto.
Instrucción 2. Genera preguntas que aborden tanto aspectos generales o amplios como detalles específicos, asegurándote que cada pregunta sea única y pueda ser respondida empleando unicamente la información en las respuestas de las preguntas proporcionadas entre tres comillas invertidas. 
Instrucción 3. Presenta las {num_questions} preguntas generadas de la siguiente manera:
1. [Aquí va la primera pregunta]
2. [Aquí va la segunda pregunta]
...
Preguntas y Respuestas:```
{questions_answer_list}```
"""
    return prompt

def get_prompt_gen_questions_based_faq_prev(faqs, num_questions = 40):
    questions_answer_list = list_json_to_txt(faqs)
    print()
    prompt = f"""
Utilizando las preguntas y respuestas proporcionadas, genera una lista de {num_questions} preguntas únicas que abarquen diferentes niveles de complejidad y cubran tanto puntos generales o amplios hasta detalles específicos. Cada pregunta debe tener una respuesta dentro de la información proporcionada. Sigue estas instrucciones:
Instrucciones:

Instrucción 1. Lee cuidadosamente las preguntas y respuestas proporcionadas para comprender completamente el contexto.
Instrucción 2. Utiliza una amplia variedad de enfoques en la formulación de las preguntas, como preguntas condicionales, de inferencia, de comparación, de causa y efecto, de definición, etc.
Instrucción 3. Asegúrate de que cada pregunta sea única y pueda ser respondida empleando la información proporcionada en las respuestas, abordando tanto aspectos generales o amplios como detalles específicos.
Instrucción 4. Presenta las {num_questions} preguntas generadas de la siguiente manera:
1. [Aquí va la primera pregunta]
2. [Aquí va la segunda pregunta]
...
Preguntas y Respuestas:
{questions_answer_list}
"""
    return prompt

def extract_questions_from_response_regex(response):
        patron = r'\d+\.\s(¿[^\?]+?\?)'
        preguntas = re.findall(patron, response)
        return preguntas

def get_num_questions(num_tokens):
        #60
        num_questions = int(round((num_tokens - 10) / 40))

        return num_questions

def generate_questions_based_faq(faqs):
    list_faqs = [faq["question"] + "\n" + "Respuesta: " +  faq["answer"] for faq in faqs]
    total_tokens = sum([count_num_tokens(faq) for faq in list_faqs])
    print("total_tokens:", total_tokens)
    num_questions = get_num_questions(total_tokens)
    
    print("num_questions:", num_questions)
    prompt = get_prompt_1_gen_questions_based_faq(list_faqs, num_questions)

    messages =  [{'role':'user', 'content': prompt}]

    response = get_completion_from_messages(
                        messages,
                        model = "gpt-4o-2024-05-13",
                        #model="gpt-3.5-turbo-0613",
                        temperature=0)

    print("response prompt-1:",response)

    preguntas_prompt_1 = extract_questions_from_response_regex(response)

    time.sleep(5)
    prompt = get_prompt_2_gen_questions_based_faq(list_faqs, num_questions)

    messages =  [{'role':'user', 'content': prompt}]

    response = get_completion_from_messages(
                        messages,
                        model = "gpt-4o-2024-05-13",
                        #model="gpt-3.5-turbo-0613",
                        temperature=0)

    print("\nresponse prompt-2:",response)
    preguntas_prompt_2 = extract_questions_from_response_regex(response)
    
    preguntas = preguntas_prompt_1 + preguntas_prompt_2
    return preguntas
    #print("Preguntas:", preguntas)

    

import random
import time

random.seed(42)

text = read_fragment_doc("./faq/faq.txt")
faqs = extract_faqs(text)
faqs = faqs[0:15]
ids = list(range(len(faqs)))


all_additional_faqs = []
times_samples = 3
for iter in range(times_samples):
    if iter  >= 1:
        continue
    choices = random.sample(ids, k = len(ids))
    num_grupos = len(choices) // 3
    grupos = [choices[i * 3:(i+1)*3] for i in range(num_grupos)]
    sobran = len(choices) % 3
    if sobran > 0:
        grupos = grupos + [choices[-3:]]
    print(grupos)
    
    additional_faqs = []
    
    for group_ids in grupos:
        print(group_ids)
        group_faqs = [faqs[id] for id in group_ids]
        preguntas = generate_questions_based_faq(group_faqs)
        time.sleep(4)
        break
        additional_faqs.append({
            "original_questions":  [ faq["question"] for faq in group_faqs], 
            "additional_questions": preguntas
        })

    text_additional_faqs = ""
    for adds_faq in additional_faqs:
        additional_questions = adds_faq["additional_questions"]
        original_questions = adds_faq["original_questions"]
        text_additional_faqs += "\nPreguntas originales:\n"+ list_json_to_txt(original_questions) + "Nuevas Preguntas:\n" + list_json_to_txt(additional_questions)
    
    all_additional_faqs.append(additional_faqs)
    file = open(f"./faq/additional_faqs/text_additional_faqs_iter{iter + 1}.txt", "w")
    file.writelines(text_additional_faqs)
    file.close()
    save_json("./faq/additional_faqs", "all_additional_faqs", all_additional_faqs)

save_json("./faq/additional_faqs", "all_additional_faqs", all_additional_faqs)

""" import evaluate
threshold_rouge = 0.8
pool_additional_faqs = []
all_pool_questions = []
rouge = evaluate.load('rouge')

total_init_adds_faqs_all = sum([len(faqs["additional_questions"]) for additional_faqs in all_additional_faqs for faqs in additional_faqs])
print(f"\nUn total de {total_init_adds_faqs_all} preguntas iniciales")


iter = 1
for additional_faqs in all_additional_faqs:
    temp_additional_faqs = []
    total_init_adds_faqs = sum([len(faqs["additional_questions"]) for faqs in additional_faqs])
    print(f"\nUn total de {total_init_adds_faqs} preguntas iniciales en la iteracion")

    for adds_faq in additional_faqs:
        additional_questions = adds_faq["additional_questions"]
        original_questions = adds_faq["original_questions"]
        temp_questions = []
        for question in additional_questions:
            if len(all_pool_questions) == 0:
                temp_questions.append(question) 
                all_pool_questions.append(question)
                continue
            rouge_results = rouge.compute(predictions=[question], references=[all_pool_questions])
            rougeL = rouge_results["rougeL"]
            if rougeL < threshold_rouge:
                all_pool_questions.append(question)
                temp_questions.append(question)

        temp_additional_faqs.append({
            "original_questions": original_questions,
            "additional_questions": temp_questions
        })

    text_additional_faqs = ""
    for temp_adds_faq in temp_additional_faqs:
        additional_questions = temp_adds_faq["additional_questions"]
        original_questions = temp_adds_faq["original_questions"]
        text_additional_faqs += "\nPreguntas originales:\n"+ list_json_to_txt(original_questions) + "Nuevas Preguntas:\n" + list_json_to_txt(additional_questions)
    
    file = open(f"./faq/text_additional_faqs_iter{iter}_filtrated.txt", "w")
    file.writelines(text_additional_faqs)
    file.close()
    iter+=1
    
    print(f"\nUn total de {len(all_pool_questions)} preguntas finales")

print(f"\nUn total de {len(all_pool_questions)} preguntas finales")


save_json("./faq","filtered_questions", all_pool_questions)

text_pool_questions = list_json_to_txt(all_pool_questions)

file = open(f"./faq/filtered_questions.txt", "w")
file.writelines(text_pool_questions)
file.close() """