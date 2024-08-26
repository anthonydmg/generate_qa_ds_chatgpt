
from utils import get_completion_from_messages
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
            text += f'\n{message["role"]}:{message["content"]}'    
        return text

def extract_need_context(response):
        match = re.search(r"La última pregunta del usuario se entiende sin necesidad del historial del chat:\s*(.*)", response)
        if match:
            resultado = match.group(1).strip().strip(".")
        else:
            resultado = None
        return resultado

def get_prompt_1(history_chat, query):
    prompt = f"""Dado el historial del chat proporcionado entre tres comillas invertidas y la última pregunta del usuario, indica si la ultima pregunta del usuario podría entenderse en su totalidad si no se tiene acceso al historial previo de la conversación. Usa estos criterios:
1. La pregunta no podria entenderse en su totalidad, si es que hace referencia directa a una situación o información específica que solo se proporcionó anteriormente pero no en el ultimo mensaje del usuario, por lo tanto, no es claro a que se refiere sin el historial del la conversación. 
2. La pregunta debería poder entenderse sin el historial si no hace referencia de ningun tipo a información específica proporcionada anteriormente en la conversación.

Ejemplos de mensajes de usuario con preguntas que hacen referencia a una situación o información especifica mencionada anteriormente: 
    - Ejemplo 1:  ¿Y cómo se hace esa solicitud? ¿Hay algún formato específico o solo es un correo al director?
        Esta pregunta hace referencia directa a "esa solicitud" que se refiere a algun proceso mencionado anteriormente pero que no es descrito en el ultimo mensaje del usuario que contiene la pregunta, por lo que, sin esa informacion no es claro a qué tipo de solicitud se refiere el usuario y la pregunta no se entenderia sin ese contexto.
    - Ejemplo 2: ¿Qué requisitos se deben cumplir para ser considerado "estudiante en posibilidad de egresar"?
		Esta pregunta hace referencia a un concepto específico ("estudiante en posibilidad de egresar") que se puede entender sin necesidad de un contexto previo, por lo que la pregunta se puede entenderse por si sola.
    - Ejemplo 3: ¿Qué pasos debo seguir entonces para poder solicitar ese tipo de matricula especial?
        Esta pregunta hace referencia a un "tipo de matricula especial" que ha sido mencionada antes por lo que se requiere esa informacion para entender completamente el contexto de la pregunta. 
    - Ejemplo 4: Entonces, si no estoy en esa situación de "posibilidad de egresar", ¿no puedo matricularme en ambos cursos al mismo tiempo?
        Esta pregunta del usuario no describe los cursos referenciados ni la condicion especial para matricularse en ellos, por lo tanto, la pregunta no se entenderia totalmente sin el hisorial del chat.
    - Ejemplo 5: ¿Qué sucede si un estudiante no cumple con el requisito de ser "estudiante en posibilidad de egresar" pero necesita matricularse en un curso y su prerequisito simultáneamente por motivos académicos o personales?
        Esta pregunta del usuario hace referencia a la situación de un estudiante que no cumple con el requisito de ser "estudiante en posibilidad de egresar" pero necesita matricularse en un curso y su prerequisito simultáneamente, sin embargo, esta situacion es descrita lo suficiente para ser entendible el ultimo mensaje del usuario, por lo tanto, la pregunta es entendible.
    - Ejemplo 6: Y si no puedo conseguir el certificado a tiempo?
        Esta pregunta hace referencia a la situacion de obtener de un certificado a tiempo, pero no se decribe en el ultimo mensaje del usuario que tipo de certificado ni la finalidad de el, por lo que, sin esa informacion no es claro a qué tipo de certificado se refiere el usuario y la pregunta no se entenderia sin el contexto previo de la conversacion. 

Ejemplos de mensajes de usuario con preguntas que no hacen referencia directa a una situación o información especifica mencionada anteriormente: 
    - Ejemplo 1: ¿Qué debo hacer si quiero inscribirme en un curso y su prerequisito en el mismo ciclo?
        Esta pregunta no hace referencia directa a ningun concepto o situacion especifica, ademas, la pregunta en entendible por si sola.

Proporciona una justificación detallada e indica si la pregunta se entiende sin necesidad del historial del chat de la siguiente manera:

Justificación: ...

La última pregunta del usuario se entiende sin necesidad del historial del chat: Sí o No

Historial del chat: {history_chat}

Último mensaje del usuario: {query}"""
    return prompt

def get_prompt_2(history_chat, query):
    prompt = f"""Dado el historial del chat proporcionado entre tres comillas invertidas y la última pregunta del usuario, analiza e indica si la ultima pregunta del usuario podría entender total por si sola, sin necesidad de tener acceso a tiene acceso al historial previo de la conversación. Has tu análisis basándote en los siguientes criterios y ejemplos:
Criterios:
1. La pregunta no podría entenderse en su totalidad, si es que hace referencia directa a una situación o información específica que solo se proporcionó anteriormente pero no en el ultimo mensaje del usuario, por lo tanto, no es claro a que se refiere sin el historial del la conversacion. 
2. La pregunta debería poder entenderse sin el historial si no hace referencia de ningún tipo a información específica proporcionada anteriormente en la conversación.

Ejemplos de mensajes de usuario con preguntas que hacen referencia a una situación o información especifica mencionada anteriormente: 
    - Ejemplo 1:  ¿Y cómo se hace esa solicitud? ¿Hay algún formato específico o solo es un correo al director?
        Análisis: Esta pregunta hace referencia directa a "esa solicitud" que se refiere a algún proceso mencionado anteriormente pero que no es descrito en el ultimo mensaje del usuario que contiene la pregunta, por lo que, sin esa informacion no es claro a qué tipo de solicitud se refiere el usuario y la pregunta no se entenderia sin ese contexto.
    - Ejemplo 2: Y si no puedo conseguir el certificado a tiempo?
        Análisis: Esta pregunta hace referencia a la situación de obtener de un certificado a tiempo, pero no se describe en el ultimo mensaje del usuario que tipo de certificado ni la finalidad de el, por lo que, sin esa información no es claro a qué tipo de certificado se refiere el usuario en la pregunta. Esta pregunta no se entenderia sin el contexto previo de la conversación. 
    - Ejemplo 3: ¿Qué requisitos se deben cumplir para ser considerado "estudiante en posibilidad de egresar"?
		Análisis: Esta pregunta hace referencia a un concepto específico ("estudiante en posibilidad de egresar") que se puede entender sin necesidad de un contexto previo, por lo que la pregunta se puede entenderse por si sola.
    - Ejemplo 4: ¿Qué pasos debo seguir entonces para poder solicitar ese tipo de matricula especial?
        Análisis: Esta pregunta hace referencia a un "tipo de matricula especial" que ha sido mencionada antes por lo que se requiere esa información para entender completamente el contexto de la pregunta. 
    - Ejemplo 5: Entonces, si no estoy en esa situación de "posibilidad de egresar", ¿no puedo matricularme en ambos cursos al mismo tiempo?
        Análisis: Esta pregunta del usuario no describe los cursos referenciados ni la condicion especial para matricularse en ellos, por lo tanto, la pregunta no se entenderia totalmente sin el hisorial del chat.
    - Ejemplo 6: ¿Qué sucede si un estudiante no cumple con el requisito de ser "estudiante en posibilidad de egresar" pero necesita matricularse en un curso y su prerequisito simultáneamente por motivos académicos o personales?
        Análisis: Esta pregunta del usuario hace referencia a la situación de un estudiante que no cumple con el requisito de ser "estudiante en posibilidad de egresar" pero necesita matricularse en un curso y su prerequisito simultáneamente, sin embargo, esta situacion es descrita lo suficiente para ser entendible el ultimo mensaje del usuario, por lo tanto, la pregunta es entendible.
    
Ejemplos de mensajes de usuario con preguntas que no hacen referencia directa a una situación o información especifica mencionada anteriormente: 
    - Ejemplo 1: ¿Qué debo hacer si quiero inscribirme en un curso y su prerequisito en el mismo ciclo?
        Análisis: Esta pregunta no hace referencia directa a ningún concepto o situación especifica, ademas, la pregunta en entendible por si sola.

Proporciona el análisis detallada e indica si la ultima pregunta del usuario se entiende sin necesidad del historial del chat de la siguiente manera:

Análisis: ...

La última pregunta del usuario se entiende sin necesidad del historial del chat: Sí o No

Historial del chat: {history_chat}

Último mensaje del usuario: {query}"""
    return prompt



