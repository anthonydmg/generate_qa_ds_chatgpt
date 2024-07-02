
from utils import count_num_tokens, get_completion_from_messages, load_json, save_json, read_fragment_doc

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
from sentence_transformers import SentenceTransformer
import numpy as np
import warnings

warnings.simplefilter(action='ignore', category=FutureWarning)

    
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
    
    def format_text_history_chat(self, history_chat):
        text = ""
        for message in history_chat:
            text += f'\n{message["role"]}:{message["content"]}'    
        return text

    def refine_answer_contextual(self, query, history):
        # inverse rol
        history_inv = [{ "role": "user" if m["role"] == "assistant" else "assistant", "content": m["content"] } for m in  history]
        history_chat = self.format_text_history_chat(history_inv)

        prompt_identify_reform = f"""Dado el historial del chat proporcionado entre tres comillas invertidas y la última pregunta del usuario, reformula la pregunta para que sea más contextual y dependiente del historial del chat, manteniendo el sentido original de la consulta y la naturalidad del lenguaje del usuario. Presenta el ultimo mensaje del usuario con la pregunta reformulada de la siguiente manera: Reformulado: mensaje reformulado

Historial del chat: ```{history_chat}```

Último mensaje del usuario: ```{query}```"""

        print("\n\nprompt_identify_reform:", prompt_identify_reform)
        messages = [{
            "role": "user", 
            "content": prompt_identify_reform
        }]

        response = get_completion_from_messages(
            messages = messages,
            model=self.model)
        
        print("\n\nrefine_answer_contextual response:", response)        
        return response

    def finish_conversation(self, message):
        num_words = random.choice([2, 4, 5, 10, 12, 15, 20])
#(Max. {num_words} palabras)
        prompt_response_message = f"""Recuerda que eres un estudiante universitario en busca de información o asesoramiento hablando con un Asistente de AI. Responde con un máximo {num_words} palabras al siguiente mensaje del asistente de IA finalizando la conversación de manera realista y natural.
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
    # me parece que el usuario esta mejor ahora mejora el asistente
    # y realiza las consultas pertinentes para satisfacer tu interés por comprender completamente todo lo relacionado con el tema consultado
    def get_prompt_start(self, start_greeting = False):
        prompt_start = "Actúa como un estudiante universitario de la Facultad de Ciencias de la Universidad Nacional de Ingeniería (UNI) que esta buscando información o asesoría.\
Tu (el estudiante universitario) estas hablando con un asistente de AI especialidad en dichos temas.\
Utiliza un tono informal adecuado para un estudiante universitario.\
Evita usar declaraciones de agradecimiento.\
Responde a los mensajes de manera concisa y significativa teniendo en cuenta el contexto del historial del diálogo en curso y realiza las consultas pertinentes para satisfacer tu interés por comprender completamente todo lo relacionado con el tema consultado"
        
        type_greeting = random.choice(["formal","informal", "semiformal", "coloquial"])
        print("type_greeting:", type_greeting)
        num_words = random.choice([5, 8, 10])
        print("num_words:", num_words)

        reference_to_ai = random.choice(["asistente de AI (Aerito)","asistente de AI", "asistente", "asistente virtual"])

        if start_greeting:
            #prompt_start += f"\nInicia la conversación con un mensaje breve con un saludo {type_greeting} al asistente de IA llamado Aerito sin nada mas que el saludo y mantén tu rol de estudiante universitario en busca de información o asesoria en las interacciones posteriores"
            prompt_start += f"\nComienza la conversación simplemente con un saludo {type_greeting} al {reference_to_ai} usando como máximo {num_words} palabras y mantén tu rol de estudiante universitario en busca de información o asesoría en las siguientes interacciones."
            
            #, 

            #en la segunda interacción realizar la consulta sobre tu tema de interés, utilizando un máximo de {num_words} palabras, y mantén este rol en las interacciones posteriores."
        else:
            prompt_start += "\nComienza la conversación con una consulta sobre el tema de interés y mantén dicho rol en las siguientes interacciones."

        print("prompt_start:", prompt_start.split("\n")[-1])
        return prompt_start


    def generate_response(self, message):
        
        #prompt_response_message = f"""Recuerda que eres un estudiante universitario en busca de información o asesoramiento que esta conversando con un asistente de AI especializado en dichos temas, responde de manera concisa y significativa al siguiente mensaje del asistente en máximo 40 palabras.
