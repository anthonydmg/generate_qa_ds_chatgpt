
from utils import get_completion_from_messages, load_json, save_json
import openai
from dotenv import load_dotenv
import os
import re
import time 

load_dotenv(override=True)

def set_openai_key():
    API_KEY = os.getenv("API_KEY")
    openai.api_key = API_KEY

set_openai_key()

def format_text_history_chat(history_chat):
        text = ""
        for message in history_chat:
            text += f'\n{message["role"]}: {message["content"]}'    
        return text

def extract_need_context(response):
        match = re.search(r"La pregunta del usuario en el último mensaje se entiende sin necesidad del historial del chat:\s*(.*)", response)
        if match:
            resultado = match.group(1).strip().strip(".")
        else:
            resultado = None
        return resultado

def extract_need_reformulate(response):
        match = re.search(r"Es estrictamente necesario reformular la consulta:\s*(.*)", response)
        if match:
            resultado = match.group(1).strip().strip(".")
        else:
            resultado = None
        return resultado
# 4. Uso de términos conocidos: Si la pregunta incluye términos como *autoseguro*, *retiro total* u otros términos académicos comunes en la Facultad de Ciencias, asume que son terminos especificos del contexto de la facultad de ciencias y no requiren mayor contexto y asistente comprende estos términos sin necesidad de explicaciones adicionales.

def get_prompt_reformulated_contextual_query_prev(query, history_chat_messages):
        history_chat = format_text_history_chat(history_chat_messages)
        prompt_identify_reform = f"""Dado el último mensaje del usuario en el contexto de la Facultad de Ciencias de la Universidad Nacional de Ingeniería de Perú, enviado a un asistente familiarizado con las normativas académicas de la universidad, analiza si la consulta realizada en su ultimo mensaje puede ser comprendida de forma completa sin necesidad de consultar el historial previo de la conversación. 

Si la consulta no es entendible por sí sola, reformúlala para que incluya el contexto necesario, de manera que sea comprensible en su totalidad sin necesidad del historial del chat. Si el último mensaje del usuario **no contiene una consulta**, no es necesario realizar ninguna reformulación. No respondas la pregunta, solo reformúlala si es necesario.

Evalúa la pregunta basándote en los siguientes criterios:

1. Contexto suficiente: El ultimo mensaje con la pregunta debe contener suficiente información para entender su propósito y referencia.
2. Claridad: La pregunta debe ser explícita sobre el tema que aborda o a quién hace referencia.
3. Especificidad: La pregunta debe ser lo suficientemente detallada para permitir una respuesta precisa.

Sigue este formato para tu respuesta:
- Análisis: [Describe si la pregunta satisface los criterios y justifica tu decisión].
- El último mensaje contiene una pregunta: Sí/No
- La pregunta del usuario en el último mensaje se entiende sin necesidad del historial del chat: Sí/No/No aplica
- Reformulación: <<Pregunta reformulada/No aplica>> [Proporciona la versión reformulada solo si es necesario]

Último mensaje del usuario: {query}

Historial previo de la conversación: <<{history_chat}>>"""
        return prompt_identify_reform

def get_prompt_reformulated_contextual_query(query, history_chat_messages):
        history_chat = format_text_history_chat(history_chat_messages)
        prompt_identify_reform = f"""Dado el último mensaje del usuario en el contexto de la Facultad de Ciencias de la Universidad Nacional de Ingeniería de Perú, enviado a un asistente familiarizado con las normativas académicas de la universidad, analiza si la consulta realizada en su último mensaje contiene suficiente información para ser comprendida de forma completa por sí sola, sin necesidad de consultar el historial previo de la conversación.

Si el ultimo mensaje por si solo es claro y tiene el contexto suficiente para su comprensión, indica que se entiende completamente por sí solo. Si no es así, reformúlalo para incluir la información necesaria para que sea autosuficiente. Si el último mensaje del usuario no contiene una consulta, no es necesario realizar ninguna reformulación.

Evalúa la consulta basada en los siguientes criterios:

1. Pertinencia: El mensaje contiene términos o referencias suficientes para que un asistente especializado en normativas académicas identifique el tema o situación descrita.
2. Claridad: La pregunta está formulada de manera que su propósito y objetivo sean comprensibles sin ambigüedades, aunque pueda haber información implícita.
3. Contexto suficiente: Aunque no se detalla en exceso, el mensaje por si solo incluye elementos que permiten al asistente especializado en normativas académicas inferir su relación con un problema o trámite académico específico sin depender del historial previo. 

Sigue este formato para tu respuesta:
- Análisis: [Describe si la pregunta satisface los criterios y justifica tu decisión].
- El último mensaje contiene una pregunta: Sí/No
- La pregunta del usuario en el último mensaje se entiende sin necesidad del historial del chat: Sí/No/No aplica
- Reformulación: <<Pregunta reformulada/No aplica>> [Proporciona la versión reformulada solo si es necesario]

Último mensaje del usuario: {query}

Historial previo de la conversación: <<{history_chat}>>"""
        return prompt_identify_reform
        