def get_prompt_3(history_chat, query):
    prompt = f"""Dado el último mensaje del usuario, analiza e indica si la ultima pregunta del usuario podría entender total por si sola, sin necesidad de tener acceso a tiene acceso al historial previo de la conversación. Has tu análisis basándote en los siguientes criterios y ejemplos:
Criterios:
1. La pregunta no podría entenderse en su totalidad, si es que hace referencia directa o implícita a una situación o información específica que solo se proporcionó anteriormente pero no en el ultimo mensaje del usuario, por lo tanto, no es claro a que se refiere sin el historial del la conversacion. 
2. La pregunta debería poder entenderse sin el historial si no hace referencia de ningún tipo a información específica proporcionada anteriormente en la conversación.

Ejemplos de mensajes de usuario con preguntas que hacen referencia a una situación o información especifica mencionada anteriormente: 
    - Ejemplo 1:  ¿Y cómo se hace esa solicitud? ¿Hay algún formato específico o solo es un correo al director?
        Análisis: Esta pregunta hace referencia directa a "esa solicitud" que se refiere a algún proceso mencionado anteriormente pero que no es descrito en el ultimo mensaje del usuario que contiene la pregunta, por lo que, sin esa información no es claro a qué tipo de solicitud se refiere el usuario y la pregunta no se entenderia sin ese contexto.
    - Ejemplo 2: Y si no puedo conseguir el certificado a tiempo?
        Análisis: Esta pregunta hace referencia a la situación de obtener de un certificado a tiempo, pero no se describe en el ultimo mensaje del usuario que tipo de certificado ni la finalidad de el, por lo que, sin esa información no es claro a qué tipo de certificado se refiere el usuario en la pregunta. Por todo esto, no seria posible entender la pregunta por si sola.    
    - Ejemplo 3: ¿Qué pasos debo seguir entonces para poder solicitar ese tipo de matricula especial?
        Análisis: Esta pregunta del usuario hace referencia a una "matrícula especial" sin especificar a qué se refiere exactamente con ese término. Por lo tanto, el concepto de "solicitar una matrícula especial" no es lo suficientemente claro y genérico como para ser entendido sin necesidad de información adicional del historial de la conversación. Por todo esto, la pregunta no podría entenderse en su totalidad por si sola.   
    - Ejemplo 4: Entonces, si no estoy en esa situación de "posibilidad de egresar", ¿no puedo matricularme en ambos cursos al mismo tiempo?
        Análisis: La pregunta del usuario hace referencia a la situación de no estar en "posibilidad de egresar" y cuestiona si es posible matricularse en ambos cursos al mismo tiempo. Aunque se menciona el concepto de "posibilidad de egresar", este término es lo suficientemente claro y genérico como para ser entendido sin necesidad de información adicional del historial de la conversación. Sin embargo, esta pregunta del usuario no describe los cursos referenciados ni la condición especial para matricularse en ellos, por lo tanto, no es posible entender totalmente la pregunta sin el historial previo del chat.
    - Ejemplo 5: Si soy un alumno en "posibilidad de egresar", entonces ¿puedo matricularme la matriculas en los dos cursos?
        Análisis: La pregunta del usuario hace referencia a la situación de no estar en "posibilidad de egresar" y cuestiona si es posible matricularse en ambos cursos al mismo tiempo. Aunque se menciona el concepto de "posibilidad de egresar", este término es lo suficientemente claro y genérico como para ser entendido sin necesidad de información adicional del historial de la conversación. Sin embargo, esta pregunta del usuario no describe los dos cursos referenciados ni la condición especial para matricularse en ellos, por lo tanto, no es posible entender totalmente la pregunta sin el historial previo del chat.
    - Ejemplo 6: ¿Qué requisitos se deben cumplir para ser considerado "estudiante en posibilidad de egresar"?
		Análisis: Esta pregunta hace referencia a un concepto específico ("estudiante en posibilidad de egresar") que se puede entender sin necesidad de un contexto previo, por lo que la pregunta se puede entenderse por si sola.
    - Ejemplo 7: ¿Qué sucede si un estudiante no cumple con el requisito de ser "estudiante en posibilidad de egresar" pero necesita matricularse en un curso y su prerequisito simultáneamente por motivos académicos o personales?
        Análisis: Esta pregunta del usuario hace referencia a la situación de un estudiante que no cumple con el requisito de ser "estudiante en posibilidad de egresar" pero necesita matricularse en un curso y su prerequisito simultáneamente, sin embargo, esta situación es descrita lo suficiente para ser entendible el ultimo mensaje del usuario, por lo tanto, la pregunta es entendible.
    - Ejemplo 8: ¿Y dónde encuentro el formulario de solicitud en la intranet?
       Análisis: Esta pregunta del usuario hace una referencia implícita a un formulario de solicitud específico, pero en el mensaje no se describe para que tipo solicitud por lo que no es posible entender la pregunta por si sola.
    - Ejemplo 9: Entiendo, ¿Y como obtengo a un modelo para realizar la solicitud?
       Análisis: Esta pregunta del usuario hace una referencia implícita a un modelo de solicitud específico, pero en el mensaje no se describe para que tipo solicitud por lo que no es posible entender la pregunta por si sola.
    - Ejemplo 10: ¡Genial! Entonces, si soy un "estudiante en posibilidad de egresar" con menos de 30 créditos pendientes, puedo matricularme en un curso y su prerequisito en el mismo ciclo. ¿Debo comunicarme con mi escuela profesional para solicitar la aprobación del director correspondiente, verdad?
       Análisis: Esta pregunta del usuario hace referencia a la situación de ser un "estudiante en posibilidad de egresar" con menos de 30 créditos pendientes y la posibilidad de matricularse en un curso y su prerequisito en el mismo ciclo lo cual se entiende sin necesidad de mayor contexto. Por otro lado, la pregunta también menciona la necesidad de comunicarse con la escuela profesional para solicitar la aprobación del director correspondiente, lo cual es entendible por si solo y no se require mayor contexto para que sea entendible. Por lo tanto, la pregunta se entiende en su totalidad sin el historial del chat.
    - Ejemplo 11: ¿Y si no tengo el certificado del Centro Médico de la UNI, puedo usar uno de una clínica privada?
       Análisis: Esta pregunta del usuario hace referencia a la posibilidad de utilizar un certificado de una clínica privada en lugar del certificado del Centro Médico de la UNI. Sin embargo, no se especifica para que o en que contexto se desea usar el certificado medica por lo que no esto no quedaría claro en la pregunta. Por todo esto, no seria posible entender la pregunta por si sola.
    - Ejemplo 12: ¿Y si no es por enfermedad grave?
       Análisis: Esta pregunta del usuario hace una referencia a un escenario hipotético en el que se cuestiona sobre una situación diferente a la enfermedad grave pero no se especifica en que contexto o en que situación especifica se daría este escenario hipotético, por lo que, la pregunta necesita del contexto previo para que sea entendible 
    - Ejemplo 13: ¿Hay algún número de teléfono para contactarlos directamente?
       Análisis: Esta pregunta del usuario hace una referencia implícita a un grupo o entidad que se desea contactar, en este caso, a "ellos", sin embargo, no especifica a quien se refiere con "ellos". Sin ese contexto adicional, no se puede identificar a quién se refiere la pregunta. Por todo esto, no seria posible entender la pregunta por si sola.
    
Ejemplos de mensajes de usuario con preguntas que no hacen referencia a una situación o información especifica mencionada anteriormente: 
    - Ejemplo 1: ¿Qué debo hacer si quiero inscribirme en un curso y su prerequisito en el mismo ciclo?
        Análisis: Esta pregunta no hace referencia a ningún concepto o situación especifica, ademas, la pregunta en entendible por si sola.

Proporciona un análisis detallada e indica si la ultima pregunta del usuario se entiende sin necesidad del historial del chat de la siguiente manera:

Análisis: ...

La última pregunta del usuario se entiende sin necesidad del historial del chat: Sí o No

Último mensaje del usuario: {query}"""
    return prompt

