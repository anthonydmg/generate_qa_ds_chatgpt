from utils import get_completion_from_messages, load_json, set_openai_key, read_fragment_doc, count_num_tokens, list_json_to_txt, save_json
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
Se te proveerá una lista de preguntas y respuestas frecuentes de la Facultad de Ciencias de Universidad para alumnos de pregrado delimitadas por tres comillas invertidas.
Utilizando las preguntas y respuestas proporcionadas, genera una lista de 8 preguntas únicas que abarquen. Cada pregunta debe tener una respuesta dentro de la información proporcionada, cumpliendo con los siguientes criterios:s:

Criterio 1. Genera las preguntas de complejidad baja y moderada utilizando una amplia variedad de enfoques en la formulación de las preguntas, como preguntas condicionales, de inferencia, de comparación, de causa y efecto, de definición, etc. 
Criterio 2. Cada pregunta deber única y poder ser respondida empleando unicamente la información en la respuesta de las pregunta proporcionadas entre tres comillas invertidas. 
Criterio 3. Las nuevas preguntas generadas deben tener relevancia para un estudiante de la Facultad de Ciencias de la UNI.
Criterio 4. Presenta las 8 preguntas generadas para cada pregunta original de la siguiente manera:

Pregunta Original 1: [Aqui la pregunta original 1]
1. [Aquí la pregunta 1 basada en la primer pregunta original]
2. [Aquí la pregunta 2 basada en la primer pregunta original]
...
8. [Aquí la pregunta 8 basada en la primer pregunta original]

Pregunta Original 2: [Aqui la pregunta original 2]
1. [Aquí la pregunta 1 basada en la segunda pregunta original]
2. [Aquí la pregunta 2 basada en la segunda pregunta original]
...
8. [Aquí la pregunta 8 basada en la segunda pregunta original]

Pregunta Original 3: [Aqui la pregunta original 3]
1. [Aquí la pregunta 1 basada en la tercer pregunta original]
2. [Aquí la pregunta 2 basada en la tercer pregunta original]
...
8. [Aquí la pregunta 8 basada en la tercer pregunta original]
...
...
Preguntas y Respuestas:```
{questions_answer_list}```
"""
    return prompt

def get_prompt_3_gen_questions_based_faq(faqs, num_questions = 40):
    questions_answer_list = list_json_to_txt(faqs)
    print()
    prompt = f"""
Se te proveerá una lista de preguntas y respuestas frecuentes sobre temas de interés para alumnos de pregrado de la Facultad de Ciencias de la Universidad Nacional de Ingeniería, delimitadas por tres comillas invertidas.
Genera 8 preguntas derivadas y únicas que cubran tanto puntos generales o amplios hasta detalles específicos para cada par de pregunta y respuesta dentro de las tres comillas invertidas, cumpliendo con los siguientes criterios:

Criterio 1. Genera la lista de preguntas de modo que aborden tanto aspectos generales o amplios como detalles específicos, asegurándote que cada pregunta sea única y pueda ser respondida empleando unicamente la información en las respuesta de la pregunta entre tres comillas invertidas. 
Criterio 2. Cada pregunta debe tener una respuesta dentro de la información proporcionada.
Criterio 3. Las nuevas preguntas generadas deben tener relevancia para un estudiante de la Facultad de Ciencias de la UNI.
Criterio 4. Presenta las 8 preguntas generadas para cada pregunta original de la siguiente manera:

Pregunta Original 1: [Aqui la pregunta original 1]
1. [Aquí la pregunta 1 basada en la primer pregunta original]
2. [Aquí la pregunta 2 basada en la primer pregunta original]
...
8. [Aquí la pregunta 8 basada en la primer pregunta original]

Pregunta Original 2: [Aqui la pregunta original 2]
1. [Aquí la pregunta 1 basada en la segunda pregunta original]
2. [Aquí la pregunta 2 basada en la segunda pregunta original]
...
8. [Aquí la pregunta 8 basada en la segunda pregunta original]

