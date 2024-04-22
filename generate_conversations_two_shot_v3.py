
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
    ],
    [ 
    {
        "pregunta": "\u00bfCu\u00e1l es el procedimiento para solicitar la reincorporaci\u00f3n a la Facultad de Ciencias de la UNI?",
        "respuesta": "El procedimiento para solicitar la reincorporaci\u00f3n a la Facultad de Ciencias de la UNI implica tramitar la solicitud en la plataforma de la ORCE seg\u00fan formato, con una anticipaci\u00f3n no menor de diez (10) d\u00edas \u00fatiles antes de la semana de matr\u00edcula y seg\u00fan el Calendario Acad\u00e9mico de la Universidad. Adem\u00e1s, se debe realizar el pago correspondiente a trav\u00e9s de la Caja UNI o bancos autorizados."
        
    },
    {
        "pregunta": "\u00bfEl Retiro Parcial procede para asignaturas repetidas dos (02) o m\u00e1s veces?",
        "respuesta": "No, el Retiro Parcial no procede para asignaturas repetidas dos (02) o m\u00e1s veces, seg\u00fan el reglamento de matr\u00edcula de la Facultad de Ciencias de la UNI, art\u00edculo 65\u00b0."
    }
    ]]


texts_qas = []
for qas in qas_lists:
    text_qas = ""
    for i , qa in enumerate(qas):
        text_qas = text_qas + "\n"+ f'{i + 1}. {qa["pregunta"]}\nrespuesta: {qa["respuesta"]}'
    texts_qas.append(text_qas)

print(texts_qas)
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

Antes de generar cada conversación, describe cómo la conversación cumplirá especificamente con los criterios 6 y 7.

Finalmente, presenta cada una de las 5 conversaciones de la siguiente manera:    
    
Conversación 1:
            user: ...
            asistente: ...
            user: ...
            ...
    
Lista de pares de preguntas y respuestas: ```{texts_qas[0]}```
    
