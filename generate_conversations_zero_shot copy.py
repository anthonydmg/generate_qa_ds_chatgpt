
from utils import get_completion_from_messages, set_openai_key
from dotenv import load_dotenv

load_dotenv()

set_openai_key()


qas = [{
                "pregunta": "\u00bfCu\u00e1l es el porcentaje m\u00ednimo de contenido que deben coincidir las asignaturas para que proceda la convalidaci\u00f3n?",
                "respuesta": "Para que proceda la convalidaci\u00f3n, los respectivos s\u00edlabos de las asignaturas a convalidar deben coincidir al menos en un 75% de su contenido y de horas dictadas."
        },
        {
                "pregunta": "\u00bfEl plazo para las convalidaciones de traslados internos es de hasta cinco (05) d\u00edas \u00fatiles desde la aprobaci\u00f3n del Consejo de Facultad o autorizaci\u00f3n del Decano?",
                "respuesta": "S\u00ed, el plazo para las convalidaciones de traslados internos es de hasta cinco (05) d\u00edas \u00fatiles desde la aprobaci\u00f3n del Consejo de Facultad o autorizaci\u00f3n del Decano, de acuerdo al reglamento de matr\u00edcula de la Facultad de Ciencias de la UNI."
        }]

text_qas = ""

for i , qa in enumerate(qas):
    text_qas = text_qas + "\n"+ f'{i + 1}. {qa["pregunta"]}\nrespuesta: {qa["respuesta"]}'

prompt = f"""
    Tu tarea es generar 5 conversaciones realistas entre un asistente de IA especializado en matrículas, trámites y procedimientos académicos de la Facultad de Ciencias de la Universidad Nacional de Ingeniería (UNI) y un usuario.
    Antes de generar las conversaciones, asegúrate de cumplir cada uno de los siguientes criterios:
        1. Las conversaciones deben ser por turnos entre el agente de IA y el usuario, siendo el usuario el que siempre comenzará la conversación.
        2. Las conversaciones deben tener al menos 3 turnos para cada hablante en la conversación.
        3. El usuario debe manejar un tono semiformal y natural.
        4. El usuario no debe repetir de la misma manera alguna pregunta en otra conversación.
        5. El asistente ante un agradecimiento o confirmación debe responder apropiandamente y adicionalmente mencionar que si tiene alguna otra duda que no dude en preguntar.
        5. Enfocate en crear diferentes conversaciones donde el usuario tenga la intención de obtener información que se encuentre dentro de los pares de preguntas y respuestas listadas abajo.  

    Finalmente, presenta cada una de las {5} conversaciones de la siguiente manera:
    
    conversacion 1:
            user: ...
            asistant: ...
            user: ...
            ...
    
    Lista de preguntas y respuestas: <<{text_qas}>>

"""

messages =  [{'role':'user', 'content':prompt}]
response = get_completion_from_messages(messages, temperature=0)
print(response)