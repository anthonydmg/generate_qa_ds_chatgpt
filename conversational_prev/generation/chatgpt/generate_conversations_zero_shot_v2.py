
from utils import get_completion_from_messages, set_openai_key, count_tokens
from dotenv import load_dotenv
import tiktoken

load_dotenv()

set_openai_key()

encoding = tiktoken.encoding_for_model('gpt-3.5-turbo')

qas_lists = [[
    {
        "pregunta": "\u00bfCu\u00e1l es el porcentaje m\u00ednimo de contenido que deben coincidir las asignaturas para que proceda la convalidaci\u00f3n?",
        "respuesta": "Para que proceda la convalidaci\u00f3n, los respectivos s\u00edlabos de las asignaturas a convalidar deben coincidir al menos en un 75% de su contenido y de horas dictadas."
    },
    {
        "pregunta": "\u00bfEl plazo para las convalidaciones de traslados internos es de hasta cinco (05) d\u00edas \u00fatiles desde la aprobaci\u00f3n del Consejo de Facultad o autorizaci\u00f3n del Decano?",
        "respuesta": "S\u00ed, el plazo para las convalidaciones de traslados internos es de hasta cinco (05) d\u00edas \u00fatiles desde la aprobaci\u00f3n del Consejo de Facultad o autorizaci\u00f3n del Decano, de acuerdo al reglamento de matr\u00edcula de la Facultad de Ciencias de la UNI."
    }],
    [{
        "pregunta": "\u00bfQu\u00e9 es el grupo cero de matr\u00edcula y qui\u00e9nes lo conforman seg\u00fan el reglamento acad\u00e9mico de la Facultad de Ciencias de la UNI?",
        "respuesta": "El grupo cero de matr\u00edcula es el listado que contiene las matr\u00edculas de quienes retornan de Separaci\u00f3n Temporal por Bajo Rendimiento Acad\u00e9mico y de los alumnos en Riesgo Acad\u00e9mico por asignaturas repetidas dos veces. La Comisi\u00f3n de Matr\u00edcula cierra el listado producido por la Tutor\u00eda, el d\u00eda anterior a la matricula y lo remite a la ORCE para su registro previo, con m\u00ednimo tres horas antes del inicio del primer turno de matr\u00edcula."
    },
    {
        "pregunta": "\u00bfSe puede retirar parcialmente de las asignaturas que son prerrequisito?",
        "respuesta": "No, no es posible retirarse parcialmente de las asignaturas que son prerrequisito, seg\u00fan el reglamento de matr\u00edcula de la Facultad de Ciencias de la UNI."
    }],
    [
    {
        "pregunta": "\u00bfQu\u00e9 se entiende por estudiante en riesgo acad\u00e9mico seg\u00fan el reglamento de la Facultad de Ciencias de la UNI?",
        "respuesta": "Un estudiante en riesgo acad\u00e9mico es aquel que tenga desaprobada una o m\u00e1s asignaturas en dos o tres oportunidades, debiendo pasar obligatoriamente por un proceso de tutor\u00eda acad\u00e9mica antes de su matr\u00edcula."
    },
    {
        "pregunta": "\u00bfSe puede solicitar la reincorporaci\u00f3n si se tiene una sanci\u00f3n vigente?",
        "respuesta": "No, no es posible solicitar la reincorporaci\u00f3n si se tiene una sanci\u00f3n vigente, seg\u00fan el reglamento de matr\u00edcula de la Facultad de Ciencias de la UNI."
    }],
    [
    {
        "pregunta": "\u00bfCu\u00e1l es el plazo para realizar un retiro parcial de asignaturas seg\u00fan el reglamento acad\u00e9mico de la Facultad de Ciencias de la UNI?",
        "respuesta": "El plazo para realizar un retiro parcial de asignaturas es hasta el \u00faltimo d\u00eda \u00fatil de la quinta semana despu\u00e9s del inicio de clases del per\u00edodo acad\u00e9mico."
    },
    {
        "pregunta": "\u00bfEl proceso de matr\u00edcula se realiza a trav\u00e9s del Portal Web del Sistema de Matr\u00edcula UNI?",
        "respuesta": "S\u00ed, el proceso de matr\u00edcula se realiza a trav\u00e9s del Portal Web del Sistema de Matr\u00edcula UNI, suministrado por la ORCE, seg\u00fan lo establecido en el reglamento de matr\u00edcula de la Facultad de Ciencias de la UNI."
    }
    ]]


texts_qas = []
for qas in qas_lists:
    text_qas = ""
    for i , qa in enumerate(qas):
        text_qas = text_qas + "\n"+ f'{i + 1}. {qa["pregunta"]}\nrespuesta: {qa["respuesta"]}'
    texts_qas.append(text_qas)

