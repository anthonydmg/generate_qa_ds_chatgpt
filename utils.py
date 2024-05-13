import json
import os
import openai
import math
import re
import tiktoken
import evaluate

def save_json(dir_path, filename, data):
    os.makedirs(dir_path, exist_ok = True)
    with open(f"{dir_path}/{filename}.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data


def format_response_json(response):
    ## Extraer json en texto
    
    match = re.search(r'\{\s*"preguntas": \[(\s|.)*\]\s*\}', response, re.MULTILINE)
    if match is None:
        raise Exception("No se encontro preguntas en formato Json")
    
    json_text = response[match.start(): match.end()]
    #patron = re.compile(r'\{"preguntas": \[\s+(.+\s+)+\]\}')
    #coincidencias = re.findall(r'\{"preguntas": \[\s+((.+\s+)+)\]\}',response)
    #print("Texto json:", coincidencias[0][0].strip())
    resp_json = json.loads(json_text)
    return resp_json

def read_fragment_doc(path):
    with open(path) as f:
        text = f.read()
        return text

def list_json_to_txt(elements, marcador = ".", numeric = True):
    text = ''
    for i ,e in enumerate(elements):
        text += str(i + 1) + f"{marcador} " + e + "\n"
    return text

def count_tokens(encoding, text): 
    return len(encoding.encode(text))


def set_openai_key():
    API_KEY = os.getenv("API_KEY")
    openai.api_key = API_KEY

def get_completion_from_messages(
        messages, 
        model="gpt-3.5-turbo-1106", 
        temperature=0,
        chat = True
        ):
    if chat:
        response = openai.chat.completions.create(
            model=model,
            messages=messages,
            #max_tokens = 0,
            temperature=temperature, # this is the degree of randomness of the model's output
        )
        return response.choices[0].message.content
    else:
        response = openai.completions.create(
            model=model,
            prompt=messages[0]["content"],
            #max_tokens = 0,
            temperature=temperature, # this is the degree of randomness of the model's output
        )
        return response.choices[0].text


def format_convesations_data(texto):
    conversaciones = re.split(r'\n*\s*Conversación \d+:\n', texto)
    if conversaciones[0] == '':
        conversaciones = conversaciones[1:]
    conversaciones_json = []
    for conv in conversaciones:
        lineas = conv.strip().split('\n')
        messages = [{"role": speaker.strip(), "content": message.strip() } for speaker, message in [turn.split(":") for turn in lineas]]
        conversaciones_json.append({
            "conversation_text": conv,
            "messages": messages
        })
    return conversaciones_json

texto = """  Conversaci1 1:
user: Hola, tengo una duda sobre las evaluaciones de regularización. ¿Es necesario haber rendido un mínimo de pruebas para poder acceder a ellas?
assistant: Hola, efectivamente, para poder rendir la evaluación de regularización, es necesario que hayas rendido al menos el 50% de las pruebas de evaluación del curso desaprobado, de acuerdo con el Reglamento de Evaluación de la UNI.
user: Entiendo, y en caso de cumplir con ese requisito, ¿a quién debo dirigir mi solicitud para realizar la evaluación de regularización?
assistant: Debes dirigir tu solicitud al Decano de la facultad. Es el procedimiento establecido en el Reglamento de Evaluación de la UNI.
user: Perfecto, muchas gracias por la información.
assistant: ¡De nada! Si tienes alguna otra duda, no dudes en preguntar. ¡Estoy aquí para ayudarte!

Conversación 2:
user: Buen día, quisiera saber si puedo rendir la evaluación de regularización si no he presentado todas las pruebas del curso.
assistant: Buen día, para poder rendir la evaluación de regularización, debes haber rendido por lo menos el 50% de las pruebas de evaluación del curso desaprobado. Es un requisito indispensable.
user: Vale, y si cumplo con eso, ¿a quién tengo que enviar la solicitud para la evaluación?
assistant: Tu solicitud para realizar una evaluación de regularización debe ser dirigida al Decano de la facultad correspondiente.
user: Genial, gracias por la ayuda.
assistant: No hay problema, recuerda que si tienes más dudas, puedes consultarme en cualquier momento. ¡Suerte con tu evaluación!

Conversación 3:
user: Hola, ¿qué tal? Tengo una consulta sobre las evaluaciones de regularización.
assistant: Hola, claro, dime en qué puedo ayudarte.
user: Quisiera saber si hay algún requisito de asistencia a pruebas para poder acceder a la evaluación de regularización.
assistant: Sí, para poder rendir la evaluación de regularización, es necesario que hayas participado en al menos el 50% de las pruebas de evaluación del curso.
user: Entendido, y suponiendo que cumplo con ese requisito, ¿a quién le hago llegar mi solicitud para la evaluación?
assistant: Deberás dirigir tu solicitud al Decano de la facultad. Es el procedimiento que se sigue según el Reglamento de Evaluación.
user: Perfecto, muchas gracias por la claridad.
assistant: De nada, si tienes más preguntas o necesitas ayuda con otro tema, no dudes en preguntar. ¡Estoy aquí para asistirte!

Conversación 4:
user: Buenas, necesito información sobre las evaluaciones de regularización.
assistant: Buenas, claro, ¿qué necesitas saber exactamente?
user: ¿Es cierto que tengo que haber rendido cierto número de pruebas para calificar para la regularización?
assistant: Así es, debes haber rendido al menos el 50% de las pruebas de evaluación del curso para poder rendir la evaluación de regularización.
user: Y si he cumplido con ese requisito, ¿a quién le envío la solicitud para poder rendir esa evaluación?
assistant: Tu solicitud debe ser dirigida al Decano de la facultad. Es el procedimiento oficial para solicitar la evaluación de regularización.
user: Genial, eso era todo lo que necesitaba saber. Muchas gracias.
assistant: ¡De nada! Si tienes alguna otra duda, no dudes en preguntar. ¡Estoy aquí para ayudarte!

Conversación 5:
user: Hola, tengo una pregunta sobre las evaluaciones de regularización.
assistant: Hola, claro, ¿en qué puedo ayudarte?
user: ¿Qué porcentaje de las pruebas de evaluación debo haber rendido para poder acceder a una evaluación de regularización?
assistant: Debes haber rendido por lo menos el 50% de las pruebas de evaluación del curso desaprobado para poder acceder a la evaluación de regularización.
user: Entiendo, y si cumplo con ese requisito, ¿a quién debo dirigir mi solicitud para realizar la evaluación?
assistant: Debes dirigir tu solicitud al Decano de la facultad, tal como lo establece el Reglamento de Evaluación.
user: Muchas gracias por la información.
assistant: ¡De nada! Si tienes alguna otra duda, no dudes en preguntar. ¡Estoy aquí para ayudarte!

Conversación 6:
user: Hola, ¿podrías ayudarme con una duda sobre las evaluaciones de regularización?
assistant: Hola, por supuesto, dime cuál es tu duda.
user: Quiero saber si necesito haber rendido un mínimo de pruebas para poder rendir la evaluación de regularización.
assistant: Sí, es necesario que hayas rendido al menos el 50% de las pruebas de evaluación del curso para poder rendir la evaluación de regularización.
user: Ya veo, y en caso de cumplir con ese requisito, ¿a quién le hago llegar mi solicitud para la evaluación?
assistant: Tu solicitud para la evaluación de regularización debe ser dirigida al Decano de la facultad.
user: Perfecto, eso aclara mi duda. Gracias.
assistant: ¡De nada! Si tienes alguna otra duda, no dudes en preguntar. ¡Estoy aquí para ayudarte!

Conversación 7:
user: Hola, tengo una consulta sobre las evaluaciones de regularización.
assistant: Hola, dime en qué puedo ayudarte.
user: ¿Es necesario haber rendido una cantidad específica de pruebas para poder rendir la evaluación de regularización?
assistant: Sí, debes haber rendido por lo menos el 50% de las pruebas de evaluación del curso para ser elegible para la evaluación de regularización.
user: Entendido, y si cumplo con ese requisito, ¿a quién debo dirigir mi solicitud para realizar la evaluación?
assistant: Debes enviar tu solicitud al Decano de la facultad, según lo establecido en el Reglamento de Evaluación.
user: Muchas gracias por la ayuda.
assistant: ¡De nada! Si tienes alguna otra duda, no dudes en preguntar. ¡Estoy aquí para ayudarte!

Conversación 8:
user: Hola, necesito información sobre las evaluaciones de regularización.
assistant: Hola, ¿qué información necesitas?
user: ¿Tengo que haber rendido un mínimo de pruebas para poder rendir la evaluación de regularización?
assistant: Correcto, es necesario que hayas rendido al menos el 50% de las pruebas de evaluación del curso.
user: Y si he cumplido con ese requisito, ¿a quién le envío la solicitud para la evaluación de regularización?
assistant: Tu solicitud debe ser dirigida al Decano de la facultad, tal como se especifica en el Reglamento de Evaluación."""

#conversaciones_json = format_convesations_data(texto)
#print(conversaciones_json)

def generate_random_groups_qa(
        file_qa = "./answers_generated.json",
        save_file = True
        ):
    import random

    random.seed(42)

    if os.path.exists("./groups_qa.json"):
        groups_qa = load_json("./groups_qa.json")
        return groups_qa

    qas = load_json(file_qa)
    groups_qa = []
    for qas_type1, qas_type2 in zip(qas[::2], qas[1::2]):
        #document = 
        question_answer_pairs_t1 = qas_type1["question_answer_pairs"]
        question_answer_pairs_t1 = [ {**qa, "source": qas_type1["document"] } for qa in question_answer_pairs_t1]
        question_answer_pairs_t2 = qas_type2["question_answer_pairs"]
        question_answer_pairs_t2 = [ {**qa, "source": qas_type2["document"] } for qa in question_answer_pairs_t2]

        qa_t1_length = len(question_answer_pairs_t1)
        qa_t2_length = len(question_answer_pairs_t2)

        choices_qa_t1 = random.sample(question_answer_pairs_t1, k = qa_t1_length)
        choices_qa_t2 = random.sample(question_answer_pairs_t2, k = qa_t2_length)
        
        min_length = min(qa_t1_length, qa_t2_length)

        for qa_t1_i, qa_t2_i in zip(choices_qa_t1[:min_length], choices_qa_t2[:min_length]):
            groups_qa.append([qa_t1_i, qa_t2_i])


        if qa_t1_length > qa_t2_length:
            last_qa_t1 = choices_qa_t1[min_length:]
            if (qa_t1_length - qa_t2_length) % 2 == 1:
                last_qa_t1 = last_qa_t1 + [choices_qa_t2[-1]]

            pairs_last = [[qa_t1_i, qa_t2_i] for qa_t1_i, qa_t2_i in zip(last_qa_t1[::2], last_qa_t1[1::2] )]
            groups_qa.extend(pairs_last)

        if qa_t2_length > qa_t1_length:
            last_qa_t2 = choices_qa_t2[min_length:]
            if (qa_t2_length - qa_t1_length) % 2 == 1:
                last_qa_t2 = last_qa_t2 + [choices_qa_t1[-1]]

            pairs_last = [[qa_t1_i, qa_t2_i] for qa_t1_i, qa_t2_i in zip(last_qa_t2[::2], last_qa_t2[1::2] )]


            groups_qa.extend(pairs_last)
    if save_file:
        save_json("./","groups_qa", groups_qa)
    return groups_qa

text = """Pregunta Original 1: ¿Qué sucede si un estudiante no ha aprobado el requisito de una asignatura?

1. ¿Cuál es el número máximo de créditos que puede matricular un estudiante que no ha aprobado el requisito de una asignatura?
2. ¿Qué sucede si un estudiante no ha aprobado el requisito de una asignatura y desea matricularse en asignaturas del ciclo siguiente?
3. ¿Cuál es el promedio ponderado mínimo requerido para matricularse en asignaturas si un estudiante no ha aprobado el requisito de una asignatura?
4. ¿Cuántos créditos puede matricular un estudiante en riesgo académico si no ha aprobado el requisito de una asignatura?
5. ¿Qué recomendaciones hace la Oficina de Tutoría y Comisión de Matrícula para los estudiantes que no han aprobado el requisito de una asignatura?
6. ¿Cuál es el número máximo de créditos que puede matricular un estudiante en riesgo académico si no ha aprobado el requisito de una asignatura?
7. ¿Qué restricciones existen para la matrícula de asignaturas si un estudiante no ha aprobado el requisito de una asignatura?
8. ¿Qué sucede si un estudiante no ha aprobado el requisito de una asignatura y desea matricularse en asignaturas de un ciclo consecutivo adicional?
9. ¿Cuáles son las excepciones para la matrícula de asignaturas si un estudiante no ha aprobado el requisito de una asignatura?
10. ¿Qué condiciones deben cumplir los estudiantes que deseen matricularse en asignaturas de un ciclo consecutivo adicional si no han aprobado el requisito de una asignatura?
11. ¿Cuál es el número máximo de créditos que puede matricular un estudiante en posibilidad de egresar si no ha aprobado el requisito de una asignatura?
12. ¿Qué requisitos deben cumplir los estudiantes en posibilidad de egresar para matricularse en asignaturas si no han aprobado el requisito de una asignatura?

Pregunta Original 2: [Aquí la pregunta original 2]
1. [Aquí la pregunta 1 basada en la segunda pregunta original]
2. [Aquí la pregunta 2 basada en la segunda pregunta original]
...
12. [Aquí la pregunta 12 basada en la segunda pregunta original]
..."""


def extracts_questions_basades(texto):
        # Expresión regular para dividir el texto en bloques de preguntas para cada pregunta orignal
        patron_bloque = r"(Pregunta Original \d+:\s+[^\[].*?)((?=Pregunta Original \d+:)|$)"
        # Buscar todos los bloques de preguntas en el texto
        bloques_preguntas = re.findall(patron_bloque, texto, re.DOTALL)

        # Iterar sobre cada bloque de preguntas
        groups_related_questions = []
        for bloque in bloques_preguntas :
            block_texto, _ = bloque
            # pregunta_original = re.search(r'Pregunta Original \d+: (.+?)\n', block_texto).group(1)
            # Expresión regular para encontrar las preguntas dentro del bloque
            patron_pregunta = r'\d+\.\s(¿[^\?]+?\?)'
             
            # Buscar todas las preguntas dentro del bloque
            preguntas = re.findall(patron_pregunta, block_texto, re.DOTALL)
            
            groups_related_questions.append(preguntas)
        
        return groups_related_questions

GPT_MODEL = "gpt-3.5-turbo"

text = """El estudiante que quiera realizar su reincorporación deberá primero generar una orden de pago, el costo por tramite de reincorporación es S/. 42.00 + S/. 10.00 por cada periodo no estudiado. Para ello, debera realzar los siguientes pasos.
    1. Acceder a la plataforma intranet-alumno (Portal INTRALU) con su código UNI y clave correspondiente.
    2. Luego, seleccionar la opción "Trámites y Pagos" para acceder al módulo de pagos.
    3. En el módulo de pagos, seleccionar el trámite correspondiente y generar un nuevo pago siguiendo las indicaciones en la plataforma. Mas detalles del proceso consultar el Manual de pagos publicado en seccion de "MATRÍCULA Y PROCEDIMIENTOS" de la Pagina Web de la Facultad de Ciencias.

Una vez generada la orden de pago, el alumno debe realizar el pago en una sucursal del BCP o utilizando la banca móvil del BCP desde su celular. 

Después de completar el pago, el alumno dentro de las fechas señaladas para este proceso (ver calendario académico) a través de la Plataforma de Intranet-Alumno. Accediendo a la plataforma, seleccionara "Reincorporación de Estudiantes" en la sección de "Mis Trámites", completara el formulario adjuntando la solicitud y el comprobante de pago, y luego seleccionara "Enviar Solicitud".
Al completar el envio de la solicitud por la plataforma se visualizara la solicitud enviada, la fecha así como el estado de la solicitud.
Una vez aprobada y realizada la reincorporacion, el estudiante podra realizar su matrícula de manera regular."""

def count_num_tokens(text, model = GPT_MODEL):
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))