#Mensaje del asistente de AI: {message}"""
        num_turn = len(self.messages) // 2 + (1 if not self.start_greeting else 0)
        print("\nNumero de turno:", num_turn)
        
        num_words = random.choice([20,25,30,35])
        
        print("num_words_user:", num_words)
        # y significativa 
        # Evita declaraciones de agradecimiento 
        # y significativa 
        #  Evita declaraciones de agradecimiento
        #realista y natural, incluyendo personalización, evitando repetir exactamente la información del asistente, usando un tono menos formal y añadiendo preguntas o comentarios adicionales si es relevante. Por ejemplo, un usuario real podría agradecer la información, pedir detalles específicos, y mostrar una reacción personal a la situación.
        # 
        # Recuerda que eres un estudiante universitario en busca de información o asesoramiento. 
        #  de manera concisa, realista y natural, personalizando tu respuesta y evitando repetir exactamente la información del asistente de IA. 
        # Ten en cuenta el contexto del historial del diálogo en curso al responder al siguiente mensaje del asistente de IA proveido en respuesta a tu mensaje anterior: {message}.
        # 

        #if num_turn > 2:    
        #    prompt_response_message = f"""Recuerda que eres un estudiante universitario en busca de información o asesoramiento hablando un Asistente de AI. Responde en menos de {num_words} palabras de manera concisa, realista y natural, personalizando tu respuesta y evitando repetir exactamente la información del asistente de IA. Ten en cuenta el contexto del historial del diálogo en curso al responder al siguiente mensaje del asistente de IA proveido en respuesta a tu mensaje anterior.
        #Mensaje del asistente de AI: {message}"""
        #else:
        #prompt_response_message = f"""Recuerda que eres un estudiante universitario en busca de información o asesoramiento hablando con un Asistente de AI. Responde de manera concisa, realista y natural, personalizando tu respuesta y evitando repetir exactamente la información proveída por el asistente de IA. Ten en cuenta el contexto del historial del diálogo en curso al responder al siguiente mensaje del asistente de IA proveído en respuesta a tu mensaje anterior.
        #Mensaje del asistente de AI: {message}"""
        
        level_conciseness = "" #numpy.random.choice(["", "bastante ", "sumamente ", "extremadamente "], 1 ,p = [0.60, 0.10, 0.15, 0.15])[0]
        limit_words = "" #numpy.random.choice(["",f" en menos de {num_words} palabras"], p = [0.50, 0.50])
        # Responde en menos de {num_words} palabras
        print("\nlevel_conciseness:", level_conciseness)
        print("\nlimit_words:", limit_words)
        prompt_response_message = f"""
Recuerda que eres un estudiante universitario en busca de información o asesoramiento hablando con un Asistente de AI. Responde al siguiente mensaje del asistente{limit_words} de manera {level_conciseness}concisa, realista y natural, evitando repetir exactamente la información proveída por el asistente de IA  y teniendo en cuenta el contexto del historial del diálogo en curso.
Mensaje del asistente de AI: {message}"""

        #if num_turn > 2:

        #    prompt_response_message = f"""Recuerda tu papel de estudiante universitario en busca de información o asesoramiento, y responde en menos de {num_words} palabras de manera concisa al siguiente mensaje del asistente de IA proveído en respuesta a tu ultimo mensaje, teniendo en cuenta el contexto del historial del diálogo en curso.
        #Mensaje del asistente de AI: {message}"""
        #else:
        #    prompt_response_message = f"""Recuerda tu papel de estudiante universitario en busca de información o asesoramiento, y responde de manera concisa al siguiente mensaje del asistente de IA proveído en respuesta a tu ultimo mensaje, teniendo en cuenta el contexto del historial del diálogo en curso.
        #Mensaje del asistente de AI: {message}"""
        
        print("\nprompt_user:", prompt_response_message.strip().split("\n")[0])

        #prompt_response_message = f"""Recuerda que tu (el estudiante universitario en busca de información o asesoramiento) estas hablando con un asistente de AI, responde de manera concisa y significativa al siguiente mensaje del asistente de IA (Max. 50 palabras), teniendo en cuenta el contexto del historial del diálogo en curso.
        #Mensaje del asistente de AI: {message}"""

        #Tu (el estudiante universitario) estas hablando con un asistente de AI especialidad
        num_tokens_context_dialog =  sum([count_num_tokens(m["content"]) for m in  self.messages])
        print("\nnum_tokens_context_dialog_user:", num_tokens_context_dialog)
        
        nnum_tokens_prompt_user = count_num_tokens(response_ai_assistant)
        print("\nnum_tokens_prompt_user:", nnum_tokens_prompt_user)

        print("\nnum_tokens_prompt_chat_user:",  nnum_tokens_prompt_user + num_tokens_context_dialog)
        
        
        response_user_ai = get_completion_from_messages(
            self.messages + [{
            "role": "user", 
            "content": prompt_response_message
            }],
            model=self.model)
        
        
        
        self.push_assistant_messages_to_history(message)

        #if num_turn >= 2:   
            #self.refine_answer_contextual(response_user_ai, history = self.messages[1:])
        
        #print("self.messages:",  self.messages)
        self.push_user_messages_to_history(response_user_ai)   
        
        return response_user_ai

