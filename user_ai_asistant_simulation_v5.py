
from utils import count_num_tokens, get_completion_from_messages, load_json, save_json

import openai
import json
from dotenv import load_dotenv
import os
import time
import re
import pandas as pd
from scipy import spatial
import ast
import random
import numpy


    
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
    def __init__(self, model = "gpt-3.5-turbo-0613", start_greeting = False) -> None:
        
        #prompt_system_role_user = self.get_prompt_system_role()
        prompt_start = self.get_prompt_start(start_greeting)
        self.start_greeting = start_greeting
        self.messages = [
            {'role': 'user', 'content': prompt_start},
            ]
        
        self.model = model
    
    def start_conversation(self):
        response_user_ai = get_completion_from_messages(
            self.messages,
            model=self.model)
        
        self.push_user_messages_to_history(response_user_ai)
        return response_user_ai

    def push_user_messages_to_history(self, message):
        # El asistente actua como un usuario
        self.messages.append({
            "role": 'assistant',
            "content": message 
        })
    
    def finish_conversation(self, message):
        num_words = random.choice([2, 4, 5, 10, 15, 20])

        prompt_response_message = f"""Recuerda que eres un estudiante universitario en busca de información o asesoramiento que esta conversando con un asistente de AI especializado en dichos temas, responde al siguiente mensaje del asistente de IA finalizando la conversación (Max. {num_words} palabras).
Mensaje del asistente de AI: {message}"""

        #prompt_response_message = f"""Recuerda tu papel de estudiante universitario en busca de información o asesoramiento, y responde al siguiente mensaje del asistente de IA finalizando la conversación (Max. {num_words} palabras).
        #Mensaje del asistente de AI: {message}"""

        response_user_ai = get_completion_from_messages(
            self.messages + [{
            "role": "user", 
            "content": prompt_response_message
            }],
            model=self.model)
        
        self.push_assistant_messages_to_history(message)
                
        self.push_user_messages_to_history(response_user_ai)
        
        return response_user_ai   

    
    def push_assistant_messages_to_history(self, message):
        # Desde la perspectiva del asistente el usuario seria seria el asistente de AI
        self.messages.append({
            "role": 'user',
            "content": message 
        })

    def get_prompt_system_role(self):
        prompt_system_role_user = """
Eres un estudiante universitario de la Facultad de Ciencias de la Universidad Nacional de Ingeniería (UNI) y estás buscando información o asesoría sobre uno o varios temas. Asegúrate de cumplir con los siguientes criterios al responder a los mensajes:

Criterio 1: Utiliza un tono semi formal adecuado para un estudiante universitario, evitando declaraciones excesivamente educadas.

Criterio 2: Ten en cuenta el contexto del historial del diálogo en curso y tu objetivo principal para responder de manera concisa y significativa.

Criterio 3: Antes de finalizar la conversación, asegúrate de satisfacer tu interés por comprender completamente todo lo relacionado con el tema o temas consultados.
"""
        return prompt_system_role_user
    # y realiza las consultas pertinentes para satisfacer tu interés por comprender completamente todo lo relacionado con el tema consultado
    def get_prompt_start(self, start_greeting = False):
        prompt_start = """Actúa como un estudiante universitario de la Facultad de Ciencias de la Universidad Nacional de Ingeniería (UNI) que estás buscando información o asesoría.
            Tu (el estudiante universitario) estas hablando con un asistente de AI especialidad en dichos temas.
            Utiliza un tono semi formal adecuado para un estudiante universitario.
            Responde a los mensajes de manera concisa y significativa teniendo en cuenta el contexto del historial del diálogo en curso y realiza las consultas pertinentes para satisfacer tu interés por comprender completamente todo lo relacionado con el tema consultado"""
        
        type_greeting = random.choice(["formal","informal", "semiformal"])
        print("type_greeting:", type_greeting)
        num_words = random.choice([1, 2, 5, 10, 15, 20])
        print("num_words", num_words)
        if start_greeting:
            prompt_start += f"\nComienza la conversación simplemente con un saludo {type_greeting} conciso al asistente (Max. {num_words} palabras) y mantén dicho rol en las siguientes interacciones."
        else:
            prompt_start += "\nComienza la conversación con una consulta sobre el tema de interés y mantén dicho rol en las siguientes interacciones."

        return prompt_start


    def generate_response(self, message):
        
        #prompt_response_message = f"""Recuerda que eres un estudiante universitario en busca de información o asesoramiento que esta conversando con un asistente de AI especializado en dichos temas, responde de manera concisa y significativa al siguiente mensaje del asistente en máximo 40 palabras.