text = """ El proceso de actualización de datos en intranet-alumnos para nuevos ingresantes en la Facultad de Ciencias de la UNI implica:
1. Recibir la clave de acceso a intranet-alumnos por parte de DIRCE.
2. Ingresar a la plataforma con tus credenciales.
3. Completar y verificar la información solicitada, como datos personales y de contacto.
4. Asegurarte de que la información sea precisa y actualizada.
Por otro lado, el registro de datos en la Facultad de Ciencias se realiza:
1. La oficina de estadística enviará la ficha de datos al correo del ingresante.
2. Llenar la ficha de datos de manera obligatoria con la información requerida.
3. Enviar la ficha de datos completada a la oficina de estadística dentro de los plazos establecidos en el cronograma de matrícula."""

print(count_num_tokens(text))
#print(count_num_tokens(text, model = GPT_MODEL))

#print(extracts_questions_basades(context))

#join_files_questions()

## extract_faq_text():

""" text = read_fragment_doc("./faq/faq.txt")

pattern_block = r"Tema: (.+?)Pregunta: (.+?)Respuesta:(.+?)(?=Tema: |$)"
bloques = re.findall(pattern_block, text, re.DOTALL)
faq_json = []
for bloq in bloques:
    tema = bloq[0].strip()
    pregunta = bloq[1].strip()
    respuesta = bloq[2].strip()

    faq_json.append({
        "question": pregunta,
        "answer": respuesta,
        "topic": tema,
        "num_tokens_answers": count_num_tokens(respuesta) 
    }) """