class AIAssistant:
    def __init__(
            self, 
            model = "gpt-3.5-turbo-0613",
            path_df_kb = "./kb/topics.csv",
            embedding_model = "jinaai/jina-embeddings-v2-base-es") -> None:
        
        prompt_system_role_assistant = self.get_prompt_system_role()
        
        self.start_greeting = False

        self.df_kb = pd.read_csv(path_df_kb)
        self.df_kb["embedding"] = self.df_kb['embedding'].apply(ast.literal_eval)

        self.messages = [
            {'role':'system', 'content': prompt_system_role_assistant}
        ]
        
        self.contexts = [None]
        self.recovered_texts = [None]
        self.reformulated_question = [None]
        self.contains_questions = [None]

        self.embedding_model = embedding_model
        self.model = model
    #     3. Evita declaraciones excesivamente formales y responde de manera concisa y servicial a mensajes de agradecimientos finales del usuario.
    #     5. Evita declaraciones excesivamente formales y responde de manera concisa y servicial a mensajes agradecimientos del usuario.
    # , sin ser excesivamente formal y responde de manera concisa y servicial a mensajes de agradecimiento del usuario
    # Evitando declaraciones excesivamente formales y responde de manera sumamente concisa y servicial a los mensajes de agradecimiento.
    # bajo el contexto de la Facultad de ciencias de la UNI
    #  Responde de manera sumamente concisa y servicial a los mensajes de agradecimiento de los usuarios, sin ser excesivamente formal.
    # Mantén un tono empático y servicial en sus interacciones.
    # Mantén un tono amigable, empático, profesional y de apoyo en tus interacciones.
    # Mantén un tono amigable, empático, profesional y de apoyo en tus interacciones.
    # informativas
    ## COmo evito mencionar reglamentos
    # vinculada a la Faculta de Ciencias
    # Cambiar borrando preferiblemente
    # lo de la ruta que no la da y lo que dervia aveces demasiado a estadistica 
    # Preferiblemente,
    # útiles
    def get_prompt_system_role(self):
        prompt_system_role_assistant = f"""
Eres Aerito un asistente de AI especializado en temas de matricula, procedimientos y tramites académicos de la Facultad de Ciencias de la Universidad Nacional de Ingeniería de Peru.
Deberás responder a los mensajes asegurándote de cumplir con los siguientes criterios.
    1. Debes proporcionar respuestas precisas y concisas a las preguntas del usuario bajo el contexto de la Facultad de ciencias de la UNI y basándote exclusivamente en la información que te sera proporcionada, no proporciones datos no respaldados en dicha información.
    2. Mantén un tono empático y servicial en sus interacciones.
    3. Responde de manera sumamente concisa pero servicial a mensajes con agradecimientos finales del usuario.
    4. Evita derivar o sugerir el contacto con una oficina a menos que sea necesario. Si no hay otra oficina más idónea, la derivación se realizará hacia la Oficina de Estadística de la Facultad de Ciencias.
    5. En caso de no encontrar información sobre la consulta en los datos proporcionados, evita proporcionar datos no respaldados en dicha información y expresa con empatía que no tienes acceso a esa información, también de manera pertinente puedes sugerir el contacto con un oficina para obtener mayor información.
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

            information += "\n\n"+ text
        
        return information

    def get_prompt_response_to_query(
            self, 
            query, 
            info_texts, 
            token_budget,
            additional_info = None):
        #print("numero de info_texts:", len(info_texts))
        #instrucction = """# sin hacer mención a la información
