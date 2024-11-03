

from utils import count_num_tokens, get_completion_from_messages, load_json, save_json, read_fragment_doc

import openai
import json
import re
from dotenv import load_dotenv
import os

load_dotenv(override=True)

def set_openai_key():
    API_KEY = os.getenv("API_KEY")
    openai.api_key = API_KEY

set_openai_key()

def conversation_to_text(messages):
    txt = ""
    for m in messages:
        txt = txt + "\n" + m["role"] + ": "+ m["content"]
    return txt


class EvaluatorLLM:
    def __init__(self, model):
        self.model = model

    def get_prompt_evaluator(self, dialog_context, information, response_ai):
        prompt = f"""Actúa como un juez imparcial y evalúa la calidad de la respuesta generada por un asistente de IA a la última pregunta del usuario en el diálogo a continuación. Usa la información proporcionada entre tres comillas invertidas para determinar si la respuesta es precisa, relevante y coherente con el contenido dado.

Realiza tu evaluación considerando estos cuatro factores:

Utilidad: ¿La respuesta es útil y aporta valor para el usuario?
Coherencia: ¿La respuesta es lógica y consistente, alineándose adecuadamente con la información proporcionada y sin contradicciones internas?
Relevancia: ¿La respuesta aborda directamente la pregunta planteada y se ajusta al contexto?
Precisión: ¿La información presentada es correcta y libre de errores?
Proporciona primero una explicación breve y objetiva que justifique tu evaluación. Luego, califica la respuesta en una escala del 1 al 5 para cada factor y brinda una calificación general que integre los cuatro aspectos.

Utiliza estrictamente el siguiente formato:

Utilidad: [[puntaje]]
Coherencia: [[puntaje]]
Relevancia: [[puntaje]]
Precisión: [[puntaje]]
Calificación General: [[puntaje]]
Sé lo más objetivo posible en tu evaluación.

Información: ```{information}```

Contexto del Dialogo:

{dialog_context}

Respuesta del Asistente de AI: {response_ai}"""

        return prompt

    def extract_scores(self, text):
        pattern = r"(Utilidad|Coherencia|Relevancia|Precisión|Calificación General): \[\[(\d+)\]\]"
        # Extraer los puntajes y almacenarlos en un diccionario
        puntajes = {match[0]: int(match[1]) for match in re.findall(pattern, text)}
        return puntajes


    def eval_response(self, dialog_context, information, response_ai):
        prompt = self.get_prompt_evaluator(dialog_context, information, response_ai)

        response = get_completion_from_messages(
            [{
            "role": "user", 
            "content": prompt
            }],
            #temperature = 0.2, 
            model=self.model)

        scores = self.extract_scores(response)

        return scores
    

    def run_evaluation(self, dataset, save_name):
        all_scores = {}

        for data in dataset:
            dialog_context = conversation_to_text(data["dialog_context"] + [{"role": "user", "content": data["user_message"]}])
            information = "\n".join(data["retrieved_texts"])
            response_ai = data["generated_response"]
            scores =  self.eval_response(self, dialog_context, information, response_ai)

            assert len(scores) == 5, "Factores de evaluación incompletos"

            for k,v in scores.items():
                if k not in all_scores:
                    all_scores[k] = [v]
                else:
                    all_scores[k].append(v)
        
        mean_scores = {}
        for k,v in all_scores.items():
            mean_scores[k] = sum(all_scores[k]) / len(all_scores[k])
        
        results = {"all_scores": all_scores , "mean_scores": mean_scores}
        save_json("./results", save_name, results)
        return results
    

if __name__ == "__main__":
    evaluator = EvaluatorLLM(model="gpt-4o-mini-2024-07-18")
    data_test_path = ""
    data_test = load_json(data_test_path)
    results = evaluator.run_evaluation(data_test, save_name="eval_1")
    print("results:", results)