
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

def get_prompt_reformulated_contextual_query_7(query, history_chat_messages):
        history_chat = format_text_history_chat(history_chat_messages)
        prompt_identify_reform = f"""Dado el último mensaje del usuario, dirigido a un asistente especializado en normativas académicas de la Facultad de Ciencias de la Universidad Nacional de Ingeniería (UNI), analiza el historial previo de la conversación junto con la consulta en el ultimo mensaje del usuario y determina si es necesario reformular la pregunta para mejorar la precision y falta de contexto de la pregunta, de manera que el asistente pueda entender la pregunta en el ultimo mensaje de usuario sin tener acceso al historial de la conversación. Solo en caso determines que es estrictamente necesario reformula la pregunta.
Usa los siguientes criterios para determinar si es estrictamente necesario reformular la consulta:
1. Contexto Académico Implícito
El asistente asume que todas las preguntas del usuario están relacionadas con la Facultad de Ciencias de la UNI, por lo que no es necesario mencionarlo explícitamente en cada consulta. En consecuencia, hacer referencia explícita a la Facultad de Ciencias de la UNI no mejora la precisión de las respuestas, y su omisión no requiere una reformulación de la pregunta.
2. Mejora en la Precisión y Claridad
Cuando el historial de conversación contiene información explícita que puede hacer la pregunta más precisa y contextualizada, se debe reformular la consulta para que el asistente pueda comprenderla sin depender del historial. Sin embargo, solo se debe incluir información explícitamente mencionada en el historial, sin añadir suposiciones ni datos externos. Como se indica en el criterio 1, hacer referencia explícita a la Facultad de Ciencias no contribuye a la claridad y no justifica una reformulación.

Analiza cada criterio de manera detallada para determinar si es necesario reformular la consulta y responde utilizando el siguiente formato:

Análisis: [Describe de manera detallada si es necesario reformular la pregunta].

El último mensaje contiene una pregunta: Sí/No

Es estrictamente necesario reformular la consulta: Sí/No/No aplica

Reformulación: <<Pregunta reformulada/No aplica>> [Proporciona la versión reformulada solo si es necesario].

Último mensaje del usuario: {query}

Historial previo de la conversación: <<{history_chat}>>"""
        return prompt_identify_reform


def get_prompt_reformulated_contextual_query_8(query, history_chat_messages):
        history_chat = format_text_history_chat(history_chat_messages)
        prompt_identify_reform = f"""Dado el último mensaje del usuario, dirigido a un asistente especializado en normativas académicas de la Facultad de Ciencias de la Universidad Nacional de Ingeniería (UNI), analiza el historial previo de la conversación junto con la consulta en el último mensaje del usuario y determina si es necesario reformular la pregunta para mejorar su precisión y claridad.

El objetivo es que el asistente pueda comprender la pregunta en el último mensaje del usuario sin tener acceso al historial de la conversación. Reformula la pregunta solo si es estrictamente necesario según los siguientes criterios:

Criterios para Reformulación
Criterio 1: Contexto Académico Implícito
El asistente siempre asume que todas las preguntas están relacionadas con la Facultad de Ciencias de la UNI, por lo que no es necesario reformular la pregunta solo para incluir esta información.
No reformules la pregunta si la única mejora posible es añadir “Facultad de Ciencias de la UNI”.
Criterio 2: Ambigüedad y Falta de Contexto
Reformula la pregunta solo si es ambigua cuando se toma de manera aislada, es decir, si el usuario menciona algo sin especificar a qué se refiere y el historial previo de la conversación puede aclararlo.
La ambigüedad ocurre cuando la pregunta tomada de manera aislada podría referirse a más de un concepto o trámite académico.
Si la pregunta incluye términos referenciales sin contexto suficiente para que el asistente los entienda sin el historial, es necesario reformularla.
El contexto previo de la conversacion no debe tomarse como suficiente para que la pregunta sea clara, es necesario reformular la pregunta para incluir el contexto suficiente para que sea clara si se toma de manera aislada.
No reformules si la pregunta sigue siendo clara sin el historial.
Criterio 3: Mejora en la Precisión
Si el historial de la conversación contiene información explícita que puede hacer la pregunta más precisa, se debe reformular.
Solo reformula si puedes usar información ya presente en el historial sin agregar suposiciones o información externa.


Ejemplos de Aplicación de los Criterios

Ejemplo 1 (Reformulación Necesaria)
Historial:
Usuario: "¿Cómo solicito un Retiro Total?"
Asistente: "Se presenta en la plataforma intranet-alumnos y debes adjuntar documentos sustentatorios."
Usuario: "¿Qué documentos se necesitan?"

Evaluación:

"¿Qué documentos se necesitan?" es ambigua si se toma aislada, ya que no menciona que se refiere al Retiro Total.
Se necesita reformular para hacer explícito que se trata de documentos para el Retiro Total.
Reformulación Correcta:
"¿Qué documentos sustentatorios se requieren para solicitar un Retiro Total?"

Ejemplo 2 (Reformulación No Necesaria)
Historial:
Usuario: "¿Cuáles son los requisitos para la matrícula?"
Asistente: "Debes presentar tu DNI y un recibo de pago."
Usuario: "¿Y cuánto cuesta la matricula?"

Evaluación:

"¿Y cuánto cuesta la matricula?" es entendible sin historial porque se menciona en la ultima pregunta que se refiere a la matricula y el historial no contiene información que puede agregarse para hacer mas clara o precisa la pregunta. No es necesario reformular.

Ejemplo 3 (Mensaje No es una Pregunta)
Historial:
Usuario: "Gracias por la ayuda."

Evaluación:

No es una pregunta.
No se necesita reformulación.

Formato de Respuesta
La respuesta debe seguir este formato estructurado:

Análisis: Explicación detallada sobre si la pregunta debe reformularse segun los criterios establecidos.
El último mensaje contiene una pregunta: Sí/No
Es estrictamente necesario reformular la consulta: Sí/No/No aplica
Reformulación: <<Pregunta reformulada/No aplica>>


Formato de Respuesta Esperado

Determina si es necesario reformular la consulta con los criterios mencionados anteriormente y responde utilizando el siguiente formato:

Análisis: [Describe de manera detallada si es necesario reformular la pregunta].

El último mensaje contiene una pregunta: Sí/No  

Es estrictamente necesario reformular la consulta: Sí/No/No aplica  

Reformulación: <<Pregunta reformulada/No aplica>>

Datos de Entrada

Último mensaje del usuario: {query}

Historial previo de la conversación: <<{history_chat}>>"""
        return prompt_identify_reform


def get_prompt_reformulated_contextual_query_9(query, history_chat_messages):
        history_chat = format_text_history_chat(history_chat_messages)
        prompt_identify_reform = f"""Dado el último mensaje del usuario, dirigido a un asistente especializado en normativas académicas de la Facultad de Ciencias de la Universidad Nacional de Ingeniería (UNI), analiza el historial previo de la conversación junto con la consulta en el último mensaje del usuario y determina si es necesario reformular la pregunta para mejorar su precisión y claridad.

El objetivo es que el asistente pueda comprender la pregunta en el último mensaje del usuario sin tener acceso al historial de la conversación. Reformula la pregunta solo si es estrictamente necesario, es decir, si sin reformulación la pregunta podría ser malinterpretada o resultar confusa.

Criterios para Reformulación
Criterio 1: Contexto Académico Implícito
No reformules la pregunta si la única mejora posible es añadir “Facultad de Ciencias de la UNI”.
El asistente ya asume que todas las preguntas se refieren a esta facultad, por lo que no es necesario explicitarlo.
Criterio 2: Ambigüedad y Falta de Contexto
Reformula únicamente si la pregunta es ambigua cuando se toma de manera aislada, es decir, si el usuario menciona algo sin especificar a qué se refiere.
Ejemplo de ambigüedad:
- "¿Cuáles son los requisitos?" → Ambigua (no se sabe requisitos de qué trámite)
- "¿Cuáles son los requisitos para la matrícula?" → Clara, no necesita reformulación.
Criterio 3: Mejora en la Precisión
Reformula solo si el historial tiene información explícita que puede hacer la pregunta más precisa.
No reformules solo para mejorar redacción o hacer la pregunta más directa si ya es comprensible.
Ejemplo de reformulación justificada:
Historial:
Usuario: "¿Cómo solicito un Retiro Total?"
Asistente: "Debes presentar documentos sustentatorios."
Usuario: "¿Qué documentos se necesitan?"
Se necesita reformular porque la pregunta original es ambigua y no especifica que se refiere al Retiro Total.
Reformulación correcta: "¿Qué documentos sustentatorios se requieren para solicitar un Retiro Total?"

Ejemplos de Aplicación de los Criterios

Ejemplo 1 (Reformulación Necesaria)
Historial:
Usuario: "¿Cómo solicito un Retiro Total?"
Asistente: "Se presenta en la plataforma intranet-alumnos y debes adjuntar documentos sustentatorios."
Usuario: "¿Qué documentos se necesitan?"

Evaluación:

"¿Qué documentos se necesitan?" es ambigua si se toma aislada, ya que no menciona que se refiere al Retiro Total.
Se necesita reformular para hacer explícito que se trata de documentos para el Retiro Total.
Reformulación Correcta:
"¿Qué documentos sustentatorios se requieren para solicitar un Retiro Total?"

Ejemplo 2 (Reformulación No Necesaria)
Historial:
Usuario: "¿Cuáles son los requisitos para la matrícula?"
Asistente: "Debes presentar tu DNI y un recibo de pago."
Usuario: "¿Y cuánto cuesta la matricula?"

Evaluación:

"¿Y cuánto cuesta la matricula?" es entendible sin historial porque se menciona en la ultima pregunta que se refiere a la matricula y el historial no contiene información que puede agregarse para hacer mas clara o precisa la pregunta. No es necesario reformular.

Ejemplo 3 (Mensaje No es una Pregunta)
Historial:
Usuario: "Gracias por la ayuda."

Evaluación:

No es una pregunta.
No se necesita reformulación.

Formato de Respuesta Esperado
Determina si es necesario reformular la consulta con los criterios mencionados anteriormente y responde utilizando el siguiente formato:

Análisis: [Explicación detallada sobre si la pregunta es ambigua y si debe reformularse].

El último mensaje contiene una pregunta: Sí/No

Es estrictamente necesario reformular la consulta: Sí/No/No aplica

Reformulación: <<Pregunta reformulada/No aplica>>

Datos de Entrada

Último mensaje del usuario: {query}

Historial previo de la conversación: <<{history_chat}>>"""
        return prompt_identify_reform