Pregunta Original 3: [Aqui la pregunta original 3]
1. [Aquí la pregunta 1 basada en la tercer pregunta original]
2. [Aquí la pregunta 2 basada en la tercer pregunta original]
...
8. [Aquí la pregunta 8 basada en la tercer pregunta original]
...

Preguntas y Respuestas:```
{questions_answer_list}```
"""
    return prompt
# abarquen diferentes niveles de complejidad y 
def get_prompt_1_gen_questions_based_faq(faqs, num_questions = 40):
    questions_answer_list = list_json_to_txt(faqs)
    print()
    prompt = f"""Se te proveerá una lista de preguntas y respuestas frecuentes sobre temas de interés para alumnos de pregrado de la Facultad de Ciencias de la Universidad Nacional de Ingeniería, delimitadas por tres comillas invertidas.
Genera 8 preguntas derivadas y únicas que cubran tanto puntos generales o amplios hasta detalles específicos para cada par de pregunta y respuesta dentro de las tres comillas invertidas, cumpliendo con los siguientes criterios:

Criterio 1. Genera la lista de preguntas de modo que aborden tanto aspectos generales o amplios como detalles específicos, asegurándote que cada pregunta sea única y pueda ser respondida empleando unicamente la información en las respuesta de la pregunta entre tres comillas invertidas. 
Criterio 2. Cada pregunta debe tener una respuesta dentro de la información proporcionada.
Criterio 3. Las nuevas preguntas generaras deben tener relevancia para un estudiante de la Facultad de Ciencias de la UNI.
Criterio 4. Presenta las 8 preguntas generadas para cada pregunta original de la siguiente manera:

Pregunta Original 1: [Aqui la pregunta original 1]
1. [Aquí la pregunta 1 basada en la primer pregunta original]
2. [Aquí la pregunta 2 basada en la primer pregunta original]
...
8. [Aquí la pregunta 8 basada en la primer pregunta original]

Pregunta Original 2: [Aqui la pregunta original 2]
1. [Aquí la pregunta 1 basada en la segunda pregunta original]
2. [Aquí la pregunta 2 basada en la segunda pregunta original]
...
8. [Aquí la pregunta 8 basada en la segunda pregunta original]

Pregunta Original 3: [Aqui la pregunta original 3]
1. [Aquí la pregunta 1 basada en la tercer pregunta original]
2. [Aquí la pregunta 2 basada en la tercer pregunta original]
...
8. [Aquí la pregunta 8 basada en la tercer pregunta original]
...

Preguntas y Respuestas:```
{questions_answer_list}```
"""
    return prompt

def get_prompt_gen_questions_reformulated(questions):
    questions_list = list_json_to_txt(questions)
    prompt = f"""Se te proveerá una lista de preguntas frecuentes sobre temas de interés para alumnos de pregrado de la Facultad de Ciencias de la Universidad Nacional de Ingeniería, delimitadas por tres comillas invertidas.
Para cada una de las preguntas dentro de las tres comillas invertidas, genera 5 diferentes maneras que un estudiante podría usar para realizar la misma consulta de manera natural y realista a un asistente de AI. Varía tanto la persona gramatical (primera persona y tercera persona) como el nivel de formalidad del lenguaje (formal, semiformal o informal). Además, varía el nivel de concisión de cada una. Algunas preguntas pueden ser sumamente concisas y directas, mientras que otras pueden ser más detalladas y elaboradas.
Presenta las nuevas preguntas para cada pregunta original de la siguiente manera:

- Pregunta Original 1: Aqui la Pregunta Original 1

Preguntas Generadas:
1. Aqui la primer pregunta generada como una manera diferente de la consultar la primer pregunta original
2. Aqui la segunda pregunta generada como una manera diferente de la consultar la primer pregunta original
...
8. Aqui la octava pregunta generada como una manera diferente de la consultar la primer pregunta original

- Pregunta Original 2: Aqui la Pregunta Original 2