prompt = f"""
    
Se proporcionará una lista de dos pares de preguntas y respuestas relacionadas con matrículas, trámites y procedimientos académicos de la Facultad de Ciencias de la Universidad Nacional de Ingeniería (UNI). 
Tu tarea es generar 5 conversaciones realistas entre un asistente de IA especializado en estos temas y un usuario.

Antes de generar las conversaciones, asegúrate de cumplir cada uno de los siguientes criterios:
    1. Las conversaciones deben ser por turnos entre el agente de IA y el usuario, siendo el usuario el que siempre comenzará la conversación.
    2. Las conversaciones deben tener al menos 3 turnos para cada hablante en la conversación.
    3. El usuario debe manejar un tono semiformal y natural de un estudiante universitario.
    4. El usuario no debe mencionar directamente el reglamento de matrícula de la Facultad de Ciencias.
    5. El asistente, ante agradecimientos o confirmaciones, debe responder adecuadamente y, además, mencionar que si tiene alguna otra duda, no dude en preguntar.
    6. Enfócate en crear diferentes conversaciones donde el usuario tenga la intención de obtener información que puedan ser inferida de los pares de preguntas y respuestas proporcionados  (delimitados por tres comillas invertidas).
    7. Evita repetir preguntas de manera idéntica en distintas conversaciones. Sé creativo y original en la forma de consultar por información del usuario, usando enfoques tanto directos como indirectos. Considera agregar un contexto proporcionado por el usuario antes de manifestar su duda.
    8. El asistente debe responder adecuadamente a las consultas del usuario inferiendo las respuestas de los pares de preguntas y respuestas proporcionados.
    9. Enriquece las conversaciones mediante interacciones naturales, como saludos, despedidas, confirmaciones y solicitudes de ayuda, entre otros elementos.

Finalmente, presenta cada una de las 5 conversaciones de la siguiente manera:    
    
Conversación 1:
            user: ...
            asistente: ...
            user: ...
            ...
    
Lista de pares de preguntas y respuestas: ```{texts_qas[0]}```
    
Conversaciones generadas:

    Conversación 1:
            user: Hola, tengo una pregunta sobre la convalidación de asignaturas. ¿Cuál es el porcentaje mínimo de contenido que deben coincidir las asignaturas para que proceda la convalidación?
            asistente: Para que proceda la convalidación, los respectivos sílabos de las asignaturas a convalidar deben coincidir al menos en un 75% de su contenido y de horas dictadas.
            user: Entiendo, tambien me gustaría saber ¿Cuál es el plazo para convalidaciones de traslados internos?.
            asistente: El período disponible para realizar convalidaciones de traslados internos se extiende hasta cinco (5) días hábiles contados a partir de la aprobación por parte del Consejo de Facultad o la autorización del Decano, conforme a lo establecido en el reglamento de matrícula de la Facultad de Ciencias de la UNI.
            user: ok gracias por la información.
            asistente: ¡De nada! Si tienes más preguntas en el futuro o necesitas ayuda, no dudes en preguntar. ¡Buena suerte con todo!
    
    Conversación: 2:
            user: Hola, buenas tardes.
            asistente: ¡Buenas tardes! ¿En qué puedo ayudarte hoy?
            user: tengo una consulta. Quiero solicitar la convalidacion de un curso pero no estoy seguro si hay un minimo de porcentaje de similitud entre los cursos.
            asistente: Para que la convalidación pueda llevarse a cabo, es necesario que los contenidos y la carga horaria de las asignaturas respectivas coincidan en al menos un 75%.
            user: Entiendo.
            asistente: Si tienes más preguntas, no dudes en preguntar. Estoy aquí para ayudar.
            user: ok 
            asistente: Perfecto. Si en el futuro tienes más preguntas, no dudes en comunicarte. ¡Que tengas un buen día!
    
    Conversacion 3:
            user: hola amigo
            asistente: ¡Hola! ¿Cómo puedo ayudarte hoy?
            user: tengo una duda, no estoy seguro si puedo convalidar el curso de Fisica I que lleve antes de trasladarme a la Facultad de Ciencias.
            asistente: Para que la convalidación sea efectiva, es necesario que el silabus y la carga horaria del curso de Física I que cursaste previamente, antes de tu traslado, coincidan en al menos un 75% con el curso que deseas convalidar.
            user: entiendo, entonces si no se cumplen esa condición no se pueden convalidar ?
            asistente: Es correcto, si las asignaturas no cumplen al menos en un 75% de su contenido y de horas dictadas no se pueden convalidar.
            user: ok, gracias.
            asistente: ¡De nada! Si tienes más preguntas o necesitas ayuda en el futuro, no dudes en preguntar. ¡Buena suerte con todo!
                
    Conversación 4:
            user: Hola que tal una consulta, acabo de trasladarme a la escuela de ingenieria fisica me diferon que puedo convalidar algunos cursos. Cuanto tiempo tengo para hacerlo?
            asistente: El plazo para realizar convalidaciones de traslados internos se extiende hasta cinco (5) días hábiles contados a partir de la aprobación por parte del Consejo de Facultad o la autorización del Decano, conforme a lo establecido en el reglamento de matrícula de la Facultad de Ciencias de la UNI.
            user: y que requisito deben cumplir los cursos para se puedan convalidar?
            asistente:  Para que la convalidación pueda llevarse a cabo, es necesario que los contenidos y la carga horaria de los cursos respectivos coincidan en al menos un 75%.
            user: ok
            asistente: Si tienes más preguntas, no dudes en consultar. Estoy aquí para ayudarte. 

    Conversación 5:
           user: dime existe un requisito para que que los cursos se puedan convalidar?
           asistente:  Para que la convalidación proceda, es necesario que los silabus y la carga horaria de los cursos respectivos coincidan en al menos un 75%.
           user: me acaban de aceptar mi traslado interno a la escuela de ciencias de la computacion. Hasta cuando puedo relizar la convalidacion de algunos cursos que ya he llevado?
           asistente: El plazo para realizar convalidaciones de traslados internos se extiende hasta cinco (5) días hábiles contados a partir de la aprobación por parte del Consejo de Facultad o la autorización del Decano, conforme a lo establecido en el reglamento de matrícula de la Facultad de Ciencias de la UNI.
           user: ok gracias por la informacion.
           asistente: ¡De nada! Si tienes más consultas, no dudes en preguntar. ¡Buena suerte con todo!

Lista de preguntas y respuestas: ```{texts_qas[2]}```

Conversaciones generadas:
"""
#print(prompt)

print(count_tokens(encoding,prompt))
messages =  [{'role':'user', 'content':prompt}]
response = get_completion_from_messages(messages, temperature=0, model= "gpt-4-1106-preview")
print(response)
print(count_tokens(encoding,response))