def get_prompt_reformulated_contextual_query_10(query, history_chat_messages):
        history_chat = format_text_history_chat(history_chat_messages)
        prompt_identify_reform = f"""Dado el último mensaje del usuario, dirigido a un asistente especializado en normativas académicas de la Facultad de Ciencias de la Universidad Nacional de Ingeniería (UNI), analiza el historial previo de la conversación junto con la consulta en el último mensaje del usuario y determina si es necesario reformular la pregunta para mejorar su precisión y claridad.

El objetivo es que el asistente pueda comprender la pregunta en el último mensaje del usuario sin tener acceso al historial de la conversación. Reformula la pregunta solo si es estrictamente necesario según los siguientes criterios:

Criterios para Reformulación
Criterio 1: Contexto Académico Implícito
El asistente siempre asume que todas las preguntas están relacionadas con la Facultad de Ciencias de la UNI, por lo que no es necesario reformular la pregunta solo para incluir esta información.
No reformules la pregunta si la única mejora posible es añadir “Facultad de Ciencias de la UNI”.
Criterio 2: Mejora en la Precisión
Si el historial de la conversación contiene información explícita que puede hacer la pregunta más precisa, se debe reformular.
Solo reformula si puedes usar información ya presente en el historial para hacer la pregunta más precisa y clara.
Si la pregunta ya menciona el tema principal y es comprensible sin el historial, NO la reformules.

Errores comunes que debes evitar
- Reformular preguntas claras solo para reorganizar la información.
- Modificar la estructura de la pregunta sin una razón estrictamente necesaria.
- Reformular solo para añadir contexto que el usuario ya mencionó en su ultimo mensaje.
- Reformular solo porque el historial menciona algo que el usuario ya dijo en su pregunta

Ejemplos de Aplicación de los Criterios

Ejemplo 1 (Reformulación Necesaria)
Historial:
Usuario: "¿Cómo solicito un Retiro Total?"
Asistente: "Se presenta en la plataforma intranet-alumnos y debes adjuntar documentos sustentatorios."
Usuario: "¿Qué documentos se necesitan?"

Evaluación:

"¿Qué documentos se necesitan?" es ambigua si se toma aislada, ya que no menciona que se refiere al Retiro Total.
Se necesita reformular para hacer explícito que se trata de documentos para el Retiro Total.
Reformulación Correcta:
"¿Qué documentos sustentatorios se requieren para solicitar un Retiro Total?"

Ejemplo 2 (Reformulación No Necesaria)
Historial:
Usuario: "¿Cuáles son los requisitos para la matrícula?"
Asistente: "Debes presentar tu DNI y un recibo de pago."
Usuario: "¿Y cuánto cuesta la matricula?"

Evaluación:

"¿Y cuánto cuesta la matricula?" es entendible sin historial porque se menciona en la ultima pregunta que se refiere a la matricula y el historial no contiene información que puede agregarse para hacer mas clara o precisa la pregunta. No es necesario reformular.

Ejemplo 3 (Mensaje No es una Pregunta)
Historial:
Usuario: "Gracias por la ayuda."

Evaluación:

No es una pregunta.
No se necesita reformulación.

Formato de Respuesta
La respuesta debe seguir este formato estructurado:

Análisis: Explicación detallada sobre si la pregunta debe reformularse segun los criterios establecidos.
El último mensaje contiene una pregunta: Sí/No
Es estrictamente necesario reformular la consulta: Sí/No/No aplica
Reformulación: <<Pregunta reformulada/No aplica>>


Formato de Respuesta Esperado

Determina si es necesario reformular la consulta con los criterios mencionados anteriormente y responde utilizando el siguiente formato:

Análisis: [Describe de manera detallada si es necesario reformular la pregunta].

El último mensaje contiene una pregunta: Sí/No  

Es estrictamente necesario reformular la consulta: Sí/No/No aplica  

Reformulación: <<Pregunta reformulada/No aplica>>

Datos de Entrada

Último mensaje del usuario: {query}

Historial previo de la conversación: <<{history_chat}>>"""
        return prompt_identify_reform


def get_prompt_reformulated_contextual_query_11(query, history_chat_messages):
        history_chat = format_text_history_chat(history_chat_messages)
        prompt_identify_reform = f"""Dado el último mensaje del usuario, dirigido a un asistente especializado en normativas académicas de la Facultad de Ciencias de la Universidad Nacional de Ingeniería (UNI), analiza el historial previo de la conversación junto con la consulta en el último mensaje del usuario y determina si es necesario reformular la pregunta para mejorar su precisión y claridad.

🔎 Paso 1: Evaluar si la reformulación es necesaria
Antes de reformular, sigue estos pasos:
1️⃣ Analiza la pregunta del usuario sin el historial:

Si la pregunta es clara y comprensible por sí sola, NO reformules.
Si la pregunta es ambigua, incompleta o puede malinterpretarse sin el historial, pasa al Paso 2.
2️⃣ Revisa el historial:

Si hay información relevante en el historial que pueda mejorar la pregunta, reformula.
Si el historial no agrega claridad o la pregunta ya es precisa, NO reformules.
⚠️ Importante:
❌ No reformules solo porque la pregunta podría sonar mejor o más natural.
❌ No reformules si la pregunta ya menciona claramente el tema principal.
❌ No reformules solo porque el historial menciona algo relacionado con la pregunta actual.

✅ Paso 2: Aplicar criterios de reformulación
Solo si en el Paso 1 determinaste que la reformulación es necesaria, usa los siguientes criterios:

1️⃣ Contexto Académico Implícito

El asistente siempre asume que todas las preguntas están relacionadas con la Facultad de Ciencias de la UNI.
No reformules solo para incluir “Facultad de Ciencias de la UNI” si no es estrictamente necesario.
2️⃣ Mejora en la Precisión

Reformula solo si la pregunta es ambigua o puede malinterpretarse sin el historial.
Si la pregunta ya menciona el tema principal y es comprensible sin el historial, NO la reformules.

3️⃣ Independencia de la Pregunta respecto al Historial ✅

Reformula la pregunta si su comprensión depende del historial.
Asegura que la pregunta pueda entenderse de manera autónoma sin necesidad de contexto previo.

Ejemplos de Aplicación de los Criterios

Ejemplo 1 (Reformulación Necesaria)
Historial:
Usuario: "¿Cómo solicito un Retiro Total?"
Asistente: "Se presenta en la plataforma intranet-alumnos y debes adjuntar documentos sustentatorios."
Usuario: "¿Qué documentos se necesitan?"

Evaluación:

"¿Qué documentos se necesitan?" es ambigua si se toma aislada, ya que no menciona que se refiere al Retiro Total.
Se necesita reformular para hacer explícito que se trata de documentos para el Retiro Total.
Reformulación Correcta:
"¿Qué documentos sustentatorios se requieren para solicitar un Retiro Total?"

Ejemplo 2 (Reformulación No Necesaria)
Historial:
Usuario: "¿Cuáles son los requisitos para la matrícula?"
Asistente: "Debes presentar tu DNI y un recibo de pago."
Usuario: "¿Y cuánto cuesta la matricula?"

✅ Ejemplo donde NO se reformula
📌 Pregunta del usuario: "¿Sabes si hay algún plazo específico para hacer el retiro parcial o la reincorporación? Y, por cierto, ¿hay algún costo asociado a estos trámites?"
📌 Evaluación:

La pregunta es clara, menciona directamente los trámites (retiro parcial y reincorporación) y los temas clave (plazo y costo).
No depende del historial para ser comprendida.
✅ Conclusión: No se reformula.
✅ Ejemplo donde SÍ se reformulaq
📌 Pregunta del usuario: "¿Cuáles son los requisitos?"
📌 Evaluación:

Es ambigua sin el historial (no sabemos a qué trámite se refiere).
Se necesita reformular para hacer explícito el contexto.
✅ Reformulación: "¿Cuáles son los requisitos para solicitar un Retiro Parcial en la Facultad de Ciencias de la UNI?"

Evaluación:

"¿Y cuánto cuesta la matricula?" es entendible sin historial porque se menciona en la ultima pregunta que se refiere a la matricula y el historial no contiene información que puede agregarse para hacer mas clara o precisa la pregunta. No es necesario reformular.

Ejemplo 3 (Mensaje No es una Pregunta)
Historial:
Usuario: "Gracias por la ayuda."

Evaluación:

No es una pregunta.
No se necesita reformulación.

Formato de Respuesta
La respuesta debe seguir este formato estructurado:

Análisis: Explicación detallada sobre si la pregunta debe reformularse segun los criterios establecidos.
El último mensaje contiene una pregunta: Sí/No
Es estrictamente necesario reformular la consulta: Sí/No/No aplica
Reformulación: <<Pregunta reformulada/No aplica>>


Formato de Respuesta Esperado

Determina si es necesario reformular la consulta con los criterios mencionados anteriormente y responde utilizando el siguiente formato:

Análisis: [Describe de manera detallada si es necesario reformular la pregunta].

El último mensaje contiene una pregunta: Sí/No  

Es estrictamente necesario reformular la consulta: Sí/No/No aplica  

Reformulación: <<Pregunta reformulada/No aplica>>

Datos de Entrada

Último mensaje del usuario: {query}

Historial previo de la conversación: <<{history_chat}>>"""
        return prompt_identify_reform

def get_prompt_reformulated_contextual_query_12(query, history_chat_messages):
        history_chat = format_text_history_chat(history_chat_messages)
        prompt_identify_reform = f"""Dado el último mensaje del usuario, dirigido a un asistente especializado en normativas académicas de la Facultad de Ciencias de la Universidad Nacional de Ingeniería (UNI), analiza el historial previo de la conversación junto con la consulta en el último mensaje del usuario y determina si es necesario reformular la pregunta para mejorar su precisión y claridad.

🔎 Paso 1: Evaluar si la reformulación es necesaria
Antes de reformular, sigue estos pasos:
1️⃣ Analiza la pregunta del usuario sin el historial:

Si la pregunta es clara y comprensible por sí sola, NO reformules.
Si la pregunta es ambigua, incompleta o puede malinterpretarse sin el historial, pasa al Paso 2.
2️⃣ Revisa el historial:
Si hay información relevante en el historial que pueda mejorar la pregunta, reformula.
Si el historial no agrega claridad o la pregunta ya es precisa, NO reformules.

⚠️ Importante:
❌ No reformules solo porque la pregunta podría sonar mejor o más natural.
❌ No reformules si la pregunta ya menciona claramente el tema principal.
❌ No reformules solo porque el historial menciona algo relacionado con la pregunta actual.
✅ Reformula si el historial aporta detalles que pueden hacer la pregunta más específica o evitar confusión.


✅ Paso 2: Aplicar criterios de reformulación
Solo si en el Paso 1 determinaste que la reformulación es necesaria, usa los siguientes criterios:

1️⃣ Contexto Académico Implícito

El asistente siempre asume que todas las preguntas están relacionadas con la Facultad de Ciencias de la UNI.
No reformules solo para incluir “Facultad de Ciencias de la UNI” si no es estrictamente necesario.
2️⃣ Mejora en la Precisión

Reformula solo si la pregunta es ambigua o puede malinterpretarse sin el historial.
Si la pregunta ya menciona el tema principal y es comprensible sin el historial, NO la reformules.

Ejemplos de Aplicación de los Criterios

Ejemplo 1 (Reformulación Necesaria)
Historial:
Usuario: "¿Cómo solicito un Retiro Total?"
Asistente: "Se presenta en la plataforma intranet-alumnos y debes adjuntar documentos sustentatorios."
Usuario: "¿Qué documentos se necesitan?"

Evaluación:

"¿Qué documentos se necesitan?" es ambigua si se toma aislada, ya que no menciona que se refiere al Retiro Total.
Se necesita reformular para hacer explícito que se trata de documentos para el Retiro Total.
Reformulación Correcta:
"¿Qué documentos sustentatorios se requieren para solicitar un Retiro Total?"

Ejemplo 2 (Reformulación No Necesaria)
Historial:
Usuario: "¿Cuáles son los requisitos para la matrícula?"
Asistente: "Debes presentar tu DNI y un recibo de pago."
Usuario: "¿Y cuánto cuesta la matricula?"
Evaluación:
"¿Y cuánto cuesta la matricula?" es entendible sin historial porque se menciona en la ultima pregunta que se refiere a la matricula y el historial no contiene información que puede agregarse para hacer mas clara o precisa la pregunta. No es necesario reformular.

Ejemplo 3 (Reformulación Necesaria por dependencia del historial)

Pregunta del usuario:
"¿Sabes si hay algún plazo específico para hacer ese trámite del autoseguro?"

📌 Historial previo:
Usuario: "¿Hay un manual o guía que explique cómo un ingresante puede generar su orden de pago para el autoseguro?"
Asistente: "Sí, puedes consultar el manual de pagos de la UNI en la web de la Facultad de Ciencias."

Evaluación:
La pregunta "¿Sabes si hay algún plazo específico para hacer ese trámite del autoseguro?" depende del historial para entenderse completamente.
"Ese trámite" es ambiguo sin el historial.
Para hacerla independiente del historial previo, se debe reformular mencionando explícitamente "la generación de la orden de pago del autoseguro".

✅ Ejemplo donde NO se reformula
📌 Pregunta del usuario: "¿Sabes si hay algún plazo específico para hacer el retiro parcial o la reincorporación? Y, por cierto, ¿hay algún costo asociado a estos trámites?"
📌 Evaluación:

La pregunta es clara, menciona directamente los trámites (retiro parcial y reincorporación) y los temas clave (plazo y costo).
No depende del historial para ser comprendida.
✅ Conclusión: No se reformula.
✅ Ejemplo donde SÍ se reformula
📌 Pregunta del usuario: "¿Cuáles son los requisitos?"
📌 Evaluación:

Es ambigua sin el historial (no sabemos a qué trámite se refiere).
Se necesita reformular para hacer explícito el contexto.
✅ Reformulación: "¿Cuáles son los requisitos para solicitar un Retiro Parcial en la Facultad de Ciencias de la UNI?"

Evaluación:

"¿Y cuánto cuesta la matricula?" es entendible sin historial porque se menciona en la ultima pregunta que se refiere a la matricula y el historial no contiene información que puede agregarse para hacer mas clara o precisa la pregunta. No es necesario reformular.

Ejemplo 3 (Mensaje No es una Pregunta)
Historial:
Usuario: "Gracias por la ayuda."

Evaluación:

No es una pregunta.
No se necesita reformulación.

Formato de Respuesta
La respuesta debe seguir este formato estructurado:

Análisis: Explicación detallada sobre si la pregunta debe reformularse segun los criterios establecidos.
El último mensaje contiene una pregunta: Sí/No
Es estrictamente necesario reformular la consulta: Sí/No/No aplica
Reformulación: <<Pregunta reformulada/No aplica>>


Formato de Respuesta Esperado

Determina si es necesario reformular la consulta con los criterios mencionados anteriormente y responde utilizando el siguiente formato:

Análisis: [Describe de manera detallada si es necesario reformular la pregunta].

El último mensaje contiene una pregunta: Sí/No  

Es estrictamente necesario reformular la consulta: Sí/No/No aplica  

Reformulación: <<Pregunta reformulada/No aplica>>

Datos de Entrada

Último mensaje del usuario: {query}

Historial previo de la conversación: <<{history_chat}>>"""
        return prompt_identify_reform
