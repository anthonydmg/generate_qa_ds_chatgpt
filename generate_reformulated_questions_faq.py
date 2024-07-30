from utils import get_completion_from_messages, set_openai_key, read_fragment_doc, count_num_tokens, list_json_to_txt, save_json
import os
import re
from dotenv import load_dotenv

load_dotenv(override=True)

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

def get_prompt_gen_questions_based_faq(faqs, num_questions = 40):
    questions_answer_list = list_json_to_txt(faqs)
    print()
    prompt = f"""
Para cada una de las preguntas dentro de las tres comillas invertidas, genera 8 diferentes maneras que un estudiante podría usar para realizar la misma consulta de manera natural y realista a un asistente de AI. Varía tanto la persona gramatical (primera persona y tercera persona) como el nivel de formalidad del lenguaje (formal, semiformal o informal). Además, varía el nivel de concisión de cada una. Algunas preguntas pueden ser sumamente concisas y directas, mientras que otras pueden ser más detalladas y elaboradas.
Presenta las nuevas preguntas para cada pregunta original de la siguiente manera:

Pregunta Original 1: Aqui la Pregunta Original 1

Preguntas Generadas:
1. Aqui la primer pregunta generada como una manera diferente de la consultar la primer pregunta original
2. Aqui la segunda pregunta generada como una manera diferente de la consultar la primer pregunta original
...
8. Aqui la octava pregunta generada como una manera diferente de la consultar la primer pregunta original

Pregunta Original 2: Aqui la Pregunta Original 2

Preguntas Generadas:
1. Aqui la primer pregunta generada como una manera diferente de la consultar la segunda pregunta original
2. Aqui la segunda pregunta generada como una manera diferente de la consultar la segunda pregunta original
...
8. Aqui la octava pregunta generada como una manera diferente de la consultar la segunda pregunta original

Pregunta Original 3: Aqui la Pregunta Original 3

Preguntas Generadas:
... 

Preguntas y Respuestas:
```{questions_answer_list}```

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

def generate_questions_reformulated_based_faq(faqs):
    print(f'\nquestion-0:{faqs[0]["question"]}')
    print(f'\nquestion-1:{faqs[1]["question"]}')
    print(f'\nquestion-2:{faqs[2]["question"]}')
    list_faqs = [faq["question"] + "\n" + "Respuesta: " +  faq["answer"] for faq in faqs]
    total_tokens = sum([count_num_tokens(faq) for faq in list_faqs])
    print("total_tokens:", total_tokens)
    num_questions = get_num_questions(total_tokens)
    
    prompt = get_prompt_gen_questions_based_faq(list_faqs, num_questions)

    messages =  [{'role':'user', 'content': prompt}]

    response = get_completion_from_messages(
                        messages,
                        model="gpt-4o-mini-2024-07-18",
                        #model="gpt-3.5-turbo-0613",
                        temperature=0.2)
    
    print("response:",response)
    print()
    original_questions, generated_questions = extract_reformulated_questions(response)

   
    num_group_question_generated = len(generated_questions)
    
    print("\nlen(generated_questions):",num_group_question_generated)
    
    questions_generated_for_questions =  []
    
    for i in range(num_group_question_generated):
        if num_group_question_generated == 3 or original_questions[i].lower() == faqs[i]["question"].strip().lower():
            questions_generated_for_questions.append({
                "original_question": faqs[i]["question"],
                "questions_generated": generated_questions[i]
            })
        else:
            questions_generated_for_questions.append({
                "original_question": original_questions[i],
                "questions_generated": generated_questions[i]
            })
    
    return questions_generated_for_questions
    

import random
import time

random.seed(42)

text = read_fragment_doc("./faq/faq.txt")
faqs = extract_faqs(text)

def generate_reformulated_faq(faqs, times_samples = 8):
    ids = list(range(len(faqs)))
    reformulated_faqs = []
    for iter in range(times_samples):
        print(f"\nIteración {iter}\n")
        

        choices = random.sample(ids, k = len(ids))
        num_grupos = len(choices) // 3
        grupos = [choices[i * 3:(i+1)*3] for i in range(num_grupos)]
        sobran = len(choices) % 3
        
        if iter < 10:
           continue

        if sobran > 0:
            grupos = grupos + [choices[-3:]]
        #print(grupos)
        
        #additional_faqs = []
        
        for group_ids in grupos:
            print(group_ids)
            group_faqs = [faqs[id] for id in group_ids]
            questions_generated_for_questions = generate_questions_reformulated_based_faq(group_faqs)
            reformulated_faqs.extend(questions_generated_for_questions)
            time.sleep(2)

        save_json("./faq", "reformulated_faqs", reformulated_faqs)

    return reformulated_faqs
        
reformulated_faqs = generate_reformulated_faq(faqs, times_samples = 12)

save_json("./faq", "reformulated_faqs", reformulated_faqs)