#context = "\nCambio De Secci\u00f3n Debido A Cruces De Horario\n\u00bfQu\u00e9 debe hacer un estudiante si desea realizar un cambio de secci\u00f3n/horario de un curso matriculado debido a cruce de horarios en sus cursos matriculados?\nLos cambios de secci\u00f3n/horario son gestionados directamente por la oficina de estad\u00edstica (AERA). Es importante tener en cuenta que solo se atender\u00e1n solicitudes en caso de que el estudiante tenga conflictos de horario entre los cursos en los que est\u00e1 matriculado. Adem\u00e1s, cualquier cambio de secci\u00f3n/horario estar\u00e1 sujeto a la disponibilidad de plazas.\nLos estudiantes que deseen realizar modificaciones en la secci\u00f3n/horario de un curso matriculado debido a conflictos de horario deben comunicarse directamente con la oficina de AERA. All\u00ed recibir\u00e1n informaci\u00f3n detallada sobre el proceso a seguir. Tambi\u00e9n, se le recomienda revisar en la pagina web de la facultad (https://fc.uni.edu.pe) avisos o formularios referentes al tema.\nHorario De Atenci\u00f3n Oficina De Estad\u00edstica O Aera\n\u00bfCu\u00e1l es el horario de atenci\u00f3n de la oficina de estad\u00edstica o AERA?\nEl horario del \u00c1rea de Estad\u00edstica y Registros Acad\u00e9micos el de De Lunes a Viernes de 8:00 a.m. a 4:00 p.m.\nAERA\n\nEl \u00c1rea de Estad\u00edstica y Registros Acad\u00e9micos (anteriormente la oficina de Estad\u00edstica) de la Facultad de Ciencias es un \u00f3rgano de apoyo administrativo, encargado de centralizar, verificar y custodiar la documentaci\u00f3n acad\u00e9mica de la Facultad de Ciencias.\n\nActividades que se realizan:\n\n1. Procesos de matr\u00edcula\nPlanificar, atender y supervisar los procedimientos de la matr\u00edcula en cada semestre Acad\u00e9mico de acuerdo al Reglamento de Matr\u00edcula de estudiantes de Antegrado vigente.\n\n    - Matr\u00edcula (ingresantes, regular, condicionada y rezagada).\n    - Reincorporaci\u00f3n.\n    - Grupo cero de Matr\u00edcula.\n    - Matr\u00edcula Condicionada.\n    - Matr\u00edcula Preferencial.\n    - Reserva de Matr\u00edcula.\n    - Retiros (Parciales, Totales y Definitivos).\n\n\n2. Procesos de evaluaci\u00f3n\nSupervisar e informar el cumplimiento de los procedimientos que regulan el sistema de calificaci\u00f3n de acuerdo al Reglamento de Evaluaci\u00f3n para estudiantes de Antegrado vigente.\n    - Supervisar el registro de notas de pr\u00e1cticas, ex\u00e1menes y solucionario.\n    - Supervisi\u00f3n en la atenci\u00f3n de los reclamos de notas de los estudiantes.\n    - Informar sobre las faltas en la entrega oportuna de notas por parte de los docentes.\n    - Gestionar el registro de nota del Examen de Regularizaci\u00f3n.\n\n3. Otras Actividades\n- Coordinar el tr\u00e1mite de los carn\u00e9s universitarios.\n- Elaborar las Constancias de Notas y/o Matr\u00edcula.\n- Verificar la informaci\u00f3n de los Certificados de notas, Constancias de Egresado y Constancias de No Adeudos emitidas por la DIRCE.\n- Entrega reportes y estad\u00edsticas a las diferentes oficinas de la Facultad para su evaluaci\u00f3n y toma de decisiones.\n- Realizar el estudio de las deudas por Decreto Legislativo 739 (Derecho de la Ense\u00f1anza) e informar al estudiante para que cumplan con la cancelaci\u00f3n respectiva.\n\nInformacion de Contacto de la oficina de estad\u00edstica (Aera)\nE-mail: estadistica_fc@uni.edu.pe\n\nHoario de Atencion de la oficina de estad\u00edstica (Aera):\nDe Lunes a Viernes de 8:00 a.m. a 4:00 p.m.\nSolicitar Vacantes Adicionales\n\u00bfQu\u00e9 debe hacer un estudiante que desea solicitar una vacante adicional para la inscripci\u00f3n a un curso?\nA los estudiantes interesados en solicitar una vacante adicional para inscribirse en un curso, se les recomienda completar su matr\u00edcula virtual en los dem\u00e1s cursos y posteriormente comunicarse con la oficina de estad\u00edstica (AERA) para obtener mayor informaci\u00f3n y que su caso sea evaluado. Tambi\u00e9n se recomienda revisar posibles publicaciones de avisos o formularios de solicitud correspondientes a la solicitud de vacantes dentro de la p\u00e1gina web de la Facultad de Ciencias (https://fc.uni.edu.pe/documentos/).\nProcedimiento Para Solicitar Una Constancia De Matricula\n\u00bfQu\u00e9 procedimiento debe seguir un estudiante para solicitar una constancia de Matricula en ingles o en espa\u00f1ol?\nPara solicitar una constancia de matr\u00edcula en ingl\u00e9s o en espa\u00f1ol, el estudiante deber seguir los siguientes pasos:\n\n1. Enviar un correo a estadistica_fc@uni.edu.pe solicitando una orden de pago para la CONSTANCIA DE MATR\u00cdCULA. En el mensaje, deber\u00e1 incluir sus datos personales: n\u00famero de DNI, apellidos, nombres, correo institucional y/o alternativo.\n\n2. La oficina de estad\u00edstica (AERA) le enviar\u00e1 la orden de pago por el monto de S/. 100.00 (dato correspondiente al a\u00f1o 2024) a su correo electr\u00f3nico.\n\n3. El alumno deber\u00e1 realizar el pago en alguna sucursal del BCP o a trav\u00e9s aplicaci\u00f3n movil del banco. En la app selecciona \"Pagar servicios\", elige la Universidad Nacional de Ingenier\u00eda, luego la opci\u00f3n de pago para estudiantes, e ingresa su n\u00famero de DNI. La app mostrar\u00e1 la orden de pago con el monto exacto para realizar el pago.\n\n4. Luego, el estudiante deber\u00e1 dejar en mesa de partes de la facultad el comprobante de pago y la solicitud correspondiente, o enviarlos por correo electr\u00f3nico a mesadepartes_fc@uni.edu.pe. Es importante que se asegure de indicar en la solicitud si desea la CONSTANCIA DE MATR\u00cdCULA en ingl\u00e9s o espa\u00f1ol. El modelo para esta solicitud est\u00e1 disponible en la secci\u00f3n \"MATR\u00cdCULA Y PROCEDIMIENTOS\" en la p\u00e1gina web de la Facultad de Ciencias (https://fc.uni.edu.pe/documentos/).\n\n5. Por \u00faltimo, AERA enviar\u00e1 un correo para notificarle que la constancia est\u00e1 lista para ser recogida en el horario de atenci\u00f3n de Lunes a Viernes, de 08:00 a 13:00 y de 14:00 a 15:30."

