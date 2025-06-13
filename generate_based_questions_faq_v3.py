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

def get_prompt_2_gen_questions_based_faq(faqs, num_questions = 40):
    questions_answer_list = list_json_to_txt(faqs)
    print()
    prompt = f"""
Se te proveerá una lista de preguntas y respuestas frecuentes de la Facultad de Ciencias de Universidad para alumnos de pregrado delimitadas por tres comillas invertidas.
Utilizando las preguntas y respuestas proporcionadas, genera una lista de 8 preguntas únicas que abarquen. Cada pregunta debe tener una respuesta dentro de la información proporcionada, cumpliendo con los siguientes criterios:

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

#    - Asegurante que las preguntas tengan respuesta en la información contenida en la respuesta original. 


def get_prompt_gen_questions_based_faq_refactor(faqs):
    questions_answer_list = list_json_to_txt(faqs)
    prompt = f"""Se te proporcionará una lista de preguntas y respuestas frecuentes sobre temas de interés para estudiantes de pregrado de la Facultad de Ciencias de la Universidad Nacional de Ingeniería, delimitadas por tres comillas invertidas. Tu tarea es generar **12 preguntas derivadas y únicas** para cada par de pregunta y respuesta, siguiendo los criterios detallados a continuación:

### **Criterios:**

1. **Cobertura de contenido:**  
   - Las preguntas generadas deben abordar tanto aspectos generales como detalles específicos del tema asegurándote de mantener la claridad y especificidad del tema consultado.  
   - Cada pregunta debe ser formulada de modo que pueda responderse únicamente con la información contenida en la respuesta original.  

2. **Variedad en la formulación:**  
   - Incluye diferentes tipos de preguntas: condicionales, de inferencia, de causa y efecto, de definición, etc. 
   - Mantén la claridad y especificidad del tema consultado, asegurándote de que cada pregunta esté formulada desde una perspectiva autónoma y no haga referencia a información externa o implícita.

3. **Relevancia:**  
   - Asegúrate de que las preguntas sean útiles y pertinentes para estudiantes de la Facultad de Ciencias de la UNI.

4. **Formato de salida:**  
   Presenta las preguntas generadas utilizando el siguiente esquema:  
   
   ```  
   **Pregunta Original 1:** [Aquí la pregunta original 1]  
   1. [Pregunta derivada 1]  
   2. [Pregunta derivada 2]  
   ...  
   12. [Pregunta derivada 12]  

   **Pregunta Original 2:** [Aquí la pregunta original 2]  
   1. [Pregunta derivada 1]  
   2. [Pregunta derivada 2]  
   ...  
   12. [Pregunta derivada 12]  
   ```  
Preguntas y Respuestas:
```{questions_answer_list}```"""
    return prompt

# abarquen diferentes niveles de complejidad y 

## colocar aca que eviten falta de especificidad en la pregunta. O evitanto falta de contexto en las preguntas.
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

def get_prompt_gen_questions_reformulated(questions, num_questions = 4):
    questions_list = list_json_to_txt(questions)
    prompt = f"""Se te proveerá una lista de preguntas frecuentes sobre temas de interés para alumnos de pregrado de la Facultad de Ciencias de la Universidad Nacional de Ingeniería, delimitadas por tres comillas invertidas.
Para cada una de las preguntas dentro de las tres comillas invertidas, genera {num_questions} diferentes maneras que un estudiante podría usar para realizar la misma consulta de manera natural y realista a un asistente de AI. Varía tanto la persona gramatical adoptando la perspectiva de un estudiante consultando a un Asistente de AI (en primera persona y tercera persona) como el nivel de formalidad del lenguaje (formal, semiformal o informal). Además, varía el nivel de concisión de cada una. Algunas preguntas pueden ser sumamente concisas y directas, mientras que otras pueden ser más detalladas y elaboradas.
Presenta las nuevas preguntas para cada pregunta original de la siguiente manera:

- Pregunta Original 1: Aqui la Pregunta Original 1

Preguntas Generadas:
1. Aqui la pregunta 1 generada como una manera diferente de la consultar la primer pregunta original
2. Aqui la pregunta 2 generada como una manera diferente de la consultar la primer pregunta original
...
{num_questions}. Aqui la pregunta {num_questions} generada como una manera diferente de la consultar la primer pregunta original

- Pregunta Original 2: Aqui la Pregunta Original 2

Preguntas Generadas:
1. Aqui la pregunta 1 generada como una manera diferente de la consultar la segunda pregunta original
2. Aqui la pregunta 2 generada como una manera diferente de la consultar la segunda pregunta original
...
{num_questions}. Aqui la pregunta {num_questions} generada como una manera diferente de la consultar la segunda pregunta original

- Pregunta Original 3: Aqui la Pregunta Original 3

Preguntas Generadas:
... 

Lista de preguntas: ```{questions_list}```
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
import math

