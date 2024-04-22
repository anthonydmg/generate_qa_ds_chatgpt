
from utils import get_completion_from_messages, set_openai_key, count_tokens
from dotenv import load_dotenv
import tiktoken

load_dotenv()

set_openai_key()

encoding = tiktoken.encoding_for_model('gpt-4-turbo')

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
#     11. Asegúrate de no inventar información que no se encuentre dentro de los pares de preguntas y respuestas proporcionados.

prompt = f"""
    
Se proporcionará una lista de dos pares de preguntas y respuestas relacionadas con matrículas, trámites y procedimientos académicos de la Facultad de Ciencias de la Universidad Nacional de Ingeniería (UNI). 
Tu tarea es generar 8 conversaciones realistas entre un asistente de IA especializado en estos temas y un usuario.

Antes de generar las conversaciones, asegúrate de cumplir cada uno de los siguientes criterios:
    1. Las conversaciones deben ser por turnos entre el agente de IA y el usuario, siendo el usuario el que siempre comenzará la conversación.
    2. Las conversaciones deben tener al menos 3 turnos para cada hablante en la conversación.
    3. El usuario debe manejar un tono semiformal y natural de un estudiante universitario.
    4. El usuario no debe mencionar directamente el reglamento de matrícula de la Facultad de Ciencias.
    5. El asistente, ante agradecimientos o confirmaciones, debe responder adecuadamente y, además, mencionar que si tiene alguna otra duda, no dude en preguntar.
    6. Enfócate en crear diferentes conversaciones donde el usuario tenga la intención de obtener información que puedan ser inferida de los pares de preguntas y respuestas proporcionados  (delimitados por tres comillas invertidas).
    7. Evita repetir preguntas de manera idéntica en distintas conversaciones. Sé creativo y original en la forma de consultar por información del usuario, usando enfoques tanto directos como indirectos. Considera agregar un contexto proporcionado por el usuario antes de manifestar su duda.
    8. El asistente debe responder adecuadamente a las consultas del usuario inferiendo las respuestas de los pares de preguntas y respuestas proporcionados, evitando inventar información adicional.
    9. Enriquece las conversaciones mediante interacciones naturales, como saludos, despedidas, confirmaciones y solicitudes de ayuda, entre otros elementos.
    10. En caso no sea posible proveer una respuesta completa con la información proporcionada o se mencione problemas con procesos de matricula sugiere consultar con la oficina del Area de Estadistica y Registros Academicos de la Facultad de ciencias (AERA).
    11. En caso sea sumamente necesario puedes usar la siguiente informacion adicional de la Facultad de Ciencias para complementar alguna respuesta:
        - La facultad de ciencias cuenta con pagina web
        - En la pagina web de la facultad se pueden entrar diferentes manuales/diagramas de diferentes procesos de matricula o procedimientos.
        - En la pagina web se publica el calendario academico.
        - En la pagina web se encuentran modelos para solicitudes de diferentes procesos academicos.
    12. Considera agregar un contexto proporcionado por el usuario antes de manifestar su duda.

Conversación 1:
            user: ...
            asistente: ...
            user: ...
            ...
    
Lista de pares de preguntas y respuestas: ```{texts_qas[0]}```
    
Conversaciones generadas:

    Conversación 1:
            user: tengo una pregunta sobre la convalidación de asignaturas. ¿Cuál es el porcentaje mínimo de contenido que deben coincidir las asignaturas para que proceda la convalidación?
            asistente: Para que proceda la convalidación, los respectivos sílabos de las asignaturas a convalidar deben coincidir al menos en un 75% de su contenido y de horas dictadas.
            user: Entiendo, tambien me gustaría saber ¿Cuál es el plazo para convalidaciones de traslados internos?.
            asistente: El período disponible para realizar convalidaciones de traslados internos se extiende hasta cinco (5) días hábiles contados a partir de la aprobación por parte del Consejo de Facultad o la autorización del Decano, conforme a lo establecido en el reglamento de matrícula de la Facultad de Ciencias de la UNI.
            user: ok gracias por la información.
            asistente: ¡De nada! Si tienes más preguntas en el futuro o necesitas ayuda, no dudes en preguntar. ¡Buena suerte con todo!
    
    Conversación 2:
    	    user: Hola, buenas tardes.
            asistente: ¡Hola!, ¿En qué puedo ayudarte hoy?
            user: tengo una consulta. Quiero solicitar la convalidacion de un curso pero no estoy seguro si hay un minimo de porcentaje de similitud entre los cursos.
            asistente: Para que la convalidación pueda llevarse a cabo, es necesario que los contenidos y la carga horaria de las asignaturas respectivas coincidan en al menos un 75%.
            user:  He llevado un curso de Programación II en otra facultad que tiene 3 créditos y quisiera convalidarlo con el curso de Programación Orientada a Objetos que tiene 4 créditos. Según mi estimación, coinciden entre un 60% a 70%. ¿Habrá alguna manera de solicitar su convalidación?
            asistente: La decisión se toma conforme al reglamento de Matrícula de la Facultad de Ciencias, que establece un mínimo del 75% de coincidencia en contenido y horas dictadas para su convalidación. Te sugiero consultar con la oficina del Área de Estadística y Registros Académicos (AERA) para obtener más información sobre posibles apelaciones.
            user: ok
            asistente: Si tienes más preguntas, no dudes en preguntar. Estoy aquí para ayudar.
            user: ok 
            asistente: Perfecto. Si en el futuro tienes más preguntas, no dudes en comunicarte. ¡Que tengas un buen día!
            
    Conversación 3:
    	    user: Estoy tramitando mi traslado interno de la escuela de matemáticas a la de ciencias de la computación. Me dijeron que una vez que sea aprobado, puedo convalidar varios cursos. ¿Cuántos días tengo como plazo límite para realizar este proceso?
    	    asistente: El plazo disponible para llevar a cabo convalidaciones luego de un traslado interno es de hasta cinco (5) días hábiles, comenzando a contar desde la aprobación por parte del Consejo de Facultad o la autorización del Decano. Esta información se basa en lo establecido en el reglamento de matrícula de la Facultad de Ciencias de la UNI.
    	    user: entonces si aprueban mi traslado interno mañana lunes tendria, hasta el proximo lunes para tramitarlo.
    	    asistente: Los días hábiles se contabilizan de lunes a viernes, excluyendo los días festivos a nivel nacional o regional. Si tu traslado interno es aprobado un lunes, dispondrás de un periodo de 5 días hábiles a partir de ese día para llevar a cabo las convalidaciones. Este plazo se cumplirá en el próximo viernes, siempre y cuando no haya feriados en ese lapso.
    	    user: a ya entiendo y que requisito deben cumplir los cursos para que se puedan convalidar?
    	    asistente:  Para que la convalidación pueda llevarse a cabo, es necesario que los contenidos y la carga horaria de los cursos respectivos coincidan en al menos un 75%.
    	    asistente:  Si tienes alguna otra duda, no dudes en consultarme. ¡Estoy aquí para ayudar!
    	    user: no eso es todo lo que queria saber
    	    asistente: Entendido. Si en el futuro surge alguna pregunta o necesitas asistencia, no dudes en volver. ¡Buena suerte con todo!
    	    
    Conversación 4:
            user: una consulta. Quiero solicitar la convalidacion del curso de fisica ii pero no estoy seguro si hay un minimo de porcentaje de similitud requerido entre los cursos.
            asistente: Para que la convalidación pueda llevarse a cabo, es necesario que los contenidos y la carga horaria de las asignaturas respectivas coincidan en al menos un 75%.
            user: como ya me aprobaron mi traslado interno, queria saber hasta cuando puedo realizar las convalidaciones de cursos.
            asistente:  El período disponible para realizar convalidaciones de traslados internos se extiende hasta cinco (5) días hábiles contados a partir de la aprobación por parte del Consejo de Facultad o la autorización del Decano, conforme a lo establecido en el reglamento de matrícula de la Facultad de Ciencias de la UNI.
            user: ok, gracias.
            asistente: ¡De nada! Si tienes alguna otra duda, no dudes en preguntar. Estoy aquí para ayudarte.
            user: ok, adios.
            asistente: ¡Adiós! Si tienes más preguntas en el futuro, no dudes en volver. ¡Hasta luego!
            
    Conversación 5:
            user: : buenas tardes, queria que me ayudes con esta duda. Estaba considerando la posibilidad de trasladarme a la escuela de física dentro de la misma facultad y me gustaría saber qué cursos podría convalidar.
            asistente: Las asignaturas a convalidar deben coincidir al menos en un 75% de su contenido y de horas dictadas, para que proceda la convalidación.
            user: entonces, si el curso que lleve tiene 4 creditos igual lo puedo convalidar con uno 5 creditos.
            asistente: Es correcto, mientras coincidan en al menos un 75% de su contenido y de horas dictadas, la convalidacion puede llevarse a acabo.
            user: y si la simitud que se encuentra es del 70%, tengo alguna opcion de apelar a la esa decisión o es definitiva?
            asistente: Según el reglamento de Matrícula de la Facultad de Ciencias, se requiere un mínimo del 75% para la convalidación. Sin embargo, puedes considerar hablar con la oficina del Área de Estadística y Registros Académicos (AERA) para obtener información detallada sobre posibles apelaciones y opciones disponibles para tu situación. ¡No dudes en buscar más orientación si lo necesitas!
            user: esta bien.
            asistente:  tienes alguna otra duda, no dudes en consultar. Estoy aquí para ayudarte.
   	   
    Conversación 6:
            user:Me aprobaron mi traslado interno el miércoles de la semana pasada, pero el jueves fue feriado nacional. Entonces, ¿Todavía tendría hasta el jueves para realizar la convalidación de cursos?
            asistente:  Según el reglamento de matrícula de la Facultad de Ciencias de la UNI, el plazo para las convalidaciones de traslados internos es de hasta cinco días hábiles desde la aprobación del Consejo de Facultad o la autorización del Decano. Dado que te aprobaron el traslado interno el miércoles de la semana pasada y el jueves fue feriado nacional, el primer día hábil sería el miércoles. Luego contaríamos el viernes, lunes, martes y miércoles. Por lo tanto, el plazo de cinco días hábiles se agotaría el miércoles de esta semana, y deberías completar la convalidación hasta ese día para cumplir con el reglamento establecido. 
            user: genial, ahora me queda mucho mas claro gracias.
            asistente:  ¡De nada! tienes alguna otra duda, no dudes en consultar. Estoy aquí para ayudarte.
            user: En caso de que me pase de ese plazo, ¿podría solicitar alguna prórroga?
            asistente: Entiendo tu preocupación. Sin embargo, los plazos deben cumplirse según lo establecido en el reglamento. Si llegara a pasarte, te recomendaría que te pongas en contacto con la oficina del Área de Estadística y Registros Académicos (AERA) lo antes posible. Explica tu situación detalladamente y pregunta si existe algún procedimiento para solicitar una prórroga en caso de que necesites más tiempo para completar la convalidación.
            user: esta bien, lo tendre en mente,  Gracias por la ayuda.
            asistente: No hay de qué. Recuerda que si tienes más preguntas en el futuro, puedes contactarme. 
           
    Conversación 7:
            user: tengo una duda, no estoy seguro si puedo convalidar el curso de Fisica I que lleve antes de trasladarme a la Facultad de Ciencias.
            asistente:  Para que la convalidación sea efectiva, es necesario que el silabus y la carga horaria del curso de Física I que cursaste previamente, antes de tu traslado, coincidan en al menos un 75% con el curso que deseas convalidar.
            user: mmm...
            asistente: ¿Hay algo específico sobre temas relacionados a la Facultad de ciencias, que incluyen incluyen procesos de matricula, procemientos y tranmites, entre otros que quisieras saber?. Estoy aquí para ayudar con cualquier pregunta adicional que puedas tener sobre estos temas.
            user: dime como esta el clima hoy.
            asistente: Lo siento, solo puedo ayudarte con temas relacionados a la Facultad de ciencias, los cuales incluyen procesos de matricula, procemientos y tranmites, entre otros.
            user: ok
            asistente: Recuerda que si tienes más preguntas en el futuro, puedes contactarme. 

    Conversación 8:
            user: una duda, acabo de trasladarme a la escuela de ingenieria fisica me diferon que puedo convalidar algunos cursos. Cuanto tiempo tengo para hacerlo?
            asistente: En el caso de traslados internos, el plazo para realizar convalidaciones se extiende hasta cinco (5) días hábiles, contados a partir de la aprobación por parte del Consejo de Facultad o la autorización del Decano. Esto está establecido en el reglamento de matrícula de la Facultad de Ciencias de la UNI.     
            user: Como ya han pasado 6 días desde que aprobaron mi traslado interno, ¿puedo solicitar la convalidación de los cursos?
            asistente: Entiendo tu situación y tu interés en solicitar la convalidación de cursos después de tu traslado interno. Según los reglamentos de la Facultad de Ciencias, el plazo para las convalidaciones es de hasta cinco (05) días hábiles desde la aprobación del Consejo de Facultad o la autorización del Decano. Dado que ya han pasado 6 días desde la aprobación, te recomendaría verificar si el plazo de los 5 días hábiles (sin contar feriados ni fines de semana) no ha caducado. En caso de que no haya expirado, puedes proceder con la convalidación de cursos antes de que concluya el plazo.
            user:  Ok, también estaba en duda en esto. ¿Existe algún requisito para que los cursos se puedan convalidar?
            asistente:  Para que la convalidación proceda, es necesario que los silabus y la carga horaria de los cursos respectivos coincidan en al menos un 75%.
            user:  entonces el curso de fisica iii que lleve en la antes de mi trasaldo puede convalidarse
            asistente: Es posible la convalidacion, si es que los silabus y la carga horaria de los cursos respectivos coincidan en al menos un 75%.
        
Lista de preguntas y respuestas: ```{texts_qas[2]}```

Conversaciones generadas:

"""
#print(prompt)

print(texts_qas[0])
print(texts_qas[2])
print("size input: ",count_tokens(encoding,prompt))
messages =  [{'role':'user', 'content':prompt}]
response = get_completion_from_messages(messages, temperature=0, model= "gpt-4-1106-preview")
print(response)
print("size output: ", count_tokens(encoding,response))