
from utils import count_num_tokens, get_completion_from_messages, load_json

import openai
import json
from dotenv import load_dotenv
import os
import time
import re
import pandas as pd
from scipy import spatial
import ast

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

class UserAISim:
    def __init__(self, first_message, model = "gpt-3.5-turbo-0613") -> None:
        
        #prompt_system_role_user = self.get_prompt_system_role()
        prompt_start = self.get_prompt_start()
        
        self.messages = [
            #{'role':'system', 'content': prompt_system_role_user},
            {'role': 'user', 'content': prompt_start},
            {"role": "assistant", "content": first_message}]
        
        self.model = model
    
    def get_prompt_system_role(self):
        prompt_system_role_user = """
Eres un estudiante universitario de la Facultad de Ciencias de la Universidad Nacional de Ingeniería (UNI) y estás buscando información o asesoría sobre uno o varios temas. Asegúrate de cumplir con los siguientes criterios al responder a los mensajes:

Criterio 1: Utiliza un tono semi formal adecuado para un estudiante universitario, evitando declaraciones excesivamente educadas.

Criterio 2: Ten en cuenta el contexto del historial del diálogo en curso y tu objetivo principal para responder de manera concisa y significativa.

Criterio 3: Antes de finalizar la conversación, asegúrate de satisfacer tu interés por comprender completamente todo lo relacionado con el tema o temas consultados.
"""
        return prompt_system_role_user
    # y realiza las consultas pertinentes para satisfacer tu interés por comprender completamente todo lo relacionado con el tema consultado
    def get_prompt_start(self):
        prompt_start = """Actua como un estudiante universitario de la Facultad de Ciencias de la Universidad Nacional de Ingeniería (UNI) que estás buscando información o asesoría.
        Tu (el estudiante universitario) estas hablando con un asistente de AI especialidad en dichos temas.
        Utiliza un tono semi formal adecuado para un estudiante universitario.
        Responde a los mensajes de manera concisa y significativa teniendo en cuenta el contexto del historial del diálogo en curso y realiza las consultas pertinentes para satisfacer tu interés por comprender completamente todo lo relacionado con el tema consultado
        Comienza la conversación con una consulta sobre el tema de interés y mantén dicho rol en las siguientes interacciones.
        """
        return prompt_start


    def generate_response(self, message):
        
        prompt_response_message = f"""Recuerda tu papel de estudiante universitario en busca de información o asesoramiento, y responde al siguiente mensaje del asistente de IA de manera concisa y significativa, teniendo en cuenta el contexto del historial del diálogo en curso.
        Mensaje del asistente de AI: {message}"""

        response_user_ai = get_completion_from_messages(
            self.messages + [{
            "role": "user", 
            "content": prompt_response_message
            }],
            model=self.model)
        
        self.messages.append({
            "role": "user", 
            "content": message
            })
            
        self.messages.append({
            "role": "assistant", 
            "content": response_user_ai
            })
        
        return response_user_ai

class AIAssistant:
    def __init__(
            self, 
            model = "gpt-3.5-turbo-0613",
            path_df_kb = "./kb/topics.csv",
            embedding_model = "text-embedding-3-small") -> None:
        
        prompt_system_role_assistant = self.get_prompt_system_role()
        
        self.df_kb = pd.read_csv(path_df_kb)
        self.df_kb["embedding"] = self.df_kb['embedding'].apply(ast.literal_eval)

        self.messages = [
            {'role':'system', 'content': prompt_system_role_assistant}
        ]
        self.embedding_model = embedding_model
        self.model = model
    
    def get_prompt_system_role(self):
        prompt_system_role_assistant = f"""
Eres Aerito un asistente de AI especializado en temas de matricula, procedimientos y tramites académicos de la Facultad de Ciencias de la Universidad Nacional de Ingenieria de Peru.
Deberas responder a los mensajes asegurandote de cumplir con los siguientes criterios.
    1. Debes proporcionar respuestas informativas, útiles y concisas a las preguntas del usuario al basándote exclusivamente en la información que sera proporcionada, sin añadir información ficticia.
    2. Mantén un tono cordial y empático en sus interacciones.
    3. Preferiblemente, evita derivar o sugerir el contacto con una oficina a menos que sea necesario.
    4. En caso de no encontrar información sobre la consulta en los datos proporcionados, expresa con empatía que no tienes acceso a dicha información.
"""
        return prompt_system_role_assistant

    def get_prompt_response_to_query(self, query, info_texts, token_budget):
        #instrucction = """