""" - Ejemplo 14: ¿Cuánto demora en estar lista la constancia después de enviar el comprobante de pago?
       Análisis: Esta pregunta del usuario hace una referencia implícita un constancia, sin embargo, no se especifica a que tipo de constancia se refiero por que se necesita ese contexto previo para entender la pregunta. Por todo esto, no seria posible entender la pregunta por si sola.
    - Ejemplo 15: ¿Sabes si hay alguna correcto de contacto disponible para escribiles?
        Análisis: Esta pregunta del usuario hace una referencia implícita a un grupo o entidad que se desea contactar por correo, en este caso, a "ellos", sin embargo, no especifica a quien se refiere con "ellos". Sin ese contexto adicional, no se puede identificar a quién se refiere la pregunta. Por todo esto, no seria posible entender la pregunta por si sola.
    - Ejemplo 16: ¿Estoy necesitando la constancia con urgencia, hay alguna manera de acelerar el proceso?
        Análisis: La pregunta del usuario hace referencia a la necesidad de obtener una constancia con urgencia y pregunta si hay alguna manera de acelerar el proceso. Sin embargo, no se menciona que tipo de constancia se esta solicituado por lo que no es lo suficientemente claro y genérico como para ser entendido sin necesidad de información adicional del historial de la conversación. Por lo tanto, la pregunta no se entiende en su totalidad sin el historial del chat.
    - Ejemplo 17: Perfecto, gracias por la info. ¿Me puede decir si hay algún formato específico para la solicitud de la constancia o solo basta con escribir un correo con mis datos?
        Análisis: La última pregunta del usuario hace referencia a la solicitud de una constancia y cuestiona si es necesario completar un formato específico o si simplemente enviar un correo con los datos es suficiente. Sin embargo, no se menciona que tipo de constancia se esta solicituado por lo que no es lo suficientemente claro y genérico como para ser entendido sin necesidad de información adicional del historial de la conversación. Por todo esto, no seria posible entender la pregunta por si sola.
 """
"""- Ejemplo 2: Y si no puedo conseguir el certificado a tiempo?
        Análisis: Esta pregunta hace referencia a la situación de obtener de un certificado a tiempo, pero no se describe en el ultimo mensaje del usuario que tipo de certificado ni la finalidad de el, por lo que, sin esa información no es claro a qué tipo de certificado se refiere el usuario en la pregunta. Por todo esto, no seria posible entender la pregunta por si sola.    
    - Ejemplo 3: ¿Qué pasos debo seguir entonces para poder solicitar ese tipo de matricula especial?
        Análisis: Esta pregunta del usuario hace referencia a una "matrícula especial" sin especificar a qué se refiere exactamente con ese término. Por lo tanto, el concepto de "solicitar una matrícula especial" no es lo suficientemente claro y genérico como para ser entendido sin necesidad de información adicional del historial de la conversación. Por todo esto, la pregunta no podría entenderse en su totalidad por si sola.   
    - Ejemplo 4: Entonces, si no estoy en esa situación de "posibilidad de egresar", ¿no puedo matricularme en ambos cursos al mismo tiempo?
        Análisis: La pregunta del usuario hace referencia a la situación de no estar en "posibilidad de egresar" y cuestiona si es posible matricularse en ambos cursos al mismo tiempo. Aunque se menciona el concepto de "posibilidad de egresar", este término es lo suficientemente claro y genérico como para ser entendido sin necesidad de información adicional del historial de la conversación. Sin embargo, esta pregunta del usuario no describe los cursos referenciados ni la condición especial para matricularse en ellos, por lo tanto, no es posible entender totalmente la pregunta sin el historial previo del chat.
    - Ejemplo 5: Si soy un alumno en "posibilidad de egresar", entonces ¿puedo matricularme la matriculas en los dos cursos?
        Análisis: La pregunta del usuario hace referencia a la situación de no estar en "posibilidad de egresar" y cuestiona si es posible matricularse en ambos cursos al mismo tiempo. Aunque se menciona el concepto de "posibilidad de egresar", este término es lo suficientemente claro y genérico como para ser entendido sin necesidad de información adicional del historial de la conversación. Sin embargo, esta pregunta del usuario no describe los dos cursos referenciados ni la condición especial para matricularse en ellos, por lo tanto, no es posible entender totalmente la pregunta sin el historial previo del chat.
    - Ejemplo 6: ¿Qué requisitos se deben cumplir para ser considerado "estudiante en posibilidad de egresar"?
		Análisis: Esta pregunta hace referencia a un concepto específico ("estudiante en posibilidad de egresar") que se puede entender sin necesidad de un contexto previo, por lo que la pregunta se puede entenderse por si sola.
    - Ejemplo 7: ¿Qué sucede si un estudiante no cumple con el requisito de ser "estudiante en posibilidad de egresar" pero necesita matricularse en un curso y su prerequisito simultáneamente por motivos académicos o personales?
        Análisis: Esta pregunta del usuario hace referencia a la situación de un estudiante que no cumple con el requisito de ser "estudiante en posibilidad de egresar" pero necesita matricularse en un curso y su prerequisito simultáneamente, sin embargo, esta situación es descrita lo suficiente para ser entendible el ultimo mensaje del usuario, por lo tanto, la pregunta es entendible.
    - Ejemplo 8: ¿Y dónde encuentro el formulario de solicitud en la intranet?
       Análisis: Esta pregunta del usuario hace una referencia implícita a un formulario de solicitud específico, pero en el mensaje no se describe para que tipo solicitud por lo que no es posible entender la pregunta por si sola.
    - Ejemplo 9: Entiendo, ¿Y como obtengo a un modelo para realizar la solicitud?
       Análisis: Esta pregunta del usuario hace una referencia implícita a un modelo de solicitud específico, pero en el mensaje no se describe para que tipo solicitud por lo que no es posible entender la pregunta por si sola.
    - Ejemplo 11: ¿Y si no tengo el certificado del Centro Médico de la UNI, puedo usar uno de una clínica privada?
       Análisis: Esta pregunta del usuario hace referencia a la posibilidad de utilizar un certificado de una clínica privada en lugar del certificado del Centro Médico de la UNI. Sin embargo, no se especifica para que o en que contexto se desea usar el certificado medica por lo que no esto no quedaría claro en la pregunta. Por todo esto, no seria posible entender la pregunta por si sola.
    - Ejemplo 12: ¿Y si no es por enfermedad grave?
       Análisis: Esta pregunta del usuario hace una referencia a un escenario hipotético en el que se cuestiona sobre una situación diferente a la enfermedad grave pero no se especifica en que contexto o en que situación especifica se daría este escenario hipotético, por lo que, la pregunta necesita del contexto previo para que sea entendible 
    - Ejemplo 13: ¿Hay algún número de teléfono para contactarlos directamente?
       Análisis: Esta pregunta del usuario hace una referencia implícita a un grupo o entidad que se desea contactar, en este caso, a "ellos", sin embargo, no especifica a quien se refiere con "ellos". Sin ese contexto adicional, no se puede identificar a quién se refiere la pregunta. Por todo esto, no seria posible entender la pregunta por si sola.
    - Ejemplo 14: ¿Cuánto demora en estar lista la constancia después de enviar el comprobante de pago?
       Análisis: Esta pregunta del usuario hace una a la tiempo para tener para obtener una constancia después de enviar el comprobante de pago. Sin embargo, no se menciona que tipo de constancia se esta solicituado por lo que no es lo suficientemente claro y genérico como para ser entendido sin necesidad de información adicional del historial de la conversación. Por lo tanto, la pregunta no se entiende en su totalidad sin el historial del chat.
    - Ejemplo 15: ¿Sabes si hay alguna correcto de contacto disponible para escribirles?
        Análisis: Esta pregunta del usuario hace una referencia implícita a un grupo o entidad que se desea contactar por correo, en este caso, a "ellos", sin embargo, no especifica a quien se refiere con "ellos". Sin ese contexto adicional, no se puede identificar a quién se refiere la pregunta. Por todo esto, no seria posible entender la pregunta por si sola.
    - Ejemplo 16: Necesito la constancia rápido ¿hay alguna manera de acelerar el proceso?
        Análisis: La pregunta del usuario hace referencia a la necesidad de obtener una constancia con urgencia y pregunta si hay alguna manera de acelerar el proceso. Sin embargo, no se menciona que tipo de constancia se esta solicituado por lo que no es lo suficientemente claro y genérico como para ser entendido sin necesidad de información adicional del historial de la conversación. Por lo tanto, la pregunta no se entiende en su totalidad sin el historial del chat.
"""