# ❌ No reformules si en el ultimo mensaje con la pregunta se menciona el tema consultado de manera clara y especifica.
# ❌ No reformules si en el ultimo mensaje ya se menciona claramente el tema principal.
# Si un término clave en la pregunta puede referirse a múltiples temas dentro de la Facultad de Ciencias y el historial lo aclara, la pregunta debe reformularse para ser completamente explícita.
#Si la pregunta ya menciona el tema principal y es comprensible sin el historial, NO la reformules.
#📌 Independencia total de la pregunta respecto al historial
#Reformula solo si la consulta del usuario en el ultimo mensaje no se entiende claramente sin el historial.
def get_prompt_reformulated_contextual_query_13(query, history_chat_messages):
        history_chat = format_text_history_chat(history_chat_messages)
        prompt_identify_reform = f"""Dado el último mensaje del usuario, dirigido a un asistente especializado en normativas académicas de la Facultad de Ciencias de la Universidad Nacional de Ingeniería (UNI), analiza el historial previo de la conversación junto con la consulta en el último mensaje del usuario y determina si es necesario reformular la pregunta para mejorar su precisión y claridad.
El objetivo es que el asistente pueda comprender la pregunta del último mensaje del usuario sin tener acceso al historial de la conversación.

🔎 Paso 1: Evaluar si la reformulación es necesaria
Aplica los siguientes de criterios para determinar la necesidad de reformulación
📌 Mejora en la precisión basada en el historial
Reformula solo si el historial contiene información relevante que puede mejorar la precision y claridad de la pregunta de manera que el asistente pueda comprender la consulta realizada en el último mensaje del usuario sin tener acceso al historial de la conversación.
No reformules si en el último mensaje ya se menciona claramente el tema o trámite específico.

📌 Contexto académico implícito
Todas las preguntas se asumen relacionadas con la Facultad de Ciencias de la UNI.
No reformules solo para incluir “Facultad de Ciencias de la UNI” si no es estrictamente necesario.

⚠️ Importante:
❌ No reformules solo porque la pregunta podría sonar mejor o más natural.
❌ No reformules solo porque el historial menciona algo relacionado con la pregunta actual.

✅ Paso 2: Aplicar la reformulación
Solo si en el Paso 1 determinaste que la reformulación es necesaria realiza la reformulación de la consulta. Usa el formato de salida descrito abajo.

Formato de Respuesta Esperado

Determina si es necesario reformular la consulta con los criterios mencionados anteriormente y responde utilizando el siguiente formato:

Análisis: [Describe de manera detallada si es necesario reformular la pregunta].

El último mensaje contiene una pregunta: Sí/No  

Es estrictamente necesario reformular la consulta: Sí/No/No aplica  

Reformulación: <<Pregunta reformulada/No aplica>>


Ejemplos de Aplicación de los Criterios

Ejemplo 1 (Reformulación Necesaria)
Historial:

Usuario: "¿Cómo solicito un Retiro Total?"
Asistente: "Se presenta en la plataforma intranet-alumnos y debes adjuntar documentos sustentatorios."
Usuario: "¿Qué documentos se necesitan?"
Evaluación:

La pregunta "¿Qué documentos se necesitan?" es ambigua sin el historial, ya que no menciona que se refiere al Retiro Total.
✅ Reformulación: "¿Qué documentos sustentatorios se requieren para solicitar un Retiro Total?"
Ejemplo 2 (Reformulación No Necesaria)
Historial:

Usuario: "¿Cuáles son los requisitos para la matrícula?"
Asistente: "Debes presentar tu DNI y un recibo de pago."
Usuario: "¿Y cuánto cuesta la matrícula?"
Evaluación:

La pregunta es clara y entendible sin el historial, y no es necesario mencionar explicitamente que se refiere a la matricula en la Facultad de Ciencias.
❌ No se necesita reformulación.
Ejemplo 3 (Reformulación Necesaria por Dependencia del Historial)
Historial:

Usuario: "¿Hay un manual o guía que explique cómo un ingresante puede generar su orden de pago para el autoseguro?"
Asistente: "Sí, puedes consultar el manual de pagos de la UNI en la web de la Facultad de Ciencias."
Usuario: "¿Sabes si hay algún plazo específico para hacer ese trámite del autoseguro?"
Evaluación:

"Ese trámite" es ambiguo sin el historial.
✅ Reformulación: "¿Sabes si hay algún plazo específico para generar la orden de pago del autoseguro?"
Ejemplo 4 (Mensaje No es una Pregunta)
Historial:

Usuario: "Gracias por la ayuda."
Evaluación:

No es una pregunta.
❌ No se necesita reformulación.
Ejemplo 5 (Reformulación No Necesaria)
Historial:

Usuario: "¿Dónde puedo encontrar información sobre el retiro parcial o la reincorporación?"
Asistente: "Puedes encontrar el procedimiento del retiro parcial o de la reincorporación en..."
Usuario: "¿Sabes si hay algún plazo específico para hacer el retiro parcial o la reincorporación? Y, por cierto, ¿hay algún costo asociado a estos trámites?"
Evaluación:
El mensaje con las preguntas ya menciona explícitamente "retiro parcial" y "reincorporación", por lo que es completamente entendible sin el historial.
No es necesario mencionar explicitamente que se refiere esos tramites en la Facultad de Ciencias.
❌ No se necesita reformulación.
❌ No se necesita reformulación.
Ejemplo 6 (Reformulación Necesaria por Ambigüedad)
Historial:

Usuario: "¿Cuándo puedo solicitar el retiro total?"
Asistente: "Hasta la penúltima semana del ciclo académico."
Usuario: "¿Cuáles son los requisitos?"
Evaluación:

"¿Cuáles son los requisitos?" es ambigua sin el historial.
✅ Reformulación: "¿Cuáles son los requisitos para solicitar un Retiro Total?"

Datos de Entrada

Último mensaje del usuario: {query}

Historial previo de la conversación: <<{history_chat}>>"""
        return prompt_identify_reform


def get_prompt_reformulated_contextual_query_14(query, history_chat_messages):
        history_chat = format_text_history_chat(history_chat_messages)
        prompt_identify_reform = f"""Dado el último mensaje del usuario, dirigido a un asistente especializado en normativas académicas de la Facultad de Ciencias de la Universidad Nacional de Ingeniería (UNI), analiza el historial previo de la conversación junto con la consulta en el último mensaje del usuario y determina si es necesario reformular la pregunta para mejorar su precisión y claridad.
El objetivo es que el asistente pueda comprender la pregunta del último mensaje del usuario sin tener acceso al historial de la conversación.

🔎 Paso 1: Evaluar si la reformulación es necesaria
Aplica los siguientes de criterios para determinar la necesidad de reformulación

📌 Ambigüedad sin el historial
Reformula solo si el asistente no podría comprender o responder con precisión el último mensaje sin acceder al historial de la conversación. Si la pregunta aún es clara y comprensible sin el historial, NO reformules.

📌 Claridad explícita
Si el último mensaje ya menciona claramente el tema principal (por ejemplo, "Retiro Total"), NO reformules aunque el historial proporcione más detalles.

📌 No reformular por estilo
No reformules solo porque la pregunta podría sonar mejor o ser más detallada si el asistente ya puede entender y responder adecuadamente.

📌 Ámbito institucional implícito
Todas las preguntas se asumen relacionadas con la Facultad de Ciencias de la UNI. No reformules solo para incluir “Facultad de Ciencias de la UNI”, a menos que la pregunta sea completamente ambigua sin esa información.

📌 Cuidado con sobre-reformular
No reformules solo porque la pregunta tiene relación con el historial.

⚠️ Importante:
❌ No reformules solo porque la pregunta podría sonar mejor o más natural.
❌ No reformules solo porque el historial menciona algo relacionado con la pregunta actual.
❌ No reformules si el único motivo es agregar Facultad de Ciencias de la UNI. Reformula solo si hay ambigüedad real.

✅ Paso 2: Aplicar la reformulación
Solo si en el Paso 1 determinaste que la reformulación es necesaria realiza la reformulación de la consulta. Usa el formato de salida descrito abajo.

Formato de Respuesta Esperado

Determina si es necesario reformular la consulta con los criterios mencionados anteriormente y responde utilizando el siguiente formato:

Análisis: [Describe de manera detallada si es necesario reformular la pregunta].

El último mensaje contiene una pregunta: Sí/No  

Es estrictamente necesario reformular la consulta: Sí/No/No aplica  

Reformulación: <<Pregunta reformulada/No aplica>>


Ejemplos de Aplicación de los Criterios

Ejemplo 1 (Reformulación Necesaria)
Historial:

Usuario: "¿Cómo solicito un Retiro Total?"
Asistente: "Se presenta en la plataforma intranet-alumnos y debes adjuntar documentos sustentatorios."
Usuario: "¿Qué documentos se necesitan?"
Evaluación:

La pregunta "¿Qué documentos se necesitan?" es ambigua sin el historial, ya que no menciona que se refiere al Retiro Total.
✅ Reformulación: "¿Qué documentos sustentatorios se requieren para solicitar un Retiro Total?"
Ejemplo 2 (Reformulación No Necesaria)
Historial:

Usuario: "¿Cuáles son los requisitos para la matrícula?"
Asistente: "Debes presentar tu DNI y un recibo de pago."
Usuario: "¿Y cuánto cuesta la matrícula?"
Evaluación:

La pregunta es clara y entendible sin el historial, y no es necesario mencionar explicitamente que se refiere a la matricula en la Facultad de Ciencias.
❌ No se necesita reformulación.
Ejemplo 3 (Reformulación Necesaria por Dependencia del Historial)
Historial:

Usuario: "¿Hay un manual o guía que explique cómo un ingresante puede generar su orden de pago para el autoseguro?"
Asistente: "Sí, puedes consultar el manual de pagos de la UNI en la web de la Facultad de Ciencias."
Usuario: "¿Sabes si hay algún plazo específico para hacer ese trámite del autoseguro?"
Evaluación:

"Ese trámite" es ambiguo sin el historial.
✅ Reformulación: "¿Sabes si hay algún plazo específico para generar la orden de pago del autoseguro?"
Ejemplo 4 (Mensaje No es una Pregunta)
Historial:

Usuario: "Gracias por la ayuda."
Evaluación:

No es una pregunta.
❌ No se necesita reformulación.
Ejemplo 5 (Reformulación No Necesaria)
Historial:

Usuario: "¿Dónde puedo encontrar información sobre el retiro parcial o la reincorporación?"
Asistente: "Puedes encontrar el procedimiento del retiro parcial o de la reincorporación en..."
Usuario: "¿Sabes si hay algún plazo específico para hacer el retiro parcial o la reincorporación? Y, por cierto, ¿hay algún costo asociado a estos trámites?"
Evaluación:
El mensaje con las preguntas ya menciona explícitamente "retiro parcial" y "reincorporación", por lo que es completamente entendible sin el historial.
No es necesario mencionar explicitamente que se refiere esos tramites en la Facultad de Ciencias.
❌ No se necesita reformulación.
❌ No se necesita reformulación.
Ejemplo 6 (Reformulación Necesaria por Ambigüedad)
Historial:

Usuario: "¿Cuándo puedo solicitar el retiro total?"
Asistente: "Hasta la penúltima semana del ciclo académico."
Usuario: "¿Cuáles son los requisitos?"
Evaluación:

"¿Cuáles son los requisitos?" es ambigua sin el historial.
✅ Reformulación: "¿Cuáles son los requisitos para solicitar un Retiro Total?"

Datos de Entrada

Último mensaje del usuario: {query}

Historial previo de la conversación: <<{history_chat}>>"""
        return prompt_identify_reform