Conversaciones generadas:

    La Conversación 1 se desorallará con 3 turnos para cada parte. 
    En el primer turno, el usuario consultará de manera directa sobre el porcentaje mínimo de coincidencia necesario para la convalidación de cursos. Esta información puede ser inferida del primer par de preguntas y respuestas, cumpliendo con el Criterio 6.
    En el segundo turno, el usuario consultará sobre el plazo para convalidaciones de traslados internos. Esta información puede ser inferida del segundo par de preguntas y respuestas, cumpliendo con el Criterio 6.
    El asistente responderá apropiamente en cada consulta inferiendo las respuestas de los pares de preguntas y respuestas proporcinados.
    La conversación se complementará y enriquesará con una interacción natural en el tercer turno, cumpliendo con el criterio 9.

    Conversación 1:
            user: Hola, tengo una pregunta sobre la convalidación de asignaturas. ¿Cuál es el porcentaje mínimo de contenido que deben coincidir las asignaturas para que proceda la convalidación?
            asistente: Para que proceda la convalidación, los respectivos sílabos de las asignaturas a convalidar deben coincidir al menos en un 75% de su contenido y de horas dictadas.
            user: Entiendo, tambien me gustaría saber ¿Cuál es el plazo para convalidaciones de traslados internos?.
            asistente: El período disponible para realizar convalidaciones de traslados internos se extiende hasta cinco (5) días hábiles contados a partir de la aprobación por parte del Consejo de Facultad o la autorización del Decano, conforme a lo establecido en el reglamento de matrícula de la Facultad de Ciencias de la UNI.
            user: ok gracias por la información.
            asistente: ¡De nada! Si tienes más preguntas en el futuro o necesitas ayuda, no dudes en preguntar. ¡Buena suerte con todo!
    
    La Conversación 2 se desorallará con 4 turnos para cada parte. 
    En el segundo turno, el usuario  consultará de manera directa pero con un enfoque sustancialmente distinto a la conversación generada anteriormente sobre el porcentaje mínimo de coincidencia necesario para la convalidación, cumpliendo con el criterio 7. La información solicitada puede ser inferida del primer par de preguntas y respuestas, cumpliendo con el Criterio 6.
    El asistente responderá apropiamente en cada consulta inferiendo las respuestas de los pares de preguntas y respuestas proporcionados.
    La Conversación se complementará y enriquesará con interacciones naturales en el primer, tercer y cuarto turno, cumpliendo con el criterio 9.

    Conversación: 2:
            user: Hola, buenas tardes.
            asistente: ¡Buenas tardes! ¿En qué puedo ayudarte hoy?
            user: tengo una consulta. Quiero solicitar la convalidacion de un curso pero no estoy seguro si hay un minimo de porcentaje de similitud entre los cursos.
            asistente: Para que la convalidación pueda llevarse a cabo, es necesario que los contenidos y la carga horaria de las asignaturas respectivas coincidan en al menos un 75%.
            user: Entiendo.
            asistente: Si tienes más preguntas, no dudes en preguntar. Estoy aquí para ayudar.
            user: ok 
            asistente: Perfecto. Si en el futuro tienes más preguntas, no dudes en comunicarte. ¡Que tengas un buen día!
    
    La Conversación 3 se desorallará con 4 turnos para cada parte. 
    En el segundo turno, el usuario consultará de manera directa pero distinta a las conversaciónes generadas anteriormente sobre una duda respecto a la posibilidad de convalidar un curso, cumpliendo así con el Criterio 7. La información solicitada puede ser inferida del primer par de preguntas y respuestas, cumpliendo con el Criterio 6.
    En el tercer turno, expresará su deseo de confirmar que ha comprendido correctamente la información, según la cual, los cursos que no cumplan con la condición mencionada no podrán ser convalidados. 
    El asistente responderá apropiamente en cada consulta inferiendo las respuestas de los pares de preguntas y respuestas proporcionados.
    La conversación se complementará y enriquesará con interacciones naturales en el primer y cuarto turno, cumpliendo con el criterio 9.

    Conversacion 3:
            user: Hola
            asistente: ¡Hola! ¿Cómo puedo ayudarte hoy?
            user: tengo una duda, no estoy seguro si puedo convalidar el curso de Fisica I que lleve antes de trasladarme a la Facultad de Ciencias.
            asistente: Para que la convalidación sea efectiva, es necesario que el silabus y la carga horaria del curso de Física I que cursaste previamente, antes de tu traslado, coincidan en al menos un 75% con el curso que deseas convalidar.
            user: entiendo, entonces si no se cumplen esa condición no se pueden convalidar ?
            asistente: Es correcto, si las asignaturas no cumplen al menos en un 75% de su contenido y de horas dictadas no se pueden convalidar.
            user: ok, gracias.
            asistente: ¡De nada! Si tienes más preguntas o necesitas ayuda en el futuro, no dudes en preguntar. ¡Buena suerte con todo!

    La Conversación 4 se desorallará con 3 turnos para cada parte. 
    En el primer turno, el usuario saludará, dará contexto sobre su situación y planteará su pregunta sobre el plazo para la convalidación de cursos de manera diferente a las conversaciones generadas anteriormente, cumplimiento con el criterios 7. La información solicitada puede ser inferida del segundo par de preguntas y respuestas, cumpliendo con el Criterio 6.
    En el segundo turno, el usuario consultará de manera directa pero distinta a las conversaciónes generadas anteriormente sobre el requisito para la convalidación de cursos, cumplimiento con el criterios 7. La información solicitada puede ser inferida del primer par de preguntas y respuestas, cumpliendo con el Criterio 6.
    El asistente responderá apropiamente en cada consulta inferiendo las respuestas de los pares de preguntas y respuestas proporcionados.
    La conversación se complementará y enriquesará con una interacción natural en el tercer turno, cumpliendo con el criterio 9.
           
    Conversación 4:
            user: Hola que tal una consulta, acabo de trasladarme a la escuela de ingenieria fisica me diferon que puedo convalidar algunos cursos. Cuanto tiempo tengo para hacerlo?
            asistente: El plazo para realizar convalidaciones de traslados internos se extiende hasta cinco (5) días hábiles contados a partir de la aprobación por parte del Consejo de Facultad o la autorización del Decano, conforme a lo establecido en el reglamento de matrícula de la Facultad de Ciencias de la UNI.
            user: y que requisito deben cumplir los cursos para se puedan convalidar?
            asistente:  Para que la convalidación pueda llevarse a cabo, es necesario que los contenidos y la carga horaria de los cursos respectivos coincidan en al menos un 75%.
            user: ok
            asistente: Si tienes más preguntas, no dudes en consultar. Estoy aquí para ayudarte. 

    La Conversación 5 se desorallará con 3 turnos para cada parte. 
    En el primer turno, el usuario consultará de manera directa pero distinta a las conversaciónes generadas anteriormente sobre sobre si existe algun requsito para que los cursos puedan convalidarse, cumplimiento con el criterio 7. La información solicitada puede ser inferida del primer par de preguntas y respuestas, cumpliendo así con el Criterio 6.
    En el segundo turno, el usuario dará contexto sobre su situación y planteará su pregunta sobre el plazo para la convalidación de cursos de manera diferente a las conversaciones generadas anteriormente, cumplimiento con el criterios 7. La información solicitada puede ser inferida del segundo par de preguntas y respuestas, cumpliendo así con el Criterio 6.
    El asistente responderá apropiamente en cada consulta inferiendo las respuestas de los pares de preguntas y respuestas proporcionados.
    La conversación se complementará y enriquesará con una interacción natural en el tercer turno, cumpliendo con el criterio 9.

    Conversación 5:
           user: dime existe un requisito para que que los cursos se puedan convalidar?
           asistente:  Para que la convalidación proceda, es necesario que los silabus y la carga horaria de los cursos respectivos coincidan en al menos un 75%.
           user: me acaban de aceptar mi traslado interno a la escuela de ciencias de la computacion. Hasta cuando puedo relizar la convalidacion de algunos cursos que ya he llevado?
           asistente: El plazo para realizar convalidaciones de traslados internos se extiende hasta cinco (5) días hábiles contados a partir de la aprobación por parte del Consejo de Facultad o la autorización del Decano, conforme a lo establecido en el reglamento de matrícula de la Facultad de Ciencias de la UNI.
           user: ok gracias por la informacion.
           asistente: ¡De nada! Si tienes más consultas, no dudes en preguntar. ¡Buena suerte con todo!