#Mensaje del asistente de AI: {message}"""
        num_turn = len(self.messages) // 2 + (1 if not self.start_greeting else 0)
        print("\nNumero de turno:", num_turn)
        if num_turn > 2:
            prompt_response_message = f"""Recuerda tu papel de estudiante universitario en busca de información o asesoramiento, y responde en menos 40 palabras de manera concisa y significativa al siguiente mensaje del asistente de IA proveído en respuesta a tu ultimo mensaje, teniendo en cuenta el contexto del historial del diálogo en curso.
        Mensaje del asistente de AI: {message}"""
        else:
            prompt_response_message = f"""Recuerda tu papel de estudiante universitario en busca de información o asesoramiento, y responde de manera concisa y significativa al siguiente mensaje del asistente de IA proveído en respuesta a tu ultimo mensaje, teniendo en cuenta el contexto del historial del diálogo en curso.
        Mensaje del asistente de AI: {message}"""

        #prompt_response_message = f"""Recuerda que tu (el estudiante universitario en busca de información o asesoramiento) estas hablando con un asistente de AI, responde de manera concisa y significativa al siguiente mensaje del asistente de IA (Max. 50 palabras), teniendo en cuenta el contexto del historial del diálogo en curso.
        #Mensaje del asistente de AI: {message}"""

        #Tu (el estudiante universitario) estas hablando con un asistente de AI especialidad

        
        response_user_ai = get_completion_from_messages(
            self.messages + [{
            "role": "user", 
            "content": prompt_response_message
            }],
            model=self.model)
        
        
        self.push_assistant_messages_to_history(message)
        #print("self.messages:",  self.messages)
        self.push_user_messages_to_history(response_user_ai)   
        
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
        
        self.contexts = [None]
        self.recovered_texts = [None]

        self.embedding_model = embedding_model
        self.model = model
    
    def get_prompt_system_role(self):
        prompt_system_role_assistant = f"""
Eres Aerito un asistente de AI especializado en temas de matricula, procedimientos y tramites académicos de la Facultad de Ciencias de la Universidad Nacional de Ingeniería de Peru.
Deberás responder a los mensajes asegurándote de cumplir con los siguientes criterios.
    1. Debes proporcionar respuestas informativas, útiles y concisas a las preguntas del usuario basándote exclusivamente en la información vinculada a la Faculta de Ciencias que sera proporcionada, sin añadir información ficticia.
    2. Mantén un tono cordial, empático y servicial en sus interacciones.
    3. Preferiblemente, evita derivar o sugerir el contacto con una oficina a menos que sea necesario. Si no hay otra oficina más idónea, la derivación se realizará hacia la Oficina de Estadística de la Facultad de Ciencias.
    4. En caso de no encontrar información sobre la consulta en los datos proporcionados, expresa con empatía que no tienes acceso a dicha información.
"""
        return prompt_system_role_assistant

    def join_info_texts(self, 
        info_texts, 
        token_budget):
        
        information = ""

        for text in info_texts:
            
            template_information = f"\nInformación: ```{information + text}```\n"

            if count_num_tokens(template_information, model=self.model) > token_budget:
                break

            information += "\n"+ text
        
        return information

    def get_prompt_response_to_query(self, query, info_texts, token_budget):
        #instrucction = """# sin hacer mención a la información