def get_prompt_reformulated_contextual_query_15(query, history_chat_messages):
        history_chat = format_text_history_chat(history_chat_messages)
        prompt_identify_reform = f"""Dado el último mensaje del usuario, dirigido a un asistente especializado en normativas académicas de la Facultad de Ciencias de la Universidad Nacional de Ingeniería (UNI), analiza el historial previo de la conversación junto con la consulta en el último mensaje del usuario y determina si es necesario reformular la pregunta para mejorar su precisión y claridad.
El objetivo es que el asistente pueda comprender la pregunta del último mensaje del usuario sin tener acceso al historial de la conversación.

🔎 Paso 1: Evaluar si la reformulación es necesaria
Aplica los siguientes de criterios para determinar la necesidad de reformulación

📌 Ambigüedad sin el historial
Reformula solo si el asistente no podría comprender o responder con precisión el último mensaje sin acceder al historial de la conversación. Si la pregunta aún es clara y comprensible sin el historial, NO reformules.

📌 Claridad explícita
Si el último mensaje ya menciona claramente el tema principal (por ejemplo, "Retiro Total"), NO reformules aunque el historial proporcione más detalles.

📌 No reformular por estilo
No reformules solo porque la pregunta podría sonar mejor o ser más detallada si el asistente ya puede entender y responder adecuadamente.

📌 Ámbito institucional implícito
Todas las preguntas se asumen relacionadas con la Facultad de Ciencias de la UNI. No reformules solo para incluir “Facultad de Ciencias de la UNI”, a menos que la pregunta sea completamente ambigua sin esa información.

📌 Cuidado con sobre-reformular
No reformules solo porque la pregunta tiene relación con el historial.

⚠️ Importante:
❌ No reformules solo porque la pregunta podría sonar mejor o más natural.
❌ No reformules solo porque el historial menciona algo relacionado con la pregunta actual.
❌ No reformules si el único motivo es agregar Facultad de Ciencias de la UNI. Reformula solo si hay ambigüedad real.

✅ Paso 2: Aplicar la reformulación
Solo si en el Paso 1 determinaste que la reformulación es necesaria realiza la reformulación de la consulta. Usa el formato de salida descrito abajo.

Formato de Respuesta Esperado

Determina si es necesario reformular la consulta con los criterios mencionados anteriormente y responde utilizando el siguiente formato:

Análisis: [Describe de manera detallada si es necesario reformular la pregunta].

El último mensaje contiene una pregunta: Sí/No  

Es estrictamente necesario reformular la consulta: Sí/No/No aplica  

Reformulación: <<Pregunta reformulada/No aplica>>

Datos de Entrada

Último mensaje del usuario: {query}

Historial previo de la conversación: <<{history_chat}>>"""
        return prompt_identify_reform

# Verifica si hay términos clave que el usuario mencionó en la conversación anterior y que podrían seguir siendo relevantes, incluso si no aparecen en el último mensaje. 
# Si el asistente solo recibe el último mensaje sin el historial previo, ¿puede comprender con claridad qué se está preguntando?
def get_prompt_reformulated_contextual_query_16(query, history_chat_messages):
        history_chat = format_text_history_chat(history_chat_messages)
        prompt_identify_reform = f"""Dado el último mensaje del usuario, dirigido a un asistente especializado en normativas académicas de la Facultad de Ciencias de la Universidad Nacional de Ingeniería (UNI), analiza el historial previo de la conversación junto con la consulta del usuario en su último mensaje y determina si es necesario reformularla para mejorar su precisión y claridad.

El objetivo es que el asistente pueda comprender y responder adecuadamente la pregunta del usuario sin tener acceso al historial de la conversación.

🔎 Paso 1: Análisis de la pregunta sin el historial
Examina el último mensaje del usuario sin considerar el historial previo y analiza los siguientes aspectos:

A. Identificación del tema
Determina si la pregunta menciona explícitamente el tema del que trata, de manera que el asistente pueda responder adecuadamente sin depender del contexto previo.

B. Evaluación de la ambigüedad
Una pregunta es ambigua únicamente si un asistente que solo lee el último mensaje sin el historial previo no puede determinar con certeza de qué trata la consulta.

🔎 Paso 2: Evaluación del historial para mejorar la pregunta
Verifica si el historial de la conversación contiene información relevante que el usuario no haya mencionado explícitamente en su último mensaje y que podría ayudar a mejorar la claridad y precisión de la consulta.
- No solo busques información explícitamente omitida, sino también conexiones que podrían ser relevantes para una mejor respuesta.
- Si el usuario inició la conversación con un tema específico y luego omitió un detalle clave en su última pregunta, evalúa si ese detalle sigue siendo relevante para garantizar una respuesta precisa.
⚠ Importante: No añadas información externa ni hagas suposiciones sobre lo que el usuario podría querer decir. Enfócate solo en si el historial contiene información que ayudaría a mejorar la pregunta.

✅ Paso 3: Decisión sobre la reformulación
Decide si la pregunta necesita ser reformulada con base en los siguientes criterios:
 - Ambigüedad sin el historial: Si la consulta en el último mensaje es completamente ambigua y el historial contiene información relevante para hacerla más clara, entonces la pregunta debe ser reformulada.
 - Precisión del tema: Si el historial contiene detalles que no han sido mencionados explícitamente en el último mensaje y que pueden hacer la pregunta más precisa y facilitar una mejor respuesta, entonces la pregunta debe ser reformulada. El objetivo es que el asistente pueda comprender y responder adecuadamente la pregunta del usuario sin tener acceso al historial de la conversación.
 - Ámbito institucional implícito: Todas las consultas se asumen relacionadas con esta facultad. No reformules la pregunta únicamente para incluir “Facultad de Ciencias de la UNI” a menos que la omisión de esta referencia haga que la pregunta sea completamente ambigua.

Antes de tomar una decisión, proporciona una breve explicación justificando si es o no necesario reformular la pregunta.

Formato de Respuesta Esperado

Determina si es necesario reformular la consulta con los criterios mencionados anteriormente y responde utilizando el siguiente formato:

Análisis: [Explicación detallada sobre por qué es o no necesario reformular la pregunta].

El último mensaje contiene una pregunta: Sí/No  

Es estrictamente necesario reformular la consulta: Sí/No/No aplica  

Reformulación: <<Pregunta reformulada/No aplica>>

Datos de Entrada

Último mensaje del usuario: {query}

Historial previo de la conversación: <<{history_chat}>>"""
        return prompt_identify_reform

def get_prompt_reformulated_contextual_query_17(query, history_chat_messages):
        history_chat = format_text_history_chat(history_chat_messages)
        prompt_identify_reform = f"""Dado el último mensaje del usuario, dirigido a un asistente especializado en normativas académicas de la Facultad de Ciencias de la Universidad Nacional de Ingeniería (UNI), analiza el historial previo de la conversación junto con la consulta del usuario en su último mensaje y determina si es necesario reformularla para mejorar su precisión y claridad.

El objetivo es que el asistente pueda comprender y responder adecuadamente la pregunta del usuario sin tener acceso al historial de la conversación.

🔎 Paso 1: Análisis de la pregunta sin el historial
Examina el último mensaje del usuario sin considerar el historial previo y analiza los siguientes aspectos:

A. Identificación del tema
Determina si el ultimo mensaje del usuario menciona explícitamente el tema del que trata la consulta, de manera que el asistente pueda responder adecuadamente sin depender del contexto previo.

B. Evaluación de la ambigüedad
Una pregunta es ambigua únicamente si un asistente que solo lee el último mensaje sin el historial previo no puede determinar con certeza de qué trata la consulta.

🔎 Paso 2: Evaluación del historial para mejorar la pregunta
Verifica si el historial de la conversación contiene información relevante que el usuario no haya mencionado explícitamente en su último mensaje y que podría ayudar a mejorar la claridad y precisión de la consulta. El objetivo es que estos términos específicos o información relevante sea incluido en el ultimo mensaje para que la consulta sea mas claridad y precisión sin depender del historial previo de la conversación.
- No solo busques información explícitamente omitida, sino también conexiones o terminos especificos que podrían ser relevantes para una mejor respuesta.
- Si el usuario inició la conversación con un tema específico y luego omitió un detalle clave en su última pregunta, evalúa si ese detalle sigue siendo relevante para garantizar una respuesta precisa.
⚠ Importante: No añadas información externa ni hagas suposiciones sobre lo que el usuario podría querer decir. Enfócate solo en si el historial contiene información que ayudaría a mejorar la pregunta.

✅ Paso 3: Decisión sobre la reformulación
Decide si la pregunta necesita ser reformulada con base en los siguientes criterios:
 - Ambigüedad sin el historial: Si la consulta en el último mensaje es completamente ambigua y el historial contiene información relevante para hacerla más clara, entonces la pregunta debe ser reformulada.
 - Precisión del tema: Si el historial contiene detalles que no han sido mencionados explícitamente en el último mensaje y que pueden hacer la pregunta más precisa y facilitar una mejor respuesta, entonces la pregunta debe ser reformulada. El objetivo es que el asistente pueda comprender y responder adecuadamente la pregunta del usuario sin tener acceso al historial de la conversación.
 - Ámbito institucional implícito: Todas las consultas se asumen relacionadas con esta facultad. No reformules la pregunta únicamente para incluir “Facultad de Ciencias de la UNI” a menos que la omisión de esta referencia haga que la pregunta sea completamente ambigua.

Antes de tomar una decisión, proporciona una breve explicación justificando si es o no necesario reformular la pregunta.

Formato de Respuesta Esperado

Determina si es necesario reformular la consulta con los criterios mencionados anteriormente y responde utilizando el siguiente formato:
Identificacion del Tema: [Explicacion sobre si el ultimo mensaje del usuario menciona explícitamente el tema del que trata la consulta]
Evaluación de la ambigüedad: [Explicacion sobre si la pregunta es ambigua para el asistente si se lee sin el historial previo]
Evaluación del historial para mejorar la pregunta:  [Explicacion sobre si el historial de la conversación contiene información relevante que el usuario no haya mencionado explícitamente en su último mensaje y que podría ayudar a mejorar la claridad y precisión de la consulta]
Análisis: [Explicación detallada sobre por qué es o no necesario reformular la pregunta].

El último mensaje contiene una pregunta: Sí/No  

Es estrictamente necesario reformular la consulta: Sí/No/No aplica  

Reformulación: <<Pregunta reformulada/No aplica>>

Ejemplos de aplicacion de criterios:

Ejemplo 1 (Reformulacion es necesaria)

Último mensaje del usuario: ¿Sabes si hay algún plazo específico que deba tener en cuenta para la orden de pago?

Historial previo de la conversación: <<
user: ¿Cuáles son las implicaciones de no generar la orden de pago antes de realizar el pago del autoseguro?
assistant: Si no se genera la orden de pago antes de realizar el pago del autoseguro, el estudiante podría enfrentar problemas para matricularse de manera regular. Es fundamental cumplir con el plazo máximo establecido en el calendario de actividades académicas, ya que de no hacerlo, la matrícula podría no habilitarse y el estudiante tendría que gestionar su matrícula como rezagado. Para verificar la situación de la matrícula, se recomienda comprobar si se habilita en las fechas de matrícula regular. Si no es así, es necesario comunicarse con la oficina de estadística (AERA) para obtener más información.>>

Análisis: El último mensaje del usuario aborda la preocupación sobre los plazos para generar la orden de pago. La pregunta sin el historial es clara, sin embargo, la ambigüedad radica en que no se especifica si se refiere a la orden de pago en general o a un contexto particular. En el historial previo de la conversación se puede deducir que la orden de pago es para el autoseguro, este detalle es relevante para hacer la pregunta mas clara y precisa, por lo tanto, sería útil reformular la pregunta para que incluya el contexto del autoseguro y asistente pueda comprender y responder adecuadamente la pregunta del usuario sin tener acceso al historial de la conversación. 

El último mensaje contiene una pregunta: Sí  

Es estrictamente necesario reformular la consulta: Sí  

Reformulación: ¿Cuál es el plazo específico que debo tener en cuenta para generar la orden de pago del autoseguro, y qué pasos debo seguir si no logro hacerlo a tiempo y tengo que matricularme como rezagado?


Ejemplo 2 (Reformulacion no es necesaria)

Último mensaje del usuario: ¿Cómo puedo hacer la solicitud de la constancia de notas? ¿Y caunto tiempo tarda el tramite?

Historial previo de la conversación: <<
user: ¿Qué entidad envía la orden de pago al estudiante después de que este solicita la constancia de notas?
assistant: La orden de pago es enviada al estudiante por la oficina de estadística (AERA) después de que este solicita la constancia de notas.>>

Análisis: La pregunta del usuario en su último mensaje se centra en el proceso para solicitar una constancia de notas y el tiempo de demora del proceso, lo cual es un tema específico y claro. El historial previo de la conversación no incluye información relevante que ayuda mejorar la precision o claridad de la pregunta ya que ya es lo suficiente clara y especifica con el que trata "proceso para solicitar una constancia de notas". Ademas, no es necesario incluir la relación con la facultad de ciencias de manera explicita, ya que no es estrictamente necesario. Por lo tanto, no es necesario reformular la consulta.

El último mensaje contiene una pregunta: Sí  

Es estrictamente necesario reformular la consulta: No  

Reformulación: No aplica

Ejemplo 3 (Mensaje No es una Pregunta)

Último mensaje del usuario: "Gracias por la ayuda."

Historial previo de la conversación: <<
user: ¿Cuanto se puede solicitar el retiro parcial?
assistant: Hasta la quinta semana de clases.

Análisis: El ultimo mensaje del usuario no incluye una consulta por lo que la reformulación no aplica"
El último mensaje contiene una pregunta: Sí  

Es estrictamente necesario reformular la consulta: No aplica  

Reformulación: No aplica


Datos de Entrada

Último mensaje del usuario: {query}

Historial previo de la conversación: <<{history_chat}>>"""
        return prompt_identify_reform