Lista de preguntas y respuestas: ```{texts_qas[1]}```

Conversaciones generadas:
    
    La Conversación 1 se desorallará con 3 turnos para cada parte. 
    En el primer turno, el usuario saludará y consultará de manera directa sobre quienes conforman el grupo cero de matricula. La información solicitada puede ser inferida del primer par de preguntas y respuestas, cumpliendo así con el Criterio 6.
    El asistente responderá apropiamente en cada consulta inferiendo las respuestas de los pares de preguntas y respuestas proporcinados.
    La conversación se complementará y enriquesará con interacciones naturales en el segundo y tercer turno, cumpliendo con el criterio 9.

    Conversación 1:
           user: Hola que tal, una duda. ¿Quiénes conforman el grupo cero de matrícula?
           asistente: El grupo cero de matrícula es el listado que contiene las matrículas de quienes retornan de Separación Temporal por Bajo Rendimiento Académico y de los alumnos en Riesgo Académico por asignaturas repetidas dos veces. La Comisión de Matrícula cierra el listado producido por la Tutoría, el día anterior a la matricula y lo remite a la ORCE para su registro previo, con mínimo tres horas antes del inicio del primer turno de matrícula.
           user: Entiendo, gracias por la información.
           asistente: ¡De nada! Si tienes más preguntas en el futuro, no dudes en preguntar,
           user: hasta luego
           asistente: ¡Hasta luego! Si tienes más preguntas en el futuro, no dudes en volver. ¡Que tengas un buen día!
    
    La Conversación 2 se desorallará con 4 turnos para cada parte. 
    En el primer turno, el usuario saludará y consultará de manera directa pero con un enfoque sustancialmente distinto a la conversación generada anteriormente sobre la posibilidad del retiro de cursos que son prerrequisito, cumplimiento con el criterio 7. La información solicitada puede ser inferida del segundo par de preguntas y respuestas, cumpliendo así con el Criterio 6.
    En el tercer turno, el usuario  consultará de manera directa pero con un enfoque sustancialmente distinto a la conversación generada anteriormente sobre que es el grupo de cero de matricula, cumplimiento con el criterio 7. La información solicitada puede ser inferida del primer par de preguntas y respuestas, cumpliendo así con el Criterio 6.
    El asistente responderá apropiamente en cada consulta inferiendo las respuestas de los pares de preguntas y respuestas proporcionados.
    La conversación se complementará y enriquesará con interacciones naturales en el segundo y cuarto turno, cumpliendo con el criterio 9.
 
    Conversación 2:
           user: Hola, buenas tardes. Tengo una duda sobre el retiro parcial. ¿Se puede retirar de los cursos que son prerrequisito?
           asistente: No, no es posible retirarse parcialmente de las asignaturas que son prerrequisito, según el reglamento de matrícula de la Facultad de Ciencias de la UNI.
           user: ok
           asistente: Si tienes más preguntas, no dudes en preguntar. Estoy aquí para ayudar.
           user: tambien tenia esta duda. ¿Que es Grupo Cero de matricula?
           asistente: El grupo cero de matrícula es el listado que incluye las matrículas de aquellos estudiantes que regresan de una Separación Temporal debido a un bajo rendimiento académico, así como de los alumnos en Riesgo Académico por haber repetido asignaturas en dos ocasiones. La Comisión de Matrícula cierra dicho listado, generado por el Departamento de Tutoría, el día anterior al inicio del proceso de matrícula. Posteriormente, lo remite a la Oficina de Registro y Control Estudiantil (ORCE) para su registro previo, asegurándose de hacerlo con un mínimo de tres horas de antelación al inicio del primer turno de matrícula.
           user: ya veo, gracias por la informacion.
           asistente: ¡De nada! Si tienes más preguntas, no dudes en preguntar. ¡Estoy aquí para ayudar!
    
    La Conversación 3 se desorallará con 4 turnos para cada parte. 
    En el primer turno, el usuario consultará de manera directa pero con un enfoque sustancialmente distinto a la conversación generada anteriormente sobre que es el grupo de cero de matrícula, cumplimiento con el criterio 7. La información solicitada puede ser inferida del primer par de preguntas y respuestas, cumpliendo así con el Criterio 6.
    En el tercer turno, el usuario  consultará de manera directa pero con un enfoque sustancialmente distinto a la conversación generada anteriormente sobre si es posible el retiro de cursos que son prerrequisito, cumplimiento con el criterio 7. La información solicitada puede ser inferida del segundo par de preguntas y respuestas, cumpliendo así con el Criterio 6.
    El asistente responderá apropiamente en cada consulta inferiendo las respuestas de los pares de preguntas y respuestas proporcionados.
    La conversación se complementará y enriquesará con interacciones naturales en el segundo y cuarto turno, cumpliendo con el criterio 9.
    
    Conversación 3:
            user: me comentaron que ahora existe el grupo cero de matricula, me puedes explicar que es?.
            asistente: El grupo cero de matrícula comprende las matrículas de aquellos estudiantes que regresan de una Separación Temporal debido a un bajo rendimiento académico, así como de aquellos que se encuentran en Riesgo Académico por haber repetido una asignatura dos veces. La Comisión de Matrícula se encarga de cerrar el listado proporcionado por el departamento Tutoría el día previo al inicio de las matrículas y lo remite a la Oficina de Registro y Control Estudiantil (ORCE) para su registro previo, asegurándose de hacerlo con un mínimo de tres horas de antelación al inicio del primer turno de matrícula.
            user: entiendo gracias.
            asistente: ¡De nada! Si tienes más dudas, no dudes en preguntar. ¡Estoy aquí para ayudar!
            user: si tengo otra, queria retirarme de un curso pero es pre requisito de otra que estoy llevando, es posible es retiro?
            asistente: Lamentablemente, no es posible retirarse parcialmente de las asignaturas que son prerrequisito, de acuerdo con el reglamento de matrícula de la Facultad de Ciencias de la UNI.
            user: Entiendo, gracias por la información.
            asistente: ¡De nada! Si tienes más preguntas, no dudes en preguntar. ¡Buena suerte con todo!
   
    La Conversación 4 se desorallará con 3 turnos para cada parte. 
    En el primer turno, el usuario consultará de manera directa pero con un enfoque sustancialmente distinto a las conversaciones generada anteriormente sobre si es posible el retiro de cursos que son prerrequisito, cumplimiento con el criterio 7. La información solicitada puede ser inferida del segundo par de preguntas y respuestas, cumpliendo así con el Criterio 6.
    En el segundo turno, el usuario consultará de manera directa pero con un enfoque sustancialmente distinto a las conversaciones generada anteriormente sobre quienes forman parte del grupo cero de matricula, cumplimiento con el criterio 7. Esta información puede ser inferida del primer par de preguntas y respuestas, cumpliendo así con el Criterio 6.
    El asistente responderá apropiamente en cada consulta inferiendo las respuestas de los pares de preguntas y respuestas proporcionados.
    La conversación se complementará y enriquesará con una interacción natural en el tercer turno, cumpliendo con el criterio 9.
    
    Conversación 4:
            user: tengo una pregunta sobre el retiro de cursos. ¿Se puede retirar parcialmente de los cursos que son prerrequisito?
            asistente: Según las normativas de matrícula de la Facultad de Ciencias de la UNI, no se permite realizar retiros parciales de cursos que son prerrequisitos.
            user: También tengo otra pregunta, ¿quiénes forman parte del grupo cero de matrícula?
            asistente: El grupo cero de matrícula está compuesto por aquellos estudiantes que retornan de una Separación Temporal debido a un Bajo Rendimiento Académico y por los alumnos que se encuentran en Riesgo Académico debido a haber repetido asignaturas en dos ocasiones. La Comisión de Matrícula cierra el listado generado por el departamento de Tutoría el día anterior al proceso de matrícula y lo remite a la Oficina de Registro y Control Estudiantil (ORCE) para su registro previo, asegurándose de enviarlo con un mínimo de tres horas antes del inicio del primer turno de matrícula.
            user: Entiendo, gracias por la información.
            asistente: Si tienes más preguntas, no dudes en preguntar. Estoy aquí para ayudarte.

    La Conversación 5 se desorallará con 3 turnos para cada parte. 
    En el primer turno, el usuario consultará de manera directa pero con un enfoque sustancialmente distinto a las conversaciones generada anteriormente sobre quienes forman parte del grupo cero de matricula, cumplimiento con el criterio 7. La información solicitada puede ser inferida del primer par de preguntas y respuestas, cumpliendo así con el Criterio 6.
    En el segundo turno, el usuario consultará de manera directa pero con un enfoque sustancialmente distinto a las conversaciones generada anteriormente sobre si es posible el retiro de cursos que son prerrequisito, cumplimiento con el criterio 7. La información solicitada puede ser inferida del segundo par de preguntas y respuestas, cumpliendo así con el Criterio 6.
    El asistente responderá apropiamente en cada consulta inferiendo las respuestas de los pares de preguntas y respuestas proporcionados.
    La conversación se complementará y enriquesará con una interacción natural en el tercer turno, cumpliendo con el criterio 9.
 
    Conversación 5:
           user:  Dime cómo puedo saber si formo parte del grupo cero de matrícula.
           asistente: El grupo cero de matrícula incluye a estudiantes que regresan de una Separación Temporal por Bajo Rendimiento Académico y a aquellos en Riesgo Académico por haber repetido asignaturas en dos ocasiones. Para determinar si eres parte de este grupo, verifica si cumples con alguno de estos criterios. La Comisión de Matrícula cierra el listado, generado por el departamento de Tutoría, un día antes del proceso de matrícula. Luego, lo envía a la Oficina de Registro y Control Estudiantil (ORCE) para su registro previo, asegurándose de enviarlo con al menos tres horas de anticipación al inicio del primer turno de matrícula..
           usuario: Entendido. También tenía curiosidad de saber si durante el ciclo puedo retirar un curso que es prerequisito de otro que estoy cursando.
           asistente: No, según el reglamento de matrícula de la Facultad de Ciencias de la UNI, no es posible retirarse parcialmente de asignaturas que sirven como prerrequisitos.
           usuario: ah ok gracias.
           asistente: ¡De nada! Si tienes más dudas , no dudes en preguntar. ¡Estoy aquí para ayudar!