# y puede inferir que las preguntas se refieren a este contexto específico
# En particular, evalúa si las referencias contextuales o términos utilizados en la consulta son lo suficientemente claros y específicos para que no generen ambigüedades o confusión sin tener acceso al historial de la converscion previo.

def get_prompt_reformulated_contextual_query_2(query, history_chat_messages):
        history_chat = format_text_history_chat(history_chat_messages)
        prompt_identify_reform = f"""Dado el último mensaje del usuario, dirigido a un asistente especializado en normativas académicas de la Facultad de Ciencias de la Universidad Nacional de Ingeniería (UNI), analiza si la consulta realizada en su último mensaje contiene suficiente información para ser comprendida de forma completa sin necesidad de consultar el historial previo de la conversación, sin necesidad de consultar el historial previo de la conversación.

Asume que el asistente está familiarizado con los trámites y normativas de esta facultad pero no tiene acceso al historial previo de la conversación. Evalúa la consulta basada en los siguientes criterios:

1. Pertinencia: El mensaje contiene términos o referencias suficientes para que un asistente especializado identifique el tema o situación descrita.
2. Claridad: La pregunta está formulada de manera que su propósito y objetivo sean comprensibles sin ambigüedades, aunque pueda haber información implícita.
3. Contexto suficiente: Aunque no se detalla en exceso, el mensaje incluye elementos que permiten al asistente inferir su relación con un problema o trámite académico específico sin tener acceso al historial previo de la conversacion. Si el mensaje no menciona explícitamente información esencial (como a qué constancias, documentos o trámites se refiere), se debe señalar que falta contexto para que sea comprensible de forma independiente.

Sigue este formato para tu respuesta:

Análisis: [Describe si la pregunta satisface los criterios y justifica tu decisión]. 
El último mensaje contiene una pregunta: Sí/No
La pregunta del usuario en el último mensaje se entiende sin necesidad del historial del chat: Sí/No/No aplica
Reformulación: <<Pregunta reformulada/No aplica>> [Proporciona la versión reformulada solo si es necesario]

Último mensaje del usuario: {query}

Historial previo de la conversación: <<{history_chat}>>"""
        return prompt_identify_reform


def get_prompt_reformulated_contextual_query_3(query, history_chat_messages):
        history_chat = format_text_history_chat(history_chat_messages)
        prompt_identify_reform = f"""Dado el último mensaje del usuario, dirigido a un asistente especializado en normativas académicas de la Facultad de Ciencias de la Universidad Nacional de Ingeniería (UNI), analiza si la consulta realizada en su último mensaje contiene suficiente información para ser comprendida de forma completa sin necesidad de consultar el historial previo de la conversación. Asume que el asistente está familiarizado con los trámites y normativas de esta facultad y que el historial previo de la conversación no está disponible como contexto adicional.

Evalúa la consulta utilizando los siguientes criterios:

1. Pertinencia: ¿El mensaje contiene términos o referencias suficientes para que un asistente especializado identifique el tema o situación descrita, basándose en su conocimiento de los trámites académicos de la UNI?
2. Claridad: ¿La pregunta está formulada de manera clara, sin ambigüedades, y permite al asistente identificar el propósito de la consulta, incluso si falta algún detalle adicional?
3. Contexto suficiente: Aunque el mensaje no debe detallar excesivamente la consulta, ¿incluye elementos clave que permitan al asistente inferir que se trata de un trámite académico específico (como retiro parcial, retiro total o reincorporación), sin necesidad de consultar el historial previo?

Responde utilizando este formato:

Análisis: [Describe si la pregunta satisface los criterios y justifica tu decisión. Enfócate en cómo el contexto del historial y el conocimiento del asistente sobre trámites académicos contribuyen a la comprensión de la consulta]. 
El último mensaje contiene una pregunta: Sí/No 
La pregunta del usuario en el último mensaje se entiende sin necesidad del historial del chat: Sí/No 
Reformulación: <<Pregunta reformulada/No aplica>> [Proporciona la versión reformulada solo si es necesario]

Último mensaje del usuario: {query}

Historial previo de la conversación: <<{history_chat}>>"""
        return prompt_identify_reform