# Esta bueno, eliminar la parte de Evalua si el ultimo mensaje del usuario podría ser ambigua para un asistente que no tiene acceso al historial previo de la conversación

def get_prompt_reformulated_contextual_query_18(query, history_chat_messages):
        history_chat = format_text_history_chat(history_chat_messages)
        prompt_identify_reform = f"""Dado el último mensaje del usuario, dirigido a un asistente especializado en normativas académicas de la Facultad de Ciencias de la Universidad Nacional de Ingeniería (UNI), analiza el historial previo de la conversación junto con la consulta del usuario en su último mensaje y determina si es necesario reformularla para mejorar su precisión y claridad.

El objetivo es que el asistente pueda comprender y responder adecuadamente la pregunta del usuario sin tener acceso al historial de la conversación.

🔎 Paso 1: Análisis de la pregunta sin el historial
Examina el último mensaje del usuario sin considerar el historial previo y analiza los siguientes aspectos:

A. Identificación del tema
Determina si el ultimo mensaje del usuario menciona explícitamente el tema del que trata la consulta, de manera que el asistente pueda responder adecuadamente sin depender del contexto previo.

B. Evaluación de la ambigüedad
Evalua si el ultimo mensaje del usuario podría ser ambigua para un asistente que no tiene acceso al historial previo de la conversación
- Una pregunta es ambigua únicamente si un asistente que solo lee el último mensaje sin el historial previo no puede determinar con certeza de qué trata la consulta porque le falta precisión o contexto. 
- No se considera ambigua solo porque pueda haber información complementaria en el historial.

🔎 Paso 2: Evaluación del historial para mejorar la pregunta
Verifica si el historial de la conversación contiene información relevante que el usuario no haya mencionado explícitamente en su último mensaje, pero que pueda mejorar la claridad y precisión de la consulta. El objetivo es incorporar estos términos o detalles específicos en la reformulación del mensaje para que la consulta sea más clara y pueda ser respondida con precisión, sin depender del historial previo.
- No te limites a buscar información omitida explícitamente, sino también conexiones o términos que puedan mejorar la comprensión y precisión de la respuesta.
- Si el usuario inició la conversación con un tema específico y luego omitió un detalle clave en su última pregunta, evalúa si dicho detalle sigue siendo relevante para garantizar una respuesta precisa.
- Si el historial no contiene detalles específicos que clarifiquen significativamente el ultimo mensaje del usuario, no se debe sugerir una reformulación.
Ejemplo 1: Si el usuario menciona "mesa de partes" en su último mensaje, pero del historial previo se infiere que se refiere a la "mesa de partes de DIRCE", es fundamental incluir esta especificación para mejorar la precisión del tema consultado y permitir una respuesta más exacta sin depender del historial previo.
Ejemplo 2: Si el usuario pregunta por una "orden de pago" en su último mensaje, pero el historial sugiere que se refiere a la "orden de pago para el autoseguro", agregar este detalle mejorará la precisión de la respuesta.
Ejemplo 3: Si el usuario pregunta sobre como generar una "orden de pago" en su último mensaje, pero el historial no contiene información especifica sobre a que concepto esta relacionada, no se debe sugerir agregar ese información ya que no se encuentra dentro del historial previo.

⚠ Importante: No añadas información externa ni hagas suposiciones sobre lo que el usuario podría querer decir. Enfócate solo en si el historial contiene información que ayudaría a mejorar la pregunta.

✅ Paso 3: Decisión sobre la reformulación
Decide si la pregunta necesita ser reformulada con base en los siguientes criterios:
 - Ambigüedad sin el historial: Si la consulta en el último mensaje es completamente ambigua y el historial contiene información relevante para hacerla más clara, entonces la pregunta debe ser reformulada.
 - Precisión del tema: Si el historial contiene detalles que no han sido mencionados explícitamente en el último mensaje y que pueden hacer la pregunta más precisa y facilitar una mejor respuesta, entonces la pregunta debe ser reformulada. El objetivo es que el asistente pueda comprender y responder adecuadamente la pregunta del usuario sin tener acceso al historial de la conversación.
 - Ámbito institucional implícito: Todas las consultas se asumen relacionadas con esta facultad. No reformules la pregunta únicamente para incluir “Facultad de Ciencias de la UNI” a menos que la omisión de esta referencia haga que la pregunta sea completamente ambigua.

Antes de tomar una decisión, proporciona una justificación que explique si es necesario reformular la pregunta. Asegúrate de que tu justificación esté alineada con la evaluación de ambigüedad, la Evaluación de historial previo de la conversación para mejorar la pregunta y los criterios establecidos para determinar si es necesario la reformulación.

✅ Paso 4: Realiza la reformarluacion si es necesario
Reformula la consulta del usuario en su último mensaje solo si lo consideras necesario según los criterios previamente establecidos, garantizando que se mantenga la intención original de la pregunta y sin añadir información no mencionada en la conversación.

Formato de Respuesta Esperado

Responde utilizando el siguiente formato:
Identificacion del Tema: [Explicacion sobre si el ultimo mensaje del usuario menciona explícitamente el tema del que trata la consulta]
Evaluación de la ambigüedad: [Explicacion sobre si la pregunta es ambigua para el asistente si se lee sin el historial previo]
Evaluación del historial para mejorar la pregunta:  [Explicacion sobre si el historial de la conversación contiene información relevante que el usuario no haya mencionado explícitamente en su último mensaje y que podría ayudar a mejorar la claridad y precisión de la consulta]
Análisis: [Explicación detallada sobre por qué es o no necesario reformular la pregunta alineada con las evaluaciones y criterios previamente establecidos].

El último mensaje contiene una pregunta: Sí/No  

Es estrictamente necesario reformular la consulta: Sí/No/No aplica  

Reformulación: <<Pregunta reformulada/No aplica>>

Ejemplos de aplicacion de criterios:

Ejemplo 1 (Reformulacion es necesaria)

Último mensaje del usuario: ¿Sabes si hay algún plazo específico que deba tener en cuenta para la orden de pago?

Historial previo de la conversación: <<
user: ¿Cuáles son las implicaciones de no generar la orden de pago antes de realizar el pago del autoseguro?
assistant: Si no se genera la orden de pago antes de realizar el pago del autoseguro, el estudiante podría enfrentar problemas para matricularse de manera regular. Es fundamental cumplir con el plazo máximo establecido en el calendario de actividades académicas, ya que de no hacerlo, la matrícula podría no habilitarse y el estudiante tendría que gestionar su matrícula como rezagado. Para verificar la situación de la matrícula, se recomienda comprobar si se habilita en las fechas de matrícula regular. Si no es así, es necesario comunicarse con la oficina de estadística (AERA) para obtener más información.>>

Análisis: El último mensaje del usuario aborda la preocupación sobre los plazos para generar la orden de pago. La pregunta sin el historial es clara, sin embargo, la ambigüedad radica en que no se especifica si se refiere a la orden de pago en general o a un contexto particular. En el historial previo de la conversación se puede deducir que la orden de pago es para el autoseguro, este detalle es relevante para hacer la pregunta mas clara y precisa, por lo tanto, sería útil reformular la pregunta para que incluya el contexto del autoseguro y asistente pueda comprender y responder adecuadamente la pregunta del usuario sin tener acceso al historial de la conversación. 

El último mensaje contiene una pregunta: Sí  

Es estrictamente necesario reformular la consulta: Sí  

Reformulación: ¿Cuál es el plazo específico que debo tener en cuenta para generar la orden de pago del autoseguro, y qué pasos debo seguir si no logro hacerlo a tiempo y tengo que matricularme como rezagado?


Ejemplo 2 (Reformulacion no es necesaria)

Último mensaje del usuario: ¿Cómo puedo hacer la solicitud de la constancia de notas? ¿Y caunto tiempo tarda el tramite?

Historial previo de la conversación: <<
user: ¿Qué entidad envía la orden de pago al estudiante después de que este solicita la constancia de notas?
assistant: La orden de pago es enviada al estudiante por la oficina de estadística (AERA) después de que este solicita la constancia de notas.>>

Análisis: La pregunta del usuario en su último mensaje se centra en el proceso para solicitar una constancia de notas y el tiempo de demora del proceso, lo cual es un tema específico y claro. El historial previo de la conversación no incluye información relevante que ayuda mejorar la precision o claridad de la pregunta ya que ya es lo suficiente clara y especifica con el que trata "proceso para solicitar una constancia de notas". Ademas, no es necesario incluir la relación con la facultad de ciencias de manera explicita, ya que no es estrictamente necesario. Por lo tanto, no es necesario reformular la consulta.

El último mensaje contiene una pregunta: Sí  

Es estrictamente necesario reformular la consulta: No  

Reformulación: No aplica

Ejemplo 3 (Mensaje No es una Pregunta)

Último mensaje del usuario: "Gracias por la ayuda."

Historial previo de la conversación: <<
user: ¿Cuanto se puede solicitar el retiro parcial?
assistant: Hasta la quinta semana de clases.

Análisis: El ultimo mensaje del usuario no incluye una consulta por lo que la reformulación no aplica"
El último mensaje contiene una pregunta: Sí  

Es estrictamente necesario reformular la consulta: No aplica  

Reformulación: No aplica

Datos de Entrada

Último mensaje del usuario: {query}

Historial previo de la conversación: <<{history_chat}>>"""
        return prompt_identify_reform