def gen_reformulated_questions(questions, num_questions = 4):
    preguntas_originals = []
    reformulated_questions = []
    num_batchs = max(1, math.ceil(len(questions)/12.0))

    for n_batch in range(num_batchs):
        print(f"Batch-Prompt-01------------------------------------------------------{n_batch}")
        time.sleep(5)
        start = n_batch*12
        end = min((n_batch + 1)*12, len(questions))
        b_preguntas_prompt_1 = questions[start: end]
        #print("b_preguntas_to_reformulated:\n", b_preguntas_prompt_1)
        prompt_gen_reformulated_question = get_prompt_gen_questions_reformulated(questions=b_preguntas_prompt_1, num_questions = num_questions)

        messages =  [{'role':'user', 'content': prompt_gen_reformulated_question}]

        response = get_completion_from_messages(
                            messages,
                            model = "gpt-4o-mini-2024-07-18",
                            #model = "gpt-4o-2024-05-13",
                            #model="gpt-3.5-turbo-0613",
                            temperature=0.2)

        print("response reformulated_question-1:", response)
        
        b_preguntas_originals, b_reformulated_questions = extract_reformulated_questions(response)
        preguntas_originals.extend(b_preguntas_originals)
        reformulated_questions.extend(b_reformulated_questions)
    return preguntas_originals, reformulated_questions
    
def generate_questions_based_faq(faqs):
    ## reformulated faqs
    list_faqs = [faq["question"] + "\n" + "Respuesta: " +  faq["answer"] for faq in faqs]

    total_tokens = sum([count_num_tokens(faq) for faq in list_faqs])
    num_questions = get_num_questions(total_tokens)
    
    prompt = get_prompt_gen_questions_based_faq_refactor(list_faqs)

    messages =  [{'role':'user', 'content': prompt}]

    response = get_completion_from_messages(
                        messages,
                        model="gpt-4o-2024-11-20",
                        #model = "gpt-4o-mini-2024-07-18",
                        temperature=0.2)

    print("response prompt-1:",response)

    preguntas_generated = extract_questions_from_response_regex(response)
    preguntas_originals, reformulated_questions = gen_reformulated_questions(preguntas_generated, num_questions=4)

    derived_preguntas = [[] for _ in range(len(faqs))]

    for i in range(len(faqs)):
        #print("i:",i)
        for j in range(12):
            print("i:", i)
            print("j:", j)
            derived_preguntas[i].extend([preguntas_originals[j + i*12]]  
                                         + reformulated_questions[j + i*12]
                                        )
    return derived_preguntas

import random
import time 

random.seed(42)

text = read_fragment_doc("./faq/faq.txt")
faqs = extract_faqs(text)
#faqs = faqs[:6]
print("faqs:", len(faqs))

def generate_derived_questions(faqs, times_samples = 1):
    num_faqs = len(faqs) 
    ids = list(range(num_faqs))

    all_derived_faqs = []

    for iter in range(times_samples):
        print(f"\n_____________iter-{iter}____________\n")
        choices = random.sample(ids, k = len(ids))
        
        num_grupos = num_faqs // 3
        grupos = [choices[i * 3:(i+1)*3] for i in range(num_grupos)]
        sobran = num_faqs % 3
        if sobran > 0:
            grupos = grupos + [choices[-sobran:]]
        #print("grupos:",grupos)

        #if iter  <= 1:
        #    continue
        derived_faqs = []
        
        for group_ids in grupos:
            print("group_ids:",group_ids)
            group_faqs = [faqs[id] for id in group_ids]
            derived_preguntas = generate_questions_based_faq(group_faqs)
            time.sleep(4)
            for id_faq , o_faq, new_derived_faq in zip(group_ids, group_faqs, derived_preguntas):
                print(len(new_derived_faq))
             
                derived_faqs.append({
                    "id_faq": id_faq,
                    "original_question":  o_faq["question"],
                    "derived_questions": new_derived_faq,
                    "iter": iter
                })
        
        
        all_derived_faqs.extend(derived_faqs)

        text_derived_faqs = ""
        for adds_faq in derived_faqs:
            derived_questions = adds_faq["derived_questions"]
            original_question = adds_faq["original_question"]
            text_derived_faqs += "\nPreguntas original: "+ original_question + "\nNuevas Preguntas:\n" + list_json_to_txt(derived_questions)
        os.makedirs("./faq/derived_faqs/", exist_ok=True)
        file = open(f"./faq/derived_faqs/text_derived_faqs_iter{iter + 1}.txt", "w")
        file.writelines(text_derived_faqs)
        file.close()
        #all_derived_faqs_prev = load_json("./faq/derived_faqs/all_derived_faqs.json")
        #all_derived_faqs_prev.extend(all_derived_faqs)
        save_json("./faq/derived_faqs", "all_derived_faqs", all_derived_faqs)
        time.sleep(10)

    all_derived_faqs = load_json("./faq/derived_faqs/all_derived_faqs.json")
    ## unir 
    joined_derived_faqs = [{"id":i, "original_question": faq["question"], "derived_questions": []} for i, faq in enumerate(faqs)]

    for add_faqs in all_derived_faqs:
        joined_derived_faqs[add_faqs["id_faq"]]["derived_questions"].extend(add_faqs["derived_questions"]) 
       
    return joined_derived_faqs

