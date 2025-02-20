
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

test_data = load_json("./test/need_reformulate_demo_test_data.json")[6:15]
print("\nlen(test_data):", len(test_data))
print()

for example in test_data[:]:
    history_messages_chat = example["dialog_context"]
    query = example["user_message"]

    prompt = get_prompt_reformulated_contextual_query_15(query, history_messages_chat)
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