#print(context)
#print(f"\nUn total de {len(faq_json)} preguntas han sido extraidas")
#save_json("./faq", "faq_json", faq_json)

""" examples = load_json("./data_nlu.json")
table_data = {}
for e in examples:
    print(e)
    intent_name = e["intent_name"]
    
    if intent_name not in table_data:
        table_data[intent_name] = {
            "intent_name": intent_name,
            "examples": []}

    table_data[intent_name]["examples"].append(e["text"])
 """
#pool_data = list(table_data.values())
#save_json("./","examples", pool_data)

#d = load_json("./conversational_data/conversations_simulated_75_to_75.json")
#print(d[0]["messages"][2]["context"])

## Pregunta chatgpt como dirias este respuesta sin mencionar informacion proporcionada.

#a = "La constancia de matr\u00edcula se puede obtener de forma f\u00edsica, debiendo ser recogida en la oficina de estad\u00edstica (AERA) en el horario de atenci\u00f3n mencionado anteriormente. No se menciona en la informaci\u00f3n proporcionada si tambi\u00e9n se puede obtener de forma digital, por lo que se recomienda contactar directamente con la oficina de estad\u00edstica para obtener informaci\u00f3n actualizada sobre la disponibilidad de constancias de matr\u00edcula en formato digital."
#print(a)