# sin embargo solo con la informacion del ultimo mesnaje no se tiene claro a que solicitud se refiere
# borrar los ejemplos
def get_prompt_reformulated_contextual_query_19(query, history_chat_messages):
        history_chat = format_text_history_chat(history_chat_messages)
        prompt_identify_reform = f"""Dado el último mensaje del usuario, dirigido a un asistente especializado en normativas académicas de la Facultad de Ciencias de la Universidad Nacional de Ingeniería (UNI), analiza el historial previo de la conversación junto con la consulta del usuario en su último mensaje y determina si es necesario reformularla para mejorar su precisión y claridad.

El objetivo es que el asistente pueda comprender y responder adecuadamente la pregunta del usuario sin tener acceso al historial de la conversación.

🔎 Paso 1: Análisis de la pregunta sin el historial
Examina solo el último mensaje del usuario sin considerar el historial previo y analiza los siguientes aspectos:

A. Identificación del tema
Analiza únicamente el último mensaje del usuario sin considerar el historial previo para determinar el tema de la consulta.

B. Evaluación de la ambigüedad
Evalua si la consulta en el ultimo mensaje del usuario podría ser ambigua para un asistente que no tiene acceso al historial previo de la conversación
- Una pregunta es ambigua únicamente si un asistente que solo lee el último mensaje sin el historial previo no puede determinar con certeza de qué trata la consulta porque le falta precisión o contexto. 
- No se considera ambigua solo porque pueda haber información complementaria en el historial.

Ejemplo 1:
Ultimo mensaje del usuario: ¿hay algún formato específico para la solicitud de la constancia?
Identificacion del Tema: El último mensaje del usuario se centra en la consulta sobre si hay un formato específico la solicitud de una constancia, solo con la informacion del ultimo mesnaje no se tiene claro a que solicitud se refiere ya que no se indica explicitamente.
Evaluación de la ambigüedad: La pregunta podria considerarse ambigua ya que no se tiene el contexto de a que constancia se refiere. 

Ejemplo 2:
Ultimo mensaje del usuario: ¿a que correo puedo enviar mi solicitud de constancia de notas?
Identificacion del Tema: El último mensaje del usuario se centra en la consulta sobre a que correo enviar una solicitud para una constancia de notas, se indica explicitamente el tipo de documento relacionada con la consulta por lo que el tema de la consulta es claro sin tener acceso al historial previo.
Evaluación de la ambigüedad: La pregunta en el último mensaje no es ambigua   ya que el usuario está preguntando de manera clara y especifica por lo que el asistente podria responder de manera precisa sin tener acceso al historial previo.

🔎 Paso 2: Evaluación del historial para mejorar la pregunta
Verifica si el historial de la conversación contiene información relevante que el usuario no haya mencionado explícitamente en su último mensaje, pero que pueda mejorar la claridad y precisión de la consulta. El objetivo es incorporar estos términos o detalles específicos en la reformulación del mensaje para que la consulta sea más clara y pueda ser respondida con precisión, sin depender del historial previo.
- No te limites a buscar información omitida explícitamente, sino también conexiones o términos que puedan mejorar la comprensión y precisión de la respuesta.
- Si el usuario inició la conversación con un tema específico y luego omitió un detalle clave en su última pregunta, evalúa si dicho detalle sigue siendo relevante para garantizar una respuesta precisa.
- Si el historial no contiene detalles específicos que clarifiquen significativamente el ultimo mensaje del usuario, no se debe sugerir una reformulación.
Ejemplo 1: Si el usuario menciona "mesa de partes" en su último mensaje, pero del historial previo se infiere que se refiere a la "mesa de partes de DIRCE", es fundamental incluir esta especificación para mejorar la precisión del tema consultado y permitir una respuesta más exacta sin depender del historial previo.
Ejemplo 2: Si el usuario pregunta por una "orden de pago" en su último mensaje, pero el historial sugiere que se refiere a la "orden de pago para el autoseguro", agregar este detalle mejorará la precisión de la respuesta.
Ejemplo 3: Si el usuario pregunta sobre como generar una "orden de pago" en su último mensaje, pero el historial no contiene información especifica sobre a que concepto esta relacionada, no se debe sugerir agregar ese información ya que no se encuentra dentro del historial previo.

⚠ Importante: No añadas información externa ni hagas suposiciones sobre lo que el usuario podría querer decir. Enfócate solo en si el historial contiene información que ayudaría a mejorar la pregunta.

✅ Paso 3: Decisión sobre la reformulación
Decide si la pregunta necesita ser reformulada con base en los siguientes criterios:
 - Ambigüedad sin el historial: Si la consulta en el último mensaje es completamente ambigua y el historial contiene información relevante para hacerla más clara, entonces la pregunta debe ser reformulada.
 - Precisión del tema: Si el historial contiene detalles que no han sido mencionados explícitamente en el último mensaje y que pueden hacer la pregunta más precisa y facilitar una mejor respuesta, entonces la pregunta debe ser reformulada. El objetivo es que el asistente pueda comprender y responder adecuadamente la pregunta del usuario sin tener acceso al historial de la conversación.
 - Ámbito institucional implícito: Todas las consultas se asumen relacionadas con esta facultad. No reformules la pregunta únicamente para incluir “Facultad de Ciencias de la UNI” a menos que la omisión de esta referencia haga que la pregunta sea completamente ambigua.

Antes de tomar una decisión, proporciona una justificación que explique si es necesario reformular la pregunta. Asegúrate de que tu justificación esté alineada con la evaluación de ambigüedad, la Evaluación de historial previo de la conversación para mejorar la pregunta y los criterios establecidos para determinar si es necesario la reformulación.

✅ Paso 4: Realiza la reformarluacion si es necesario
Reformula la consulta del usuario en su último mensaje solo si lo consideras necesario según los criterios previamente establecidos, garantizando que se mantenga la intención original de la pregunta y sin añadir información no mencionada en la conversación.

Formato de Respuesta Esperado

Responde utilizando el siguiente formato:
Identificacion del Tema: [Analisis solo del último mensaje del usuario para determinar el tema de la consulta sin tener acceso al historial previo]
Evaluación de la ambigüedad: [Explicacion sobre si la pregunta es ambigua para el asistente si se lee sin el historial previo]
Evaluación del historial para mejorar la pregunta:  [Explicacion sobre si el historial de la conversación contiene información relevante que el usuario no haya mencionado explícitamente en su último mensaje y que podría ayudar a mejorar la claridad y precisión de la consulta]
Análisis: [Explicación detallada sobre por qué es o no necesario reformular la pregunta alineada con las evaluaciones y criterios previamente establecidos].

El último mensaje contiene una pregunta: Sí/No  

Es estrictamente necesario reformular la consulta: Sí/No/No aplica  

Reformulación: <<Pregunta reformulada/No aplica>>

Ejemplos de aplicacion de criterios:

Ejemplo 1 (Reformulacion es necesaria)

Último mensaje del usuario: ¿Sabes si hay algún plazo específico que deba tener en cuenta para la orden de pago?

Historial previo de la conversación: <<
user: ¿Cuáles son las implicaciones de no generar la orden de pago antes de realizar el pago del autoseguro?
assistant: Si no se genera la orden de pago antes de realizar el pago del autoseguro, el estudiante podría enfrentar problemas para matricularse de manera regular. Es fundamental cumplir con el plazo máximo establecido en el calendario de actividades académicas, ya que de no hacerlo, la matrícula podría no habilitarse y el estudiante tendría que gestionar su matrícula como rezagado. Para verificar la situación de la matrícula, se recomienda comprobar si se habilita en las fechas de matrícula regular. Si no es así, es necesario comunicarse con la oficina de estadística (AERA) para obtener más información.>>

Análisis: El último mensaje del usuario aborda la preocupación sobre los plazos para generar la orden de pago. La pregunta sin el historial es clara, sin embargo, la ambigüedad radica en que no se especifica si se refiere a la orden de pago en general o a un contexto particular. En el historial previo de la conversación se puede deducir que la orden de pago es para el autoseguro, este detalle es relevante para hacer la pregunta mas clara y precisa, por lo tanto, sería útil reformular la pregunta para que incluya el contexto del autoseguro y asistente pueda comprender y responder adecuadamente la pregunta del usuario sin tener acceso al historial de la conversación. 

El último mensaje contiene una pregunta: Sí  

Es estrictamente necesario reformular la consulta: Sí  

Reformulación: ¿Cuál es el plazo específico que debo tener en cuenta para generar la orden de pago del autoseguro, y qué pasos debo seguir si no logro hacerlo a tiempo y tengo que matricularme como rezagado?


Ejemplo 2 (Reformulacion no es necesaria)

Último mensaje del usuario: ¿Cómo puedo hacer la solicitud de la constancia de notas? ¿Y caunto tiempo tarda el tramite?

Historial previo de la conversación: <<
user: ¿Qué entidad envía la orden de pago al estudiante después de que este solicita la constancia de notas?
assistant: La orden de pago es enviada al estudiante por la oficina de estadística (AERA) después de que este solicita la constancia de notas.>>

Análisis: La pregunta del usuario en su último mensaje se centra en el proceso para solicitar una constancia de notas y el tiempo de demora del proceso, lo cual es un tema específico y claro. El historial previo de la conversación no incluye información relevante que ayuda mejorar la precision o claridad de la pregunta ya que ya es lo suficiente clara y especifica con el que trata "proceso para solicitar una constancia de notas". Ademas, no es necesario incluir la relación con la facultad de ciencias de manera explicita, ya que no es estrictamente necesario. Por lo tanto, no es necesario reformular la consulta.

El último mensaje contiene una pregunta: Sí  

Es estrictamente necesario reformular la consulta: No  

Reformulación: No aplica

Ejemplo 3 (Mensaje No es una Pregunta)

Último mensaje del usuario: "Gracias por la ayuda."

Historial previo de la conversación: <<
user: ¿Cuanto se puede solicitar el retiro parcial?
assistant: Hasta la quinta semana de clases.

Análisis: El ultimo mensaje del usuario no incluye una consulta por lo que la reformulación no aplica"
El último mensaje contiene una pregunta: Sí  

Es estrictamente necesario reformular la consulta: No aplica  

Reformulación: No aplica

Datos de Entrada

Último mensaje del usuario: {query}

Historial previo de la conversación: <<{history_chat}>>"""
        return prompt_identify_reform

