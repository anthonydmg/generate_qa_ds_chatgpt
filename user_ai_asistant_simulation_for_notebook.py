
#from utils import get_completion_from_messages_from_messages, load_json,

import time
import random
import numpy
import requests
import openai

def get_completion_from_messages(messages, model="gpt-3.5-turbo"): # Andrew mentioned that the prompt/ completion paradigm is preferable for this class
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=0, # this is the degree of randomness of the model's output
    )
    return response.choices[0].message["content"]

def conversation_to_text(messages):
    txt = ""
    for m in messages:
        txt = txt + "\n" + m["role"] + ": "+ m["content"]
    return txt

class UserAISim:
    def __init__(self, model = "gpt-3.5-turbo-0613", start_greeting = False) -> None:
        
        #prompt_system_role_user = self.get_prompt_system_role()
        prompt_start = self.get_prompt_start(start_greeting)
        
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

        prompt_response_message = f"""Recuerda tu papel de estudiante universitario en busca de información o asesoramiento, y responde al siguiente mensaje del asistente de IA finalizando la conversación (Max. {num_words} palabras).
        Mensaje del asistente de AI: {message}"""

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
        
        prompt_response_message = f"""Recuerda tu papel de estudiante universitario en busca de información o asesoramiento, y responde al siguiente mensaje del asistente de IA de manera concisa y significativa (Max. 50 palabras), teniendo en cuenta el contexto del historial del diálogo en curso.
        Mensaje del asistente de AI: {message}"""

        response_user_ai = get_completion_from_messages(
            self.messages + [{
            "role": "user", 
            "content": prompt_response_message
            }],
            model=self.model)
        
        
        self.push_assistant_messages_to_history(message)
 
        self.push_user_messages_to_history(response_user_ai)   
        
        return response_user_ai

class AIAssistant:
    def __init__(
            self, 
            model = "gpt-3.5-turbo-0613") -> None:
        
        prompt_system_role_assistant = self.get_prompt_system_role()

        self.messages = [
            {'role':'system', 'content': prompt_system_role_assistant}
        ]
        self.model = model
    
    def get_prompt_system_role(self):
        prompt_system_role_assistant = f"""
Eres Aerito un asistente de AI especializado en temas de matricula, procedimientos y tramites académicos de la Facultad de Ciencias de la Universidad Nacional de Ingeniería de Peru.
Deberás responder a los mensajes asegurándote de cumplir con los siguientes criterios.
    1. Debes proporcionar respuestas informativas, útiles y concisas a las preguntas del usuario al basándote exclusivamente en la información que sera proporcionada, sin añadir información ficticia.
    2. Mantén un tono cordial, empático y servicial en sus interacciones.
    3. Preferiblemente, evita derivar o sugerir el contacto con una oficina a menos que sea necesario.
    4. En caso de no encontrar información sobre la consulta en los datos proporcionados, expresa con empatía que no tienes acceso a dicha información.
"""
        return prompt_system_role_assistant
    
    def request_num_tokens(self, messages):
        url = 'https://demo-ant-api-b26e14484ab9.herokuapp.com/count_tokens/'
        # Datos que quieres enviar en la solicitud POST
        #messages = []

        response = requests.post(url, json=messages)
        if response.status_code == 200:
            # La solicitud fue exitosa, mostrar la respuesta
            count_tokens = response.json()
            return count_tokens["num_tokens"]
        else:
            print("La solicitud falló con el código de estado:", response.status_code)

    def request_information(self, query, token_budget):
        url = 'https://demo-ant-api-b26e14484ab9.herokuapp.com/retrieval_info/'
        # Datos que quieres enviar en la solicitud POST
        data = {
            "content": query,
            "token_budget": token_budget
        }

        # Enviar la solicitud POST
        response = requests.post(url, json=data)

        # Verificar el código de estado de la respuesta
        if response.status_code == 200:
            # La solicitud fue exitosa, mostrar la respuesta
            information = response.json()
            return information["content"]
        else:
            print("La solicitud falló con el código de estado:", response.status_code)

    def get_prompt_response_to_query(self, query, token_budget):
        instrucction = """Proporciona una respuesta concisa y significativa al siguiente mensaje del usuario, considerando el contexto del historial del diálogo en curso. Utiliza solo la información entre tres comillas invertidas para responder de manera informativa. Evita proporcionar datos no respaldados. Usa máximo 100 palabras."""
        
        mensaje_user = f"""Mensaje del usuario: {query}"""

        information = self.request_information(query, token_budget=token_budget)

        template_information = f"""\nInformación: ```{information}```\n"""

        prompt_response_to_query = instrucction + template_information + mensaje_user

        return prompt_response_to_query

    def generate_response(self, message, use_kb = True):
        if use_kb == True:
            messages = [{"content": m["content"] } for m in self.messages]
            num_tokens_context_dialog =  self.request_num_tokens(messages)
           
            print("\nnum_tokens_context_dialog:", num_tokens_context_dialog)
            max_tokens_response = 600

            prompt_response_to_query = self.get_prompt_response_to_query(
                message, token_budget= 4096 - num_tokens_context_dialog - max_tokens_response)
            
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
            
        print()
        
        self.messages.append({"role": "assistant", "content": response_ai_assistant})
        
        return response_ai_assistant



if __name__ == "__main__":

    questions_topics = load_json("./refined_questions_generated.json")
    questions_faq = load_json("./faq/filtered_questions.json")

    #for questions_about_topic in questions_topics[0:1]:
    #    questions = questions_about_topic["questions"]
        #information = questions_about_topic["context"]
        #opening_lines = [question["question"] for question in questions]
    
    for i, question in enumerate(questions_faq[3:5]):
        print(f"\n\nConversación {i + 1}.......................................................\n\n")

        ai_assistant = AIAssistant()
        
        start_greeting = numpy.random.choice([True, False],1, p = [0.3,0.7])[0]
        user_ai_sim = UserAISim(start_greeting = start_greeting)
        print("start_greeting:", start_greeting)
        
        if start_greeting:
            response_user_ai = user_ai_sim.start_conversation()
            print("\nUser:", response_user_ai)
            response_ai_assistant = ai_assistant.generate_response(message = response_user_ai, use_kb= False)
            print("\nAssistant:", response_ai_assistant)
        
        user_ai_sim.push_user_messages_to_history(question) 
        
        print("\nUser:", question)
        response_ai_assistant = ai_assistant.generate_response(message = question)
        print("\nAssistant:", response_ai_assistant)
        
        time.sleep(4)

        for i in range(2):
            finish_conversation = numpy.random.choice([True, False],1, p = [0.3,0.7])[0]
            
            print("\nfinish_conversation:",finish_conversation)
            
            if finish_conversation:
                response_user_ai = user_ai_sim.finish_conversation(message=response_ai_assistant)
                
                print("\nUser:", response_user_ai)

                response_ai_assistant = ai_assistant.generate_response(message = response_user_ai, use_kb= False)

                print("\nAssistant:", response_ai_assistant)
                break

            response_user_ai = user_ai_sim.generate_response(message=response_ai_assistant)

            print("\nUser:", response_user_ai)
            
            time.sleep(5)

            response_ai_assistant = ai_assistant.generate_response(message = response_user_ai)

            print("\nAssistant:", response_ai_assistant)
            
            time.sleep(5)

            