""" data_conv_prev = load_json("./conversations_generated.json")

print(len(data_conv_prev))

data_conv = load_json("conversational_data/conversational_dataset.json")

print(len(data_conv))

all_conversational_data = data_conv_prev + data_conv


print(len(all_conversational_data)) """

def join_reformulated_questions(reformulated_faqs = []):
    tab_all_questions = {}

    for reformulated_faq in reformulated_faqs:
        original_question = reformulated_faq["original_question"]
        questions_generated = reformulated_faq["questions_generated"]
        
        if original_question not in tab_all_questions:
            tab_all_questions[original_question] = questions_generated
        else:
            tab_all_questions[original_question].extend(questions_generated)
    
    ## Format questions
    
    reformulated_faqs_joined = [ {"original_question": k, "questions_generated": v } for k,v in tab_all_questions.items()]

    return reformulated_faqs_joined

""" reformulated_faqs = load_json("./faq/reformulated_faqs.json")


reformulated_faqs_joined = join_reformulated_questions(reformulated_faqs)

save_json("./faq", "reformulated_faqs_joined", reformulated_faqs_joined)
 """



def filtered_questions_reformulated_rouge(
    reformulated_faqs_joined,
    threshold_rouge = 0.9):

    rouge = evaluate.load('rouge') 
    filtered_questions_reformulated = []
    for reformulated_faq in reformulated_faqs_joined:
        original_question = reformulated_faq["original_question"]
        questions_generated = reformulated_faq["questions_generated"]
        print("Inicial questions: ", len(questions_generated))
        all_pool_questions = [original_question]

        for question in questions_generated:

            rouge_results = rouge.compute(predictions=[question], references=[all_pool_questions])
            rougeL = rouge_results["rougeL"]
            if rougeL < threshold_rouge:
                all_pool_questions.append(question)
        
        print("Final questions: ", len(all_pool_questions))

        filtered_questions_reformulated.append({
            "original_question": original_question,
            "questions_generated": all_pool_questions
        })
    return filtered_questions_reformulated