def get_prompt_5(history_chat, query):
    prompt = f"""Dado el último mensaje del usuario, analiza e indica si la ultima pregunta del usuario podría entender total por si sola, sin necesidad de tener acceso a tiene acceso al historial previo de la conversación. Has tu análisis basándote en los siguientes criterios y ejemplos:
Criterios:
1. La pregunta no podría entenderse en su totalidad, si es que hace referencia directa o implícita a una situación o información específica que solo se proporcionó anteriormente pero no en el ultimo mensaje del usuario, por lo tanto, no es claro a que se refiere sin el historial del la conversación. 
2. La pregunta no podría entenderse, si es que no tiene un sentido completo sin el contexto previo.

Ejemplos de mensajes de usuario con preguntas que hacen referencia a una situación o información especifica mencionada anteriormente: 
    - Ejemplo 1: ¿Y cómo se hace esa solicitud? ¿Hay algún formato específico o solo es un correo al director?
        Análisis: Esta pregunta hace referencia directa a "esa solicitud" que se refiere a algún proceso mencionado anteriormente pero que no es descrito en el ultimo mensaje del usuario que contiene la pregunta. Sin esa información no es claro a qué tipo de solicitud se refiere el usuario por lo tanto la pregunta no sea entendible sin ese contexto.
        La última pregunta del usuario se entiende sin necesidad del historial del chat: No
    - Ejemplo 2: ¿Y cómo puedo conseguir el certificado?
        Análisis: Esta pregunta hace referencia implícita a un certificado, pero no se especifica cuál. Sin ese contexto previo, esta referencia no es clara, por lo tanto, la pregunta no es entendible por si sola.
        La última pregunta del usuario se entiende sin necesidad del historial del chat: No
    - Ejemplo 3: ¿Sabes si hay alguna correo de contacto disponible para escribirles?
        Análisis: Esta pregunta del usuario hace una referencia implícita a un grupo o entidad que se desea contactar por correo, en este caso, a "ellos", sin embargo, no especifica a quien se refiere con "ellos". Sin ese contexto adicional, no se puede identificar a quién se refiere la pregunta. Por todo esto, no seria posible entender la pregunta por si sola.
        La última pregunta del usuario se entiende sin necesidad del historial del chat: No
    - Ejemplo 4: Si no cumplo con el requisito de ser "estudiante en posibilidad de egresar" pero necesito matricularse en un curso y su prerequisito al mismo tiempo, ¿Que puedo hacer?
        Análisis: Esta pregunta hace referencia a una situación específica donde un estudiante no cumple con un requisito pero necesita matricularse en un curso y su prerequisito simultáneamente. A pesar de no especificar el curso la pregunta es clara ya que la consulta se hace en forma general independientemente del curso en cuestión,por otra lado, la expresión "estudiante en posibilidad de egresar" es suficiente clara ni necesidad de contexto. Por todo esto, es posible entender la pregunta por si sola.
        La última pregunta del usuario se entiende sin necesidad del historial del chat: Sí
    - Ejemplo 5: Y si no el certificado, no puedo realizar la solicitud?
        Análisis: Esta pregunta hace referencia implícita a un certificado y a una solicitud, pero no se especifica cuál cual certificado ni para que solicitud. Sin ese contexto previo, esta referencia no es clara, por lo tanto, la pregunta no es entendible por si sola.
        La última pregunta del usuario se entiende sin necesidad del historial del chat: No
    - Ejemplo 6: Cuanto tiempo tardaran en darme, la constancia?
        Análisis: Esta pregunta hace referencia implícita a una constancia, pero no se especifica cual constancia. En este caso esta información es necesaria ya que la pregunta es especifica hacia un tipo de constancia pero no se menciona a cual. Por lo tanto, la pregunta no es entendible por si sola.
        La última pregunta del usuario se entiende sin necesidad del historial del chat: No
    - Ejemplo 7: ¿Hay alguna manera de acelerar el tramite, para que me den mi constancia cuanto antes?
        Análisis: Esta pregunta hace referencia a un tramite y a una constancia pero no se especifica cuál cual constancia ni ha que tramite se refiere. En este caso esta información es necesaria ya que la pregunta es especifica hacia un tipo de constancia pero no se menciona a cual, por lo que, la pregunta no se entenderia sin ese contexto.
        La última pregunta del usuario se entiende sin necesidad del historial del chat: No
    - Ejemplo 8: ¿También podría usar el certificado medico, de una clínica privada?
        Análisis: La pregunta puede resultar confusa porque no especifica claramente el contexto ni el propósito del certificado del Centro Médico de la UNI ni por qué se considera usar uno de una clínica privada como alternativa. 
        La última pregunta del usuario se entiende sin necesidad del historial del chat: No

Ejemplos de mensajes de usuario que no tiene sentido sin el contexto previo:
    - Ejemplo 1: ¿En caso no sea por enfermedad de gravedad?
       Análisis: Esta pregunta plantea una situación donde no es un enfermada de gravedad, pero, sin el contexto previo dicha pregunta es bastante ambigua y depende de un contexto anterior par tener sentido. Por lo tanto, la pregunta no es entendible por si sola
       La última pregunta del usuario se entiende sin necesidad del historial del chat: No

Realiza el análisis de manera minuciosa basándote en los criterios y ejemplos anteriores e indica de la misma manera que en dichos ejemplos si es que la ultima pregunta del usuario proporcionada se entiende sin necesidad del historial 
Último mensaje del usuario: {query}"""
    
    return prompt

def get_prompt_6(history_chat, query):
    prompt = f"""Dado el último mensaje del usuario, analiza e indica si la ultima pregunta del usuario podría entender total por si sola, sin necesidad de tener acceso a tiene acceso al historial previo de la conversación. Has tu análisis basándote en los siguientes criterios y ejemplos:
Criterios:
1. La pregunta no podría entenderse en su totalidad, si es que hace referencia directa o implícita a una situación o información específica que solo se proporcionó anteriormente pero no en el ultimo mensaje del usuario, por lo tanto, no es claro a que se refiere sin el historial del la conversación. 
2. La pregunta no podría entenderse, si es que no tiene un sentido completo sin el contexto previo.

Ejemplos de mensajes de usuario con preguntas que hacen referencia a una situación o información especifica mencionada anteriormente: 
    - Ejemplo 1: ¿Y cómo se hace esa solicitud? ¿Hay algún formato específico o solo es un correo al director?
        Análisis: Esta pregunta hace referencia directa a "esa solicitud" que se refiere a algún proceso mencionado anteriormente pero que no es descrito en el ultimo mensaje del usuario que contiene la pregunta. Sin esa información no es claro a qué tipo de solicitud se refiere el usuario por lo tanto la pregunta no sea entendible sin ese contexto.
        La última pregunta del usuario se entiende sin necesidad del historial del chat: No
    
Ejemplos de mensajes de usuario que no tiene sentido sin el contexto previo:
    - Ejemplo 1: ¿En caso no sea por enfermedad de gravedad?
       Análisis: Esta pregunta plantea una situación donde no es un enfermada de gravedad, pero, sin el contexto previo dicha pregunta es bastante ambigua y depende de un contexto anterior par tener sentido. Por lo tanto, la pregunta no es entendible por si sola
       La última pregunta del usuario se entiende sin necesidad del historial del chat: No

Realiza el análisis de manera minuciosa basándote en los criterios y ejemplos anteriores e indica de la misma manera que en dichos ejemplos si es que la ultima pregunta del usuario proporcionada se entiende sin necesidad del historial 
Último mensaje del usuario: {query}"""
    
    return prompt