#Proporciona una respuesta informativa, significativa y concisa al siguiente mensaje del usuario basándote exclusivamente en la información delimitada por tres comillas invertidas, evitando proporcionar información que no esté explícitamente sustentada en dicha informacion y teniendo en el contexto del historial del diálogo en curso."""
        instrucction = """Proporciona una respuesta concisa, informativa y significativa al siguiente mensaje del usuario utilizando únicamente la información contenida entre tres comillas invertidas. Evita ofrecer datos no respaldados por dicha información y ten en cuenta el contexto del historial del diálogo en curso. Usa maximo 100 palabras"""
        #instrucction = """Proporciona una respuesta informativa, significativa y concisa al siguiente mensaje del usuario basándote exclusivamente en la información delimitada por tres comillas invertidas, evitando proporcionar información que no esté explícitamente sustentada en dicha información y teniendo en cuenta el contexto del historial del diálogo en curso."""
        mensaje_user = f"""Mensaje del usuario: {query}"""

        information = ""

        for text in info_texts:
            
            #template_information = f"""\nInformacion: ```{information}```\n"""
            template_information = f"\nInformación: ```{information + text}```\n"
            prompt_response_to_query = instrucction + template_information + mensaje_user

            if count_num_tokens(prompt_response_to_query, model=self.model) > token_budget:
                break

            information += "\n"+ text

        template_information = f"""\nInformación: ```{information}```\n"""

        prompt_response_to_query = instrucction + template_information + mensaje_user

        return prompt_response_to_query

    def strings_ranked_by_relatedness(
        self,
        query,
        df,
        relatedness_fn=lambda x, y: 1 - spatial.distance.cosine(x, y),
        top_n = 5
    ):
        """Returns a list of strings and relatednesses, sorted from most related to least."""
        query_embedding_response = openai.embeddings.create(
            model= self.embedding_model,
            input=query,
        )

        query_embedding = query_embedding_response.data[0].embedding
        strings_and_relatednesses = [
            (row["text"], relatedness_fn(query_embedding, row["embedding"]))
            for i, row in df.iterrows()
        ]
        strings_and_relatednesses.sort(key=lambda x: x[1], reverse=True)
        strings, relatednesses = zip(*strings_and_relatednesses)
        return strings[:top_n], relatednesses[:top_n]

    def generate_response(self, message):
        
        info_texs, relatednesses = self.strings_ranked_by_relatedness(query=message, df= self.df_kb, top_n=5)

        print("\nrelatednesses:", relatednesses)

        num_tokens_context_dialog =  sum([count_num_tokens(m["content"]) for m in  self.messages])
        print("\nnum_tokens_context_dialog:", num_tokens_context_dialog)
        max_tokens_response = 600

        prompt_response_to_query = self.get_prompt_response_to_query(
            message, info_texs, token_budget= 4096 - num_tokens_context_dialog - max_tokens_response)
        
        #print("\nprompt_response_to_query:", prompt_response_to_query)
        print()

        response_ai_assistant = get_completion_from_messages(
            messages=  self.messages + [{"role": "user", "content": prompt_response_to_query}],
            model=self.model)
        
        self.messages.append({"role": "user", "content": message})
        self.messages.append({"role": "assistant", "content": response_ai_assistant})
        
        return response_ai_assistant



if __name__ == "__main__":

    questions_topics = load_json("./refined_questions_generated.json")
    questions_faq = load_json("./faq/filtered_questions.json")

    #for questions_about_topic in questions_topics[0:1]:
    #    questions = questions_about_topic["questions"]
        #information = questions_about_topic["context"]
        #opening_lines = [question["question"] for question in questions]
        
    for i, question in enumerate(questions_faq[9:10]):
        print(f"\n\nConversacion {i + 1}.......................................................\n\n")

        ai_assistant = AIAssistant()
        user_ai_sim = UserAISim(first_message = question)
        
        print("\nUser:", question)
        response_ai_assistant = ai_assistant.generate_response(message = question)
        print("\nAssitant:", response_ai_assistant)
        
        time.sleep(4)

        for i in range(2):
            response_user_ai = user_ai_sim.generate_response(message=response_ai_assistant)

            print("\nUser:", response_user_ai)
            
            time.sleep(5)

            response_ai_assistant = ai_assistant.generate_response(message = response_user_ai)

            print("\nAssistant:", response_ai_assistant)
            
            time.sleep(5)