def get_prompt_reformulated_contextual_query_4(query, history_chat_messages):
        history_chat = format_text_history_chat(history_chat_messages)
        prompt_identify_reform = f"""Dado el último mensaje del usuario, dirigido a un asistente especializado en normativas académicas de la Facultad de Ciencias de la Universidad Nacional de Ingeniería (UNI), analiza si la consulta contiene suficiente información para ser comprendida de manera completa sin necesidad de consultar el historial previo de la conversación. Solo reformula la consulta si es necesario para proporcionar contexto suficiente, de modo que la consulta se entienda por sí sola y el asistente pueda identificar su relación con un problema o trámite académico específico, sin acceder al historial previo. Si el contexto del historial previo no es necesario para comprender la consulta, no la reformules.

Responde utilizando el siguiente formato:

Análisis: [Describe si la pregunta cumple con los criterios establecidos y justifica tu decisión. Enfócate en cómo el contexto del historial y el conocimiento del asistente sobre trámites académicos contribuyen a la comprensión de la consulta].

El último mensaje contiene una pregunta: Sí/No 

La pregunta del usuario en el último mensaje se entiende sin necesidad del historial del chat: Sí/No 

Reformulación: <<Pregunta reformulada/No aplica>> [Proporciona la versión reformulada solo si es necesario].

Último mensaje del usuario: {query}

Historial previo de la conversación: <<{history_chat}>>"""
        return prompt_identify_reform


def get_prompt_reformulated_contextual_query_5(query, history_chat_messages):
        history_chat = format_text_history_chat(history_chat_messages)
        prompt_identify_reform = f"""Dado el último mensaje del usuario, dirigido a un asistente especializado en normativas académicas de la Facultad de Ciencias de la Universidad Nacional de Ingeniería (UNI), analiza si la consulta contiene suficiente información para ser comprendida de manera completa sin necesidad de tener conocimiento del historial previo de la conversación. Solo reformula la consulta si es necesario para proporcionar contexto suficiente, de modo que la consulta se entienda por sí sola y el asistente pueda identificar su relación con un problema o trámite académico específico. Si el contexto del historial previo no es necesario para comprender la consulta, no la reformules.

Asume un contexto implícito que la preguntas estan relacionados con la Facultad de Ciencias de la UNI por lo que es necesario detallarlo en execso.

Evalúa la consulta utilizando los siguientes criterios:

1. Contexto suficiente: Aunque no se detalla en exceso, el último mensaje por sí solo debe contener suficientes detalles como nombres de documentos, trámites o solicitudes que hayan sido mencionados previamente para que el asistente comprenda claramente a qué se refiere el usuario sin tener conocimiento del historial previo de la conversacion.  Concéntrate únicamente en la información mencionada previamente en la conversación que sea relevante para mejorar la precision de la última pregunta del usuario y que no haya sido mencionada en el último mensaje del usuario. 

2. Claridad y especificidad del contexto: La consulta debe incluir suficientes detalles sobre el tema o trámite específico al que hace referencia, como nombres de documentos o tipos de trámites, para que sea completamente comprensible sin tener concomiento del historial previo de conversacion.

Responde utilizando el siguiente formato:

Análisis: [Describe y analiza de manera detallada si la pregunta cumple con los criterios establecidos y justifica tu decisión].

El último mensaje contiene una pregunta: Sí/No

La pregunta del usuario en el último mensaje se entiende sin necesidad del historial del chat: Sí/No

Reformulación: <<Pregunta reformulada/No aplica>> [Proporciona la versión reformulada solo si es necesario].

Último mensaje del usuario: {query}

Historial previo de la conversación: <<{history_chat}>>"""
        return prompt_identify_reform


