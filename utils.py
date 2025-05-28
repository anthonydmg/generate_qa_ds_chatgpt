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


def join_reformulated_questions(reformulated_faqs = []):
    tab_all_questions = {}
    tab_ids_faq = {}
    for reformulated_faq in reformulated_faqs:
        original_question = reformulated_faq["original_question"]
        questions_generated = reformulated_faq["questions_generated"]
        
        if original_question not in tab_all_questions:
            tab_all_questions[original_question] = questions_generated
            tab_ids_faq[original_question] = reformulated_faq["id_faq"]
        else:
            tab_all_questions[original_question].extend(questions_generated)
    
    ## Format questions
    
    reformulated_faqs_joined = [ {"id_faq": tab_ids_faq[k]  ,"original_question": k, "questions_generated": v } for k,v in tab_all_questions.items()]

    return reformulated_faqs_joined
""" 
reformulated_faqs = load_json("./faq/reformulated_faqs.json")


reformulated_faqs_joined = join_reformulated_questions(reformulated_faqs)

save_json("./faq", "reformulated_faqs_joined", reformulated_faqs_joined) """


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
            "id_faq": reformulated_faq["id_faq"],
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




def split_file_questions_refomulated(dir_path, filtered_questions_reformulated_rouge):
    for i, reformulated_faq in enumerate(filtered_questions_reformulated_rouge):
        #original_question = reformulated_faq["original_question"]
        id_faq = reformulated_faq["id_faq"]
        questions_generated = reformulated_faq["questions_generated"]
        save_json(dir_path, f"faq_{id_faq}_reformulated", questions_generated)
    return 

def split_file_questions_derived(dir_path, filtered_questions_derived_rouge):
    for i, derived_faq in enumerate(filtered_questions_derived_rouge):
        #original_question = derived_faq["original_question"]
        id_faq = derived_faq["id_faq"]
        questions_generated = derived_faq["additional_questions"]
        save_json(dir_path, f"faq_{id_faq + 1}_derived", questions_generated)
    return

#dir_path_d = "./faq-derived/data"
#filtered_questions_derived_rouge = load_json("faq/derived_faqs_rouge_0.75/filtered_questions.json")
#split_file_questions_derived(dir_path_d, filtered_questions_derived_rouge)
""" 
dir_path = "./faq-reformulated/data"
filtered_questions_reformulated_rouge = load_json("./faq/reformulated_0.8/filtered_questions_reformulated_rouge_0.8.json")

ids_faqs = [faq["id_faq"] for faq in filtered_questions_reformulated_rouge]
ids_faqs = ids_faqs[:15]

from glob import glob

files = glob("./conversational_faq/data/*.json")
filenames = [os.path.basename(file) for file in files]
new_filenames = []
for filename in filenames:
    pattern = r'faq_(\d+)'
    # Extraer el número usando re.search()
    match = re.search(pattern, filename)
    if match:
        old_number = match.group(1)
        old_number = int(old_number)
        print(f"El número extraído es: {old_number}")
        new_number = ids_faqs[old_number - 1]
        new_filename = re.sub(r'faq_\d+', f'faq_{new_number}' , filename)
        new_filenames.append(new_filename)
    else:
        print("No se encontró ningún número.")

print("filenames[1]", filenames[1])
print("new_filenames[1]", new_filenames[1])
print("new_filenames:", len(new_filenames))
print("filenames:", len(filenames))
print("ids_faqs:", ids_faqs)
import shutil

dir_path = "./conversational_faq/data/"
dir_path_save = "./conversational_faq/data_ordered/"
os.makedirs(dir_path_save, exist_ok=True)
for old_filename, new_filename in zip(filenames, new_filenames):
   shutil.copy2(os.path.join(dir_path, old_filename), os.path.join(dir_path_save, new_filename)) """

