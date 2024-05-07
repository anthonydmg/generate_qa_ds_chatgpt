import json
import os
import openai
import math
import re
import tiktoken


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
import evaluate


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

dir_path = "./faq-reformulated"


def split_file_questions_refomulated(dir_path, filtered_questions_reformulated_rouge):
    for i, reformulated_faq in enumerate(filtered_questions_reformulated_rouge):
        #original_question = reformulated_faq["original_question"]
        questions_generated = reformulated_faq["questions_generated"]
        save_json(dir_path, f"faq_{i+1}_reformulated", questions_generated)
    return 

""" filtered_questions_reformulated_rouge_list = load_json("./faq/filtered_questions_reformulated_rouge_0.85.json")

split_file_questions_refomulated(dir_path, filtered_questions_reformulated_rouge_list)
 """

#filtered_reformulated_question_list = flat_questions_reformulate(filtered_questions_reformulated_rouge_list)

#save_json("./faq", f"filtered_reformulated_question_list", filtered_reformulated_question_list)

a = questions_faq = [
    "\u00bfCuales son los requisitos y el proceso de matr\u00edcula para nuevos ingresantes de pregrado en la Facultad de Ciencias de la Universidad Nacional de Ingenier\u00eda?",
    "\u00bfCu\u00e1l es la fecha l\u00edmite para completar la matr\u00edcula de nuevos ingresantes en la Facultad de Ciencias de la Universidad Nacional de Ingenier\u00eda?",
    "\u00bfQu\u00e9 sucede si un nuevo ingresante no completa su matr\u00edcula en la Facultad de Ciencias de la Universidad Nacional de Ingenier\u00eda?",
    "\u00bfSe puede realizar la matr\u00edcula de nuevos ingresantes de forma presencial en la Facultad de Ciencias de la Universidad Nacional de Ingenier\u00eda?",
    "\u00bfCu\u00e1ntos cursos debe inscribir un nuevo ingresante en la Facultad de Ciencias de la Universidad Nacional de Ingenier\u00eda?",
    "\u00bfCu\u00e1l es el procedimiento para solicitar una beca de matr\u00edcula para nuevos ingresantes en la Facultad de Ciencias de la Universidad Nacional de Ingenier\u00eda?",
    "\u00bfQu\u00e9 sucede si un nuevo ingresante no cuenta con todos los documentos requeridos para la matr\u00edcula en la Facultad de Ciencias de la Universidad Nacional de Ingenier\u00eda?",
    "\u00bfCu\u00e1l es el horario de atenci\u00f3n para realizar la matr\u00edcula de nuevos ingresantes en la Facultad de Ciencias de la Universidad Nacional de Ingenier\u00eda?",
    "\u00bfCu\u00e1les son los pasos a seguir para matricularse como nuevo ingresante de pregrado en la Facultad de Ciencias de la UNI?",
    "\u00bfQu\u00e9 documentos se necesitan para completar la matr\u00edcula como nuevo ingresante de pregrado en la Facultad de Ciencias de la UNI?",
    "\u00bfD\u00f3nde se puede obtener informaci\u00f3n sobre el proceso de matr\u00edcula para nuevos ingresantes de pregrado en la Facultad de Ciencias de la UNI?",
    "\u00bfCu\u00e1l es el plazo para realizar la matr\u00edcula como nuevo ingresante de pregrado en la Facultad de Ciencias de la UNI?",
    "\u00bfQu\u00e9 costos est\u00e1n asociados con el proceso de matr\u00edcula para nuevos ingresantes de pregrado en la Facultad de Ciencias de la UNI?",
    "\u00bfEs obligatorio asistir a una charla informativa antes de realizar la matr\u00edcula como nuevo ingresante de pregrado en la Facultad de Ciencias de la UNI?",
    "\u00bfQu\u00e9 documentos necesita presentar un nuevo ingresante de pregrado para completar su matr\u00edcula en la Facultad de Ciencias de la UNI?",
    "\u00bfCu\u00e1l es el procedimiento que deben seguir los nuevos ingresantes de pregrado para pagar el autoseguro en la UNI?",
    "\u00bfD\u00f3nde se publica el cronograma de actividades de matr\u00edcula para nuevos ingresantes de pregrado en la Facultad de Ciencias de la UNI?",
    "\u00bfC\u00f3mo se realiza la inscripci\u00f3n de cursos para los nuevos ingresantes de pregrado en la Facultad de Ciencias de la UNI?",
    "\u00bfCu\u00e1l es el plazo para que los nuevos ingresantes de pregrado entreguen los documentos requeridos para la matr\u00edcula en la Facultad de Ciencias de la UNI?",
    "\u00bfQu\u00e9 informaci\u00f3n debe completar un nuevo ingresante de pregrado en la ficha de datos para la matr\u00edcula en la Facultad de Ciencias de la UNI?",
    "\u00bfD\u00f3nde puede un nuevo ingresante de pregrado de la Facultad de Ciencias de la UNI ver el horario de sus cursos?",
    "\u00bfCu\u00e1les son los pasos a seguir y los documentos necesarios para la matr\u00edcula de nuevos ingresantes de pregrado en la Facultad de Ciencias de la Universidad Nacional de Ingenier\u00eda?",
    "\u00bfQu\u00e9 requisitos se necesitan y cu\u00e1l es el procedimiento de matr\u00edcula para nuevos ingresantes de pregrado en la Facultad de Ciencias de la Universidad Nacional de Ingenier\u00eda?",
    "\u00bfCu\u00e1l es el proceso y qu\u00e9 documentos se requieren para la matr\u00edcula de nuevos ingresantes de pregrado en la Facultad de Ciencias de la Universidad Nacional de Ingenier\u00eda?",
    "\u00bfC\u00f3mo es el proceso de matr\u00edcula y cu\u00e1les son los requisitos para nuevos ingresantes de pregrado en la Facultad de Ciencias de la Universidad Nacional de Ingenier\u00eda?",
    "\u00bfQu\u00e9 pasos deben seguir y qu\u00e9 documentos deben presentar los nuevos ingresantes de pregrado para su matr\u00edcula en la Facultad de Ciencias de la Universidad Nacional de Ingenier\u00eda?",
    "\u00bfQu\u00e9 documentos se necesitan y cu\u00e1l es el proceso a seguir para la matr\u00edcula de nuevos ingresantes de pregrado en la Facultad de Ciencias de la Universidad Nacional de Ingenier\u00eda?",
    "\u00bfQu\u00e9 debe hacer un ingresante para obtener su constancia de ingreso en la Universidad Nacional de Ingenier\u00eda?",
    "\u00bfCu\u00e1l es el primer paso que debe realizar un ingresante para completar su matr\u00edcula en la Facultad de Ciencias?",
    "\u00bfC\u00f3mo puede un ingresante actualizar sus datos en la plataforma Intranet-Alumnos?",
    "\u00bfQu\u00e9 documentos debe entregar un ingresante a la oficina de estad\u00edstica para completar su matr\u00edcula en la Facultad de Ciencias?",
    "\u00bfCu\u00e1l es el plazo establecido para realizar el pago por autoseguro en el cronograma de actividades de matr\u00edcula para ingresantes?",
    "\u00bfQu\u00e9 har\u00e1 la oficina de estad\u00edstica una vez que un ingresante haya entregado los documentos requeridos para la matr\u00edcula?",
    "\u00bfC\u00f3mo recibir\u00e1n los ingresantes matriculados su horario de cursos en la Facultad de Ciencias?",
    "\u00bfQu\u00e9 documentos se necesitan para el proceso de matr\u00edcula de nuevos ingresantes de pregrado en la Facultad de Ciencias de la Universidad Nacional de Ingenier\u00eda?",
    "\u00bfCu\u00e1les son los pasos para que un nuevo ingresante de pregrado se matricule en la Facultad de Ciencias de la Universidad Nacional de Ingenier\u00eda?",
    "\u00bfQu\u00e9 tr\u00e1mites deben realizar los nuevos ingresantes de pregrado para su matr\u00edcula en la Facultad de Ciencias de la Universidad Nacional de Ingenier\u00eda?",
    "\u00bfD\u00f3nde deben entregar los documentos los nuevos ingresantes de pregrado para su matr\u00edcula en la Facultad de Ciencias de la Universidad Nacional de Ingenier\u00eda?",
    "\u00bfCu\u00e1l es el plazo para completar el proceso de matr\u00edcula de nuevos ingresantes de pregrado en la Facultad de Ciencias de la Universidad Nacional de Ingenier\u00eda?",
    "\u00bfCu\u00e1l es el procedimiento y la documentaci\u00f3n requerida para la matr\u00edcula de nuevos ingresantes de pregrado en la Facultad de Ciencias de la Universidad Nacional de Ingenier\u00eda?",
    "\u00bfCu\u00e1les son los pasos y requisitos que deben cumplir los nuevos ingresantes de pregrado para realizar la matr\u00edcula en la Facultad de Ciencias de la Universidad Nacional de Ingenier\u00eda?",
    "\u00bfCu\u00e1l es el procedimiento y los requisitos que deben seguir los nuevos ingresantes de pregrado para inscribirse en la Facultad de Ciencias de la Universidad Nacional de Ingenier\u00eda?",
    "\u00bfCu\u00e1les son los requisitos y el proceso que deben seguir los nuevos ingresantes de pregrado para matricularse en la Facultad de Ciencias de la Universidad Nacional de Ingenier\u00eda?",
    "\u00bfCu\u00e1les son los pasos a seguir para la matr\u00edcula de nuevos ingresantes de pregrado en la Facultad de Ciencias de la UNI?",
    "\u00bfCu\u00e1l es el procedimiento de matr\u00edcula para los nuevos ingresantes de pregrado en la Facultad de Ciencias de la UNI?",
    "\u00bfCu\u00e1l es el cronograma de actividades para la matr\u00edcula de nuevos ingresantes de pregrado en la Facultad de Ciencias de la UNI?",
    "\u00bfCu\u00e1l es el horario de atenci\u00f3n para el proceso de matr\u00edcula de nuevos ingresantes de pregrado en la Facultad de Ciencias de la UNI?",
    "\u00bfC\u00f3mo es el proceso de matr\u00edcula para los nuevos ingresantes en la Facultad de Ciencias de la Universidad Nacional de Ingenier\u00eda?",
    "\u00bfCu\u00e1l es el procedimiento de inscripci\u00f3n para los nuevos ingresantes en la Facultad de Ciencias de la Universidad Nacional de Ingenier\u00eda?",
    "\u00bfD\u00f3nde se publica la informaci\u00f3n sobre la matr\u00edcula de nuevos ingresantes en la Facultad de Ciencias de la Universidad Nacional de Ingenier\u00eda?",
    "\u00bfQu\u00e9 pasos se deben seguir para pagar el autoseguro como nuevo ingresante de pregrado en la Facultad de Ciencias de la UNI?",
    "\u00bfEs obligatorio presentar un certificado m\u00e9dico para completar la matr\u00edcula como nuevo ingresante de pregrado en la Facultad de Ciencias de la UNI?",
    "\u00bfD\u00f3nde se pueden obtener los formularios necesarios para la matr\u00edcula de nuevos ingresantes en la Facultad de Ciencias de la Universidad Nacional de Ingenier\u00eda?",
    "\u00bfC\u00f3mo pueden los nuevos ingresantes de pregrado obtener informaci\u00f3n sobre los requisitos y el proceso de matr\u00edcula en la Facultad de Ciencias de la Universidad Nacional de Ingenier\u00eda?",
    "\u00bfD\u00f3nde pueden los nuevos ingresantes de pregrado encontrar la lista de requisitos para la matr\u00edcula en la Facultad de Ciencias de la Universidad Nacional de Ingenier\u00eda?",
    "\u00bfQu\u00e9 documentos se requieren para la matr\u00edcula de nuevos ingresantes en la Facultad de Ciencias de la UNI?",
    "\u00bfC\u00f3mo se realiza la matr\u00edcula de nuevos ingresantes en la Facultad de Ciencias de la UNI?",
    "\u00bfQu\u00e9 tr\u00e1mites deben realizar los nuevos ingresantes para matricularse en la Facultad de Ciencias de la UNI?",
    "\u00bfCu\u00e1l es el plazo l\u00edmite para solicitar el retiro total?",
    "\u00bfCu\u00e1ndo vence el plazo para pedir el retiro total?",
    "\u00bfHasta cu\u00e1ndo es posible solicitar el retiro total?",
    "\u00bfCu\u00e1l es la fecha l\u00edmite para solicitar el retiro total?",
    "\u00bfHasta qu\u00e9 fecha se puede pedir el retiro total?",
    "\u00bfCu\u00e1ndo expira el plazo para solicitar el retiro total?",
    "\u00bfHasta cu\u00e1ndo tiene un estudiante para solicitar el retiro total?",
    "\u00bfCu\u00e1l es el \u00faltimo d\u00eda para pedir el retiro total?",
    "\u00bfQu\u00e9 pasos deben seguir los nuevos ingresantes para completar su matr\u00edcula en la Facultad de Ciencias de la UNI?",
    "\u00bfCu\u00e1l es el procedimiento de matr\u00edcula para los estudiantes que ingresan a la Facultad de Ciencias de la UNI?",
    "\u00bfCu\u00e1l es el proceso de inscripci\u00f3n para los nuevos estudiantes de pregrado en la Facultad de Ciencias de la UNI?",
    "\u00bfCu\u00e1les son los documentos necesarios para la matr\u00edcula de nuevos ingresantes en la Facultad de Ciencias de la UNI?",
    "\u00bfQu\u00e9 pasos deben seguir los nuevos estudiantes para inscribirse en la Facultad de Ciencias de la UNI?",
    "\u00bfCu\u00e1les son los requisitos para nuevos ingresantes de pregrado en la Facultad de Ciencias de la Universidad Nacional de Ingenier\u00eda y c\u00f3mo es el proceso de matr\u00edcula?",
    "\u00bfCu\u00e1l es el proceso de matr\u00edcula para nuevos ingresantes de pregrado en la Facultad de Ciencias de la Universidad Nacional de Ingenier\u00eda y cu\u00e1les son los requisitos?",
    "\u00bfCu\u00e1l es el procedimiento de matr\u00edcula y cu\u00e1les son los pasos a seguir para nuevos ingresantes de pregrado en la Facultad de Ciencias de la Universidad Nacional de Ingenier\u00eda?"
]
#print(a)