#Proporciona una respuesta informativa, significativa y concisa al siguiente mensaje del usuario basándote exclusivamente en la información delimitada por tres comillas invertidas, evitando proporcionar información que no esté explícitamente sustentada en dicha informacion y teniendo en el contexto del historial del diálogo en curso."""
        #  en lugar menciona que no tienes acceso a dicha información según sea necesario
        num_turn = len(self.messages) // 2

        min_turn = 1 if not self.start_greeting else 2
        #                 "context": "\n\nSolicitud Certificado De Quinto Y/O Tercio Superior En Fc De La Uni\n\u00bfQu\u00e9 procedimiento debe seguir un estudiante de la Facultad de ciencias de la UNI para solicitar certificado de d\u00e9cimo o quinto superior?\nLas constancias de Quinto y/o Tercio Superior son emitidas por la oficina de Escuelas Profesionales de la Facultad correspondiente a la especialidad del estudiante. Por lo tanto, se recomienda a los estudiantes de la Facultad de Ciencias contactar con dicha oficina para obtener m\u00e1s detalles sobre el proceso y requisitos para este tr\u00e1mite, a trav\u00e9s de las siguientes direcciones de correo electr\u00f3nico, seg\u00fan su Escuela Profesional:\n\nPara F\u00edsica, Qu\u00edmica o Ciencia de la Computaci\u00f3n: escuelas_fc1@uni.edu.pe\nPara Matem\u00e1ticas o Ingenier\u00eda F\u00edsica: escuelas_fc2@uni.edu.pe\nEl horario de atenci\u00f3n de las oficinas de Escuelas Profesionales es de lunes a viernes de 8:30 a.m. a 4:00 p.m.\n\nProcedimiento Para Solicitar Constancia De Ayudantia Acad\u00e9mica\n\u00bfQu\u00e9 procedimiento debe seguir un estudiante de pregrado de la Facultad de Ciencias de la UNI para solicitar su constancia de Ayudantia acad\u00e9mica?\nEl tr\u00e1mite se realiza con el Director de Escuela correspondiente. El estudiante puede solicitar informaci\u00f3n a las siguientes direcciones de correo electr\u00f3nico seg\u00fan su escuela profesional.\nPara F\u00edsica, Qu\u00edmica o Ciencia de la Computaci\u00f3n: escuelas_fc1@uni.edu.pe\nPara Matem\u00e1ticas o Ingenier\u00eda F\u00edsica: escuelas_fc2@uni.edu.pe\nEl horario de atenci\u00f3n de las oficinas de Escuelas Profesionales es de lunes a viernes de 8:30 a.m a 4:00 p.m\n\nProcedimiento Para Realizar Ayudant\u00eda Acad\u00e9mica\n\u00bfCual es el procedimiento a seguir para que un estudiante de pregrado de la Facultad de Ciencias de la UNI pueda realizar ayudant\u00eda academica?\nLos estudiantes que deseen realizar ayudant\u00eda acad\u00e9mica deben ponerse en contacto con el departamento de su Escuela Profesional correspondiente para obtener m\u00e1s informaci\u00f3n. A continuaci\u00f3n se detallan las direcciones de correo electr\u00f3nico seg\u00fan la escuela profesional:\nF\u00edsica, Qu\u00edmica o Ciencia de la Computaci\u00f3n: escuelas_fc1@uni.edu.pe\nMatem\u00e1ticas o Ingenier\u00eda F\u00edsica: escuelas_fc2@uni.edu.pe\n\nProcedimiento Para Solicitar El Correo Institucional\n\u00bfQu\u00e9 procedimiento debe seguir un estudiante de la UNI para solicitar su correo institucional?\nPara solicitar su correo institucional de la UNI, enviar un correo obtenercorreo@uni.pe proporcionndo la siguiente informaci\u00f3n:\n    C\u00f3digo de Alumno.\n    Nombres y Apellidos.\n    DNI.\n    Especialidad.\n    Indicar si es estudiante de pregrado o posgrado.\n    Correo personal (que no sea @uni.pe ni @UNI.PE) donde se le enviar\u00e1 la clave.\n    N\u00famero de Celular.\n    Facultad.\n\nProcedimiento Para Solicitar De Constancia De Notas\n\u00bfQu\u00e9 procedimiento debe seguir un estudiante para solicitar una constancia de notas?\nPara solicitar una constancia de notas (constancia de estudios simple) en ingl\u00e9s o en espa\u00f1ol, el estudiante deber seguir los siguientes pasos:\n\n1. Enviar un correo a estadistica_fc@uni.edu.pe solicitando una orden de pago para la CONSTANCIA DE NOTAS. En el mensaje, deber\u00e1 incluir sus datos personales: n\u00famero de DNI, apellidos, nombres, correo institucional y/o alternativo.\n\n2. La oficina de estad\u00edstica (AERA) le enviar\u00e1 la orden de pago por el monto de S/. 100.00 (dato correspondiente al a\u00f1o 2024) a su correo electr\u00f3nico.\n\n3. El alumno deber\u00e1 realizar el pago en alguna sucursal del BCP o a trav\u00e9s aplicaci\u00f3n movil del banco. En la app selecciona \"Pagar servicios\", elige la Universidad Nacional de Ingenier\u00eda, luego la opci\u00f3n de pago para estudiantes, e ingresa su n\u00famero de DNI. La app mostrar\u00e1 la orden de pago con el monto exacto para realizar el pago.\n\n4. Luego, el estudiante deber\u00e1 dejar en mesa de partes de la facultad el comprobante de pago y la solicitud correspondiente, o enviarlos por correo electr\u00f3nico a mesadepartes_fc@uni.edu.pe. Es importante que se asegure de indicar en la solicitud si desea la CONSTANCIA DE NOTAS en ingl\u00e9s o espa\u00f1ol. El modelo para esta solicitud est\u00e1 disponible en la secci\u00f3n [\"MATR\u00cdCULA Y PROCEDIMIENTOS\" en la p\u00e1gina web de la Facultad de Ciencias](https://fc.uni.edu.pe/documentos/).\n\n5. Por \u00faltimo, AERA enviar\u00e1 un correo para notificarle que la constancia est\u00e1 lista para ser recogida en el horario de atenci\u00f3n de Lunes a Viernes, de 08:00 a 13:00 y de 14:00 a 15:30.\n\nRequisitos Y Procedimiento Para Matricula De Un Ingresante\n\u00bfCuales son los requisitos y el proceso de ma tr\u00edcula para nuevos ingresantes de pregrado en la Facultad de Ciencias de la Universidad Nacional de Ingenier\u00eda?\nLos nuevos alumnos de pregrado ingresantes a la Facultad de Ciencias, realizaran el siguiente proceso para completar su matricula (primera matricula al primer ciclo):\n    1. Recabar su constancia de ingreso. Luego de gestionar la emisi\u00f3n de su constancia de ingreso, la Direcci\u00f3n de Admisi\u00f3n (DIAD) de la UNI enviar\u00e1 a su correo la constancia de ingreso.\n    2. Actualizaci\u00f3n de datos en intranet. DIRCE har\u00e1 llegar a su correo su clave para acceder a la plataforma de intranet-alumnos y completar sus datos.\n    3. Registrar los datos en la Facultad de Ciencias. La oficina de estad\u00edstica de la facultad enviar\u00e1 al correo del ingresante la ficha de datos. El llenado es car\u00e1cter obligatorio.\n    4. Efectuar el pago por autoseguro en el plazo establecido en el cronograma. Para ello, primero generar una orden de pago atravez de la plataforma intranet-alumnos.\n    5. Realizar la entrega de los siguientes documentos a la oficina de estad\u00edstica seg\u00fan el cronograma de actividades de matr\u00edcula para ingresantes publicado en la secci\u00f3n 'MATR\u00cdCULA Y PROCEDIMIENTOS' en la p\u00e1gina web de la Facultad de Ciencias.\n        - Constancia de Ingreso\n        - Ficha de datos\n        - Constancia de Evaluaci\u00f3n Socioecon\u00f3mica\n        - Certificado M\u00e9dico expedido por el Centro Medico UNI\n        - Comprobante de pago de Autoseguro Estudiantil\n    6. La oficina de estad\u00edstica ejecutar\u00e1 la matr\u00edcula (inscripci\u00f3n de cursos) de los ingresantes seg\u00fan el cronograma de actividades, \u00fanicamente para aquellos que hayan cumplido con la entrega de la entrega de los documentos requeridos en de las fechas establecidas en el cronograma.\n    7. Los ingresantes matriculados recibir\u00e1n un correo con el horario de sus cursos y tambi\u00e9n podr\u00e1n visualizar sus cursos y horarios en la plataforma intranet-alumnos.",

        print("num_turn asistant:", num_turn)
        # Se conciso, claro y l
        #  y significativa
        #if num_turn >= min_turn:
        #    instrucction = """Como asistente de AI proporciona una respuesta clara y concisa al siguiente mensaje del usuario, considerando el contexto del historial del diálogo en curso. Usa únicamente la información entre tres comillas invertidas para responder a las preguntas del usuario. No proporciones información que no esté claramente respaldada o desarrollada en esa información; en su lugar, indica claramente que no tienes acceso a esa información cuando sea relevante. Limita la respuesta a un máximo de 130 palabras."""
        #else:
        #    instrucction = """Como asistente de AI proporciona una respuesta clara y concisa al siguiente mensaje del usuario. Usa únicamente la información entre tres comillas invertidas para responder a las preguntas del usuario. No proporciones información que no esté claramente respaldada o desarrollada en esa información; en su lugar, indica claramente que no tienes acceso a esa información cuando sea relevante. Limita la respuesta a un máximo de 130 palabras."""
        # se borro bastante
        #
        if num_turn >= min_turn:
            instrucction = """Como asistente de AI proporciona una respuesta precisa, clara y concisa al siguiente mensaje del usuario, considerando el contexto del historial del diálogo en curso. Usa la información entre tres comillas invertidas como tu unica fuente de conocimiento para responder a las preguntas del usuario. No proporciones información que no esté claramente respaldada o desarrollada en esa información; en su lugar, indica claramente que no tienes acceso a esa información cuando sea relevante. Limita la respuesta a un máximo de 130 palabras."""
        else:
            instrucction = """Como asistente de AI proporciona una respuesta precisa, clara y concisa al siguiente mensaje del usuario. Usa la información entre tres comillas invertidas como tu unica fuente de conocimiento para responder a las preguntas del usuario. No proporciones información que no esté claramente respaldada o desarrollada en esa información; en su lugar, indica claramente que no tienes acceso a esa información cuando sea relevante. Limita la respuesta a un máximo de 130 palabras."""


            #instrucction = """Como asistente de AI proporciona una respuesta clara y concisa al siguiente mensaje del usuario. Utiliza la información entre tres comillas invertidas como tu única fuente de conocimiento para responder a consultas del usuario. Evita ofrecer datos no respaldados explícitamente o no bien desarrollados en dicha información; en su lugar, indica claramente que no tienes acceso a esa información cuando sea relevante. Limita la respuesta a un máximo de 130 palabras."""

        #print("\ninstrucction:", instrucctfion)

        # descrita a continuación 
        #instrucction = """Proporciona una respuesta concisa y significativa al siguiente mensaje del usuario, considerando el contexto del historial del diálogo en curso. Utiliza solo la información entre tres comillas invertidas para responder de manera informativa a consultas del usuario. Evita proporcionar datos no respaldados explícitamente en dicha información. Usa máximo 100 palabras."""
        
        #instrucction = """Proporciona una respuesta concisa, informativa y significativa al siguiente mensaje del usuario utilizando únicamente la información contenida entre tres comillas invertidas. Evita ofrecer datos no respaldados por dicha información y ten en cuenta el contexto del historial del diálogo en curso. Usa máximo 100 palabras"""
        #instrucction = """Proporciona una respuesta informativa, significativa y concisa al siguiente mensaje del usuario basándote exclusivamente en la información delimitada por tres comillas invertidas, evitando proporcionar información que no esté explícitamente sustentada en dicha información y teniendo en cuenta el contexto del historial del diálogo en curso."""
        mensaje_user = f"""Mensaje del usuario: {query}"""
        
        token_budget = token_budget - count_num_tokens(instrucction + mensaje_user, model=self.model)
        
        print("\ntoken_budget asistant:", token_budget)
        information = self.join_info_texts(info_texts, token_budget)
        
        if additional_info is not None:
            information = information + "\n" + additional_info

        self.contexts.append(information)
        
        template_information = f"""\nInformación: ```{information}```\n"""

        prompt_response_to_query = instrucction + template_information + mensaje_user

        return prompt_response_to_query
    ## prev context
    def create_embedding_from_hf(self, query, model_name):
        model = SentenceTransformer(model_name, trust_remote_code=True)
        embeddings = model.encode(query)
        #print("embeddings shape:", embeddings.shape)
        return embeddings
    
            #print(type(embeddings))
        #embeddings = embeddings.numpy()
        #print(type(embeddings))
        #print("embeddings shape:", embeddings.shape)
        #embeddings_list = [np.array2string(embeddings[i], separator=",") for i in range(embeddings.shape[0])]
    
    def create_embedding_from_openai(self, query, model_name):
        query_embedding_response = openai.embeddings.create(
            model = model_name,
            input=query,
        )

        query_embedding = query_embedding_response.data[0].embedding
        return query_embedding
    
    def strings_ranked_by_relatedness(
        self,
        query,
        df,
        context = None,
        relatedness_fn=lambda x, y: 1 - spatial.distance.cosine(x, y),
        top_n = 5,
        weighted_source = {
            "faq": 1, "topic-specific-document": 0.80, "regulation": 0.75, "general_information": 1.10},
        weigthed_embeddings = {"query": 0.68, "context": 0.32} 
    ):
        """Returns a list of strings and relatednesses, sorted from most related to least."""
        query_embedding = self.create_embedding_from_hf(query, self.embedding_model)
        
        if context is not None:
            context_embedding = self.create_embedding_from_hf(context, self.embedding_model)

            strings_and_relatednesses = [
                (row["text"], (weigthed_embeddings["query"]* relatedness_fn(query_embedding, row["embedding"]) + 
                               weigthed_embeddings["context"] * relatedness_fn(context_embedding, row["embedding"])
                               ) * weighted_source[row["type_source"]])
                for i, row in df.iterrows()
            ]
        
        else:
            strings_and_relatednesses = [
                (row["text"], relatedness_fn(query_embedding, row["embedding"]) * weighted_source[row["type_source"]])
                for i, row in df.iterrows()
            ]
        
        strings_and_relatednesses.sort(key=lambda x: x[1], reverse=True)
        strings, relatednesses = zip(*strings_and_relatednesses)
        return strings[:top_n], relatednesses[:top_n]

    ## no lo esta haciendo bien
    # Conversación 1....................................................... probar con el segundo mensaje
    # User: ¿Un estudiante puede matricularse en un curso y su pre requisito?
    # Assistant: Los estudiantes en posibilidad de egresar pueden matricularse en un curso y su prerequisito en el mismo ciclo. Deben comunicarse con su escuela profesional para solicitar la evaluación y aprobación por el director de la escuela correspondiente. Este beneficio aplica a aquellos alumnos que les falten como máximo treinta créditos para completar su Plan de Estudios y graduarse de la Universidad. Es importante cumplir con esta condición para poder matricularse en un curso y su prerequisito en el mismo ciclo académico.
    # User: ¡Genial! Gracias por la información. ¿Puedes decirme cuáles son los pasos específicos que debo seguir para solicitar la evaluación y aprobación por el director de la escuela correspondiente?
    def extract_contains_questions(self, response):
        match = re.search(r"Contiene Preguntas:\s*(.*)", response)
        if match:
            resultado = match.group(1).strip()
        else:
            resultado = None
        return resultado

    def extract_need_context(self, response):
        match = re.search(r"La última pregunta del usuario se entiende sin necesidad del historial del chat:\s*(.*)", response)
        if match:
            resultado = match.group(1).strip()
        else:
            resultado = None
        return resultado

    def eval_contains_questions(self, query):
        prompt_question_identification = f"""Dado el siguiente mensaje un usuario proveído a un asistente de AI, determina si contiene preguntas (ya sean implícitas o explícitas). Mencionado de la siguiente manera: Contiene Preguntas: Sí o Contiene Preguntas: No
mensaje del usuario: ```{query}```
    """
    
        messages = [{"role": "user", "content": prompt_question_identification}]
    
        response  = get_completion_from_messages(
        messages=messages,
        model="gpt-3.5-turbo-0125")
        
        return self.extract_contains_questions(response) != "No"


    def get_reformulated_contextal_query(self, query, history_chat_messages):
        
        print("\noriginal_user_query: ", query)

        #history_chat_messages = history_chat_messages + [{"role": "user", "content": query}]
        
        history_chat = self.format_text_history_chat(history_chat_messages)
        #print("\nhistory_chat:", history_chat)
        
        prompt_identify_reform = f"""Dado el historial del chat proporcionado entre tres comillas invertidas y la ultima pregunta del usuario, indica si la pregunta puede entenderse en su totalidad sin necesidad del historial del chat. Mencionado de la siguiente manera: La última pregunta del usurio se entiende sin necesidad del historial del chat: Sí o La última pregunta del usurio se entiende sin necesidad del historial del chat: No

        Historial del chat: ```{history_chat}```

        Último mensaje del usuario: ```{query}```
        """
        messages = [{"role": "user", "content": prompt_identify_reform}]
        
        response = get_completion_from_messages(
                            messages,
                            model= self.model)

        print("\nresponde need context:", response)

        not_need_context = self.extract_need_context(response)

        if not_need_context == "Sí":
            
            return query

        print("\nNot Need context:", not_need_context)
        
        prompt_3 = f"""Dado el historial del chat proporcionado entre tres comillas invertidas y la ultima pregunta del usuario, reformula la pregunta de manera que incluya todo el contexto necesario para que pueda entenderse en su totalidad sin necesidad del historial del chat. No respondas el mensaje, solo reformúlalo y proporciona la pregunta reformulada de la siguiente manera: Reformulación: Pregunta reformulada.

        Historial del chat: {history_chat}

        Último mensaje del usuario: {query}
        """

        prompt = f"""Dado el historial del chat proporcionado entre tres comillas invertidas y las preguntas del usuario en su último mensaje, reformula las preguntas de manera que incluyan todo el contexto necesario para que se entiendan completamente sin necesidad de revisar el historial del chat. No respondas las preguntas, solo reformúlalas.
Proporciona el mensaje con las preguntas reformuladas de la siguiente manera:
Reformulación: 'Aquí el mensaje con las preguntas reformuladas'

Historial del chat: {history_chat}

Último mensaje del usuario: {query}"""

        #print("\nprompt reformulated_contextal_query:", prompt)
        
        messages = [{"role": "user", "content": prompt_3}]

        reformulated_query = get_completion_from_messages(
                            messages,
                            model= self.model)
        
        reformulated_query = reformulated_query.replace("Reformulación:","").strip()
        print("reformulated_query: ", reformulated_query)

        return reformulated_query


    def refine_answer_mention_articule(self, respuesta):
        prompt = f"""Corrige esta respuesta proporcionada por un asistente de AI para no mencionar numerales de articulos de reglamentos, manteniendo el sentido original de la respuesta.
        Respuesta: {respuesta}"""
        messages = [{"role": "user", "content": prompt}]

        new_answer = get_completion_from_messages(
                            messages,
                            model= self.model)
        return new_answer

    def get_rifined_answer(self, respuesta):
        if "artículo" in respuesta.lower():
            new_answer = self.refine_answer_mention_articule(respuesta)
        else:
            prompt = f"""Corrige esta respuesta proporcionada por un asistente de AI para no mencionar "información proporcionada", manteniendo el sentido original de la respuesta. Es preferible que no menciones dicha frase. En caso se refiera a falta informacion corrige el mensaje para que en su lugar se menciones de manera empatica que no se tienes accesso a dicha informacion.
        Respuesta: {respuesta}"""

            messages = [{"role": "user", "content": prompt}]

            new_answer = get_completion_from_messages(
                                messages,
                                model= self.model)
        
        return new_answer
        
    def contains_bad_keywords(self, message):
        keywords = ["información proporcionada", "artículo"]
        return any(keyword in message.lower() for keyword in keywords)
    
    def format_text_history_chat(self, history_chat):
        text = ""
        for message in history_chat:
            text += f'\n{message["role"]}:{message["content"]}'    
        return text
    
    def generate_response(self, message, use_kb = True):
        if use_kb == True:
            #query = self.messages[-1]["content"] + "\n" + message if len(self.messages) > 1 else message
            query = message
            
            contains_questions = self.eval_contains_questions(query)
            print("\n user message contains_questions:", contains_questions)

            if len(self.messages) > 1 and contains_questions:
                reformulated_query = self.get_reformulated_contextal_query(query = query, history_chat_messages = self.messages[1:])
                #context = self.messages[-2]["content"] + "\n" + self.messages[-1]["content"]
                context = None
                query = reformulated_query 
            else:
                context = None
                
            #print("query:", query)
            
            info_texs, relatednesses = self.strings_ranked_by_relatedness(
                query = query, 
                context = context,
                df = self.df_kb, 
                top_n = 10
                )
            
            self.recovered_texts.append([{"text": text, "relatedness": relatedness } for text , relatedness in zip(info_texs, relatednesses)])
            
            print("\nrelatednesses:", relatednesses)

            ## Filter low relatednesess
            cut_idx = len(relatednesses)
            for i in range(len(relatednesses)):
                if relatednesses[i] < 0.40:
                    cut_idx = i
                    print(f"\nSimilarity lower than threshold {relatednesses[i]}, idx {cut_idx}")
                    break

            info_texs = info_texs[:cut_idx]
            relatednesses = relatednesses[:cut_idx]

            #for  in zip(info_texs, relatednesses):
            
            num_tokens_context_dialog =  sum([count_num_tokens(m["content"]) for m in  self.messages])
            print("\nnum_tokens_context_dialog:", num_tokens_context_dialog)
            max_tokens_response = 950

            general_contact_information = read_fragment_doc("./documentos/informacion_general_contacto.txt")
            #general_information_fc = read_fragment_doc("./documentos/otros/informacion_general_fc.txt")
            #general_information = general_information_aera + "\n" + general_information_fc
            num_tokens_general_context = count_num_tokens(general_contact_information)

            token_budget = min(1850, 4096 - num_tokens_context_dialog - max_tokens_response - num_tokens_general_context)

            #print("\nnum_tokens_general_context:", num_tokens_general_context)

            prompt_response_to_query = self.get_prompt_response_to_query(
                message, 
                info_texs, 
                token_budget = token_budget,
                additional_info = general_contact_information #general_information
                )
            

            num_tokens_prompt_asistant = count_num_tokens(prompt_response_to_query)
            print("\nnum_tokens_prompt_asistant:", num_tokens_prompt_asistant)

            print("\nnum_tokens_prompt_plus_history_chat_assitant:",  num_tokens_prompt_asistant + num_tokens_context_dialog)


            response_ai_assistant = get_completion_from_messages(
            messages= self.messages + [{"role": "user", "content": prompt_response_to_query}],
            model = self.model
            )

            response_ai_assistant = response_ai_assistant.replace("```","").strip()

            if self.contains_bad_keywords(response_ai_assistant):
                print("Refinando la respuesta")
                print()
                print("Original response AI:", response_ai_assistant)
                response_ai_assistant = self.get_rifined_answer(response_ai_assistant)
                print("Refined response AI:", response_ai_assistant)
                

            self.messages.append({"role": "user", "content": message})
            self.reformulated_question.append(query)
            self.contains_questions.append(contains_questions)
        else:
            if len(self.messages) // 2 < 1:
                self.start_greeting  = True

            self.messages.append({"role": "user", "content": message})
            response_ai_assistant = get_completion_from_messages(
            messages= self.messages,
            model = self.model)
            self.contexts.append(None)
            self.recovered_texts.append(None)
            self.reformulated_question.append(message)
            self.contains_questions.append(False)
            
            
        print()
        
        self.messages.append({"role": "assistant", "content": response_ai_assistant})
        self.contexts.append(None)
        self.recovered_texts.append(None)
        self.reformulated_question.append(None)
        self.contains_questions.append(None)
        
        return response_ai_assistant
    
    def get_history_dialog(self, include_context = True):
        if include_context:
            history_dialog = []
            dialog_data = zip(self.messages[1:], self.contexts[1:], self.recovered_texts[1:], self.contains_questions [1:], self.reformulated_question[1:])
            for message, context, texts, contains_questions, reformulated_question  in dialog_data:
                history_dialog.append({
                    "role": message["role"],
                    "content": message["content"],
                    "context": context,
                    "recovered_texts": texts,
                    "contains_questions": contains_questions,
                    "reformulated_question": reformulated_question
                })
                
            return history_dialog
        else:
            return self.messages[1:]


