
from utils import get_completion_from_messages, set_openai_key, count_tokens
from dotenv import load_dotenv
import tiktoken

load_dotenv()

set_openai_key()

encoding = tiktoken.encoding_for_model('gpt-3.5-turbo')

qas_e1 = [{
                "pregunta": "\u00bfCu\u00e1l es el porcentaje m\u00ednimo de contenido que deben coincidir las asignaturas para que proceda la convalidaci\u00f3n?",
                "respuesta": "Para que proceda la convalidaci\u00f3n, los respectivos s\u00edlabos de las asignaturas a convalidar deben coincidir al menos en un 75% de su contenido y de horas dictadas."
        },
        {
                "pregunta": "\u00bfEl plazo para las convalidaciones de traslados internos es de hasta cinco (05) d\u00edas \u00fatiles desde la aprobaci\u00f3n del Consejo de Facultad o autorizaci\u00f3n del Decano?",
                "respuesta": "S\u00ed, el plazo para las convalidaciones de traslados internos es de hasta cinco (05) d\u00edas \u00fatiles desde la aprobaci\u00f3n del Consejo de Facultad o autorizaci\u00f3n del Decano, de acuerdo al reglamento de matr\u00edcula de la Facultad de Ciencias de la UNI."
        }]

text_qas_e1 = ""

for i , qa in enumerate(qas_e1):
    text_qas_e1 = text_qas_e1 + "\n"+ f'{i + 1}. {qa["pregunta"]}\nrespuesta: {qa["respuesta"]}'

qas_e2 = [{
                "pregunta": "\u00bfQu\u00e9 es el grupo cero de matr\u00edcula y qui\u00e9nes lo conforman seg\u00fan el reglamento acad\u00e9mico de la Facultad de Ciencias de la UNI?",
                "respuesta": "El grupo cero de matr\u00edcula es el listado que contiene las matr\u00edculas de quienes retornan de Separaci\u00f3n Temporal por Bajo Rendimiento Acad\u00e9mico y de los alumnos en Riesgo Acad\u00e9mico por asignaturas repetidas dos veces. La Comisi\u00f3n de Matr\u00edcula cierra el listado producido por la Tutor\u00eda, el d\u00eda anterior a la matricula y lo remite a la ORCE para su registro previo, con m\u00ednimo tres horas antes del inicio del primer turno de matr\u00edcula."
    },
    {
                "pregunta": "\u00bfSe puede retirar parcialmente de las asignaturas que son prerrequisito?",
                "respuesta": "No, no es posible retirarse parcialmente de las asignaturas que son prerrequisito, seg\u00fan el reglamento de matr\u00edcula de la Facultad de Ciencias de la UNI."
    }]

text_qas_e2 = ""

for i , qa in enumerate(qas_e2):
    text_qas_e2 = text_qas_e2 + "\n"+ f'{i + 1}. {qa["pregunta"]}\nrespuesta: {qa["respuesta"]}'


qas = [
     {
                "pregunta": "\u00bfQu\u00e9 se entiende por estudiante en riesgo acad\u00e9mico seg\u00fan el reglamento de la Facultad de Ciencias de la UNI?",
                "respuesta": "Un estudiante en riesgo acad\u00e9mico es aquel que tenga desaprobada una o m\u00e1s asignaturas en dos o tres oportunidades, debiendo pasar obligatoriamente por un proceso de tutor\u00eda acad\u00e9mica antes de su matr\u00edcula."
    },
    {
                "pregunta": "\u00bfSe puede solicitar la reincorporaci\u00f3n si se tiene una sanci\u00f3n vigente?",
                "respuesta": "No, no es posible solicitar la reincorporaci\u00f3n si se tiene una sanci\u00f3n vigente, seg\u00fan el reglamento de matr\u00edcula de la Facultad de Ciencias de la UNI."
    }
]

text_qas = ""

for i , qa in enumerate(qas):
    text_qas = text_qas + "\n"+ f'{i + 1}. {qa["pregunta"]}\nrespuesta: {qa["respuesta"]}'