def get_prompt_7(history_chat, query):
    prompt = f"""Dado el último mensaje del usuario dado en el contexto de Facultad de Ciencias de La Universidad Nacional de Ingeniería de Peru enviado a un asistente familiarizado con las normativas académicas de la universidad, analiza e indica si la ultima pregunta del usuario podría entender total por si sola, sin necesidad de tener acceso a tiene acceso al historial previo de la conversación. Has tu análisis para identificar si la pregunta es entendible basándote en los siguientes criterios:

Criterios:
1. Contexto Suficiente: Debe de haber suficiente contexto en el mensaje para entender a que se refiere la pregunta.
2. Claridad: La pregunta debe ser clara con respecto al tema que trata o a quien se refiere.
3. Especificidad: El mensaje con la pregunta debe ser lo suficiente especifico para que se pueda responder de manera correcta.

Ejemplos:
- Ejemplo 1: ¿También podría usar el certificado medico, de una clínica privada?
        - Análisis: La pregunta del usuario se refiere a la posibilidad de utilizar un certificado médico de una clínica privada en lugar de uno específico del Centro Médico de la UNI. Sin embargo, no se proporciona contexto adicional sobre el propósito del certificado, lo que es relevante para entender completamente la pregunta. La pregunta es clara en su formulación y se entiende que el usuario está buscando una alternativa a un requisito específico. Sin embargo, la falta de información sobre el contexto (por ejemplo, si se trata de un requisito para un examen, un trámite, etc.) dificulta la comprensión total de la situación. En cuestión de especificidad, la pregunta es concreta y puede ser respondida con un "sí" o "no", pero la falta de información sobre el propósito del certificado limita la comprensión total de la situación. Por lo tanto, aunque la pregunta es clara y específica, la falta de contexto hace que no se entienda completamente por sí sola.
        - La última pregunta del usuario se entiende sin necesidad del historial del chat: No

Realiza el análisis de manera minuciosa basándote en los criterios y ejemplos anteriores e indica de la siguiente manera si es que la ultima pregunta del usuario proporcionada se entiende sin necesidad del historial:
 
- Análisis: ...
- La última pregunta del usuario se entiende sin necesidad del historial del chat: Sí o No


Último mensaje del usuario: {query}"""
    
    return prompt
## Aqui probar poniendo un ejemplo donde el se dice que la pregunta es aunque no es se menciona el contexto ya que al asistente aqui va dirigido ya estafamilirado con los terminos y los requisitos y normativas.
"""- Ejemplo 3: Si que no cumplo con el requisito de ser un "estudiante en posibilidad de egresar" pero quiero  matricularse en un curso y su prerequisito simultáneamente, ¿Que puedo hacer?
        - Análisis: La pregunta del usuario se refiere a una situación específica relacionada con los requisitos académicos de la Facultad de Ciencias de la Universidad Nacional de Ingeniería. El usuario menciona un requisito particular ("ser estudiante en posibilidad de egresar") y plantea una situación en la que un estudiante necesita matricularse en un curso y su prerequisito al mismo tiempo. Aunque el contexto sobre las normativas específicas de la universidad y las implicaciones de no cumplir con el requisito mencionado no se proporciona, el asistente al estar familiarizado con las normativas académicas podrá entender a que se refiere. Ademas la pregunta es clara y especifica al describir el requisito particular que no se esta cumpliendo y la situación específica. Por lo tanto, la pregunta es comprensible y se puede responder sin necesidad de acceder al historial de la conversación.
        - La última pregunta del usuario se entiende sin necesidad del historial del chat: Sí"""

def get_prompt_8(history_chat, query):
    prompt = f"""Dado el último mensaje del usuario dado en el contexto de Facultad de Ciencias de La Universidad Nacional de Ingeniería de Peru enviado a un asistente familiarizado con las normativas académicas de la universidad, analiza e indica si la ultima pregunta del usuario podría entender total por si sola, sin necesidad de tener acceso a tiene acceso al historial previo de la conversación. Has tu análisis para identificar si la pregunta es entendible basándote en los siguientes criterios:

Criterios:
1. Contexto Suficiente: Debe de haber suficiente contexto en el mensaje para entender a que se refiere la pregunta.
2. Claridad: La pregunta debe ser clara con respecto al tema que trata o a quien se refiere.
3. Especificidad: El mensaje con la pregunta debe ser lo suficiente especifico para que se pueda responder de manera correcta.

Ejemplos:
- Ejemplo 1: ¿También podría usar el certificado medico, de una clínica privada?
        - Análisis: La pregunta del usuario se refiere a la posibilidad de utilizar un certificado médico de una clínica privada en lugar de uno específico del Centro Médico de la UNI. Sin embargo, no se proporciona contexto adicional sobre el propósito del certificado, lo que es relevante para poder entender completamente la pregunta. La pregunta es clara en su formulación y se entiende que el usuario está buscando una alternativa a un requisito específico. Sin embargo, la falta de información sobre el contexto (por ejemplo, si se trata de un requisito para un examen, un trámite, etc.) dificulta la comprensión total de la situación. En cuestión de especificidad, la pregunta es concreta y puede ser respondida con un "sí" o "no", pero la falta de información sobre el propósito del certificado limita la comprensión total de la situación. Por lo tanto, aunque la pregunta es clara y específica, la falta de contexto hace que no se entienda completamente por sí sola.
        - La última pregunta del usuario se entiende sin necesidad del historial del chat: No
- Ejemplo 2: ¿Y cómo se hace esa solicitud? ¿Hay algún formato específico o solo es un correo al director?
        - Análisis: La pregunta del usuario se refiere a una solicitud de una constancia y si hay algún formato o se envía solo un correo al director. Sin embargo, el contexto sobre qué tipo de solicitud se está solicitando no se menciona, lo que es relevante para entender completamente la pregunta. A pesar, que el asistente este familiarizado con las normativas académicas de la universidad no podría inferir de que tramite se trata, si ese información la pregunta no seria clara ni especifica sobre a que se refiere y no se podría responder de forma adecuada. Por lo tanto, la falta de contexto hace que la pregunta no se entienda completamente por sí sola.
        - La última pregunta del usuario se entiende sin necesidad del historial del chat: No

Realiza el análisis de manera minuciosa basándote en los criterios y ejemplos anteriores e indica de la siguiente manera si es que la ultima pregunta del usuario proporcionada se entiende sin necesidad del historial:
 
- Análisis: ...
- La última pregunta del usuario se entiende sin necesidad del historial del chat: Sí o No

Último mensaje del usuario: {query}"""
    
    return prompt

def get_prompt_9(history_chat, query):
    prompt = f"""Dado el último mensaje del usuario dado en el contexto de Facultad de Ciencias de La Universidad Nacional de Ingeniería de Peru enviado a un asistente familiarizado con las normativas académicas de la universidad, analiza e indica si la ultima pregunta del usuario podría entender total por si sola, sin necesidad de tener acceso a tiene acceso al historial previo de la conversación. Has tu análisis para identificar si la pregunta es entendible basándote en los siguientes criterios:

Criterios:
1. Contexto Suficiente: Debe de haber suficiente contexto en el mensaje para entender a que se refiere la pregunta.
2. Claridad: La pregunta debe ser clara con respecto al tema que trata o a quien se refiere.
3. Especificidad: El mensaje con la pregunta debe ser lo suficiente especifico para que se pueda responder de manera correcta.

Ejemplos:
- Ejemplo 1: ¿También podría usar el certificado medico, de una clínica privada?
        - Análisis: La pregunta del usuario se refiere a la posibilidad de utilizar un certificado médico de una clínica privada en lugar de uno específico del Centro Médico de la UNI. Sin embargo, no se proporciona contexto adicional sobre el propósito del certificado, lo que es relevante para poder entender completamente la pregunta. Aunque, la pregunta es clara en su formulación y se entiende que el usuario está buscando una alternativa a un requisito específico, la falta de información sobre el contexto (por ejemplo, si se trata de un requisito para un examen, un trámite, etc.) dificulta la comprensión total de la situación. En cuestión de especificidad, la pregunta es concreta y puede ser respondida con un "sí" o "no", pero la falta de información sobre el propósito del certificado limita la comprensión total de la situación, a pesar de, que el asistente este familiarizado con las normativas académicas de la universidad no podría inferir sobre que certificado se trata y tampoco se podría proporcionar una respuesta adecuada. Por lo tanto, aunque la pregunta es clara y específica, la falta de contexto hace que no se entienda completamente por sí sola.
        - La última pregunta del usuario se entiende sin necesidad del historial del chat: No
- Ejemplo 2: ¿Y cómo se hace esa solicitud? ¿Hay algún formato específico o solo es un correo al director?
        - Análisis: La pregunta del usuario se refiere a una solicitud de una constancia y si hay algún formato o se envía solo un correo al director. Sin embargo, el contexto sobre qué tipo de solicitud se está solicitando no se menciona, lo que es relevante para entender completamente la pregunta. A pesar, que el asistente este familiarizado con las normativas académicas de la universidad no podría inferir de que tramite se trata, si ese información la pregunta no seria clara ni especifica sobre a que se refiere y no se podría responder de forma adecuada. Por lo tanto, la falta de contexto hace que la pregunta no se entienda completamente por sí sola.
        - La última pregunta del usuario se entiende sin necesidad del historial del chat: No
- Ejemplo 3: Entiendo, ¿También quisiera saber si es que un dia con menos fluencia de personas en la Mesa de Partes o siempre es igual?
        - Análisis: La pregunta del usuario se refiere a la afluencia de personas en la Mesa de Partes de la universidad, buscando información sobre si hay días más tranquilos para realizar un trámite. A pesar, que no se proporciona contexto adicional sobre a que facultad o universidad pertenece la Mesa de Partes al manejarse por defecto el contexto de la facultad de ciencias de la UNI el asistente puede inferir que se esta preguntando sobre la Mesa de Parte de la Facultad sin necesidad de tener mayor contexto. Ademas, la pregunta es clara, directa y específica en cuanto a lo que se busca saber: la variabilidad en la afluencia de personas, lo cual es algo general que se puede responder de manera adecuada sin necesidad de mayor contexto. Por lo tanto, hay suficiente contexto para entender la pregunta sin necesidad de información adicional.
        - La última pregunta del usuario se entiende sin necesidad del historial del chat: Sí
- Ejemplo 4: Cuanto tiempo tardaran en darme, la constancia?
        - Análisis: La pregunta del usuario se refiere al tiempo que tarda en estar lista una constancia. A pesar, de manejar por defecto el contexto de la facultad y que el asistente conozca las normativas de la Universidad es relevante saber de que constancia especifica se esta hablando para poder responde de manera precisa y adecuada. Por otra lado. La pregunta es clara y directa, ya que busca información específica sobre el tiempo de espera, lo cual podría responderse de manera general, sin embargo, para responderse de manera mas adecuada y especifica es necesario la información sobre el tipo de constancia. Por lo tanto, no hay suficiente contexto para entender la pregunta sin necesidad del contexto previo.
        - La última pregunta del usuario se entiende sin necesidad del historial del chat: No

Realiza el análisis de manera minuciosa basándote en los criterios y ejemplos anteriores e indica de la siguiente manera si es que la ultima pregunta del usuario proporcionada se entiende sin necesidad del historial:
 
- Análisis: ...
- La última pregunta del usuario se entiende sin necesidad del historial del chat: Sí o No

Último mensaje del usuario: {query}"""
    
    return prompt