context = "\n\nCalendario De Actividades Acad\u00e9micas\n\u00bfQu\u00e9 es el calendario de actividades acad\u00e9micas de la Facultad de Ciencias de la UNI y d\u00f3nde se publica?\nEl Calendario de Actividades Acad\u00e9micas es un documento oficial que establece las fechas y horarios de las principales actividades acad\u00e9micas durante un per\u00edodo acad\u00e9mico (ciclo semestral). Este calendario incluye informaci\u00f3n clave, como:\n- Fechas para la presentaci\u00f3n de solicitudes de traslado interno, reincorporaci\u00f3n y reserva de matr\u00edcula.\n- Fechas de inicio y finalizaci\u00f3n de clases.\n- Fechas para la matr\u00edcula regular, de ingresantes y matr\u00edcula rezagada.\n- Fechas de ex\u00e1menes parciales, finales y sustitutorios.\n- Fechas para el retiro parcial y retiro total de asignaturas.\n- Entre otras actividades relevantes para los estudiantes.\nSe recomienda revisar el calendario completo para conocer todos los detalles.\n\nEl calendario de actividades acad\u00e9micas es publicado en las seccion [Matr\u00edcula y Procedimientos de la Pagina Web de la Facultad de Ciencias](https://fc.uni.edu.pe/estadistica/documentos/)\n\nHorarios De Cursos\n\u00bfD\u00f3nde puede un estudiante visualizar la lista de cursos y sus respectivos horarios para el ciclo academico actual o el pr\u00f3ximo a empezar?\nLa lista completa de los cursos que ser\u00e1n impartidos en el ciclo academico (semestre) junto con sus horarios y profesores correspondientes es publicado con respectiva anticipaci\u00f3n a la matricula dentro de la secci\u00f3n [\"Matr\u00edcula y Procedimientos\" de la p\u00e1gina web de la Facultad de Ciencias](https://fc.uni.edu.pe/estadistica/documentos/). Adem\u00e1s, cada estudiante tambien puede encontrar informaci\u00f3n sobre los cursos y horarios en el modulo de Matricula dentro de la plataforma intranet-alumnos.\n\nFechas De Matricula\n\u00bfD\u00f3nde puede un estudiante de pregrado de la Facultad de Ciencias consultar la fecha y turno correspondiente para la matr\u00edcula para el ciclo acad\u00e9mico?\nLas fechas de matr\u00edcula para cada ciclo acad\u00e9mico se encuentran disponibles en el calendario de actividades academicas, el cual se publica dentro de la secci\u00f3n \"Matr\u00edcula y Procedimientos\" p\u00e1gina web de la Facultad de Ciencias, puede ingresar a dicha secci\u00f3n de la pagina en siguiente enlace: https://fc.uni.edu.pe/estadistica/documentos/.\nLos horarios de matr\u00edcula, conocidos como turnos, son asignados de acuerdo al promedio ponderado de los \u00faltimos dos ciclos, en un orden de m\u00e9rito. Aquellos estudiantes con los promedios m\u00e1s altos recibir\u00e1n prioridad en los primeros turnos, seguidos por los dem\u00e1s en sucesi\u00f3n. La lista de este orden de m\u00e9rito, junto con los respectivos turnos de matr\u00edcula, se publica dentro de la secci\u00f3n \"Matr\u00edcula y Procedimientos\" de la p\u00e1gina web de la facultad de ciencias para garantizar que todos los alumnos est\u00e9n informados. Adem\u00e1s, cada alumno puede verificar su turno correspondiente en modulo de Matr\u00edcula dentro de la plataforma intranet-alumnos.\n\nInformacion General Fc\nFacultad de Ciencias de la Universidad Nacional de Ingenier\u00eda\n\nLa Facultad de Ciencias es una de las 11 facultades de la Universidad Nacional de Ingenier\u00eda (UNI) de Per\u00fa.\nEsta facultad ofrece 5 carreras universitarias, las cuales conforman las escuelas profesionales. Estas son:\n    - Escuela Profesional de Ingenier\u00eda F\u00edsica\n    - Escuela Profesional de Qu\u00edmica\n    - Escuela Profesional de F\u00edsica\n    - Escuela Profesional de Matem\u00e1ticas\n    - Escuela Profesional de Ciencias de la Computaci\u00f3n\n\nPagina Web de las Facultad de Ciencias: https://fc.uni.edu.pe/\n\nEn la secci\u00f3n de Matr\u00edcula y Procedimientos de esta pagina web se publica:\n    * Manuales/Documentos informativos sobre diferentes procesos de matr\u00edcula, procedimientos y tr\u00e1mites acad\u00e9micos para estudiantes de pregrado de la Facultad.\n    * El calendario de actividades acad\u00e9micas.\n    * Modelos de solicitudes para distintos procesos acad\u00e9micos.\n    * Reglamentos acad\u00e9micos de pregrado: \n        - Reglamento de Matr\u00edcula\n        - Reglamento de Evaluaci\u00f3n\n        - Reglamento de Tutor\u00eda\n\nAcceso Y Contenido De La Plataforma Intralu De La Uni\n\u00bfC\u00f3mo un estudiante de pregrado de la UNI puede acceder a la plataforma INTRALU de la UNI y que informaci\u00f3n o funcionalidades ofrece la plataforma?\nPara acceder a INTRALU, el estudiante debe ingresar a la [p\u00e1gina web de la DIRCE de la UNI](https://dirce.uni.edu.pe/) y seleccionar la opci\u00f3n \"INTRALU\", lo cual abrir\u00e1 la plataforma INTRALU en una nueva pesta\u00f1a. Tambi\u00e9n puede acceder directamente con el siguiente enlace: https://alumnos.uni.edu.pe/login\nPara iniciar sesi\u00f3n, el estudiante deber\u00e1 proporcionar su c\u00f3digo de alumno UNI y la clave de acceso proporcionada por DIRCE. Tambi\u00e9n puede optar por utilizar la autenticaci\u00f3n a trav\u00e9s del correo institucional.\nEn INTRALU, el estudiante podr\u00e1 consultar los cursos en los que se encuentra matriculado durante el periodo acad\u00e9mico actual, as\u00ed como revisar las calificaciones de dichos cursos y de ciclos anteriores. Tambi\u00e9n tendr\u00e1 acceso a su plan de estudios y podr\u00e1 visualizar su avance curricular, el cual incluye los cursos aprobados correspondientes a cada ciclo seg\u00fan el plan de estudios, junto con los promedios obtenidos y los cr\u00e9ditos acumulados.\nAdem\u00e1s, la plataforma permite acceder a las fichas acad\u00e9micas, que contienen el detalle de los cursos cursados en cada periodo acad\u00e9mico matriculado. el estudiante puede gestionar diversos tr\u00e1mites acad\u00e9micos, solicitudes y pagos, tales como: retiro parcial, retiro total, reserva de matr\u00edcula, as\u00ed como la solicitud y el pago de distintos certificados (por ejemplo, constancia de estudios \u2014simple o depurada\u2014, constancia de primera matr\u00edcula y constancia de no adeudos, entre otros). Del mismo modo, se pueden generar \u00f3rdenes de pago y realizar pagos por diferentes conceptos como el AUTOSEGURO estudiantil, el carn\u00e9 universitario, la matr\u00edcula rezagada y la reincorporaci\u00f3n, entre otros. Para m\u00e1s detalles sobre el proceso de pagos, se recomienda consultar el manual disponible en la p\u00e1gina web de la Facultad de Ciencias.\n\nProcedimiento Para Realizar Ayudant\u00eda Acad\u00e9mica\n\u00bfCu\u00e1l es el procedimiento a seguir para que un estudiante de pregrado de la Facultad de Ciencias de la UNI pueda realizar ayudant\u00eda academica?\nLos estudiantes que deseen realizar ayudant\u00eda acad\u00e9mica deben ponerse en contacto con el departamento de su Escuela Profesional correspondiente para obtener m\u00e1s informaci\u00f3n. A continuaci\u00f3n se detallan las direcciones de correo electr\u00f3nico seg\u00fan la escuela profesional:\nF\u00edsica, Qu\u00edmica o Ciencia de la Computaci\u00f3n: escuelas_fc1@uni.edu.pe\nMatem\u00e1ticas o Ingenier\u00eda F\u00edsica: escuelas_fc2@uni.edu.pe\n\nConceptos Matricula\n\tj. Oferta de Matr\u00edcula: Formato con el listado de asignaturas que cada alumnom encontrar\u00e1 en pantalla, para seleccionar su matr\u00edcula. Aplica los prerrequisitos y la dispersi\u00f3n de hasta tres ciclos. Destaca las asignaturas para matr\u00edcula obligatoria.\n\n\tk. Reporte de Matr\u00edcula: es el documento que muestra las asignaturas matriculadas en el per\u00edodo acad\u00e9mico vigente, y deber\u00e1 ser visado por la Oficina de Estad\u00edstica de la Facultad.\n\n\tl. Boleta de Matr\u00edcula: es el documento que muestra las asignaturas registradas en la DIRCE, luego del Cierre de Matr\u00edcula, para el per\u00edodo acad\u00e9mico vigente.\nRequiere del visado por la Oficina de Estad\u00edstica de la Facultad.\n\n\tm. Turno de Matr\u00edcula: es el lapso de apertura digital publicado en el portal web del Sistema de Matr\u00edcula UNI y deber\u00e1 establecer la fecha y horario en que el estudiante realizar\u00e1 su matr\u00edcula. Los turnos se organizan seg\u00fan el promedio ponderado de los dos \u00faltimos semestres acad\u00e9micos en el que un estudiante presenta matricula regular.\n\n\tn. Grupo Cero de matr\u00edcula: Es el listado que contiene las matr\u00edculas de quienes retornan de Separaci\u00f3n Temporal por Bajo Rendimiento Acad\u00e9mico y de los alumnos en Riesgo Acad\u00e9mico por asignaturas repetidas dos veces. La Comisi\u00f3n de Matr\u00edcula cierra el listado producido por la Tutor\u00eda, el d\u00eda anterior a la matricula y lo remite a la DIRCE para su registro previo, con m\u00ednimo tres horas antes del inicio del primer turno de matr\u00edcula.\n\n\to. Asignatura paralela: Este concepto surge durante los procesos de implementaci\u00f3n de nuevos planes de estudio. Es la asignatura similar o equivalente del anterior Plan de Estudios que con nuevo c\u00f3digo se dicta en el plan vigente. Seg\u00fan la disponibilidad de vacantes o docentes, puede darse con acta paralela en secci\u00f3n \u00fanica o en secci\u00f3n especial (con docente u horario diferente). La DIRCE la instala a pedido expreso de la Facultad, para estudiantes que est\u00e1n por culminar y que conservan el Plan anterior.\nEscuelas Profesionales de la Facultad de Ciencias de la UNI\n\nInformaci\u00f3n de Contacto:\nSeg\u00fan la escuela profesional (carrera universitaria), el correo de contacto es el siguiente:\n\nPara F\u00edsica, Qu\u00edmica o Ciencia de la Computaci\u00f3n: escuelas_fc1@uni.edu.pe\nPara Matem\u00e1ticas o Ingenier\u00eda F\u00edsica: escuelas_fc2@uni.edu.pe\n\nHorario de Atenci\u00f3n de Escuelas Profesionales: De Lunes a Viernes de 8:30 a.m a 4:00 p.m\n\n\u00c1rea de Estad\u00edstica y Registros Acad\u00e9micos de la Facultad de Ciencias de la UNI\n\nInformaci\u00f3n de Contacto de la oficina de estad\u00edstica (AERA)\nE-mail: estadistica_fc@uni.edu.pe\n\nHorario de Atenci\u00f3n de la oficina de estad\u00edstica (AERA):\nDe Lunes a Viernes de 8:00 a.m. a 4:00 p.m."
print(context)


#print("ids_faqs:", ids_faqs[0:15])


#split_file_questions_refomulated(dir_path, filtered_questions_reformulated_rouge)

#a = "\u00bfCuales son los requisitos y el proceso de matr\u00edcula regular para alumnos de pregrado en la Facultad de Ciencias de la Universidad Nacional de Ingenier\u00eda?"
#print(a)
#filtered_reformulated_question_list = flat_questions_reformulate(filtered_questions_reformulated_rouge_list)

#save_json("./faq", f"filtered_reformulated_question_list", filtered_reformulated_question_list)