Lista de preguntas y respuestas: ```{texts_qas[2]}```

Conversaciones generadas:

    La Conversación 1 se desorallará con 3 turnos para cada parte. 
    En el primer turno, el usuario saludará y consultará de manera directa sobre que se entiende por estudiante en riesgo académico. La información solicitada puede ser inferida del primer par de preguntas y respuestas, cumpliendo así con el Criterio 6.
    El asistente responderá apropiamente en cada consulta inferiendo las respuestas de los pares de preguntas y respuestas proporcinados.
    La conversación se complementará y enriquesará con interacciones naturales en el segundo y tercer turno, cumpliendo con el criterio 9.
    
    Conversación 1:
           user: Hola, tengo una pregunta sobre el riesgo académico. ¿Qué se entiende por estudiante en riesgo académico?
           asistente: Un estudiante en riesgo académico es aquel que tenga desaprobada una o más asignaturas en dos o tres oportunidades, debiendo pasar obligatoriamente por un proceso de tutoría académica antes de su matrícula.
           user: Entiendo, gracias por la información.
           asistente: ¡De nada! Si tienes más preguntas en el futuro, no dudes en preguntar.
           user: Hasta luego.
           asistente: ¡Hasta luego! Si tienes más preguntas en el futuro, no dudes en volver. ¡Que tengas un buen día!

    La Conversación 2 se desorallará con 4 turnos para cada parte. 
    En el primer turno, el usuario saludará y consultará de manera directa pero con un enfoque sustancialmente distinto a la conversación generada anteriormente sobre la posibilidad de reincorporación con una sancion vigente, cumplimiento con el criterio 7. La información solicitada puede ser inferida del segundo par de preguntas y respuestas, cumpliendo así con el Criterio 6.
    En el tercer turno, el usuario consultará de manera directa pero con un enfoque sustancialmente distinto a la conversación generada anteriormente sobre que es un estudiante en riesgo academico, cumplimiento con el criterio 7. La información solicitada puede ser inferida del primer par de preguntas y respuestas, cumpliendo así con el Criterio 6.
    El asistente responderá apropiamente en cada consulta inferiendo las respuestas de los pares de preguntas y respuestas proporcionados.
    La conversación se complementará y enriquesará con interacciones naturales en el segundo y cuarto turno, cumpliendo con el criterio 9.
 
    Conversación 2:
            user: Hola, buenas tardes. Tengo una duda sobre las sanciones. ¿Se puede solicitar la reincorporación si se tiene una sanción vigente?
            asistente: No, no es posible solicitar la reincorporación si se tiene una sanción vigente, según el reglamento de matrícula de la Facultad de Ciencias de la UNI.
            user: Entiendo, gracias por la información.
            asistente: Si tienes más preguntas, no dudes en preguntar. Estoy aquí para ayudar.
            user: tambien tenia esta duda. ¿Qué es un estudiante en riesgo académico?
            asistente: Un estudiante en riesgo académico es aquel que tenga desaprobada una o más asignaturas en dos o tres oportunidades, debiendo pasar obligatoriamente por un proceso de tutoría académica antes de su matrícula.
            user: ya veo, gracias por la informacion.
            asistente: ¡De nada! Si tienes más preguntas, no dudes en preguntar. ¡Estoy aquí para ayudar!

    La Conversación 3 se desorallará con 4 turnos para cada parte. 
    En el primer turno, el usuario saludará y consultará de manera directa pero con un enfoque sustancialmente distinto a la conversaciones generadas anteriormente sobre que se entiende por estudiante en riesgo académico, cumplimiento con el criterio 7. La información solicitada puede ser inferida del primer par de preguntas y respuestas, cumpliendo así con el Criterio 6.
    En el tercer turno, el usuario consultará de manera indirecta con un enfoque sustancialmente distinto a la conversaciones generadas anteriormente sobre la posibilidad de reincorporación con una sancion vigente, cumplimiento con el criterio 7. La información solicitada puede ser inferida del primer par de preguntas y respuestas, cumpliendo así con el Criterio 6.
    El asistente responderá apropiamente en cada consulta inferiendo las respuestas de los pares de preguntas y respuestas proporcionados.
    La conversación se complementará y enriquesará con interacciones naturales en el segundo y cuarto turno, cumpliendo con el criterio 9.
 
    Conversación 3:
            user: Hola, me gustaría saber qué se entiende por estudiante en riesgo académico.
            asistente: Un estudiante en riesgo académico se refiere a aquel que ha desaprobado una o más asignaturas en dos o tres ocasiones, siendo necesario que pase obligatoriamente por un proceso de tutoría académica antes de su matrícula.
            user: Entiendo
            asistente: ¡De nada! Si tienes más dudas, no dudes en preguntar. ¡Estoy aquí para ayudar!
            user: otra duda que tengo es que mi compañero ha sido suspendido por un año de la universidad, pero queria solicitar la reincorporacion el siguiente semestre. 
            asistente: Lamentablemente, no es posible solicitar la reincorporación si se tiene una sanción vigente, según el reglamento de matrícula de la Facultad de Ciencias de la UNI.
            user: Entiendo, gracias por la información.
            asistente: ¡De nada! Si tienes más preguntas, no dudes en preguntar. ¡Buena suerte con todo!
    
    La Conversación 4 se desorallará con 4 turnos para cada parte. 
    En el primer turno, el usuario saludará, proveerá un contexto y consultará de manera directa pero con un enfoque sustancialmente distinto a la conversaciones generadas anteriormente sobre que se entiende por estudiante en riesgo académico, cumplimiento con el criterio 7. La información solicitada puede ser inferida del primer par de preguntas y respuestas, cumpliendo así con el Criterio 6.
    En el tercer turno, el usuario consultará de manera directa pero con un enfoque sustancialmente distinto a la conversaciones generadas anteriormente sobre la posibilidad de reincorporación con una sancion vigente, cumplimiento con el criterio 7. La información solicitada puede ser inferida del segundo par de preguntas y respuestas, cumpliendo así con el Criterio 6.
    El asistente responderá apropiamente en cada consulta inferiendo las respuestas de los pares de preguntas y respuestas proporcionados.
    La conversación se complementará y enriquesará con interacciones naturales en el segundo y cuarto turno, cumpliendo con el criterio 9.
 
    Conversación 4:
            user: Hola, el ciclo pasado desaprove por segunda vez un curso y me han dicho que ahora seria un estudiante en riesgo academico que significa o implica esto?
            asistente: Un estudiante en riesgo académico es aquel que tenga desaprobada una o más asignaturas en dos o tres oportunidades, debiendo pasar obligatoriamente por un proceso de tutoría académica antes de su matrícula.
            user: Entiendo, gracias por la información.
            asistente: Si tienes más preguntas, no dudes en preguntar. Estoy aquí para ayudarte.
            user: También quería saber si se puede solicitar la reincorporación si se tiene algun tipo de sanción.
            asistente: No, no es posible solicitar la reincorporación si se tiene una sanción vigente, según el reglamento de matrícula de la Facultad de Ciencias de la UNI.
            user: Entiendo, gracias por la información.
            asistente: Si tienes más preguntas, no dudes en preguntar. Estoy aquí para ayudarte.

    La Conversación 5 se desorallará con 4 turnos para cada parte. 
    En el primer turno, el usuario saludará, proveerá un contexto y consultará de manera directa pero con un enfoque sustancialmente distinto a la conversaciones generadas sobre que se entiende por estudiante en riesgo académico, cumplimiento con el criterio 7. La información solicitada puede ser inferida del segundo par de preguntas y respuestas, cumpliendo así con el Criterio 6.
    En el tercer turno, el usuario proveerá un contexto y consultará de manera directa pero con un enfoque sustancialmente distinto a la conversaciones generadas sobre la desaprobación de un curso por segunda vez y sus implicaciones en la matrícula, cumplimiento con el criterio 7. La información solicitada puede ser inferida del primer par de preguntas y respuestas, cumpliendo así con el Criterio 6.
    El asistente responderá apropiamente en cada consulta inferiendo las respuestas de los pares de preguntas y respuestas proporcionados.
    La conversación se complementará y enriquesará con interacciones naturales en el segundo y cuarto turno, cumpliendo con el criterio 9.
 
    Conversación 5:
            user: Hola, he sido suspendido de la universidad y quiero reincorporarme el siguiente ciclo, es posible?
            asistente: En caso que la sancion siga vigente en el siguiente periodo académico no es posible la reincorporación, según el reglamento de matrícula de la Facultad de Ciencias de la UNI.
            user: ok
            asistente: Si tienes más dudas, no dudes en preguntar. ¡Estoy aquí para ayudar!
            user: un compañero ha desaprobado un curso por segunda vez queria saber si podra seguir matricurlandose de manera normal en el siguiente ciclo?
            asistente: Un estudiante que tenga desaprobada una o más asignaturas en dos o tres oportunidades se califica como "estudiante en riesgo académico", y deberá pasar obligatoriamente por un proceso de tutoría académica antes de su matrícula.
            user: Entiendo, gracias por la información.
            asistente: ¡De nada! Si tienes más preguntas, no dudes en preguntar. ¡Buena suerte con todo!