def get_prompt_10(history_chat, query):
    prompt = f"""Dado el último mensaje del usuario dado en el contexto de Facultad de Ciencias de La Universidad Nacional de Ingeniería de Peru enviado a un asistente familiarizado con las normativas académicas de la universidad, analiza e indica si la ultima pregunta del usuario podría entender total por si sola, sin necesidad de tener acceso a tiene acceso al historial previo de la conversación. Has tu análisis para identificar si la pregunta es entendible basándote en los siguientes criterios:

Criterios:
1. Contexto Suficiente: Debe de haber suficiente contexto en el mensaje para entender a que se refiere la pregunta.
2. Claridad: La pregunta debe ser clara con respecto al tema que trata o a quien se refiere.
3. Especificidad: El mensaje con la pregunta debe ser lo suficiente especifico para que se pueda responder de manera correcta.

Ejemplos:
- Ejemplo 1: ¿También podría usar el certificado medico, de una clínica privada?
        - Análisis: La pregunta del usuario se refiere a la posibilidad de utilizar un certificado médico de una clínica privada en lugar de uno específico del Centro Médico de la UNI. Esta pregunta indica que hay requisito relacionado con la presentación de un certificado médico, a pesar de ser especifico en cuanto al tipo de certificado la información sobre el contexto (por ejemplo, si se trata de un requisito para un examen, un trámite, etc.), es necesaria para comprender la situación completa. Aunque, el asistente esté familiarizado con las normativas académicas de la universidad, no podría inferir con certeza a qué requisito o trámite se refiere la presentación del certificado, lo cual es crucial es esta caso para que la pregunta pueda responderse de manera satisfactoria y adecuada. Por lo tanto, aunque la pregunta es clara y específica, la falta de contexto impide que se entienda completamente por sí sola.
        - La última pregunta del usuario se entiende sin necesidad del historial del chat: No
- Ejemplo 2: ¿Y cómo se hace esa solicitud? ¿Hay algún formato específico o solo es un correo al director?
        - Análisis: La pregunta del usuario se refiere a una solicitud de una constancia y si hay algún formato o se envía solo un correo al director. Sin embargo, el contexto sobre qué tipo de solicitud se está solicitando no se menciona, lo que es relevante para entender completamente la pregunta. A pesar, que el asistente este familiarizado con las normativas académicas de la universidad no podría inferir de que tramite se trata, si ese información la pregunta no seria clara ni especifica sobre a que se refiere y no se podría responder de forma adecuada. Por lo tanto, la falta de contexto hace que la pregunta no se entienda completamente por sí sola.
        - La última pregunta del usuario se entiende sin necesidad del historial del chat: No
- Ejemplo 3: Entiendo, ¿También quisiera saber si es que un dia con menos fluencia de personas en la Mesa de Partes o siempre es igual?
        - Análisis: La pregunta del usuario se refiere a la afluencia de personas en la Mesa de Partes de la universidad, buscando información sobre si hay días más tranquilos para realizar un trámite. A pesar, que no se proporciona contexto adicional sobre a que facultad o universidad pertenece la Mesa de Partes al manejarse por defecto el contexto de la facultad de ciencias de la UNI el asistente puede inferir que se esta preguntando sobre la Mesa de Parte de la Facultad sin necesidad de tener mayor contexto. Ademas, la pregunta es clara, directa y específica en cuanto a lo que se busca saber: la variabilidad en la afluencia de personas, lo cual es algo general que se puede responder de manera adecuada sin necesidad de mayor contexto. Por lo tanto, hay suficiente contexto para entender la pregunta sin necesidad de información adicional.
        - La última pregunta del usuario se entiende sin necesidad del historial del chat: Sí
- Ejemplo 4: Cuanto tiempo tardaran en darme, la constancia?
        - Análisis: La pregunta del usuario se refiere al tiempo que tarda en estar lista una constancia. A pesar, de manejar por defecto el contexto de la facultad y que el asistente conozca las normativas de la Universidad es relevante saber de que constancia especifica se esta hablando para poder responde de manera precisa y adecuada. Por otra lado. La pregunta es clara y directa, ya que busca información específica sobre el tiempo de espera, lo cual podría responderse de manera general, sin embargo, para responderse de manera adecuada y especifica es necesario la información sobre el tipo de constancia. Por lo tanto, no hay suficiente contexto para entender la pregunta sin necesidad del contexto previo.
        - La última pregunta del usuario se entiende sin necesidad del historial del chat: No
- Ejemplo 5: Entonces, ¿Sabes si la oficina de escuelas profesionales tiene un horario fijo para atender de manera presencial?
        - Análisis: La pregunta del usuario se refiere a si la oficina de escuelas profesionales tiene un horario fijo para la atención presencial. Es específica y clara en cuanto a la oficina de la cual se desea obtener información y al tipo de información solicitada (el horario de atención de la oficina de escuelas profesionales). Esta consulta puede ser respondida de manera adecuada sin necesidad de mayor contexto sobre el trámite que se desea realizar o el motivo de la visita. Por lo tanto, hay suficiente contexto para entender la pregunta sin requerir información adicional.
        - La última pregunta del usuario se entiende sin necesidad del historial del chat: Sí
- Ejemplo 6: Y que correo puedo escribirles?
        - Análisis: La pregunta del usuario por un correo para contactar a una entidad o persona específica, aunque no se menciona explícitamente a quién se refiere con "ellos". Esa informacion contextual es crucial y relevante en esta pregunta, para poder dar una respuesta adecuada a la consulta. A pesar que el asistente este familiarizado con las normativas academico y se asuma que se refiere a algun contacto dentro del ámbito académico de la universidad, al no tener la informacion especifica de a quien se refiere no se podria podricirnar una respuesta adecuada. Por lo tanto, no hay suficiente contexto para entender la pregunta sin necesidad del contexto previo.
        - La última pregunta del usuario se entiende sin necesidad del historial del chat: No

Realiza el análisis de manera minuciosa basándote en los criterios y ejemplos anteriores e indica de la siguiente manera si es que la ultima pregunta del usuario proporcionada se entiende sin necesidad del historial:
 
- Análisis: ...
- La última pregunta del usuario se entiende sin necesidad del historial del chat: Sí o No

Último mensaje del usuario: {query}"""
    
    return prompt