prompt = f"""
    Se proporcionará una lista de dos pares de preguntas y respuestas.  
    Tu tarea es usar la información que pueda ser inferida de la lista de preguntas y respuestas para generar 5 conversaciones realistas entre un asistente de IA especializado en matrículas, trámites y procedimientos académicos de la Facultad de Ciencias de la Universidad Nacional de Ingeniería (UNI) y un usuario.
    Antes de generar las conversaciones, asegúrate de cumplir cada uno de los siguientes criterios:
        1. Las conversaciones deben ser por turnos entre el agente de IA y el usuario, siendo el usuario el que siempre comenzará la conversación.
        2. Las conversaciones deben tener al menos 3 turnos para cada hablante en la conversación.
        3. El usuario debe manejar un tono semiformal y natural de un estudiante universitario.
        4. El usuario no debe de mencionar directamente al reglemento de matricula de la facultad de ciencias.
        5. El asistente ante un agradecimiento o confirmación debe responder apropiandamente y adicionalmente mencionar que si tiene alguna otra duda que no dude en preguntar.
        6. Enfocate en crear diferentes conversaciones donde el usuario tenga la intención de obtener información que pueda ser inferida de los pares de preguntas y respuestas listadas proporcionados (delimitados por tres comillas invertidas).
        7. Evita repetir preguntas de manera idéntica en distintas conversaciones, en su lugar, sé creativo y original en la forma de consultar por informacion del usuario. Puedes emplear enfoques tanto de preguntas directas como indirectas. Además, considera agregar un contexto brindado por parte del usuario antes de manifestar su duda.
        8. El asistente debe responder apropiadamente a las consultas del usuario inferiendo la respuestas de los pares de preguntas y respuestas listadas proporcionados (delimitados por tres comillas invertidas).
        9. Enriquece las conversaciones mediante interacciones naturales entre el usuario y el asistente, que pueden abarcar saludos, despedidas, confirmaciones y solictudes de ayuda, entre otros elementos.
        
    Antes de generar cada conversación describe como la conversacion cumplira con todos los criterios mencionados anteriormente.            

    Finalmente, presenta cada una de las {5} conversaciones de la siguiente manera:
    
    Conversación 1:
            user: ...
            asistente: ...
            user: ...
            ...
    
    Lista de pares de preguntas y respuestas: ```{text_qas_e1}```
    
    Conversaciones generadas:

    La conversación 1 se dara por turnos, comenzando con el usuario, como se establece en el criterio 1. 
    Habrá 3 turnos para el usuario, y 3 turnos para el asistente, cumpliendo de esta manera con el criterio 2.
    El usuario mantendrá un tono semi formal acorde con el perfil de un estudiante universitario, cumpliendo asi con el criterio 3.
    El usuario consultará primeramente por el porcentaje mínimo de contenido que deben coincidir las asignaturas para que proceda la convalidación, sin hacer referencia directa al reglamento de Matrícula. Esta informacion puede ser inferida del par de pregunta y respuesta numero 1, cumpliendo así con los criterios 4 y 6.
    Luego, el asistente responderá apropiadamente a la consulta inferiendo la respuesta del par de pregunta y respuesta numero 1, cumpliendo con el criterio 8.
    En el segundo turno, siguiendo apropiamente la conversación el usuario manifestará su deseo de saber si el plazo para convalidaciones para de traslados internos sin mencionar directamente al reglamento de Matricula. Información que puede ser deducida del par de pregunta y respuesta numero 2. Por lo tanto, se cumple con el criterio 6 y 7.
    El asistente responderá apropiadamente a la consulta inferiendo la respuesta del pregunta y repuestas numero 2, cumpliendo asi el criterio 8.
    Finalmente, en el tercer turno, se llevará a cabo una interacción natural entre el asistente y el usuario. Durante esta interacción, el usuario expresará su agradecimiento por la información proporcionada, y el asistente responderá de manera apropiada. Además, recordará al usuario la disponibilidad para futuras consultas, asegurando así el cumplimiento de los criterios 5 y 8 establecidos.  

    Conversación 1:
            user: Hola, tengo una pregunta sobre la convalidación de asignaturas. ¿Cuál es el porcentaje mínimo de contenido que deben coincidir las asignaturas para que proceda la convalidación?
            asistente: Para que proceda la convalidación, los respectivos sílabos de las asignaturas a convalidar deben coincidir al menos en un 75% de su contenido y de horas dictadas.
            user: Entiendo, tambien me gustaría saber ¿Cuál es el plazo para convalidaciones de traslados internos?.
            asistente: El período disponible para realizar convalidaciones de traslados internos se extiende hasta cinco (5) días hábiles contados a partir de la aprobación por parte del Consejo de Facultad o la autorización del Decano, conforme a lo establecido en el reglamento de matrícula de la Facultad de Ciencias de la UNI.
            user: ok gracias por la información.
            asistente: ¡De nada! Si tienes más preguntas en el futuro o necesitas ayuda, no dudes en preguntar. ¡Buena suerte con todo!
    
    La conversación 2 se dara por turnos, comenzando con el usuario, como se establece en el criterio 1. 
    Habrá 4 turnos para el usuario, y 4 turnos para el asistente, cumpliendo de esta manera con el criterio 2.
    El usuario mantendrá un tono semi formal acorde con el perfil de un estudiante universitario, cumpliendo asi con el criterio 3.
    En el primer turno, para enriquecer la conversación con una interacción natural entre el asistente y el usuario. El usuario saludará al asistente, y el asistente responderá de manera apropiadamente al saludo y le consultara en que puede ayudarle. De esta menera, se cumple con lo establecido en el criterio 9.  
    En el segunto turno, el usuario consultará de manera directa pero distinta a la conversacion anterior sobre el porcentaje mínimo de contenido que deben coincidir las asignaturas para que proceda la convalidación. Esta informacion puede ser inferida del par de pregunta y respuesta numero 1, cumpliendo así con los criterios 4, 6 y 7
    Ademas, el usuario no hara referencia directa al reglamento de Matrícula, cumpliendo con el criterio 4.
    Luego, el asistente responderá apropiadamente a la consulta inferiendo la respuesta del par de pregunta y respuesta numero 1, cumpliendo con el criterio 8.
    En el tercer turno, para enriquecer la conversación con una interacción natural entre el asistente y el usuario, cumpliendo el criterio 9. El usuario manifestara comprender la informacion, y el asistente respondera apropiadamente indicando que si tiene mas preguntaras estara ahi para ayudar, cumpliendo con el criterio 5
    Finalmente, en el cuarto turno, para enriquecer la conversación con una interacción natural entre el asistente y el usuario , cumpliendo el criterio 9.  El usuario expresará su agradecimiento por la información proporcionada, y el asistente responderá de manera apropiada. Además, recordará al usuario la disponibilidad para futuras consultas, asegurando así el cumplimiento del criterio 5.
   
   Conversación: 2:
            user: Hola, buenas tardes.
            asistente: ¡Buenas tardes! ¿En qué puedo ayudarte hoy?
            user: tengo una consulta. Quiero solicitar la convalidacion de un curso pero no estoy seguro si hay un minimo de porcentaje de similitud entre los cursos.
            asistente: Para que la convalidación pueda llevarse a cabo, es necesario que los contenidos y la carga horaria de las asignaturas respectivas coincidan en al menos un 75%.
            user: Entiendo.
            asistente: Si tienes más preguntas, no dudes en preguntar. Estoy aquí para ayudar.
            user: ok 
            asistente: Perfecto. Si en el futuro tienes más preguntas, no dudes en comunicarte. ¡Que tengas un buen día!
     
    La conversación 3 se dara por turnos, comenzando con el usuario, como se establece en el criterio 1. 
    Habrá 4 turnos para el usuario, y 4 turnos para el asistente, cumpliendo de esta manera con el criterio 2.
    El usuario mantendrá un tono semi formal acorde con el perfil de un estudiante universitario, cumpliendo asi con el criterio 3.
    En el primer turno, para enriquecer la conversación con una interacción natural entre el asistente y el usuario. El usuario saludará al asistente, y el asistente responderá de manera apropiadamente al saludo y le consultara en que puede ayudarle. De esta menera, se cumple con lo establecido en el criterio 9.  
    En el segunto turno, el usuario consultará de una manera indirecta distinta a las conversaciones anteriores sobre una duda respecto a la posibilidad de convalidar un curso. Esta informacion puede ser inferida del par de pregunta y respuesta numero 1, cumpliendo así con los criterios 4, 6 y 7. 
    Ademas, el usuario no hara referencia directa al reglamento de Matrícula, cumpliendo con el criterio 4.
    Luego, el asistente responderá apropiadamente a la consulta inferiendo la respuesta del par de pregunta y respuesta numero 1, cumpliendo con el criterio 8.
    En el tercer turno, para enriquecer la conversación con una interacción natural entre el asistente y el usuario, cumpliendo el criterio 9.  
    El usuario expresará su deseo de confirmar que ha comprendido correctamente la información, según la cual, los cursos que no cumplan con la condición mencionada no podrán ser convalidados y el asistente respondera apropiadamente basado en la informacion proveida en el par de pregunta y respuesta numero 1, cumpliendo asi el criterio 8.
    Finalmente, en el cuarto turno, para enriquecer la conversación con una interacción natural entre el asistente y el usuario , cumpliendo el criterio 9.  El usuario expresará su agradecimiento por la información proporcionada, y el asistente responderá de manera apropiada. Además, recordará al usuario la disponibilidad para futuras consultas, asegurando así el cumplimiento del criterio 5.
   
    Conversacion 3:
            user: Hola
            asistente: ¡Hola! ¿Cómo puedo ayudarte hoy?
            user: tengo una duda, no estoy seguro si puedo convalidar el curso de Fisica I que lleve antes de trasladarme a la Facultad de Ciencias.
            asistente: Para que la convalidación sea efectiva, es necesario que el silabus y la carga horaria del curso de Física I que cursaste previamente, antes de tu traslado, coincidan en al menos un 75% con el curso que deseas convalidar.
            user: entiendo, entonces si no se cumplen esa condición no se pueden convalidar ?
            asistente: Es correcto, si las asignaturas no cumplen al menos en un 75% de su contenido y de horas dictadas no se pueden convalidar.
            user: ok, gracias.
            asistente: ¡De nada! Si tienes más preguntas o necesitas ayuda en el futuro, no dudes en preguntar. ¡Buena suerte con todo!
                

    La conversación 4 se dara por turnos, comenzando con el usuario, como se establece en el criterio 1. 
    Habrá 3 turnos para el usuario, y 3 turnos para el asistente, cumpliendo de esta manera con el criterio 2.
    El usuario mantendrá un tono semi formal acorde con el perfil de un estudiante universitario, cumpliendo asi con el criterio 3.
    En el primer turno, el usuario saludará y proverá un contexto sobre su situación antes de exponer su duda sobre el plazo para la convalidación de cursos de una manera diferente a las anteriones conversaciones, cumpliendo asi con el criterio 7.
    La información sobre el plazo para la convalidación de cursos puede ser inferida del par de preguntas numero 2, cumpliendo con el criterio 6. 
    Ademas, el usuario no hara referencia directa al reglamento de Matrícula, cumpliendo con el criterio 4.
    Luego, el asistente responderá apropiadamente a la consulta inferiendo la respuesta del par de pregunta y respuesta numero 2, cumpliendo con el criterio 8.
    En el segundo turno, el usuario de manera directa diferente a las otras conversaciones el deseo de saber que requisito deben cumplir los cursos poder convalidarse, cumpliendo asi el criterio 7.
    Esta consulta puede ser respondira basado en la informacion proveida en el par de preguntas y respuestas numero 1, cumpliendo con el criterio 6.
    Ademas, el usuario no hara referencia directa al reglamento de Matrícula, cumpliendo con el criterio 4.
    Luego, el asistente responderá apropiadamente a la consulta inferiendo la respuesta del par de pregunta y respuesta numero 1, cumpliendo con el criterio 8.
    Finalmente, en el tercer turno, para enriquecer la conversación con una interacción natural entre el asistente y el usuario , cumpliendo el criterio 9.  
    El usuario expresará de manera consisa haber entendido la informacion, y el asistente responderá de manera apropiada. Además, recordará al usuario la disponibilidad para futuras consultas, asegurando así el cumplimiento del criterio 5.
    
    Conversación 4:
            user: Hola que tal una consulta, acabo de trasladarme a la escuela de ingenieria fisica me diferon que puedo convalidar algunos cursos. Cuanto tiempo tengo para hacerlo?
            asistente: El plazo para realizar convalidaciones de traslados internos se extiende hasta cinco (5) días hábiles contados a partir de la aprobación por parte del Consejo de Facultad o la autorización del Decano, conforme a lo establecido en el reglamento de matrícula de la Facultad de Ciencias de la UNI.
            user: y que requisito deben cumplir los cursos para se puedan convalidar?
            asistente:  Para que la convalidación pueda llevarse a cabo, es necesario que los contenidos y la carga horaria de los cursos respectivos coincidan en al menos un 75%.
            user: ok
            asistente: Si tienes más preguntas, no dudes en consultar. Estoy aquí para ayudarte. 


    La conversación 5 se dara por turnos, comenzando con el usuario, como se establece en el criterio 1. 
    Habrá 3 turnos para el usuario, y 3 turnos para el asistente, cumpliendo de esta manera con el criterio 2.
    El usuario mantendrá un tono semi formal acorde con el perfil de un estudiante universitario, cumpliendo asi con el criterio 3.
    En el primer turno, de una manera directa y diferente a las otras conversaciones generadas anteriormente consultara sobre si existe algun requsito para que los cursos puedan convalidarse, cumpliendo asi el criterio 7.
    Esta consulta puede ser respondira basado en la informacion proveida en el par de preguntas y respuestas numero 1, cumpliendo con el criterio 6.
    Ademas, el usuario no hara referencia directa al reglamento de Matrícula, cumpliendo con el criterio 4.
    Luego, el asistente responderá apropiadamente a la consulta inferiendo la respuesta del par de pregunta y respuesta numero 2, cumpliendo con el criterio 8.
    En el segundo turno, proverá un contexto sobre su situación antes de exponer su duda sobre el plazo para la convalidación de cursos de una manera diferente a las anteriones conversaciones, cumpliendo asi con el criterio 7.
    La información sobre el plazo para la convalidación de cursos puede ser inferida del par de preguntas numero 2, cumpliendo con el criterio 6. 
    Ademas, el usuario no hara referencia directa al reglamento de Matrícula, cumpliendo con el criterio 4.
    Luego, el asistente responderá apropiadamente a la consulta inferiendo la respuesta del par de pregunta y respuesta numero 2, cumpliendo con el criterio 8.
    Finalmente, en el tercer turno, para enriquecer la conversación con una interacción natural entre el asistente y el usuario , cumpliendo el criterio 9.  
    El usuario expresará su agradecimiento por la información proporcionada, y el asistente responderá de manera apropiada. Además, recordará al usuario la disponibilidad para futuras consultas, asegurando así el cumplimiento del criterio 5.

    Conversación 5:
           user: dime existe un requisito para que que los cursos se puedan convalidar?
           asistente:  Para que la convalidación proceda, es necesario que los silabus y la carga horaria de los cursos respectivos coincidan en al menos un 75%.
           user: me acaban de aceptar mi traslado interno a la escuela de ciencias de la computacion. Hasta cuando puedo relizar la convalidacion de algunos cursos que ya he llevado?
           asistente: El plazo para realizar convalidaciones de traslados internos se extiende hasta cinco (5) días hábiles contados a partir de la aprobación por parte del Consejo de Facultad o la autorización del Decano, conforme a lo establecido en el reglamento de matrícula de la Facultad de Ciencias de la UNI.
           user: ok gracias por la informacion.
           asistente: ¡De nada! Si tienes más consultas, no dudes en preguntar. ¡Buena suerte con todo!

    Lista de preguntas y respuestas: ```{text_qas_e2}```

    Conversaciones generadas:
    
    La conversación 1 se dara por turnos, comenzando con el usuario, como se establece en el criterio 1. 
    Habrá 3 turnos para el usuario, y 3 turnos para el asistente, cumpliendo de esta manera con el criterio 2.
    El usuario mantendrá un tono semi formal acorde con el perfil de un estudiante universitario, cumpliendo asi con el criterio 3.
    El usuario consultará primeramente por información sobre quienes conforman el grupo cero de matricula, sin hacer referencia directa al reglamento de Matrícula. Esta informacion puede ser inferida del par de pregunta y respuesta numero 1, cumpliendo así con los criterios 4 y 6.
    Luego, el asistente responderá apropiadamente a la consulta inferiendo la respuesta del par de pregunta y respuesta numero 1, cumpliendo con el criterio 8.
    En el segundo turno, para enriquecer la conversacion se llevará a cabo una interacción natural entre el asistente y el usuario. Durante esta interacción, el usuario expresará su agradecimiento por la información proporcionada, y el asistente responderá de manera apropiada. Además, recordará al usuario la disponibilidad para futuras consultas, asegurando así el cumplimiento de los criterios 5 y 8 establecidos.  
    Finalmente, en el tercer turno, se llevará a cabo una interacción natural entre el asistente y el usuario. Durante esta interacción, el usuario se despedira del asistente, y el asistente responderá de manera apropiada. Además, recordará al usuario la disponibilidad para futuras consultas, asegurando así el cumplimiento de los criterios 5 y 8 establecidos.  
 
    Conversación 1:
           user: Hola que tal, una duda. ¿Quiénes conforman el grupo cero de matrícula?
           asistente: El grupo cero de matrícula es el listado que contiene las matrículas de quienes retornan de Separación Temporal por Bajo Rendimiento Académico y de los alumnos en Riesgo Académico por asignaturas repetidas dos veces. La Comisión de Matrícula cierra el listado producido por la Tutoría, el día anterior a la matricula y lo remite a la ORCE para su registro previo, con mínimo tres horas antes del inicio del primer turno de matrícula.
           user: Entiendo, gracias por la información.
           asistente: ¡De nada! Si tienes más preguntas en el futuro, no dudes en preguntar,
           user: hasta luego
           asistente: ¡Hasta luego! Si tienes más preguntas en el futuro, no dudes en volver. ¡Que tengas un buen día!
    
           
    La conversación 2 se dara por turnos, comenzando con el usuario, como se establece en el criterio 1. 
    Habrá 4 turnos para el usuario, y 4 turnos para el asistente, cumpliendo de esta manera con el criterio 2.
    El usuario mantendrá un tono semi formal acorde con el perfil de un estudiante universitario, cumpliendo asi con el criterio 3.
    En el primer turno, el usuario saludará y consultara de manera directa sobre si es posible el retiro de cursos que son prerrequisito. Esta información puede ser inferida del par de pregunta y respuesta numero 2, cumpliendo así con los criterios 4, 6 y 7
    En el segundo turno, para enriquecer la conversación con una interacción natural entre el asistente y el usuario, cumpliendo el criterio 9. El usuario manifestara comprender la informacion, y el asistente respondera apropiadamente indicando que si tiene mas preguntaras estara ahi para ayudar, cumpliendo con el criterio 5
    En el tercer turno, de una manera directa y diferente a las otras conversaciones generadas anteriormente consultara obre que es el grupo de cero de matricula, cumpliendo asi el criterio 7.
    La información que es el grupo cero de matricula puede ser inferida del par de preguntas numero 1, cumpliendo con el criterio 6. 
    Ademas, el usuario no hara referencia directa al reglamento de Matrícula, cumpliendo con el criterio 4.
    Luego, el asistente responderá apropiadamente a la consulta inferiendo la respuesta del par de pregunta y respuesta numero 1, cumpliendo con el criterio 8.
    Finalmente, en el cuarto turno, para enriquecer la conversación con una interacción natural entre el asistente y el usuario , cumpliendo el criterio 9.  El usuario expresará su agradecimiento por la información proporcionada, y el asistente responderá de manera apropiada. Además, recordará al usuario la disponibilidad para futuras consultas, asegurando así el cumplimiento del criterio 5.
   
    Conversación 2:
           user: Hola, buenas tardes. Tengo una duda sobre el retiro parcial. ¿Se puede retirar de los cursos que son prerrequisito?
           asistente: No, no es posible retirarse parcialmente de las asignaturas que son prerrequisito, según el reglamento de matrícula de la Facultad de Ciencias de la UNI.
           user: ok
           asistente: Si tienes más preguntas, no dudes en preguntar. Estoy aquí para ayudar.
           user: tambien tenia esta duda. ¿Que es Grupo Cero de matricula?
           asistente: El grupo cero de matrícula es el listado que incluye las matrículas de aquellos estudiantes que regresan de una Separación Temporal debido a un bajo rendimiento académico, así como de los alumnos en Riesgo Académico por haber repetido asignaturas en dos ocasiones. La Comisión de Matrícula cierra dicho listado, generado por el Departamento de Tutoría, el día anterior al inicio del proceso de matrícula. Posteriormente, lo remite a la Oficina de Registro y Control Estudiantil (ORCE) para su registro previo, asegurándose de hacerlo con un mínimo de tres horas de antelación al inicio del primer turno de matrícula.
           user: ya veo, gracias por la informacion.
           asistente: ¡De nada! Si tienes más preguntas, no dudes en preguntar. ¡Estoy aquí para ayudar!
    
    La conversación 3 se dara por turnos, comenzando con el usuario, como se establece en el criterio 1. 
    Habrá 4 turnos para el usuario, y 4 turnos para el asistente, cumpliendo de esta manera con el criterio 2.
    El usuario mantendrá un tono semi formal acorde con el perfil de un estudiante universitario, cumpliendo asi con el criterio 3.
    En el primer turno, consultara de manera directa y diferente a las otras conversaciones generadas anteriormente consultara sobre que es el grupo de cero de matricula, cumpliendo asi el criterio 7. 
    Esta información puede ser inferida del par de pregunta y respuesta numero 1, cumpliendo así con el criterio 6.
    Ademas, el usuario no hara referencia directa al reglamento de Matrícula, cumpliendo con el criterio 4.
    Luego, el asistente responderá apropiadamente a la consulta inferiendo la respuesta del par de pregunta y respuesta numero 1, cumpliendo con el criterio 8.
    En el segundo turno, para enriquecer la conversación con una interacción natural entre el asistente y el usuario, cumpliendo el criterio 9. El usuario manifestara su agradecimiento por la informacion, y el asistente respondera apropiadamente indicando que si tiene mas preguntaras estara ahi para ayudar, cumpliendo con el criterio 5
    En el tercer turno, de una manera directa y diferente a las otras conversaciones generadas anteriormente consultara sobre si es posible el retiro de cursos que son prerrequisito, cumpliendo asi el criterio 7.
    Esta información puede ser inferida del par de pregunta y respuesta numero 2, cumpliendo así con el criterio 6.
    Ademas, el usuario no hara referencia directa al reglamento de Matrícula, cumpliendo con el criterio 4.
    Luego, el asistente responderá apropiadamente a la consulta inferiendo la respuesta del par de pregunta y respuesta numero 2, cumpliendo con el criterio 8.
    Finalmente, en el cuarto turno, para enriquecer la conversación con una interacción natural entre el asistente y el usuario , cumpliendo el criterio 9.  El usuario expresará su agradecimiento por la información proporcionada, y el asistente responderá de manera apropiada. Además, recordará al usuario la disponibilidad para futuras consultas, asegurando así el cumplimiento del criterio 5.
   
    Conversación 3:
            user: me comentaron que ahora existe el grupo cero de matricula, me puedes explicar que es?.
            asistente: El grupo cero de matrícula comprende las matrículas de aquellos estudiantes que regresan de una Separación Temporal debido a un bajo rendimiento académico, así como de aquellos que se encuentran en Riesgo Académico por haber repetido una asignatura dos veces. La Comisión de Matrícula se encarga de cerrar el listado proporcionado por el departamento Tutoría el día previo al inicio de las matrículas y lo remite a la Oficina de Registro y Control Estudiantil (ORCE) para su registro previo, asegurándose de hacerlo con un mínimo de tres horas de antelación al inicio del primer turno de matrícula.
            user: entiendo gracias.
            asistente: ¡De nada! Si tienes más dudas, no dudes en preguntar. ¡Estoy aquí para ayudar!
            user: si tengo otra, queria retirarme de un curso pero es pre requisito de otra que estoy llevando, es posible es retiro?
            asistente: Lamentablemente, no es posible retirarse parcialmente de las asignaturas que son prerrequisito, de acuerdo con el reglamento de matrícula de la Facultad de Ciencias de la UNI.
            user: Entiendo, gracias por la información.
            asistente: ¡De nada! Si tienes más preguntas, no dudes en preguntar. ¡Buena suerte con todo!
   
    La conversación 4 se dara por turnos, comenzando con el usuario, como se establece en el criterio 1. 
    Habrá 3 turnos para el usuario, y 4 turnos para el asistente, cumpliendo de esta manera con el criterio 2.
    El usuario mantendrá un tono semi formal acorde con el perfil de un estudiante universitario, cumpliendo asi con el criterio 3.
    En el primer turno, el usuario consultará de manera directa y diferente a las otras conversaciones generadas anteriormente consultara sobre el retiro de parcial de cursos que son pre requisitos, cumpliendo asi el criterio 7. 
    Esta información puede ser inferida del par de pregunta y respuesta numero 2, cumpliendo así con el criterio 6.
    Ademas, el usuario no hara referencia directa al reglamento de Matrícula, cumpliendo con el criterio 4.
    Luego, el asistente responderá apropiadamente a la consulta inferiendo la respuesta del par de pregunta y respuesta numero 2, cumpliendo con el criterio 8.
    En el segundo turno, el usuario consultará de manera directa y diferente a las otras conversaciones generadas anteriormente consultara sobre quienes forman parte del grupo cero de matricula, cumpliendo asi el criterio 7. 
    Esta información puede ser inferida del par de pregunta y respuesta numero 1, cumpliendo así con el criterio 6.
    Ademas, el usuario no hara referencia directa al reglamento de Matrícula, cumpliendo con el criterio 4.
    Luego, el asistente responderá apropiadamente a la consulta inferiendo la respuesta del par de pregunta y respuesta numero 1, cumpliendo con el criterio 8.
    Finalmente, en el tercer turno, para enriquecer la conversación con una interacción natural entre el asistente y el usuario , cumpliendo el criterio 9.  El usuario expresará su agradecimiento por la información proporcionada, y el asistente responderá de manera apropiada. Además, recordará al usuario la disponibilidad para futuras consultas, asegurando así el cumplimiento del criterio 5.

    Conversación 4:
            user: tengo una pregunta sobre el retiro de cursos. ¿Se puede retirar parcialmente de los cursos que son prerrequisito?
            asistente: Según las normativas de matrícula de la Facultad de Ciencias de la UNI, no se permite realizar retiros parciales de cursos que son prerrequisitos.
            user: También tengo otra pregunta, ¿quiénes forman parte del grupo cero de matrícula?
            asistente: El grupo cero de matrícula está compuesto por aquellos estudiantes que retornan de una Separación Temporal debido a un Bajo Rendimiento Académico y por los alumnos que se encuentran en Riesgo Académico debido a haber repetido asignaturas en dos ocasiones. La Comisión de Matrícula cierra el listado generado por el departamento de Tutoría el día anterior al proceso de matrícula y lo remite a la Oficina de Registro y Control Estudiantil (ORCE) para su registro previo, asegurándose de enviarlo con un mínimo de tres horas antes del inicio del primer turno de matrícula.
            user: Entiendo, gracias por la información.
            asistente: Si tienes más preguntas, no dudes en preguntar. Estoy aquí para ayudarte.

    La conversación 5 se dara por turnos, comenzando con el usuario, como se establece en el criterio 1. 
    Habrá 3 turnos para el usuario, y 4 turnos para el asistente, cumpliendo de esta manera con el criterio 2.
    El usuario mantendrá un tono semi formal acorde con el perfil de un estudiante universitario, cumpliendo asi con el criterio 3.
    En el primer turno, el usuario consultará de manera directa y diferente a las otras conversaciones generadas anteriormente consultara sobre quienes forman parte del grupo de matricula, cumpliendo asi el criterio 7. 
    Esta información puede ser inferida del par de pregunta y respuesta numero 1, cumpliendo así con el criterio 6.
    Ademas, el usuario no hara referencia directa al reglamento de Matrícula, cumpliendo con el criterio 4.
    Luego, el asistente responderá apropiadamente a la consulta inferiendo la respuesta del par de pregunta y respuesta numero 1, cumpliendo con el criterio 8.
    En el segundo turno, el usuario consultará de manera directa y diferente a las otras conversaciones generadas anteriormente consultara sobre si se puede retirar de un curso que es prerequisito de otro, cumpliendo asi el criterio 7. 
    Esta información puede ser inferida del par de pregunta y respuesta numero 2, cumpliendo así con el criterio 6.
    Ademas, el usuario no hara referencia directa al reglamento de Matrícula, cumpliendo con el criterio 4.
    Luego, el asistente responderá apropiadamente a la consulta inferiendo la respuesta del par de pregunta y respuesta numero 2, cumpliendo con el criterio 8.
    Finalmente, en el tercer turno, para enriquecer la conversación con una interacción natural entre el asistente y el usuario , cumpliendo el criterio 9.  El usuario expresará su agradecimiento por la información proporcionada, y el asistente responderá de manera apropiada. Además, recordará al usuario la disponibilidad para futuras consultas, asegurando así el cumplimiento del criterio 5.

    Conversación 5:
           user:  Dime cómo puedo saber si formo parte del grupo cero de matrícula.
           asistente: El grupo cero de matrícula incluye a estudiantes que regresan de una Separación Temporal por Bajo Rendimiento Académico y a aquellos en Riesgo Académico por haber repetido asignaturas en dos ocasiones. Para determinar si eres parte de este grupo, verifica si cumples con alguno de estos criterios. La Comisión de Matrícula cierra el listado, generado por el departamento de Tutoría, un día antes del proceso de matrícula. Luego, lo envía a la Oficina de Registro y Control Estudiantil (ORCE) para su registro previo, asegurándose de enviarlo con al menos tres horas de anticipación al inicio del primer turno de matrícula..
           usuario: Entendido. También tenía curiosidad de saber si durante el ciclo puedo retirar un curso que es prerequisito de otro que estoy cursando.
           asistente: No, según el reglamento de matrícula de la Facultad de Ciencias de la UNI, no es posible retirarse parcialmente de asignaturas que sirven como prerrequisitos.
           usuario: ah ok gracias.
           asistente: ¡De nada! Si tienes más dudas , no dudes en preguntar. ¡Estoy aquí para ayudar!

     Lista de preguntas y respuestas: ```{text_qas}```

     Conversaciones generadas:
"""
print(count_tokens(encoding,prompt))
messages =  [{'role':'user', 'content':prompt}]
response = get_completion_from_messages(messages, temperature=0)
print(response)