Lista de preguntas y respuestas: ```{texts_qas[3]}```

Conversaciones generadas:

    La Conversación 1 se desorallará con 3 turnos para cada parte. 
    En el primer turno, el usuario saludará y consultará de manera directa sobre el plazo para realizar un retiro parcial de asignaturas. La información solicitada puede ser inferida del primer par de preguntas y respuestas, cumpliendo así con el Criterio 6.
    El asistente responderá apropiadamente en cada consulta inferiendo las respuestas de los pares de preguntas y respuestas proporcionados.
    La conversación se complementará y enriquesará con interacciones naturales en el segundo y tercer turno, cumpliendo con el criterio 9.

    Conversación 1:
            user: Hola, tengo una pregunta sobre el retiro de asignaturas. ¿Cuál es el plazo para realizar un retiro parcial de asignaturas?
            asistente: El plazo para realizar un retiro parcial de asignaturas es hasta el último día útil de la quinta semana después del inicio de clases del período académico.
            user: Entiendo, gracias por la información.
            asistente: ¡De nada! Si tienes más preguntas en el futuro, no dudes en preguntar.
            user: Hasta luego.
            asistente: ¡Hasta luego! Si tienes más preguntas en el futuro, no dudes en volver. ¡Que tengas un buen día!

    La Conversación 2 se desorallará con 4 turnos para cada parte. 
    En el primer turno, el usuario saludará y consultará de manera directa pero con un enfoque sustancialmente distinto a la conversaciones generadas anteriormente sobre si el proceso de matrícula se realiza a través del Portal Web del Sistema de Matrícula UNI, cumplimiento con el criterio 7. La información solicitada puede ser inferida del segundo par de preguntas y respuestas, cumpliendo así con el Criterio 6.
    En el tercer turno, el usuario consultará de manera directa pero con un enfoque sustancialmente distinto a la conversaciones generadas anteriormente sobre el plazo para realizar un retiro parcial de asignaturas, cumplimiento con el criterio 7. La información solicitada puede ser inferida del primer par de preguntas y respuestas, cumpliendo así con el Criterio 6.
    El asistente responderá apropiadamente en cada consulta inferiendo las respuestas de los pares de preguntas y respuestas proporcionados.
    La conversación se complementará y enriquesará con interacciones naturales en el segundo y cuarto turno, cumpliendo con el criterio 9.

    Conversación 2:
            user: Hola, buenas tardes. Tengo una duda sobre el proceso de matrícula. ¿El proceso de matrícula se realiza a través del Portal Web del Sistema de Matrícula UNI?
            asistente: Sí, el proceso de matrícula se realiza a través del Portal Web del Sistema de Matrícula UNI, suministrado por la ORCE, según lo establecido en el reglamento de matrícula de la Facultad de Ciencias de la UNI.
            user: Entiendo, gracias por la información.
            asistente: Si tienes más preguntas, no dudes en preguntar. Estoy aquí para ayudar.
            user: también quería que me indiques hasta cuando se puede realizar el retiro parcial?
            asistente: El plazo para realizar un retiro parcial de asignaturas es hasta el último día útil de la quinta semana después del inicio de clases del período académico.
            user: Entiendo, gracias por la información.
            asistente: ¡De nada! Si tienes más preguntas, no dudes en preguntar. ¡Buena suerte con todo!

    La Conversación 3 se desorallará con 4 turnos para cada parte. 
    En el primer turno, el usuario saludará, proverá un contexto y consultará de manera directa pero con un enfoque sustancialmente distinto a la conversaciones generadas anteriormente sobre el proceso de matrícula, cumplimiento con el criterio 7. La información solicitada puede ser inferida del segundo par de preguntas y respuestas, cumpliendo así con el Criterio 6.
    En el tercer turno, el usuario consultará de manera directa pero con un enfoque sustancialmente distinto a la conversaciones generadas anteriormente sobre el plazo para realizar un retiro parcial de asignaturas, cumplimiento con el criterio 7. La información solicitada puede ser inferida del primer par de preguntas y respuestas, cumpliendo así con el Criterio 6.
    El asistente responderá apropiadamente en cada consulta inferiendo las respuestas de los pares de preguntas y respuestas proporcionados.
    La conversación se complementará y enriquesará con interacciones naturales en el segundo y cuarto turno, cumpliendo con el criterio 9.

    Conversación 3:
            user: Buenas, soy estudiante de segundo ciclo de la carrera de matematica queria que me indiques como se realiza la matricula.
            asistente: El proceso de matrícula se realiza a través del Portal Web del Sistema de Matrícula UNI, suministrado por la ORCE, según lo establecido en el reglamento de matrícula de la Facultad de Ciencias de la UNI.
            user: Entiendo, gracias por la información.
            asistente: ¡De nada! Si tienes más preguntas en el futuro, no dudes en preguntar.
            user: también quería saber en caso quiero solicitar el retiro parcial de algun curso hasta que fecha tengo para hacerlo.
            asistente: El plazo para realizar un retiro parcial de asignaturas es hasta el último día útil de la quinta semana después del inicio de clases del período académico.
            user: Entiendo, gracias por la información.
            asistente: ¡De nada! Si tienes más preguntas, no dudes en preguntar. ¡Buena suerte con todo!

    La Conversación 4 se desorallará con 3 turnos para cada parte. 
    En el primer turno, el usuario consultará de manera indirecta con un enfoque sustancialmente distinto a la conversaciones generadas anteriormente sobre el plazo para realizar un retiro parcial de asignaturas, cumplimiento con el criterio 7. La información solicitada puede ser inferida del primer par de preguntas y respuestas, cumpliendo así con el Criterio 6.
    En el segundo turno, el usuario consultará de manera directa pero con un enfoque sustancialmente distinto a la conversaciones generadas anteriormente sobre si el proceso de matrícula se realiza a través del Portal Web del Sistema de Matrícula UNI, cumplimiento con el criterio 7. La información solicitada puede ser inferida del segundo par de preguntas y respuestas, cumpliendo así con el Criterio 6.
    El asistente responderá apropiadamente en cada consulta inferiendo las respuestas de los pares de preguntas y respuestas proporcionados.
    La conversación se complementará y enriquesará con una interacción natural en el tercer turno, cumpliendo con el criterio 9.

    Conversación 4:
            user: estoy con una duda ya es la semana 5 de este ciclo y no estoy seguro si puedo solicitar el retiro parcial de un curso.         
            asistente: El plazo para realizar un retiro parcial de asignaturas es hasta el último día útil de la quinta semana después del inicio de clases del período académico.
            user: otra duda mas, la matricula siempre se realizar por el portal web.           
            asistente: Sí, el proceso de matrícula se realiza a través del Portal Web del Sistema de Matrícula UNI, suministrado por la ORCE, según lo establecido en el reglamento de matrícula de la Facultad de Ciencias de la UNI.
            user: Entiendo, gracias por la información.
            asistente: ¡De nada! Si tienes más preguntas, no dudes en preguntar. Estoy aquí para ayudarte.

    La Conversación 5 se desorallará con 3 turnos para cada parte. 
    En el primer turno, el usuario consultará de manera directa pero con un enfoque sustancialmente distinto a la conversaciones generadas anteriormente sobre si el proceso de matrícula se realiza a través del Portal Web del Sistema de Matrícula UNI, cumplimiento con el criterio 7. La información solicitada puede ser inferida del segundo par de preguntas y respuestas, cumpliendo así con el Criterio 6.
    En el segundo turno, el usuario provera un contexto y consultará de manera indirecta con un enfoque sustancialmente distinto a la conversaciones generadas anteriormente anteriormente sobre el plazo para realizar un retiro parcial de asignaturas, cumplimiento con el criterio 7. La información solicitada puede ser inferida del primer par de preguntas y respuestas, cumpliendo así con el Criterio 6.
    El asistente responderá apropiadamente en cada consulta inferiendo las respuestas de los pares de preguntas y respuestas proporcionados.
    La conversación se complementará y enriquesará con una interacción natural en el tercer turno, cumpliendo con el criterio 9.

    Conversación 5:
            user: estoy con una duda si la matricula debo realizarla por el portal web o ir presencialmente a la UNI.
            asistente: El proceso de matrícula se realiza a través del Portal Web del Sistema de Matrícula UNI, suministrado por la ORCE, según lo establecido en el reglamento de matrícula de la Facultad de Ciencias de la UNI.
            user: es la sexta semana de clases y quisiera solicitar el retiro de un curso, es posible ?
            asistente: Lamentablemente, el retiro parcial solo se puede realizar hasta el último día útil de la quinta semana después del inicio de clases del período académico.
            user: Entiendo, gracias por la información.
            asistente: ¡De nada! Si tienes más preguntas, no dudes en preguntar. ¡Buena suerte con todo!