def get_prompt_reformulated_contextual_query_6(query, history_chat_messages):
        history_chat = format_text_history_chat(history_chat_messages)
        prompt_identify_reform = f"""Dado el último mensaje del usuario, dirigido a un asistente especializado en normativas académicas de la Facultad de Ciencias de la Universidad Nacional de Ingeniería (UNI), analiza el historial previo de la conversación junto con la consulta en el ultimo mensaje del usuario y determina si es necesario reformular la pregunta para mejorar la precision y falta de contexto de la pregunta, de manera que el asistente pueda entender la pregunta sin tener acceso al historial de la conversación. Solo en caso determines que es estrictamente necesario reformula la pregunta.
Usa los siguientes criterios para determinar si es estrictamente necesario reformular la consulta:
1. Contexto Académico Implicito: El asistente asume un contexto implícito que la preguntas enviadas por el usuario están relacionados con la Facultad de Ciencias de la UNI por lo que no es necesario detallarlo en exceso. Por lo tanto, a pesar no tener acceso al historial del dialogo el asistente asume este contexto.
2. Mejora en la precision y claridad: La reformulación de la pregunta se considera una mejora en precisión si incorpora información relevante mencionada en el historial de la conversación (excepto el último mensaje), siempre que esta información sea útil para hacer la pregunta más precisa. Solo se debe utilizar información explícitamente presente en el historial de la conversación, sin incluir suposiciones adicionales ni datos externos.

Responde utilizando el siguiente formato:

Análisis: [Describe de manera detallada si es necesario reformular la pregunta para mejorar la precision y falta de contexto de la pregunta].

El último mensaje contiene una pregunta: Sí/No

Es estrictamente necesario reformular la consulta: Sí/No/No aplica

Reformulación: <<Pregunta reformulada/No aplica>> [Proporciona la versión reformulada solo si es necesario].

Último mensaje del usuario: {query}

Historial previo de la conversación: <<{history_chat}>>"""
        return prompt_identify_reform

## Agregar esto a eso
# La pregunta del usuario se refiere al proceso de matrícula en la universidad y si hay plazos específicos que deben considerarse. Aunque la pregunta es clara y directa, el contexto sobre qué tipo de matrícula se está refiriendo (por ejemplo, matrícula inicial, matrícula para un ciclo académico específico, etc.) no se menciona. Sin embargo, dado que el término "matrícula" es común en el ámbito académico y el asistente está familiarizado con las normativas de la universidad, se puede inferir que se refiere al proceso general de matrícula en la Facultad de Ciencias de la UNI. La pregunta es específica en cuanto a la búsqueda de información sobre el proceso y los plazos, lo que permite que se pueda responder de manera adecuada. Por lo tanto, hay suficiente contexto para entender la pregunta sin necesidad de información adicional.

## gen data test
train_contextualize_questions_dataset = load_json("conversational_faq/data/train_contextualize_questions_dataset.json")
train_contextualize_questions_need_context = [sample for sample in train_contextualize_questions_dataset if sample["need_context"]]
print("train_contextualize_questions_need_context:", len(train_contextualize_questions_need_context))

train_contextualize_questions_not_need_context = [sample for sample in train_contextualize_questions_dataset if not sample["need_context"] and len(sample["dialog_context"]) > 0]
print("train_contextualize_questions_not_need_context:", len(train_contextualize_questions_not_need_context))
count_good_pred = 0

test_data = train_contextualize_questions_not_need_context[18:22] #+ train_contextualize_questions_need_context[0:10]
#test_data = train_contextualize_questions_need_context[10:22]
#save_json("./test/", "contextualize_demo_test_data", test_data)

#test_data = load_json("./test/contextualize_demo_test_data.json")[:5]

for example in test_data[:]:
# que no es suficientemente descrita en el mensaje para poder entender completamente el contexto del mensaje.
    history_messages_chat = example["dialog_context"]
    query = example["user_message"]

    prompt = get_prompt_reformulated_contextual_query_6(query, history_messages_chat)
    expected_need_context = not example["need_context"]
    print()
    print("-"*90)
    print("\n".join(prompt.split("\n")[-2:]))

    print("\nprompt:\n\n", prompt)
    
    messages = [{"role": "user", "content": prompt}]
       
    #messages = [{"role": "user", "content": prompt_identify_reform}, {"role": "assistant", "content": "La última pregunta del usuario se entiende sin necesidad del historial del chat: Sí"}, {"role": "user", "content": "esta respuesta esta mal"}]

    response = get_completion_from_messages(
                        messages,
                        model = "gpt-4o-mini-2024-07-18"
                        #model= "gpt-3.5-turbo-0125"
                        )

    print("\n\033[32mresponde need context:\033[0m", response)


    need_context = extract_need_reformulate(response)
    pred_entendible = not (need_context == "Sí")

    if pred_entendible == expected_need_context:
        count_good_pred += 1
    else:
        print('\n'+ "\033[31m" + f'Bad Prediction, Expected: entendible={expected_need_context}' + "\033[0m")
      
        
        messages = [{"role": "user", "content": prompt},
            {"role": "assistant", "content": response},
            {"role": "user", "content": "explicame a detalle en que criterios y ejemplos te basaste para llegar a esa conclusion"}]

        response = get_completion_from_messages(
                            messages,
                            model = "gpt-4o-mini-2024-07-18",
                            #model= "gpt-3.5-turbo-0125"
                            )
        print()
        print("\n\033[32mExplicacion:\033[0m", response)
        
    time.sleep(3)
print("Exactitud:", count_good_pred / len(test_data))