a = "\n\nRequisitos Y Procedimiento Para Matricula De Un Ingresante\n\u00bfCuales son los requisitos y el proceso de matr\u00edcula para nuevos ingresantes de pregrado en la Facultad de Ciencias de la Universidad Nacional de Ingenier\u00eda?\nLos ingresantes, realizaran el siguiente proceso para completar su matricula (primera matricula al primer ciclo):\n    1. Recabar su constancia de ingreso. Luego de gestionar la emisi\u00f3n de su constancia de ingreso, la Direcci\u00f3n de Admisi\u00f3n (DIAD) de la UNI enviar\u00e1 a su correo la constancia de ingreso.\n    2. Actualizaci\u00f3n de datos en intranet. DIRCE har\u00e1 llegar a su correo su clave para acceder a la plataforma de intranet-alumnos y completar sus datos.\n    3. Registrar los datos en la Facultad de Ciencias. La oficina de estad\u00edstica de la facultad enviar\u00e1 al correo del ingresante la ficha de datos. El llenado es car\u00e1cter obligatorio.\n    4. Efectuar el pago por autoseguro dentro del plazo establecido en el cronograma. Para ello, primero generar una orden de pago atravez de la plataforma intranet-alumnos.\n    5. Realizar la entrega de los siguientes documentos a la oficina de estad\u00edstica seg\u00fan el cronograma de actividades de matr\u00edcula para ingresantes publicado en la secci\u00f3n 'MATR\u00cdCULA Y PROCEDIMIENTOS' en la p\u00e1gina web de la Facultad de Ciencias.\n        - Constancia de Ingreso\n        - Ficha de datos\n        - Constancia de Evaluaci\u00f3n Socioecon\u00f3mica\n        - Certificado M\u00e9dico expedido por el Centro Medico UNI\n        - Comprobante de pago de Autoseguro Estudiantil\n    6. La oficina de estad\u00edstica ejecutar\u00e1 la matr\u00edcula (inscripci\u00f3n de cursos) de los ingresantes seg\u00fan el cronograma de actividades, \u00fanicamente para aquellos que hayan cumplido con la entrega de la entrega de los documentos requeridos en de las fechas establecidas en el cronograma.\n    7. Los ingresantes matriculados recibir\u00e1n un correo con el horario de sus cursos y podr\u00e1n verlos en la plataforma intranet alumnos.\n\nRequisitos Y Procedimiento Matricula Regular\n\u00bfCuales son los requisitos y el proceso de matr\u00edcula regular para alumnos de pregrado en la Facultad de Ciencias de la Universidad Nacional de Ingenier\u00eda?\nSon requisitos para la matr\u00edcula regular efectuar el pago por autoseguro estudiantil y no presentar adeudos con su Facultad ya sea econ\u00f3micas, por libros o cualquier otro material de ense\u00f1anza en general. Adem\u00e1s, los alumnos en riesgo acad\u00e9mico deben haber completado la tutor\u00eda obligatoria previa a la matr\u00edcula.\n\nEl proceso para que un alumno de pregrado realice su matr\u00edcula regular al ciclo acad\u00e9mico, es el siguiente:\n1. Generar una orden de pago para el autoseguro estudiantil a trav\u00e9s de la plataforma intranet-alumnos. En esta plataforma, selecciona la opci\u00f3n \"Tr\u00e1mites y Pagos\" para acceder al m\u00f3dulo de pagos (Portal INTRALU). En dicho m\u00f3dulo, selecciona el tr\u00e1mite correspondiente en el men\u00fa desplegable, haz clic en el bot\u00f3n \"Nuevo\" y sigue las indicaciones hasta generar la orden de pago.\n2. Realizar el pago dentro de los plazos establecidos en el calendario de actividades acad\u00e9micos, acerc\u00e1ndose a un sucursal del BCP o atravez de la aplicaci\u00f3n movil del banco.\n3. Luego, en la fecha y turno asignado, el estudiante llevar\u00e1 a cabo a su matr\u00edcula de forma virtual, es decir, realizar\u00e1 la inscripci\u00f3n de sus cursos a trav\u00e9s de la plataforma intranet-alumnos. Acceder\u00e1 al m\u00f3dulo de Matr\u00edcula UNI dentro de esta plataforma, seleccionar\u00e1 las asignaturas y horarios deseados, y finalizar\u00e1 confirmando la matr\u00edcula en todas las asignaturas elegidas en el sistema.\nLos turnos para la matr\u00edcula, son asignados por grupos de acuerdo al promedio ponderado de los \u00faltimos ciclos, en un orden de m\u00e9rito. Cada alumno puede verificar su turno correspondiente dentro de la plataforma intranet-alumnos.\n\nM\u00e1ximo De Cr\u00e9ditos A Matricularse Para Un Estudiante\n\u00bfEn cuantos cr\u00e9ditos como m\u00e1ximo puede matricularse un estudiante de Facultad de Ciencias de la UNI?\nEl n\u00famero m\u00e1ximo de cr\u00e9ditos en los que un estudiante de la Facultad de Ciencias de la UNI puede matricularse var\u00eda dependiendo de su situaci\u00f3n acad\u00e9mica y el promedio ponderado de los dos \u00faltimos semestres acad\u00e9micos.\n\nPara estudiantes que hayan aprobado todas las asignaturas del primer ciclo en su primera matr\u00edcula y tengan un promedio ponderado igual o mayor a doce (12), podr\u00e1n matricularse en todas las asignaturas del segundo ciclo y adelantar como m\u00e1ximo dos asignaturas adicionales, siempre y cuando el plan de estudios lo permita.\n\nPara estudiantes que hayan cursado solo el primer ciclo y no cumplan con los requisitos anteriores, as\u00ed como para aquellos que hayan cursado dos o m\u00e1s ciclos, el n\u00famero m\u00e1ximo de cr\u00e9ditos permitidos a matricularse se establece seg\u00fan el promedio ponderado de los dos \u00faltimos semestres acad\u00e9micos cursados y est\u00e1 indicado en la Tabla 1, descrita en el CAP\u00cdTULO VI del Reglamento de Matr\u00edcula publicado en la secci\u00f3n \"Matr\u00edcula y Procedimientos\" de la p\u00e1gina web de la Facultad de Ciencias (https://fc.uni.edu.pe/documentos/). Esta tabla asigna un l\u00edmite de cr\u00e9ditos seg\u00fan el promedio ponderado de los dos \u00faltimos semestres, desde 28 cr\u00e9ditos para promedios entre 14 y 20, hasta 15 cr\u00e9ditos para promedios entre 0 y 8.\n\nEs importante mencionar que para estudiantes en riesgo acad\u00e9mico, la determinaci\u00f3n de la cantidad de cr\u00e9ditos a matricular no se basar\u00e1 en dicha Tabla, sino que ser\u00e1 recomendada por la Oficina de Tutor\u00eda y la Comisi\u00f3n de Matr\u00edcula de la Facultad. Dicha cantidad de cr\u00e9ditos a matricularse para un estudiante en riesgo academico usualmente es mas limitada poniendo mayor prioridad en la matricula de los cursos desaprobados mas de dos veces.\n\nAdemas, en el caso de nuevos ingresantes\n\nProcedimiento Para Reserva De Matricula\n\u00bfCu\u00e1l es el procedimiento que debe seguir un estudiante para reservar su matricula?\nEl estudiante o apoderado deber\u00e1 presentar la solicitud de Reserva de Matr\u00edcula dirigida al Decano, a trav\u00e9s de la plataforma SIGA-DIRCE (intranet-alumnos), antes de la semana oficial de matr\u00edcula en los plazos establecidos en el calendario de actividades acad\u00e9micas. El modelo de la solicitud para la reserva de matricula se puede encontrar publicado en la secci\u00f3n \"Matr\u00edcula y Procedimientos\" de la pagina web de la facultad de ciencias (https://fc.uni.edu.pe/documentos/). La reserva de matr\u00edcula, realizada por solicitud procede por razones de salud, trabajo o de otras naturaleza debidamente sustentada, para tal efecto el estudiante adjuntar\u00e1 los documentos que acrediten la raz\u00f3n invocada.\nEn caso no se presente esta solicitud y el estudiante no haya concretado su matr\u00edcula en el periodo academico actual, DIRCE realizar\u00e1, de oficio, la reserva de matr\u00edcula del estudiante.\nEl periodo de reserva de matr\u00edcula no exceder\u00e1 a los tres (03) a\u00f1os (o seis semestres) acad\u00e9micos consecutivos o alternos (equivalente a 06 periodos acad\u00e9micos).\nEl tramite de la reserva de matricula no tiene ning\u00fan pago asociado."

print(a)