#reformulated_faqs_joined = load_json("./faq/reformulated_faqs_joined.json")


""" threshold_rouge = 0.85
filtered_questions_reformulated = filtered_questions_reformulated_rouge(reformulated_faqs_joined, threshold_rouge)

save_json("./faq", f"filtered_questions_reformulated_rouge_{threshold_rouge}", filtered_questions_reformulated)

 """
#filtered_questions_reformulated_rouge = load_json("./faq/filtered_questions_reformulated_rouge_0.85.json")



def flat_questions_reformulate(filtered_questions_reformulated_rouge):
    filtered_reformulated_question_list = []
    for reformulated_faq in filtered_questions_reformulated_rouge:
        original_question = reformulated_faq["original_question"]
        questions_generated = reformulated_faq["questions_generated"]
        filtered_reformulated_question_list.extend(questions_generated)
    return filtered_reformulated_question_list

#dir_path = "./faq-reformulated"


def split_file_questions_refomulated(dir_path, filtered_questions_reformulated_rouge):
    for i, reformulated_faq in enumerate(filtered_questions_reformulated_rouge):
        #original_question = reformulated_faq["original_question"]
        questions_generated = reformulated_faq["questions_generated"]
        save_json(dir_path, f"faq_{i+1}_reformulated", questions_generated)
    return 

""" filtered_questions_reformulated_rouge_list = load_json("./faq/filtered_questions_reformulated_rouge_0.85.json")

split_file_questions_refomulated(dir_path, filtered_questions_reformulated_rouge_list)
 """

a = "\u00bfCuales son los requisitos y el proceso de matr\u00edcula regular para alumnos de pregrado en la Facultad de Ciencias de la Universidad Nacional de Ingenier\u00eda?"
print(a)
#filtered_reformulated_question_list = flat_questions_reformulate(filtered_questions_reformulated_rouge_list)

#save_json("./faq", f"filtered_reformulated_question_list", filtered_reformulated_question_list)