def get_prompt_reformulated_contextual_query_17_2(query, history_chat_messages):
        history_chat = format_text_history_chat(history_chat_messages)
        prompt_identify_reform = f"""Dado el último mensaje del usuario, dirigido a un asistente especializado en normativas académicas de la Facultad de Ciencias de la Universidad Nacional de Ingeniería (UNI), analiza el historial previo de la conversación junto con la consulta del usuario en su último mensaje y determina si es necesario reformularla para mejorar su precisión y claridad.

El objetivo es que el asistente pueda comprender y responder adecuadamente la pregunta del usuario sin tener acceso al historial de la conversación.

🔎 Paso 1: Análisis de la pregunta sin el historial
Examina el último mensaje del usuario sin considerar el historial previo y analiza los siguientes aspectos:

A. Identificación del tema
Determina si el ultimo mensaje del usuario menciona explícitamente el tema del que trata la consulta, de manera que el asistente pueda responder adecuadamente sin depender del contexto previo.

B. Evaluación de la ambigüedad
Una pregunta es ambigua únicamente si un asistente que solo lee el último mensaje sin el historial previo no puede determinar con certeza de qué trata la consulta.

Ejemplo 1:
Ultimo mensaje del usuario: ¿hay algún formato específico para la solicitud de la constancia?
Identificacion del Tema: El último mensaje del usuario se centra en la consulta sobre si hay un formato específico la solicitud de una constancia, solo con la informacion del ultimo mesnaje no se tiene claro a que solicitud se refiere ya que no se indica explicitamente.
Evaluación de la ambigüedad: La pregunta es algo ambigua si se lee sin el historial previo ya que no se tiene el contexto de a que constancia se refiere. 

Ejemplo 2:
Ultimo mensaje del usuario: ¿a que correo puedo enviar mi solicitud de constancia de notas?
Identificacion del Tema: El último mensaje del usuario se centra en la consulta sobre a que correo enviar una solicitud para una constancia de notas, se indica explicitamente el tipo de documento relacionada con la consulta por lo que el tema de la consulta es claro sin tener acceso al historial previo.
Evaluación de la ambigüedad: La pregunta en el último mensaje no es ambigua  ya que el usuario está preguntando de manera clara y especifica por lo que el asistente podria responder de manera precisa sin tener acceso al historial previo.

🔎 Paso 2: Evaluación del historial para mejorar la pregunta
Verifica si el historial de la conversación contiene información relevante que el usuario no haya mencionado explícitamente en su último mensaje, pero que pueda mejorar la claridad y precisión de la consulta. El objetivo es incorporar estos términos o detalles específicos en la reformulación del mensaje para que la consulta sea más clara y pueda ser respondida con precisión, sin depender del historial previo.
- No solo busques información explícitamente omitida, sino también conexiones o terminos especificos que podrían ser relevantes para una mejor respuesta.
- Si el usuario inició la conversación con un tema específico y luego omitió un detalle clave en su última pregunta, evalúa si ese detalle sigue siendo relevante para garantizar una respuesta precisa.
⚠ Importante: No añadas información externa ni hagas suposiciones sobre lo que el usuario podría querer decir. Enfócate solo en si el historial contiene información que ayudaría a mejorar la pregunta.

✅ Paso 3: Decisión sobre la reformulación
Decide si la pregunta necesita ser reformulada con base en los siguientes criterios:
 - Ambigüedad sin el historial: Si la consulta en el último mensaje es completamente ambigua y el historial contiene información relevante para hacerla más clara, entonces la pregunta debe ser reformulada.
 - Precisión del tema: Si el historial contiene detalles que no han sido mencionados explícitamente en el último mensaje y que pueden hacer la pregunta más precisa y facilitar una mejor respuesta, entonces la pregunta debe ser reformulada. El objetivo es que el asistente pueda comprender y responder adecuadamente la pregunta del usuario sin tener acceso al historial de la conversación.
 - Ámbito institucional implícito: Todas las consultas se asumen relacionadas con esta facultad. No reformules la pregunta únicamente para incluir “Facultad de Ciencias de la UNI” a menos que la omisión de esta referencia haga que la pregunta sea completamente ambigua.

Antes de tomar una decisión, proporciona una breve explicación justificando si es o no necesario reformular la pregunta.

Formato de Respuesta Esperado

Determina si es necesario reformular la consulta con los criterios mencionados anteriormente y responde utilizando el siguiente formato:
Identificacion del Tema: [Explicacion sobre si el ultimo mensaje del usuario menciona explícitamente el tema del que trata la consulta]
Evaluación de la ambigüedad: [Explicacion sobre si la pregunta es ambigua para el asistente si se lee sin el historial previo]
Evaluación del historial para mejorar la pregunta:  [Explicacion sobre si el historial de la conversación contiene información relevante que el usuario no haya mencionado explícitamente en su último mensaje y que podría ayudar a mejorar la claridad y precisión de la consulta]
Análisis: [Explicación detallada sobre por qué es o no necesario reformular la pregunta].

El último mensaje contiene una pregunta: Sí/No  

Es estrictamente necesario reformular la consulta: Sí/No/No aplica  

Reformulación: <<Pregunta reformulada/No aplica>>

Ejemplos de aplicacion de criterios:

Ejemplo 1 (Reformulacion es necesaria)

Último mensaje del usuario: ¿Sabes si hay algún plazo específico que deba tener en cuenta para la orden de pago?

Historial previo de la conversación: <<
user: ¿Cuáles son las implicaciones de no generar la orden de pago antes de realizar el pago del autoseguro?
assistant: Si no se genera la orden de pago antes de realizar el pago del autoseguro, el estudiante podría enfrentar problemas para matricularse de manera regular. Es fundamental cumplir con el plazo máximo establecido en el calendario de actividades académicas, ya que de no hacerlo, la matrícula podría no habilitarse y el estudiante tendría que gestionar su matrícula como rezagado. Para verificar la situación de la matrícula, se recomienda comprobar si se habilita en las fechas de matrícula regular. Si no es así, es necesario comunicarse con la oficina de estadística (AERA) para obtener más información.>>

Análisis: El último mensaje del usuario aborda la preocupación sobre los plazos para generar la orden de pago. La pregunta sin el historial es clara, sin embargo, la ambigüedad radica en que no se especifica si se refiere a la orden de pago en general o a un contexto particular. En el historial previo de la conversación se puede deducir que la orden de pago es para el autoseguro, este detalle es relevante para hacer la pregunta mas clara y precisa, por lo tanto, sería útil reformular la pregunta para que incluya el contexto del autoseguro y asistente pueda comprender y responder adecuadamente la pregunta del usuario sin tener acceso al historial de la conversación. 

El último mensaje contiene una pregunta: Sí  

Es estrictamente necesario reformular la consulta: Sí  

Reformulación: ¿Cuál es el plazo específico que debo tener en cuenta para generar la orden de pago del autoseguro, y qué pasos debo seguir si no logro hacerlo a tiempo y tengo que matricularme como rezagado?


Ejemplo 2 (Reformulacion no es necesaria)

Último mensaje del usuario: ¿Cómo puedo hacer la solicitud de la constancia de notas? ¿Y caunto tiempo tarda el tramite?

Historial previo de la conversación: <<
user: ¿Qué entidad envía la orden de pago al estudiante después de que este solicita la constancia de notas?
assistant: La orden de pago es enviada al estudiante por la oficina de estadística (AERA) después de que este solicita la constancia de notas.>>

Análisis: La pregunta del usuario en su último mensaje se centra en el proceso para solicitar una constancia de notas y el tiempo de demora del proceso, lo cual es un tema específico y claro. El historial previo de la conversación no incluye información relevante que ayuda mejorar la precision o claridad de la pregunta ya que ya es lo suficiente clara y especifica con el que trata "proceso para solicitar una constancia de notas". Ademas, no es necesario incluir la relación con la facultad de ciencias de manera explicita, ya que no es estrictamente necesario. Por lo tanto, no es necesario reformular la consulta.

El último mensaje contiene una pregunta: Sí  

Es estrictamente necesario reformular la consulta: No  

Reformulación: No aplica

Ejemplo 3 (Mensaje No es una Pregunta)

Último mensaje del usuario: "Gracias por la ayuda."

Historial previo de la conversación: <<
user: ¿Cuanto se puede solicitar el retiro parcial?
assistant: Hasta la quinta semana de clases.

Análisis: El ultimo mensaje del usuario no incluye una consulta por lo que la reformulación no aplica"
El último mensaje contiene una pregunta: Sí  

Es estrictamente necesario reformular la consulta: No aplica  

Reformulación: No aplica


Datos de Entrada

Último mensaje del usuario: {query}

Historial previo de la conversación: <<{history_chat}>>"""
        return prompt_identify_reform

# Determina si un asistente que solo lee el último mensaje sin el historial previo no puede determinar con certeza de qué trata la consulta, de manera que el asistente pueda responder adecuadamente sin depender del contexto previo.
#Evaluación de la claridad: [Explicacion sobre si la pregunta es clara o ambigua para el asistente si se lee sin el historial previo]
#Presta especial atención a términos específicos que no han sido mencionados explícitamente en el ultimo mensaje pero si en mensajes anteriores que sean clave para la consulta, como tipos de constancias, solicitudes, carnets, entre otros.
#Antes de determinar que alguna información no se menciona explícitamente en el último mensaje, repite el ultimo mensaje del usuario y analizalo en busqueda de dicha informacion y asegurate que realmente no está especificada de alguna manera. 
# Identifica que imformacion que sea relevante para el identificar el tema de la consulta esta o no esta descrita o especificada de manera explicita en el ultimo mensaje. Presta especial atención a términos específicos que no han sido mencionados explícitamente en el ultimo mensaje pero si en mensajes anteriores que sean clave para la consulta, como tipos de constancias, solicitudes, carnets, entre otros.
# Solo considera informacion relevante que ayude a un asistente que no lee el ultimo mensaje sin acceso al historia de la conversion a responder de una manera adecuado y precisa sin deoender del historial previo.
# Considera si la falta de contexto previo o la posible falta de especificidad en el último mensaje dificultarían la correcta identificación del tema.
# Evalúa si un asistente que solo analiza el último mensaje, sin acceso al historial previo, puede identificar con certeza el mismo tema de consulta que determinaste en el paso anterior y responder de manera adecuada y precisa. 
# Centrate en determinar el ultimo mensaje es lo suficientemente claro para un asistente que no tiene acceso al historial previo.

# - No solo busques información explícitamente omitida, sino también conexiones o terminos especificos que podrían ser relevantes para una mejor respuesta.
#- Si el usuario inició la conversación con un tema específico y luego omitió un detalle clave en su última pregunta, evalúa si ese detalle sigue siendo relevante para garantizar una respuesta precisa.

# ⚠ Importante: No añadas información externa ni hagas suposiciones sobre lo que el usuario podría querer decir. Enfócate solo en si el historial previo de la conversación contiene información que ayudaría a mejorar la pregunta.
#Solo considera información relevante que permita a un asistente, sin acceso al historial de la conversación, entender y responder de manera adecuada y precisa, sin depender de mensajes previos.
#Si la informacion no esta expliciamente descrita en el ultimo mensaje solo indicalo sin hacer 

def get_prompt_reformulated_contextual_query_20(query, history_chat_messages):
        history_chat = format_text_history_chat(history_chat_messages)
        prompt_identify_reform = f"""Dado el último mensaje del usuario, dirigido a un asistente especializado en normativas académicas de la Facultad de Ciencias de la Universidad Nacional de Ingeniería (UNI), analiza el historial previo de la conversación junto con la consulta del usuario en su último mensaje y determina si es necesario reformularla para mejorar su precisión y claridad.

El objetivo es que el asistente pueda comprender y responder adecuadamente la pregunta del usuario sin tener acceso al historial de la conversación.

🔎 Paso 1: Análisis del ultimo mensaje del usuario
Examina el último mensaje del usuario y analiza los siguientes aspectos:
A. Reconocimiento de consulta
Determina si el usuario esta realizando una consulta en su ultimo mensaje. En caso no realize alguna consulta en el resto de los pasos responde con "No aplica".

B. Identificación del tema de consulta
Identifica de que trata la consulta del usuario y describelo de manera concisa.

C. Identificacion de informacion descrita
Determina qué información relevante para identificar el tema de la consulta está presente o ausente en el último mensaje del usuario.
Presta especial atención a términos especificos que no hayan sido mencionados explícitamente en el ultimo mensaje del usuario, pero que sí aparecieron en mensajes anteriores y sean esenciales para la consulta, como tipos de constancias, solicitudes o carnets. Ejemplo: en el ultimo mensaje no se menciona que se refiere al carnert universitario si no solo menciona "carnet" lo cual es relevante para que el asistente sin acceso al historial de la conversación responde de manera precisa.

🔎 Paso 2: Evaluación de claridad del mensaje sin el historial previo 
Alineado con la información que esta expliciamente descrita en el ultimo mensaje, evalua si un asistente puede responder de manera adecuada y precisa a la consulta del usario sin necesidad del historial previo. Se detallado con tu explicacion.

🔎 Paso 3: Evaluación del historial para mejorar la pregunta
Verifica si el historial previo de la conversación contiene información relevante que el usuario no haya mencionado explícitamente en su último mensaje, pero que pueda mejorar la claridad y precisión de la consulta. El objetivo es incorporar estos términos o detalles específicos en la reformulación del mensaje para que la consulta sea más clara y pueda ser respondida con precisión, sin depender del historial previo.
Si el historial previo de la conversación no aporta datos útiles para mejorar la consulta, indícalo sin hacer suposiciones ni sugerencias adicionales. Enfócate solo en si el historial previo de la conversación contiene información que ayudaría a mejorar la pregunta.

✅ Paso 4: Decisión sobre la reformulación
Antes de tomar una decisión, proporciona una explicación justificando si es o no necesario reformular la pregunta, base en los siguientes criterios:
 - Ambigüedad sin el historial: Si la consulta en el último mensaje es completamente ambigua y el historial contiene información relevante para hacerla más clara, entonces la pregunta debe ser reformulada.
 - Precisión del tema: Si el historial contiene detalles que no han sido mencionados explícitamente en el último mensaje y que pueden hacer la pregunta más precisa y facilitar una mejor respuesta, entonces la pregunta debe ser reformulada. El objetivo es que el asistente pueda comprender y responder adecuadamente la pregunta del usuario sin tener acceso al historial de la conversación.
 - Ámbito institucional implícito: Todas las consultas se asumen relacionadas con esta facultad. No reformules la pregunta únicamente para incluir “Facultad de Ciencias de la UNI” a menos que la omisión de esta referencia haga que la pregunta sea completamente ambigua.

Formato de Respuesta Esperado

Determina si es necesario reformular la consulta con los criterios mencionados anteriormente y responde utilizando el siguiente formato:
Identificacion del Tema: [Identifica de que trata la consulta del usuario y describelo de manera concisa.]
Informacion explicitamente descrita el ultimo mensaje: [información explicitimante descrita de alguna forma en el ultimo mensaje del usuario que sea relevante para la identificacion del tema de consulta]
Informacion no descrita el ultimo mensaje: [Información relevante para identificar con precisión el tema de la consulta que no ha sido mencionada explícitamente en el último mensaje del usuario, pero que sí aparece en mensajes anteriores, como el tipo específico de constancia, solicitud o carnet al que se hace referencia] 
Evaluación de la claridad: [Análisis detallado si el ultimo mensaje del usuario en lo suficiente claro para que un asistente pueda responder de manera adecuada y precisa a la consulta del usuario sin necesidad del historial previo].
Evaluación del historial para mejorar la pregunta:  [Explicacion sobre si el historial previo de la conversación contiene información relevante que el usuario no haya mencionado explícitamente en su último mensaje y que podría ayudar a mejorar la claridad y precisión de la consulta]
Análisis: [Explicación detallada sobre por qué es o no estrictamente necesario reformular la pregunta].

El último mensaje contiene una pregunta: Sí/No  

Es estrictamente necesario reformular la consulta: Sí/No/No aplica  

Reformulación: <<Pregunta reformulada/No aplica>>

Ejemplos de aplicacion de criterios:

Ejemplo 1 (Reformulacion es necesaria)

Último mensaje del usuario: ¿Sabes si hay algún plazo específico que deba tener en cuenta para la orden de pago?

Historial previo de la conversación: <<
user: ¿Cuáles son las implicaciones de no generar la orden de pago antes de realizar el pago del autoseguro?
assistant: Si no se genera la orden de pago antes de realizar el pago del autoseguro, el estudiante podría enfrentar problemas para matricularse de manera regular. Es fundamental cumplir con el plazo máximo establecido en el calendario de actividades académicas, ya que de no hacerlo, la matrícula podría no habilitarse y el estudiante tendría que gestionar su matrícula como rezagado. Para verificar la situación de la matrícula, se recomienda comprobar si se habilita en las fechas de matrícula regular. Si no es así, es necesario comunicarse con la oficina de estadística (AERA) para obtener más información.>>

Análisis: El último mensaje del usuario aborda la preocupación sobre los plazos para generar la orden de pago. La pregunta sin el historial es clara, sin embargo, la ambigüedad radica en que no se especifica si se refiere a la orden de pago en general o a un contexto particular. En el historial previo de la conversación se puede deducir que la orden de pago es para el autoseguro, este detalle es relevante para hacer la pregunta mas clara y precisa, por lo tanto, sería útil reformular la pregunta para que incluya el contexto del autoseguro y asistente pueda comprender y responder adecuadamente la pregunta del usuario sin tener acceso al historial de la conversación. 

El último mensaje contiene una pregunta: Sí  

Es estrictamente necesario reformular la consulta: Sí  

Reformulación: ¿Cuál es el plazo específico que debo tener en cuenta para generar la orden de pago del autoseguro, y qué pasos debo seguir si no logro hacerlo a tiempo y tengo que matricularme como rezagado?


Ejemplo 2 (Reformulacion no es necesaria)

Último mensaje del usuario: ¿Cómo puedo hacer la solicitud de la constancia de notas? ¿Y caunto tiempo tarda el tramite?

Historial previo de la conversación: <<
user: ¿Qué entidad envía la orden de pago al estudiante después de que este solicita la constancia de notas?
assistant: La orden de pago es enviada al estudiante por la oficina de estadística (AERA) después de que este solicita la constancia de notas.>>

Análisis: La pregunta del usuario en su último mensaje se centra en el proceso para solicitar una constancia de notas y el tiempo de demora del proceso, lo cual es un tema específico y claro. El historial previo de la conversación no incluye información relevante que ayuda mejorar la precision o claridad de la pregunta ya que ya es lo suficiente clara y especifica con el que trata "proceso para solicitar una constancia de notas". Ademas, no es necesario incluir la relación con la facultad de ciencias de manera explicita, ya que no es estrictamente necesario. Por lo tanto, no es necesario reformular la consulta.

El último mensaje contiene una pregunta: Sí  

Es estrictamente necesario reformular la consulta: No  

Reformulación: No aplica

Ejemplo 3 (Mensaje No es una Pregunta)

Último mensaje del usuario: "Gracias por la ayuda."

Historial previo de la conversación: <<
user: ¿Cuanto se puede solicitar el retiro parcial?
assistant: Hasta la quinta semana de clases.

Análisis: El ultimo mensaje del usuario no incluye una consulta por lo que la reformulación no aplica"
El último mensaje contiene una pregunta: Sí  

Es estrictamente necesario reformular la consulta: No aplica  

Reformulación: No aplica


Datos de Entrada

Último mensaje del usuario: {query}

Historial previo de la conversación: <<{history_chat}>>"""
        return prompt_identify_reform