def get_prompt_11(history_chat, query):
    prompt = f"""Dado el último mensaje del usuario dado en el contexto de Facultad de Ciencias de La Universidad Nacional de Ingeniería de Peru enviado a un asistente familiarizado con las normativas académicas de la universidad, analiza e indica si la ultima pregunta del usuario podría entender total por si sola, sin necesidad de tener acceso a tiene acceso al historial previo de la conversación. Has tu análisis para identificar si la pregunta es entendible basándote en los siguientes criterios:

Criterios:
1. Contexto Suficiente: Debe de haber suficiente contexto en el mensaje para entender a que se refiere la pregunta.
2. Claridad: La pregunta debe ser clara con respecto al tema que trata o a quien se refiere.
3. Especificidad: El mensaje con la pregunta debe ser lo suficiente especifico para que se pueda responder de manera correcta.

Ejemplos:
- Ejemplo 1: ¿También podría usar el certificado medico, de una clínica privada?
        - Análisis: La pregunta del usuario se refiere a la posibilidad de utilizar un certificado médico de una clínica privada en lugar de uno específico del Centro Médico de la UNI. Esta pregunta indica que hay requisito relacionado con la presentación de un certificado médico, a pesar de ser especifico en cuanto al tipo de certificado la información sobre el contexto (por ejemplo, si se trata de un requisito para un examen, un trámite, etc.), es necesaria para comprender la situación completa. Aunque, el asistente esté familiarizado con las normativas académicas de la universidad, no podría inferir con certeza a qué requisito o trámite se refiere la presentación del certificado, lo cual es crucial es esta caso para que la pregunta pueda responderse de manera satisfactoria y adecuada. Por lo tanto, aunque la pregunta es clara y específica, la falta de contexto impide que se entienda completamente por sí sola.
        - La última pregunta del usuario se entiende sin necesidad del historial del chat: No
- Ejemplo 2: ¿Y cómo se hace esa solicitud? ¿Hay algún formato específico o solo es un correo al director?
        - Análisis: La pregunta del usuario se refiere a una solicitud de una constancia y si hay algún formato o se envía solo un correo al director. Sin embargo, el contexto sobre qué tipo de solicitud se está solicitando no se menciona, lo que es relevante para entender completamente la pregunta. A pesar, que el asistente este familiarizado con las normativas académicas de la universidad no podría inferir de que tramite se trata, si ese información la pregunta no seria clara ni especifica sobre a que se refiere y no se podría responder de forma adecuada. Por lo tanto, la falta de contexto hace que la pregunta no se entienda completamente por sí sola.
        - La última pregunta del usuario se entiende sin necesidad del historial del chat: No
- Ejemplo 3: Entiendo, ¿También quisiera saber si es que un dia con menos fluencia de personas en la Mesa de Partes o siempre es igual?
        - Análisis: La pregunta del usuario se refiere a la afluencia de personas en la Mesa de Partes de la universidad, buscando información sobre si hay días más tranquilos para realizar un trámite. A pesar, que no se proporciona contexto adicional sobre a que facultad o universidad pertenece la Mesa de Partes al manejarse por defecto el contexto de la facultad de ciencias de la UNI el asistente puede inferir que se esta preguntando sobre la Mesa de Parte de la Facultad sin necesidad de tener mayor contexto. Ademas, la pregunta es clara, directa y específica en cuanto a lo que se busca saber: la variabilidad en la afluencia de personas, lo cual es algo general que se puede responder de manera adecuada sin necesidad de mayor contexto. Por lo tanto, hay suficiente contexto para entender la pregunta sin necesidad de información adicional.
        - La última pregunta del usuario se entiende sin necesidad del historial del chat: Sí
- Ejemplo 4: Cuanto tiempo tardaran en darme, la constancia?
        - Análisis: La pregunta del usuario se refiere al tiempo que tarda en estar lista una constancia. A pesar, de manejar por defecto el contexto de la facultad y que el asistente conozca las normativas de la Universidad es relevante saber de que constancia especifica se esta hablando para poder responde de manera precisa y adecuada. Por otra lado. La pregunta es clara y directa, ya que busca información específica sobre el tiempo de espera, lo cual podría responderse de manera general, sin embargo, para responderse de manera adecuada y especifica es necesario la información sobre el tipo de constancia. Por lo tanto, no hay suficiente contexto para entender la pregunta sin necesidad del contexto previo.
        - La última pregunta del usuario se entiende sin necesidad del historial del chat: No
- Ejemplo 5: Entonces, ¿Sabes si la oficina de escuelas profesionales tiene un horario fijo para atender de manera presencial?
        - Análisis: La pregunta del usuario se refiere a si la oficina de escuelas profesionales tiene un horario fijo para la atención presencial. Es específica y clara en cuanto a la oficina de la cual se desea obtener información y al tipo de información solicitada (el horario de atención de la oficina de escuelas profesionales). Esta consulta puede ser respondida de manera adecuada sin necesidad de mayor contexto sobre el trámite que se desea realizar o el motivo de la visita. Por lo tanto, hay suficiente contexto para entender la pregunta sin requerir información adicional.
        - La última pregunta del usuario se entiende sin necesidad del historial del chat: Sí
- Ejemplo 6: Y que correo puedo escribirles?
        - Análisis: La pregunta del usuario por un correo para contactar a una entidad o persona específica, aunque no se menciona explícitamente a quién se refiere con "ellos". Esa informacion contextual es crucial y relevante en esta pregunta, para poder dar una respuesta adecuada a la consulta. A pesar que el asistente este familiarizado con las normativas academico y se asuma que se refiere a algun contacto dentro del ámbito académico de la universidad, al no tener la informacion especifica de a quien se refiere no se podria proporcionar una respuesta adecuada. Por lo tanto, no hay suficiente contexto para entender la pregunta sin necesidad del contexto previo.
        - La última pregunta del usuario se entiende sin necesidad del historial del chat: No
- Ejemplo 7: Entonces, ¿como se realiza el retiro parcial?. ¿Tengo que presentar algo?
        - Análisis: La pregunta del usuario se refiere al proceso de solicitar un retiro parcial, lo cual implica un trámite administrativo en la universidad. El asistente, al estar familiarizado con las normativas universitarias, puede entender a qué se refiere con "retiro parcial" sin necesidad de mayor contexto, ya que es un término específico. Además, la pregunta es clara y específica con la información que se busca sobre el proceso del retiro parcial, por lo que es posible proporcionar una respuesta adecuada. Por lo tanto, la pregunta se entiende sin necesidad de contexto previo.
        - La última pregunta del usuario se entiende sin necesidad del historial del chat: Sí
- Ejemplo 8: ¿Cómo funciona el proceso de matrícula?
        - Análisis: La pregunta del usuario se refiere al proceso de matrícula en la universidad. Aunque la pregunta es clara y directa, el contexto sobre qué tipo de matrícula se está refiriendo no se menciona. Sin embargo, dado que el término "matrícula" es común en el ámbito universitario y el asistente está familiarizado con las normativas de la universidad, se puede inferir que se refiere al proceso general de matrícula en la Facultad de Ciencias de la UNI. La pregunta es específica en cuanto a la búsqueda de información sobre el proceso, lo que permite que se pueda responder de manera adecuada. Por lo tanto, hay suficiente contexto para entender la pregunta sin necesidad de información adicional.
        - La última pregunta del usuario se entiende sin necesidad del historial del chat: Sí

Realiza el análisis de manera minuciosa basándote en los criterios y ejemplos anteriores e indica de la siguiente manera si es que la ultima pregunta del usuario proporcionada se entiende sin necesidad del historial:
 
- Análisis: ...
- La última pregunta del usuario se entiende sin necesidad del historial del chat: Sí o No

Último mensaje del usuario: {query}"""
    
    return prompt