Preguntas Generadas:
1. Aqui la primer pregunta generada como una manera diferente de la consultar la segunda pregunta original
2. Aqui la segunda pregunta generada como una manera diferente de la consultar la segunda pregunta original
...
8. Aqui la octava pregunta generada como una manera diferente de la consultar la segunda pregunta original

- Pregunta Original 3: Aqui la Pregunta Original 3

Preguntas Generadas:
... 

Lista de preguntas: ```{questions_list}```
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

def extract_reformulated_questions(text):
    matches = re.findall(r'Pregunta Original (\d+):\*?\*?(.+?)(?=Pregunta Original|\Z)', text, re.DOTALL)
    
    original_questions = []
    generated_questions = []
    # Iterar sobre los resultados
    for match in matches:
        pregunta_original_numero = match[0]
        pregunta_original = match[1].strip()
        preguntas_generadas = re.findall(r'\d+\. (.+)', pregunta_original)
        pregunta_original = pregunta_original.split('\n')[0].strip()
        #print("\nPregunta Original:", pregunta_original)
        #print("Preguntas Generadas:", preguntas_generadas)
        #print()

        original_questions.append(pregunta_original)
        generated_questions.append(preguntas_generadas)
    
    return original_questions, generated_questions

def extract_questions_from_response_regex(response):
        patron = r'\d+\.\s(¿?[^\?]+?\?)'
        preguntas = re.findall(patron, response)
        return preguntas

def get_num_questions(num_tokens):
        #60
        num_questions = int(round((num_tokens - 10) / 40))

        return num_questions