Lista de preguntas y respuestas: ```{texts_qas[4]}```

Conversaciones generadas:
"""

t1 = """ La Conversación 1 se desorallará con 3 turnos para cada parte. 
    En el primer turno, el usuario saludará y consultará de manera directa sobre el plazo para realizar un retiro parcial de asignaturas. La información solicitada puede ser inferida del primer par de preguntas y respuestas, cumpliendo así con el Criterio 6.
    El asistente responderá apropiadamente en cada consulta inferiendo las respuestas de los pares de preguntas y respuestas proporcionados.
    La conversación se complementará y enriquesará con interacciones naturales en el segundo y tercer turno, cumpliendo con el criterio 9.
"""

t2 = """ La Conversación 2 se desorallará con 4 turnos para cada parte. 
    En el segundo turno,  consultará de manera directa pero con un enfoque sustancialmente distinto a la conversación generada anteriormente sobre el porcentaje mínimo de coincidencia necesario para la convalidación. Esta información puede ser inferida del primer par de preguntas y respuestas, cumpliendo con el Criterio 6.
    El asistente responderá apropiamente en cada consulta inferiendo las respuestas de los pares de preguntas y respuestas proporcionados.
    La Conversación se complementará y enriquesara con interacciones naturales en el primer, tercer y cuarto turno, cumpliendo con el criterio 9.
"""
print(count_tokens(encoding,t1))
print(count_tokens(encoding,t2))

print(count_tokens(encoding,prompt))
messages =  [{'role':'user', 'content':prompt}]
response = get_completion_from_messages(messages, temperature=0, model= "gpt-4-1106-preview")
print(response)