def get_prompt_4(history_chat, query):
    prompt = f"""Dado el último mensaje del usuario, analiza e indica si la ultima pregunta del usuario podría entender total por si sola, sin necesidad de tener acceso a tiene acceso al historial previo de la conversación. Has tu análisis basándote en los siguientes criterios y ejemplos:
Criterios:
1. La pregunta no podría entenderse en su totalidad, si es que hace referencia directa o implícita a una situación o información específica que solo se proporcionó anteriormente pero no en el ultimo mensaje del usuario, por lo tanto, no es claro a que se refiere sin el historial del la conversación. 
2. La pregunta debería poder entenderse sin el historial si no hace referencia de ningún tipo a información específica proporcionada anteriormente en la conversación.

Ejemplos de mensajes de usuario con preguntas que hacen referencia a una situación o información especifica mencionada anteriormente: 
    - Ejemplo 1:  ¿Y cómo se hace esa solicitud? ¿Hay algún formato específico o solo es un correo al director?
        Análisis: Esta pregunta hace referencia directa a "esa solicitud" que se refiere a algún proceso mencionado anteriormente pero que no es descrito en el ultimo mensaje del usuario que contiene la pregunta, por lo que, sin esa información no es claro a qué tipo de solicitud se refiere el usuario y la pregunta no se entenderia sin ese contexto.
    
Ejemplos de mensajes de usuario con preguntas que no hacen referencia a una situación o información especifica mencionada anteriormente: 
    - Ejemplo 1: ¿Qué debo hacer si quiero inscribirme en un curso y su prerequisito en el mismo ciclo?
        Análisis: Esta pregunta no hace referencia a ningún concepto o situación especifica, ademas, la pregunta en entendible por si sola.

Proporciona un análisis detallada e indica si la ultima pregunta del usuario se entiende sin necesidad del historial del chat de la siguiente manera:

Análisis: ...

La última pregunta del usuario se entiende sin necesidad del historial del chat: Sí o No

Último mensaje del usuario: {query}"""
    return prompt


examples = [{
    "history_chat_messages": [],
    "query": "¿Qué pasos debo seguir entonces para poder solicitar esa matricula especial?",
    "entendible": False
},
{
    "history_chat_messages": [],
    "query": "\u00bfQu\u00e9 sucede si un estudiante no cumple con el requisito de ser \"estudiante en posibilidad de egresar\" pero necesita matricularse en un curso y su prerequisito simult\u00e1neamente por motivos acad\u00e9micos o personales?",
    "entendible": True
},{
    "history_chat_messages":  [],
    "query" : "\u00a1Genial! Entonces, si soy un \"estudiante en posibilidad de egresar\" con menos de 30 cr\u00e9ditos pendientes, puedo matricularme en un curso y su prerequisito en el mismo ciclo. \u00bfDebo comunicarme con mi escuela profesional para solicitar la aprobaci\u00f3n del director correspondiente, verdad?",
    "entendible": True
},{
    "history_chat_messages": [],
    "query": "\u00bfQu\u00e9 debo hacer si quiero inscribirme en un curso y su prerequisito en el mismo ciclo?",
    "entendible": True
},{
    "history_chat_messages":  [],
    "query": "\u00bfY c\u00f3mo se hace esa solicitud? \u00bfHay alg\u00fan formato espec\u00edfico o solo es un correo al director?",
    "entendible": False
},{
    "history_chat_messages": [],
    "query":  "Entonces, si no estoy en esa situaci\u00f3n de \"posibilidad de egresar\", \u00bfno puedo matricularme en ambos cursos al mismo tiempo?",
    "entendible": False
},{
    "history_chat_messages": [],
    "query":"\u00bfY si no puedo conseguir el certificado a tiempo?",
    "entendible": False
},{
    "history_chat_messages" : [],
    "query": "¿Y dónde encuentro el formulario de solicitud en la intranet?",
    "entendible": False
},{
    "history_chat_messages": [],
     "query": "¿Y si no tengo el certificado del Centro Médico de la UNI, puedo usar uno de una clínica privada?",
     "entendible": False
},
{   
    "history_chat_messages": [],
    "query": "¿Y si no es por enfermedad grave?",
    "entendible": False
},
{   
    "history_chat_messages": [],
    "query": "¿Sabes si hay algún número de teléfono para contactarlos directamente?",
    "entendible": False
},
{   "history_chat_messages": [],
    "query": "¿Y cuánto tiempo suele tardar en estar lista la constancia después de enviar el comprobante de pago?",
    "entendible": False

},
{   "history_chat_messages": [],
    "query": "¿Y si necesito la constancia con urgencia, hay alguna manera de acelerar el proceso?",
    "entendible": False
},{ 
    "history_chat_messages": [],
    "query": "Perfecto, gracias por la info. ¿Sabes si hay algún formato específico para la solicitud de la constancia o solo basta con escribir un correo con mis datos?",
    "entendible": False
},
{   "history_chat_messages": [],
    "query": "Perfecto, eso me ayuda. ¿Sabes si hay algún día en particular que sea más tranquilo para ir a Mesa de Partes, o siempre está igual de lleno?",
    "entendible": True
},
{   "history_chat_messages": [],
    "query": "¿Y cuánto tiempo suele tardar en procesarse la constancia una vez que entrego todo? ¿Hay algún horario específico para dejar el comprobante en mesa de partes?",
    "entendible": False
},
{   
    "history_chat_messages": [],
    "query": 'Entendido, lo haré. ¿Sabes si la oficina de estadística tiene un horario fijo para atender en persona? A veces es complicado encontrar horarios que coincidan.',
    "entendible": True
},
{   "history_chat_messages": [],
    "query": "¿Y cómo se hace el proceso para solicitar el retiro total? ¿Hay algún formulario específico o algo que deba presentar?",
    "entendible": True
},
{   "history_chat_messages": [],
    "query": "¿Y cómo funciona el proceso de matrícula? ¿Hay algún plazo específico que deba tener en cuenta?",
    "entendible": True
}
] 
## Agregar esto a eso
# La pregunta del usuario se refiere al proceso de matrícula en la universidad y si hay plazos específicos que deben considerarse. Aunque la pregunta es clara y directa, el contexto sobre qué tipo de matrícula se está refiriendo (por ejemplo, matrícula inicial, matrícula para un ciclo académico específico, etc.) no se menciona. Sin embargo, dado que el término "matrícula" es común en el ámbito académico y el asistente está familiarizado con las normativas de la universidad, se puede inferir que se refiere al proceso general de matrícula en la Facultad de Ciencias de la UNI. La pregunta es específica en cuanto a la búsqueda de información sobre el proceso y los plazos, lo que permite que se pueda responder de manera adecuada. Por lo tanto, hay suficiente contexto para entender la pregunta sin necesidad de información adicional.

## Respuesta a esto:
"""Análisis: La pregunta del usuario se refiere a la afluencia de personas en la Mesa de Partes de la universidad, buscando identificar si hay días más tranquilos para realizar un trámite. Sin embargo, no se proporciona contexto adicional sobre el tipo de trámite que desea realizar ni la razón por la cual le interesa saber sobre los días más tranquilos. Aunque la pregunta es clara en su formulación y se entiende que el usuario busca información sobre la carga de trabajo en la Mesa de Partes, la falta de información sobre el propósito específico de su visita limita la comprensión total de la situación. En términos de especificidad, la pregunta es concreta y puede ser respondida con información sobre los días más o menos concurridos, pero la ausencia de contexto sobre el trámite o la urgencia de su visita hace que no se entienda completamente por sí sola. Por lo tanto, aunque la pregunta es clara y específica, la falta de contexto hace que no se entienda completamente por sí sola.
- La última pregunta del usuario se entiende sin necesidad del historial del chat: No"""
count_good_pred = 0

for example in examples[:]:
# que no es suficientemente descrita en el mensaje para poder entender completamente el contexto del mensaje.
    history_messages_chat = example["history_chat_messages"]
    history_chat = format_text_history_chat(history_messages_chat)
    query = example["query"]

    prompt = get_prompt_11(history_chat, query)

    
    print()
    print("-"*90)
    print("\n".join(prompt.split("\n")[-2:]))

    messages = [{"role": "user", "content": prompt}]
                
    #messages = [{"role": "user", "content": prompt_identify_reform}, {"role": "assistant", "content": "La última pregunta del usuario se entiende sin necesidad del historial del chat: Sí"}, {"role": "user", "content": "esta respuesta esta mal"}]

    response = get_completion_from_messages(
                        messages,
                        model = "gpt-4o-mini-2024-07-18"
                        #model= "gpt-3.5-turbo-0125"
                        )

    print("\n\033[32mresponde need context:\033[0m", response)


    not_need_context = extract_need_context(response)
    pred_entendible = not_need_context == "Sí"

    if pred_entendible == example["entendible"]:
        count_good_pred += 1
    else:
        print('\n'+ "\033[31m" + f'Bad Prediction, Expected: entendible={example["entendible"]}' + "\033[0m")
        print("\nprompt:\n", prompt)
        
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
print("Exactitud:", count_good_pred / len(examples))
print(f"{count_good_pred}/{len(examples)}")