#Proporciona una respuesta informativa, significativa y concisa al siguiente mensaje del usuario basándote exclusivamente en la información delimitada por tres comillas invertidas, evitando proporcionar información que no esté explícitamente sustentada en dicha informacion y teniendo en el contexto del historial del diálogo en curso."""
        #  en lugar menciona que no tienes acceso a dicha información según sea necesario
        instrucction = """Proporciona una respuesta concisa y significativa al siguiente mensaje del usuario, considerando el contexto del historial del diálogo en curso. Utiliza solo la información entre tres comillas invertidas para responder de manera informativa a consultas del usuario. Evita ofrecer datos no respaldados explícitamente o no bien desarrollados en dicha información; en su lugar, indica claramente que "no tienes acceso a esa información" cuando sea relevante. Limita la respuesta a un máximo de 100 palabras."""

        #instrucction = """Proporciona una respuesta concisa y significativa al siguiente mensaje del usuario, considerando el contexto del historial del diálogo en curso. Utiliza solo la información entre tres comillas invertidas para responder de manera informativa a consultas del usuario. Evita proporcionar datos no respaldados explícitamente en dicha información. Usa máximo 100 palabras."""
        
        #instrucction = """Proporciona una respuesta concisa, informativa y significativa al siguiente mensaje del usuario utilizando únicamente la información contenida entre tres comillas invertidas. Evita ofrecer datos no respaldados por dicha información y ten en cuenta el contexto del historial del diálogo en curso. Usa máximo 100 palabras"""
        #instrucction = """Proporciona una respuesta informativa, significativa y concisa al siguiente mensaje del usuario basándote exclusivamente en la información delimitada por tres comillas invertidas, evitando proporcionar información que no esté explícitamente sustentada en dicha información y teniendo en cuenta el contexto del historial del diálogo en curso."""
        mensaje_user = f"""Mensaje del usuario: {query}"""
        
        token_budget = token_budget - count_num_tokens(instrucction + mensaje_user, model=self.model)
        
        information = self.join_info_texts(info_texts, token_budget)
        
        self.contexts.append(information)
        
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

    def generate_response(self, message, use_kb = True):
        if use_kb == True:
            query = self.messages[-1]["content"] + "\n" + message if len(self.messages) > 1 else message

            #print("query:", query)
            info_texs, relatednesses = self.strings_ranked_by_relatedness(query=query, df= self.df_kb, top_n=5)
            
            self.recovered_texts.append([{"text": text, "relatedness": relatedness } for text , relatedness in zip(info_texs, relatednesses)])
            
            print("\nrelatednesses:", relatednesses)

            num_tokens_context_dialog =  sum([count_num_tokens(m["content"]) for m in  self.messages])
            print("\nnum_tokens_context_dialog:", num_tokens_context_dialog)
            max_tokens_response = 1000

            prompt_response_to_query = self.get_prompt_response_to_query(
                message, info_texs, token_budget= 4096 - num_tokens_context_dialog - max_tokens_response)
            
            response_ai_assistant = get_completion_from_messages(
            messages= self.messages + [{"role": "user", "content": prompt_response_to_query}],
            model = self.model
            )

            self.messages.append({"role": "user", "content": message})

        else:
            self.messages.append({"role": "user", "content": message})
            response_ai_assistant = get_completion_from_messages(
            messages= self.messages,
            model = self.model)
            self.contexts.append(None)
            self.recovered_texts.append(None)
            
        print()
        
        self.messages.append({"role": "assistant", "content": response_ai_assistant})
        self.contexts.append(None)
        self.recovered_texts.append(None)
        
        return response_ai_assistant
    
    def get_history_dialog(self, include_context = True):
        if include_context:
            history_dialog = []
            for message, context, texts in zip(self.messages[1:], self.contexts[1:], self.recovered_texts[1:]):
                history_dialog.append({
                    "role": message["role"],
                    "content": message["content"],
                    "context": context,
                    "recovered_texts": texts
                })
                
            return history_dialog
        else:
            return self.messages[1:]


if __name__ == "__main__":
    random.seed(42)
    #questions_topics = load_json("./refined_questions_generated.json")
    questions_faq = load_json("./faq/filtered_questions.json")
    conversations_simulated = []
    #for questions_about_topic in questions_topics[0:1]:
    #    questions = questions_about_topic["questions"]
        #information = questions_about_topic["context"]
        #opening_lines = [question["question"] for question in questions]
    
    start = 220
    end = 230
    for i, question in enumerate(questions_faq[start:end]):
        print(f"\n\nConversación {i + 1}.......................................................\n\n")

        #conversation = [{}]
        ai_assistant = AIAssistant()
        
        start_greeting = numpy.random.choice([True, False],1, p = [0.2,0.8])[0]
        user_ai_sim = UserAISim(start_greeting = start_greeting)
        print("start_greeting:", start_greeting)
        
        if start_greeting:
            response_user_ai = user_ai_sim.start_conversation()
            print("\nUser:", response_user_ai)
            response_ai_assistant = ai_assistant.generate_response(message = response_user_ai, use_kb= False)
            print("\nAssistant:", response_ai_assistant)
            user_ai_sim.push_assistant_messages_to_history(response_ai_assistant)
        
        user_ai_sim.push_user_messages_to_history(question) 
        
        print("\nUser:", question)
        response_ai_assistant = ai_assistant.generate_response(message = question)
        print("\nAssistant:", response_ai_assistant)
        
        time.sleep(4)
        num_turns = random.choice([2,3])
        for i in range(num_turns):
            
            finish_conversation = numpy.random.choice([True, False],1, p = [0.3,0.7])[0]
           
            if i >= 1 and finish_conversation:
                print("\nfinish_conversation:",finish_conversation)
                response_user_ai = user_ai_sim.finish_conversation(message=response_ai_assistant)
                
                print("\nUser:", response_user_ai)

                response_ai_assistant = ai_assistant.generate_response(message = response_user_ai, use_kb= False)

                print("\nAssistant:", response_ai_assistant)

                 ## save conversation

                #messages = ai_assistant.get_history_dialog(include_context=True)
                #conversations_simulated.append({
                #    "openline": question,
                #    "messages": messages
                #})
            
                break

            response_user_ai = user_ai_sim.generate_response(message=response_ai_assistant)

            print("\nUser:", response_user_ai)
            
            time.sleep(5)

            response_ai_assistant = ai_assistant.generate_response(message = response_user_ai)

            print("\nAssistant:", response_ai_assistant)
            
            time.sleep(5)

        ## save conversation

        messages = ai_assistant.get_history_dialog(include_context=True)
        conversations_simulated.append({
            "openline": question,
            "messages": messages
        })
            

    save_json("./conversational_data", f"conversations_simulated_{start}_to_{end-1}", conversations_simulated)