def generate_questions_based_faq(faqs):
    list_faqs = [faq["question"] + "\n" + "Respuesta: " +  faq["answer"] for faq in faqs]
    total_tokens = sum([count_num_tokens(faq) for faq in list_faqs])
    #print("total_tokens:", total_tokens)
    num_questions = get_num_questions(total_tokens)
    
    #print("num_questions:", num_questions)
    prompt = get_prompt_1_gen_questions_based_faq(list_faqs, num_questions)

    messages =  [{'role':'user', 'content': prompt}]

    response = get_completion_from_messages(
                        messages,
                        model = "gpt-4o-mini-2024-07-18",
                        #model="gpt-3.5-turbo-0613",
                        temperature=0.2)

    print("response prompt-1:",response)

    preguntas_prompt_1 = extract_questions_from_response_regex(response)

   
    preguntas_originals_p1 = []
    reformulated_questions_p1 = []
    for n_batch in range(len(preguntas_prompt_1)//12):
        print(f"Batch-Prompt-01------------------------------------------------------{n_batch}")
        #print("n_batch:", n_batch)
        time.sleep(5)
        b_preguntas_prompt_1 = preguntas_prompt_1[n_batch*12: (n_batch + 1)*12]
        #print("b_preguntas_prompt_1:", len(b_preguntas_prompt_1))
        prompt_gen_reformulated_question = get_prompt_gen_questions_reformulated(questions=b_preguntas_prompt_1)

        messages =  [{'role':'user', 'content': prompt_gen_reformulated_question}]

        response = get_completion_from_messages(
                            messages,
                            model = "gpt-4o-mini-2024-07-18",
                            #model = "gpt-4o-2024-05-13",
                            #model="gpt-3.5-turbo-0613",
                            temperature=0.2)

        print("response reformulated_question-1:",response)
        
        b_preguntas_originals_p1, b_reformulated_questions_p1 = extract_reformulated_questions(response)
        preguntas_originals_p1.extend(b_preguntas_originals_p1)
        reformulated_questions_p1.extend(b_reformulated_questions_p1)

        #print("preguntas_originals_p1:", preguntas_originals_p1)
        #print("preguntas_originals_p1:", len(preguntas_originals_p1))
        #print("reformulated_questions_p1:", len(reformulated_questions_p1))
    
    time.sleep(5)
    
    prompt = get_prompt_2_gen_questions_based_faq(list_faqs, num_questions)

    messages =  [{'role':'user', 'content': prompt}]

    response = get_completion_from_messages(
                        messages,
                        model = "gpt-4o-mini-2024-07-18",
                        #model="gpt-3.5-turbo-0613",
                        temperature=0.2)

    print("\nresponse prompt-2:",response)

    preguntas_prompt_2 = extract_questions_from_response_regex(response)

    #time.sleep(5)
    
    preguntas_originals_p2 = []
    reformulated_questions_p2 = []
    #print("preguntas_prompt_2:", len(preguntas_prompt_2))
    
    for n_batch in range(len(preguntas_prompt_2)//12):
        print(f"Batch-Prompt-01------------------------------------------------------{n_batch}")
        #print("n_batch:", n_batch)
        time.sleep(5)
        b_preguntas_prompt_2 = preguntas_prompt_2[n_batch*12: (n_batch + 1)*12]
        #print("b_preguntas_prompt_2:", len(b_preguntas_prompt_2))
        prompt_gen_reformulated_question = get_prompt_gen_questions_reformulated(questions=b_preguntas_prompt_2)

        messages =  [{'role':'user', 'content': prompt_gen_reformulated_question}]

        response = get_completion_from_messages(
                            messages,
                            model = "gpt-4o-mini-2024-07-18",
                            #model = "gpt-4o-2024-05-13",
                            #model="gpt-3.5-turbo-0613",
                            temperature=0.2)

        print("\nresponse reformulated_question:",response)

        b_preguntas_originals_p2, b_reformulated_questions_p2 = extract_reformulated_questions(response)
        preguntas_originals_p2.extend(b_preguntas_originals_p2)
        reformulated_questions_p2.extend(b_reformulated_questions_p2)

        #print("preguntas_originals_p2:", preguntas_originals_p2)
        #print("preguntas_originals_p2:", len(preguntas_originals_p2))
        #print("reformulated_questions_p2:", len(reformulated_questions_p2))

    derived_preguntas = [[] for _ in range(len(faqs))]
    print("derived_preguntas:", len(derived_preguntas))
    print("preguntas_originals_p1:", len(preguntas_originals_p1))
    print("reformulated_questions_p1:", len(reformulated_questions_p1))
    print("preguntas_originals_p2:", len(preguntas_originals_p2))
    print("reformulated_questions_p2:", len(reformulated_questions_p2))
    for i in range(len(faqs)):
        #print("i:",i)
        for j in range(8):
            print("i:", i)
            print("j:", j)
            #print("j:", j)
            #print("preguntas_originals_p1[j]", preguntas_originals_p1[j])
            #print("reformulated_questions_p1[j]", reformulated_questions_p1[j])
            derived_preguntas[i].extend([preguntas_originals_p1[j + i*8]] + reformulated_questions_p1[j + i*8])
            derived_preguntas[i].extend([preguntas_originals_p2[j + i*8]] + reformulated_questions_p2[j + i*8])
    return derived_preguntas
    #print("Preguntas:", preguntas)

    

import random
import time 

random.seed(42)

text = read_fragment_doc("./faq/faq.txt")
faqs = extract_faqs(text)
#faqs = faqs[:6]
#print("faqs:", faqs)

def generate_derived_questions(faqs, times_samples = 1):
    ids = list(range(len(faqs)))

    all_additional_faqs = []

    for iter in range(times_samples):
        #if iter  >= 1:
        #    continue
        choices = random.sample(ids, k = len(ids))
        num_grupos = len(choices) // 3
        grupos = [choices[i * 3:(i+1)*3] for i in range(num_grupos)]
        sobran = len(choices) % 3
        if sobran > 0:
            grupos = grupos + [choices[-3:]]
        print(grupos)
        
        additional_faqs = []
        
        for group_ids in grupos:
            print("group_ids:",group_ids)
            group_faqs = [faqs[id] for id in group_ids]
            derived_preguntas = generate_questions_based_faq(group_faqs)
            time.sleep(4)
            for id_faq , o_faq, derived_faq in zip(group_ids, group_faqs, derived_preguntas):
                print(len(derived_faq))
                additional_faqs.append({
                    "id_faq": id_faq,
                    "original_question":  o_faq["question"],
                    "additional_questions": derived_faq
                })
        
        
        all_additional_faqs.extend(additional_faqs)

        text_additional_faqs = ""
        for adds_faq in additional_faqs:
            additional_questions = adds_faq["additional_questions"]
            original_question = adds_faq["original_question"]
            text_additional_faqs += "\nPreguntas original: "+ original_question + "\nNuevas Preguntas:\n" + list_json_to_txt(additional_questions)
       
        file = open(f"./faq/additional_faqs/text_additional_faqs_iter{iter + 1}.txt", "w")
        file.writelines(text_additional_faqs)
        file.close()
        save_json("./faq/additional_faqs", "all_additional_faqs", all_additional_faqs)
        time.sleep(10)

    ## unir 
    joined_additional_faqs = [{"id":i, "original_question": faq["question"], "additional_questions": []} for i, faq in enumerate(faqs)]

    for add_faqs in all_additional_faqs:
        joined_additional_faqs[add_faqs["id_faq"]]["additional_questions"].extend(add_faqs["additional_questions"]) 
       
    return joined_additional_faqs

joined_additional_faqs = generate_derived_questions(faqs, times_samples = 2)
save_json("./faq/additional_faqs", "joined_additional_faqs", joined_additional_faqs)

joined_additional_faqs = load_json("./faq/additional_faqs/joined_additional_faqs.json")

import evaluate
threshold_rouge = 0.75

def filter_derived_question( joined_additional_faqs, threshold_rouge = 0.8):
   
    rouge = evaluate.load('rouge')
    total_init_adds_faqs_all = sum([len(additional_faqs["additional_questions"]) for additional_faqs in joined_additional_faqs])
    print(f"\nUn total de {total_init_adds_faqs_all} preguntas iniciales")

    filtered_additional_faqs = []

    for adds_faq in joined_additional_faqs:
        additional_questions = adds_faq["additional_questions"]
        original_question = adds_faq["original_question"]
        print(f"\nUn total de {len(additional_questions)} preguntas iniciales")
        #temp_questions = []
        all_pool_questions = []
        for question in additional_questions:
            if len(all_pool_questions) == 0:
                #temp_questions.append(question) 
                all_pool_questions.append(question)
                continue
            rouge_results = rouge.compute(predictions=[question], references=[all_pool_questions])
            rougeL = rouge_results["rougeL"]
            if rougeL < threshold_rouge:
                all_pool_questions.append(question)
                #temp_questiosns.append(question)

        filtered_additional_faqs.append({
            "id_faq": adds_faq["id"],
            "original_question": original_question,
            "additional_questions": all_pool_questions
        })
        print(f"\nUn total de {len(all_pool_questions)} preguntas finales")


    total_end_adds_faqs_all = sum([len(additional_faqs["additional_questions"]) for additional_faqs in filtered_additional_faqs])
    print(f"\nUn total de {total_end_adds_faqs_all} preguntas finales")

    save_json(f"./faq/derived_faqs_rouge_{str(threshold_rouge)}",f"filtered_questions", filtered_additional_faqs)

    text_additional_faqs = ""
    for filt_adds_faq in filtered_additional_faqs:
        additional_questions = filt_adds_faq["additional_questions"]
        original_question = filt_adds_faq["original_question"]
        text_additional_faqs += "\nPreguntas originales: "+ original_question + "\nNuevas Preguntas:\n" + list_json_to_txt(additional_questions)
   
    file = open(f"./faq/derived_faqs_rouge_{str(threshold_rouge)}/text_additional_faqs_iter_filtrated.txt", "w")
    file.writelines(text_additional_faqs)
    file.close()


    text_pool_questions = list_json_to_txt(all_pool_questions)

    file = open(f"./faq/derived_faqs_rouge_{str(threshold_rouge)}/filtered_questions.txt", "w")
    file.writelines(text_pool_questions)
    file.close() 

filter_derived_question(joined_additional_faqs, threshold_rouge = threshold_rouge)