def get_prompt_reformulated_contextual_query_21(query, history_chat_messages):
        history_chat = format_text_history_chat(history_chat_messages)
        prompt_identify_reform = f"""Dado el último mensaje del usuario, dirigido a un asistente especializado en normativas académicas de la Facultad de Ciencias de la Universidad Nacional de Ingeniería (UNI), analiza el historial previo de la conversación junto con la consulta del usuario en su último mensaje y determina si es necesario reformularla para mejorar su precisión y claridad.

El objetivo es que el asistente pueda comprender y responder adecuadamente la pregunta del usuario sin tener acceso al historial de la conversación.

🔎 Paso 1: Análisis del ultimo mensaje del usuario
Examina el último mensaje del usuario y analiza los siguientes aspectos:
A. Reconocimiento de consulta
Determina si el usuario esta realizando una consulta en su ultimo mensaje. En caso no realize alguna consulta en el resto de los pasos responde con "No aplica".

🔎 Paso 2: Evaluación de claridad del mensaje sin el historial previo 
Alineado con la información que esta expliciamente descrita en el ultimo mensaje, evalua si un asistente puede responder de manera adecuada y precisa a la consulta del usario sin necesidad del historial previo. Se detallado con tu explicacion.

🔎 Paso 3: Evaluación del historial para mejorar la pregunta
Verifica si el historial previo de la conversación contiene información relevante que el usuario no haya mencionado explícitamente en su último mensaje, pero que pueda mejorar la claridad y precisión de la consulta. El objetivo es incorporar estos términos o detalles específicos en la reformulación del mensaje para que la consulta sea más clara y pueda ser respondida con precisión, sin depender del historial previo.
Presta especial atención a términos especificos que no hayan sido mencionados explícitamente en el ultimo mensaje del usuario, pero que sí aparecieron en mensajes anteriores y sean esenciales para la consulta, como tipos de constancias, solicitudes o carnets. Ejemplo: en el ultimo mensaje no se menciona que se refiere al carnert universitario si no solo menciona "carnet" lo cual es relevante para que el asistente sin acceso al historial de la conversación responde de manera precisa.
Si el historial previo de la conversación no aporta datos útiles para mejorar la consulta, indícalo sin hacer suposiciones ni sugerencias adicionales. Enfócate solo en si el historial previo de la conversación contiene información que ayudaría a mejorar la pregunta.

✅ Paso 4: Decisión sobre la reformulación
Antes de tomar una decisión, proporciona una explicación justificando si es o no necesario reformular la pregunta, base en los siguientes criterios:
 - Ambigüedad sin el historial: Si la consulta en el último mensaje es completamente ambigua y el historial contiene información relevante para hacerla más clara, entonces la pregunta debe ser reformulada.
 - Precisión del tema: Si el historial contiene detalles que no han sido mencionados explícitamente en el último mensaje y que pueden hacer la pregunta más precisa y facilitar una mejor respuesta, entonces la pregunta debe ser reformulada. El objetivo es que el asistente pueda comprender y responder adecuadamente la pregunta del usuario sin tener acceso al historial de la conversación.
 - Ámbito institucional implícito: Todas las consultas se asumen relacionadas con esta facultad. No reformules la pregunta únicamente para incluir “Facultad de Ciencias de la UNI” a menos que la omisión de esta referencia haga que la pregunta sea completamente ambigua.

Formato de Respuesta Esperado
El último mensaje contiene una pregunta: Sí/No
Determina si es necesario reformular la consulta con los criterios mencionados anteriormente y responde utilizando el siguiente formato:
Evaluación de la claridad: [Análisis detallado si el ultimo mensaje del usuario en lo suficiente claro para que un asistente pueda responder de manera adecuada y precisa a la consulta del usuario sin necesidad del historial previo].
Evaluación del historial para mejorar la pregunta:  [Explicacion sobre si el historial previo de la conversación contiene información relevante que el usuario no haya mencionado explícitamente en su último mensaje y que podría ayudar a mejorar la claridad y precisión de la consulta]
Análisis: [Explicación detallada sobre por qué es o no estrictamente necesario reformular la pregunta].
Es estrictamente necesario reformular la consulta: Sí/No/No aplica  

Reformulación: <<Pregunta reformulada/No aplica>>

Ejemplos de aplicacion de criterios:

Ejemplo 1 (Reformulacion es necesaria)

Último mensaje del usuario: ¿Sabes si hay algún plazo específico que deba tener en cuenta para la orden de pago?

Historial previo de la conversación: <<
user: ¿Cuáles son las implicaciones de no generar la orden de pago antes de realizar el pago del autoseguro?
assistant: Si no se genera la orden de pago antes de realizar el pago del autoseguro, el estudiante podría enfrentar problemas para matricularse de manera regular. Es fundamental cumplir con el plazo máximo establecido en el calendario de actividades académicas, ya que de no hacerlo, la matrícula podría no habilitarse y el estudiante tendría que gestionar su matrícula como rezagado. Para verificar la situación de la matrícula, se recomienda comprobar si se habilita en las fechas de matrícula regular. Si no es así, es necesario comunicarse con la oficina de estadística (AERA) para obtener más información.>>

Análisis: El último mensaje del usuario aborda la preocupación sobre los plazos para generar la orden de pago. La pregunta sin el historial es clara, sin embargo, la ambigüedad radica en que no se especifica si se refiere a la orden de pago en general o a un contexto particular. En el historial previo de la conversación se puede deducir que la orden de pago es para el autoseguro, este detalle es relevante para hacer la pregunta mas clara y precisa, por lo tanto, sería útil reformular la pregunta para que incluya el contexto del autoseguro y asistente pueda comprender y responder adecuadamente la pregunta del usuario sin tener acceso al historial de la conversación. 

El último mensaje contiene una pregunta: Sí  

Es estrictamente necesario reformular la consulta: Sí  

Reformulación: ¿Cuál es el plazo específico que debo tener en cuenta para generar la orden de pago del autoseguro, y qué pasos debo seguir si no logro hacerlo a tiempo y tengo que matricularme como rezagado?


Ejemplo 2 (Reformulacion no es necesaria)

Último mensaje del usuario: ¿Cómo puedo hacer la solicitud de la constancia de notas? ¿Y caunto tiempo tarda el tramite?

Historial previo de la conversación: <<
user: ¿Qué entidad envía la orden de pago al estudiante después de que este solicita la constancia de notas?
assistant: La orden de pago es enviada al estudiante por la oficina de estadística (AERA) después de que este solicita la constancia de notas.>>

Análisis: La pregunta del usuario en su último mensaje se centra en el proceso para solicitar una constancia de notas y el tiempo de demora del proceso, lo cual es un tema específico y claro. El historial previo de la conversación no incluye información relevante que ayuda mejorar la precision o claridad de la pregunta ya que ya es lo suficiente clara y especifica con el que trata "proceso para solicitar una constancia de notas". Ademas, no es necesario incluir la relación con la facultad de ciencias de manera explicita, ya que no es estrictamente necesario. Por lo tanto, no es necesario reformular la consulta.

El último mensaje contiene una pregunta: Sí  

Es estrictamente necesario reformular la consulta: No  

Reformulación: No aplica

Ejemplo 3 (Mensaje No es una Pregunta)

Último mensaje del usuario: "Gracias por la ayuda."

Historial previo de la conversación: <<
user: ¿Cuanto se puede solicitar el retiro parcial?
assistant: Hasta la quinta semana de clases.

Análisis: El ultimo mensaje del usuario no incluye una consulta por lo que la reformulación no aplica"
El último mensaje contiene una pregunta: Sí  

Es estrictamente necesario reformular la consulta: No aplica  

Reformulación: No aplica


Datos de Entrada

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
#print("train_contextualize_questions_not_need_context:", len(train_contextualize_questions_not_need_context))
count_good_pred = 0

#test_data = train_contextualize_questions_not_need_context[10:20] #+ train_contextualize_questions_need_context[0:10]
#test_data = train_contextualize_questions_not_need_context[150:160] + train_contextualize_questions_not_need_context[200:210]
#save_json("./test/", "not_need_reformulate_demo_test_data_2", test_data)
# 11, 12
test_data = load_json("./test/not_need_reformulate_demo_test_data.json")[11:12]
print("\nlen(test_data):", len(test_data))
print()

for example in test_data[:]:
    history_messages_chat = example["dialog_context"]
    query = example["user_message"]

    prompt = get_prompt_reformulated_contextual_query_20(query, history_messages_chat)
    expected_need_context = not example["need_context"]
    print()
    print("-"*90)
    #print("\n".join(prompt.split("\n")[-2:])) 
    start_input = prompt.find("Datos de Entrada")
    print("\nprompt:\n\n", prompt[start_input:])
    
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
        continue
        
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
        
    time.sleep(10)
print("Exactitud:", count_good_pred / len(test_data))