def questions_generation_based_faqs(faqs):
    fqs = [faq["question"] for faq in faqs]
    originals_questions, reformulated_questions = gen_reformulated_questions(fqs, num_questions=5)
    print("originals_questions:", len(originals_questions))
    print("reformulated_questions:", len(reformulated_questions))
    reformulated_faqs = []
    #reformulated_faqs = load_json("./faq/reformulated_faqs/reformulated_faqs.json")
    #prev_num = len(reformulated_faqs)
    for id_q in range(len(fqs)):
        reformulated_faqs.append({
                        "id_faq": id_q,
                        "original_question": originals_questions[id_q],
                        "reformulated_questions": reformulated_questions[id_q]
                    })
    
    save_json("./faq/reformulated_faqs", "reformulated_faqs", reformulated_faqs)
    joined_additional_faqs = generate_derived_questions(faqs, times_samples = 3)
    save_json("./faq/derived_faqs", "joined_derived_faqs", joined_additional_faqs)

#questions_generation_based_faqs(faqs)

import evaluate


def split_file_questions_derived(dir_path, filtered_questions_derived_rouge):
    for i, derived_faq in enumerate(filtered_questions_derived_rouge):
        #original_question = derived_faq["original_question"]
        id_faq = derived_faq["id_faq"]
        questions_generated = derived_faq["derived_questions"]
        save_json(dir_path, f"derived_questions_faq_{id_faq + 1}", questions_generated)
    return

def filter_generated_question(threshold_rouge = 0.8):
    joined_derived_faqs = load_json("./faq/derived_faqs/joined_derived_faqs.json")
    reformulated_faqs = load_json("./faq/reformulated_faqs/reformulated_faqs.json")
    rouge = evaluate.load('rouge', module_type="metric")
    total_init_adds_faqs_all = sum([len(derived_faqs["derived_questions"]) for derived_faqs in joined_derived_faqs]) + sum([len(reform_faqs["reformulated_questions"]) for reform_faqs in reformulated_faqs])
    print(f"\nUn total de {total_init_adds_faqs_all} preguntas iniciales")
    
    filtered_generated_faqs = []

    for derived_faqs, reform_faqs in zip(joined_derived_faqs, reformulated_faqs):
        derived_questions = reform_faqs["reformulated_questions"] + derived_faqs["derived_questions"]
        original_question = derived_faqs["original_question"]
        print(f"\nUn total de {len(derived_questions)} preguntas iniciales")
        #temp_questions = []
        all_pool_questions = []
        for question in derived_questions:
            if len(all_pool_questions) == 0:
                #temp_questions.append(question) 
                all_pool_questions.append(question)
                continue
            rouge_results = rouge.compute(predictions=[question], references=[all_pool_questions])
            rougeL = rouge_results["rougeL"]
            if rougeL < threshold_rouge:
                all_pool_questions.append(question)
                #temp_questiosns.append(question)

        filtered_generated_faqs.append({
            "id_faq": derived_faqs["id"],
            "original_question": original_question,
            "derived_questions": all_pool_questions
        })
        print(f"\nUn total de {len(all_pool_questions)} preguntas finales")


    total_end_adds_faqs_all = sum([len(additional_faqs["derived_questions"]) for additional_faqs in filtered_generated_faqs])
    print(f"\nUn total de {total_end_adds_faqs_all} preguntas finales")

    save_json(f"./faq/final_derived_faqs_rouge_{str(threshold_rouge)}",f"filtered_questions", filtered_generated_faqs)

    text_additional_faqs = ""
    for filt_adds_faq in filtered_generated_faqs:
        derived_questions = filt_adds_faq["derived_questions"]
        original_question = filt_adds_faq["original_question"]
        text_additional_faqs += "\nPreguntas originales: "+ original_question + "\nNuevas Preguntas:\n" + list_json_to_txt(derived_questions)
   
    file = open(f"./faq/final_derived_faqs_rouge_{str(threshold_rouge)}/text_additional_faqs_iter_filtrated.txt", "w")
    file.writelines(text_additional_faqs)
    file.close()

    text_pool_questions = list_json_to_txt(all_pool_questions)

    file = open(f"./faq/final_derived_faqs_rouge_{str(threshold_rouge)}/filtered_questions.txt", "w")
    file.writelines(text_pool_questions)
    file.close()

    split_file_questions_derived(f"./faq/final_derived_faqs_rouge_{str(threshold_rouge)}", filtered_generated_faqs)

if __name__ == "__main__":
    threshold_rouge = 0.70
    #questions_generation_based_faqs(faqs)
    #filter_generated_question(threshold_rouge = threshold_rouge)


