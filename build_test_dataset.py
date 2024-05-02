import evaluate
from user_ai_asistant_simulation_v3 import AIAssistant as AIAssistantV3
from user_ai_asistant_simulation_v5 import AIAssistant as AIAssistantV5

from utils import read_fragment_doc, list_json_to_txt, set_openai_key, save_json, load_json
import re
import os
from dotenv import load_dotenv
import time
load_dotenv()

set_openai_key()

rouge = evaluate.load('rouge')

def read_data_questions_from_text(path):
    text = read_fragment_doc(path)
    data = []
    pattern = r"Tema:\s+(.+?)Preguntas:(.+?)(?=Tema:|$)"
    matches = re.findall(pattern, text, re.DOTALL)
    for m in matches:
        tema, preguntas = m
        pattern_question = r'\d+\.\s(.+?)(?=\d+\.|$)'
        list_questions = re.findall(pattern_question, preguntas, re.DOTALL)
        list_questions = [q.strip() for q in list_questions]
        data.append({
            "topic": tema.strip(),
            "questions": list_questions
        })
    return data

def filter_questions_by_rouge(data, threshold_rouge = 0.6):
    all_pool_questions = []
    for row in data:
        questions = row["questions"]
        intent_name = row["topic"]
        print("intent_name:", intent_name)
        print(f"\nUn total de {len(questions)} preguntas iniciales")
        pool_questions = [questions[0]]
        for example in questions[1:]:
            rouge_results = rouge.compute(predictions=[example], references=[pool_questions])
            print()
            max_rouge_score = max(rouge_results.values())
            print("max_rouge_score:", max_rouge_score)
            if max_rouge_score < threshold_rouge:
                pool_questions.append(example)
        
        all_pool_questions.append({
            "topic": intent_name,
            "questions": pool_questions
        })
        print(f"\nSe encontro {len(pool_questions)} consultas diferentes, rouge menor a {threshold_rouge}")
    return all_pool_questions

def save_pools_questions(all_pool_questions, threshold_rouge = 0.6):
    text = ""
    for pool_questions in all_pool_questions:
        title = pool_questions["topic"].title()
        list_text = list_json_to_txt(pool_questions["questions"])
        text += "\n" + f"Tema: {title}" + "\n\n" + "Preguntas:\n" + list_text
        
    file = open(f"./tests/test_examples_rouge_{threshold_rouge}.txt", "w")
    file.writelines([text])
    file.close()


#test_data = "./tests/test_examples.txt"
test_data = "./tests/test_examples_rouge_0.5.txt"

data = read_data_questions_from_text(test_data)
total_examples = sum([len(e["questions"]) for e in data])
print("Original Total Preguntas:", total_examples)

filter_question_by_rouge = False

if filter_question_by_rouge:
    threshold_rouge = 0.50

    filtered_pools_questions = filter_questions_by_rouge(data, threshold_rouge)

    new_total_examples = sum([len(e["questions"]) for e in filtered_pools_questions])

    print(f"Filtrado quedan {new_total_examples} examples de {total_examples}:")

    save_pools_questions(filtered_pools_questions, threshold_rouge)
    data = filtered_pools_questions

## Responder preguntas:
cache_path = "./tests/cache.json"
cache = load_json(cache_path) if os.path.exists(cache_path) else {}
test_data = []

print("Numero de Temas:", len(data))

for row in data[0:32]:
    questions = row["questions"]
    for question in questions:
        print("\nUser:", question)
        if question not in cache:
            #ai_assistant_v3 = AIAssistantV3(path_df_kb="./kb/topics.csv")
            ai_assistant_v5 = AIAssistantV5(path_df_kb="./kb/topics.csv")
            #response_ai_assistant_v3 = ai_assistant_v3.generate_response(message = question)
            response_ai_assistant_v5 = ai_assistant_v5.generate_response(message = question)
            #print("\nAssitant V3:", response_ai_assistant_v3)
            #print("\nAssitant V5:", response_ai_assistant_v5)
            response_ai_assistant = response_ai_assistant_v5
            cache[question] = response_ai_assistant
        else:
            response_ai_assistant = cache[question]
        print("\nAssitant:", response_ai_assistant)
        time.sleep(2)
        test_data.append({
            "question": question,
            "answer": response_ai_assistant
        })

save_json("./tests", "cache", cache)
save_json("./test", "test_data", test_data)