if __name__ == "__main__":
    random.seed(42)
    #questions_topics = load_json("./refined_questions_generated.json")
    
    #questions_faq = load_json("./faq/filtered_questions.json")
    conversations_simulated = []

    path_file = "./faq-reformulated/data/faq_4_reformulated.json"
    filename = "faq_4_reformulated.json"
    questions_faq = load_json(path_file)

    #for questions_about_topic in questions_topics[0:1]:
    #    questions = questions_about_topic["questions"]
        #information = questions_about_topic["context"]
        #opening_lines = [question["question"] for question in questions]
    
    start = 0   
    end = 5 
    for i, question in enumerate(questions_faq[start:end]):
        print(f"\n\nConversación {i + 1}.......................................................\n\n")

        #conversation = [{}]+a
        ai_assistant = AIAssistant(model="gpt-3.5-turbo-0125")
        
        start_greeting = numpy.random.choice([True, False],1, p = [0.25,0.75])[0]
        user_ai_sim = UserAISim(model="gpt-3.5-turbo-0125", start_greeting = start_greeting)
        print("start_greeting:", start_greeting)
        
        if start_greeting:
            response_user_ai = user_ai_sim.start_conversation()
            print("\nUser:", response_user_ai)
            response_ai_assistant = ai_assistant.generate_response(message = response_user_ai, use_kb= False)
            print("\nAssistant:", response_ai_assistant)
            user_ai_sim.push_assistant_messages_to_history(response_ai_assistant)
        
        time.sleep(5)
        #continue
        user_ai_sim.push_user_messages_to_history(question) 
        
        print("\nUser:", question)
        response_ai_assistant = ai_assistant.generate_response(message = question)
        print("\nAssistant:", response_ai_assistant)
        
        time.sleep(15)
        num_turns = random.choice([2,3])
        
        for i in range(num_turns):
            additional_prob_finish = (i) * 0.05 
            finish_conversation = numpy.random.choice([True, False],1, p = [0.3 + additional_prob_finish,0.7 - additional_prob_finish])[0]
           
            if i >= 1 and finish_conversation:
                print("\nfinish_conversation:",finish_conversation)
                response_user_ai = user_ai_sim.finish_conversation(message=response_ai_assistant)
                
                print("\nUser:", response_user_ai)

                response_ai_assistant = ai_assistant.generate_response(
                    message = response_user_ai, 
                    #use_kb= False
                    )

                print("\nAssistant:", response_ai_assistant)

                break

            response_user_ai = user_ai_sim.generate_response(message=response_ai_assistant)

            print("\nUser:", response_user_ai)
            
            time.sleep(15)

            response_ai_assistant = ai_assistant.generate_response(message = response_user_ai)

            print("\nAssistant:", response_ai_assistant)
            
            time.sleep(15)

        ## save conversation

        messages = ai_assistant.get_history_dialog(include_context=True)
        conversations_simulated.append({
            "openline": question,
            "messages": messages
        })
            
    save_json("./conversational_faq/data", f"conv_sim_{filename[:-5]}_{start}_to_{end-1}", conversations_simulated)

    #save_json("./conversational_data", f"conversations_simulated_{start}_to_{end-1}", conversations_simulated)

