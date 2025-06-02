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

#context = "\n\nRequisitos Y Procedimiento Para Matricula Solo Para Ingresantes\n\u00bfCuales son los requisitos y el proceso de matr\u00edcula para nuevos ingresantes de pregrado en la Facultad de Ciencias de la Universidad Nacional de Ingenier\u00eda?\nLos nuevos alumnos de pregrado ingresantes a la Facultad de Ciencias, realizaran el siguiente proceso para completar su primera matricula (primera matricula al primer ciclo):\n    1. Recabar su constancia de ingreso. Luego de gestionar la emisi\u00f3n de su constancia de ingreso, la Direcci\u00f3n de Admisi\u00f3n (DIAD) de la UNI enviar\u00e1 a su correo la constancia de ingreso.\n    2. Actualizaci\u00f3n de datos en intranet. DIRCE har\u00e1 llegar a su correo su clave para acceder a la plataforma de intranet-alumnos y completar sus datos.\n    3. Registrar los datos en la Facultad de Ciencias. La oficina de estad\u00edstica de la facultad enviar\u00e1 al correo del ingresante la ficha de datos. El llenado es car\u00e1cter obligatorio.\n    4. Efectuar el pago por autoseguro (S/. 55.00) en el plazo establecido en el cronograma. Para ello, primero generar una orden de pago a traves de la plataforma intranet-alumnos.\n    5. Realizar la entrega de los siguientes documentos a la oficina de estad\u00edstica seg\u00fan el cronograma de actividades de matr\u00edcula para ingresantes publicado dentro de la secci\u00f3n 'MATR\u00cdCULA Y PROCEDIMIENTOS' en la p\u00e1gina web de la Facultad de Ciencias.\n        - Constancia de Ingreso\n        - Ficha de datos\n        - Constancia de Evaluaci\u00f3n Socioecon\u00f3mica\n        - Certificado M\u00e9dico expedido por el Centro Medico UNI\n        - Comprobante de pago de Autoseguro Estudiantil\n    6. La oficina de estad\u00edstica ejecutar\u00e1 la matr\u00edcula (inscripci\u00f3n de cursos) de los ingresantes seg\u00fan el cronograma de actividades, \u00fanicamente para aquellos que hayan cumplido con la entrega de la entrega de los documentos requeridos en de las fechas establecidas en el cronograma.\n    7. Los ingresantes matriculados recibir\u00e1n un correo con el horario de sus cursos y tambi\u00e9n podr\u00e1n visualizar sus cursos y horarios en la plataforma intranet-alumnos.\n\nRequisitos Y Procedimiento Matricula Regular\n\u00bfCuales son los requisitos y el proceso de matr\u00edcula regular al ciclo acad\u00e9mico para alumnos regulares de pregrado en la Facultad de Ciencias de la Universidad Nacional de Ingenier\u00eda?\nSon requisitos para la matr\u00edcula regular efectuar el pago por autoseguro estudiantil y no presentar adeudos con su Facultad ya sea econ\u00f3micas, por pr\u00e9stamo de libros o cualquier otro material de ense\u00f1anza en general en la biblioteca. Adem\u00e1s, los alumnos en riesgo acad\u00e9mico deben haber completado la tutor\u00eda obligatoria previa a la matr\u00edcula. Los estudiantes que hayan dejado de estudiar, o reservado matr\u00edcula  reservado matr\u00edcula, o solicitado su retiro total en el \u00faltimo per\u00edodo en que estuvieron matriculados, deber\u00e1n previamente haber tramitado su reincorporaci\u00f3n a traves de la plataforma intranet-alumnos.\n\nEl proceso para que un alumno de pregrado realice su matr\u00edcula regular al ciclo acad\u00e9mico, es el siguiente:\n1. Generar una orden de pago para el autoseguro estudiantil a trav\u00e9s de la plataforma INTRALU. En esta plataforma, selecciona la opci\u00f3n \"Tr\u00e1mites\" para acceder al m\u00f3dulo de tramites y pagos. En dicho m\u00f3dulo, selecciona el tr\u00e1mite correspondiente en el men\u00fa desplegable, haz clic en el bot\u00f3n \"Nuevo\" y sigue las indicaciones hasta generar la orden de pago.\n2. Realizar el pago del autoseguro dentro de los plazos establecidos en el calendario de actividades acad\u00e9micas, acerc\u00e1ndose a un sucursal del BCP o a traves de la aplicaci\u00f3n movil del banco.\n3. Luego, en la fecha y turno asignado, el estudiante llevar\u00e1 a cabo a su matr\u00edcula de forma virtual, es decir, realizar\u00e1 la inscripci\u00f3n de sus cursos a trav\u00e9s de la plataforma intranet-alumnos. Acceder\u00e1 al m\u00f3dulo de Matr\u00edcula UNI dentro de esta plataforma, seleccionar\u00e1 las asignaturas y horarios deseados, y finalizar\u00e1 confirmando la matr\u00edcula en todas las asignaturas elegidas en el sistema.\n\nNo se requiere la entrega del voucher de pago del autoseguro ni otros documentos para la matricula regular.  \nLos turnos para la matr\u00edcula, son asignados por grupos de acuerdo al promedio ponderado de los \u00faltimos dos ciclos, en un orden de m\u00e9rito. Cada alumno puede verificar su turno correspondiente dentro de la plataforma intranet-alumnos.\n\nM\u00e1ximo De Cr\u00e9ditos A Matricularse Para Un Estudiante\n\u00bfEn cuantos cr\u00e9ditos como m\u00e1ximo puede matricularse un estudiante de la Facultad de Ciencias de la UNI?\nEl n\u00famero m\u00e1ximo de cr\u00e9ditos en los que un estudiante de la Facultad de Ciencias de la UNI puede matricularse var\u00eda dependiendo de su situaci\u00f3n acad\u00e9mica y el promedio ponderado de los dos \u00faltimos semestres acad\u00e9micos.\n\nPara estudiantes que hayan aprobado todas las asignaturas del primer ciclo en su primera matr\u00edcula y tengan un promedio ponderado igual o mayor a doce (12), podr\u00e1n matricularse en todas las asignaturas del segundo ciclo y adelantar como m\u00e1ximo dos asignaturas adicionales, siempre y cuando el plan de estudios lo permita.\n\nPara estudiantes que hayan cursado solo el primer ciclo y no cumplan con los requisitos anteriores, as\u00ed como para aquellos que hayan cursado dos o m\u00e1s ciclos, el n\u00famero m\u00e1ximo de cr\u00e9ditos permitidos a matricularse se establece seg\u00fan el promedio ponderado de los dos \u00faltimos semestres acad\u00e9micos cursados y est\u00e1 indicado en la Tabla 1, descrita en el CAP\u00cdTULO VI del Reglamento de Matr\u00edcula publicado dentro de la secci\u00f3n [\"Matr\u00edcula y Procedimientos\" de la p\u00e1gina web de la Facultad de Ciencias](https://fc.uni.edu.pe/estadistica/documentos/). Esta tabla asigna un l\u00edmite de cr\u00e9ditos seg\u00fan el promedio ponderado de los dos \u00faltimos semestres, desde 28 cr\u00e9ditos para promedios entre 14 y 20, hasta 15 cr\u00e9ditos para promedios entre 0 y 8.\n\nEs importante mencionar que para estudiantes en riesgo acad\u00e9mico, la determinaci\u00f3n de la cantidad de cr\u00e9ditos a matricular no se basar\u00e1 en dicha Tabla, sino que ser\u00e1 recomendada por la Oficina de Tutor\u00eda y la Comisi\u00f3n de Matr\u00edcula de la Facultad. Dicha cantidad de cr\u00e9ditos a matricularse para un estudiante en riesgo academico usualmente es mas limitada poniendo mayor prioridad en la matricula de los cursos desaprobados mas de dos veces.\n\nAdem\u00e1s, en el caso de los nuevos ingresantes, \u00fanicamente podr\u00e1n inscribirse en asignaturas correspondientes al primer ciclo. No es obligatorio inscribirse al m\u00e1ximo de cr\u00e9ditos permitidos. Esta inscripci\u00f3n ser\u00e1 efectuada directamente por la oficina de estad\u00edsticas (AERA).\n\nProceso De Matricula\nDe los Requisitos de la Matr\u00edcula\nArt. 46\u00b0 La ense\u00f1anza en el antegrado es gratuita para la primera carrera profesional. Son requisitos para la matr\u00edcula, los siguientes:\n\ta. Cumplir con los requisitos acad\u00e9micos establecidos en el presente reglamento .\n\tb. Realizar el pago por concepto de Autoseguro M\u00e9dico. En caso de inconvenientes, presentar por correo o de forma f\u00edsica el recibo de pago.\n\tc. En caso de la matricula regular, reincorporaci\u00f3n o traslado interno, no presentar adeudos con su Facultad (econ\u00f3mico, libros, enseres, o material de ense\u00f1anza en general)\n\td. Aquellos estudiantes que no puedan cumplir con las deudas del tipo econ\u00f3mico podr\u00e1n solicitar, con diez (1O) d\u00edas \u00fatiles de anticipaci\u00f3n, facilidades a la Comisi\u00f3n de Matr\u00edcula y comprometerse a una forma de pago a plazos, evitando que sea una restricci\u00f3n de su matr\u00edcula. Esta ventaja se perder\u00e1 si no hubiese cumplido con similar compromiso en su anterior matr\u00edcula.\n\te. En el caso de los traslados internos, externos, graduados, titulados, convenios internacionales, adem\u00e1s de los incisos anteriores, deben presentar la Constancia o la Resoluci\u00f3n Directora! de convalidaci\u00f3n de las asignaturas. \n\tf. Los estudiantes que realizan su matr\u00edcula en forma rezagada deber\u00e1n efectuar el pago correspondiente establecido en las normas de la UNI. \n\tg. Los estudiantes que hayan dejado de estudiar, o reservado matr\u00edcula o hayan solicitado su retiro total en alg\u00fan periodo anterior, deber\u00e1n previamente haber solicitado su reincorporaci\u00f3n ante su Decano y su tr\u00e1mite lo realizar\u00e1 v\u00eda la plataforma DIRCE-UNI.\n\t\t Si requiriesen cambio previo de Plan de Estudios y convalidaciones correspondientes, \u00e9stas ya deben haberse tramitado. En estos casos , el tr\u00e1mite de reincorporaci\u00f3n debe hacerse con no menos de una semana adicional de anticipaci\u00f3n.\n\th. El pago del carn\u00e9 universitario no es requisito para la matr\u00edcula.\n\ti. No ser\u00e1 necesario que los estudiantes hayan participado en el \u00faltimo proceso electoral para ser matriculados, sin que esto signifique exonerarlo de la multa correspondiente. \n\tj. Otros de acuerdo con lo establecido en las normas de la UNI.\nEscuelas Profesionales de la Facultad de Ciencias de la UNI\n\nInformaci\u00f3n de Contacto:\nSeg\u00fan la escuela profesional (carrera universitaria), el correo de contacto es el siguiente:\n\nPara F\u00edsica, Qu\u00edmica o Ciencia de la Computaci\u00f3n: escuelas_fc1@uni.edu.pe\nPara Matem\u00e1ticas o Ingenier\u00eda F\u00edsica: escuelas_fc2@uni.edu.pe\n\nHorario de Atenci\u00f3n de Escuelas Profesionales: De Lunes a Viernes de 8:30 a.m a 4:00 p.m\n\n\u00c1rea de Estad\u00edstica y Registros Acad\u00e9micos de la Facultad de Ciencias de la UNI\n\nInformaci\u00f3n de Contacto de la oficina de estad\u00edstica (AERA)\nE-mail: estadistica_fc@uni.edu.pe\n\nHorario de Atenci\u00f3n de la oficina de estad\u00edstica (AERA):\nDe Lunes a Viernes de 8:00 a.m. a 4:00 p.m."
#print(context)

#context= "\n\nInformacion General Fc\nFacultad de Ciencias de la Universidad Nacional de Ingenier\u00eda\n\nLa Facultad de Ciencias es una de las 11 facultades de la Universidad Nacional de Ingenier\u00eda (UNI) de Per\u00fa.\nEsta facultad ofrece 5 carreras universitarias, las cuales conforman las escuelas profesionales. Estas son:\n    - Escuela Profesional de Ingenier\u00eda F\u00edsica\n    - Escuela Profesional de Qu\u00edmica\n    - Escuela Profesional de F\u00edsica\n    - Escuela Profesional de Matem\u00e1ticas\n    - Escuela Profesional de Ciencias de la Computaci\u00f3n\n\nPagina Web de las Facultad de Ciencias: https://fc.uni.edu.pe/\n\nEn la secci\u00f3n de Matr\u00edcula y Procedimientos de esta pagina web se publica:\n    * Manuales/Documentos informativos sobre diferentes procesos de matr\u00edcula, procedimientos y tr\u00e1mites acad\u00e9micos para estudiantes de pregrado de la Facultad.\n    * El calendario de actividades acad\u00e9micas.\n    * Modelos de solicitudes para distintos procesos acad\u00e9micos.\n    * Reglamentos acad\u00e9micos de pregrado: \n        - Reglamento de Matr\u00edcula\n        - Reglamento de Evaluaci\u00f3n\n        - Reglamento de Tutor\u00eda\n\nFechas De Matricula\n\u00bfD\u00f3nde puede un estudiante de pregrado de la Facultad de Ciencias consultar la fecha y turno correspondiente para la matr\u00edcula para el ciclo acad\u00e9mico?\nLas fechas de matr\u00edcula para cada ciclo acad\u00e9mico se encuentran disponibles en el calendario de actividades academicas, el cual se publica dentro de la secci\u00f3n \"Matr\u00edcula y Procedimientos\" p\u00e1gina web de la Facultad de Ciencias, puede ingresar a dicha secci\u00f3n de la pagina en siguiente enlace: https://fc.uni.edu.pe/estadistica/documentos/.\nLos horarios de matr\u00edcula, conocidos como turnos, son asignados de acuerdo al promedio ponderado de los \u00faltimos dos ciclos, en un orden de m\u00e9rito. Aquellos estudiantes con los promedios m\u00e1s altos recibir\u00e1n prioridad en los primeros turnos, seguidos por los dem\u00e1s en sucesi\u00f3n. La lista de este orden de m\u00e9rito, junto con los respectivos turnos de matr\u00edcula, se publica dentro de la secci\u00f3n \"Matr\u00edcula y Procedimientos\" de la p\u00e1gina web de la facultad de ciencias para garantizar que todos los alumnos est\u00e9n informados. Adem\u00e1s, cada alumno puede verificar su turno correspondiente en modulo de Matr\u00edcula dentro de la plataforma intranet-alumnos.\n\nInformacion General Escuelas Profesionales\nEscuelas Profesionales de la Facultad de Ciencias de la UNI\n\nLas Escuelas Profesionales son uno de los \u00f3rganos de l\u00ednea dentro de la estructura administrativa de la Facultad de Ciencias.\n\nInformaci\u00f3n de Contacto:\nSeg\u00fan la escuela profesional (carrera universitaria), el correo de contacto es el siguiente:\n\nPara F\u00edsica, Qu\u00edmica o Ciencia de la Computaci\u00f3n: escuelas_fc1@uni.edu.pe\nPara Matem\u00e1ticas o Ingenier\u00eda F\u00edsica: escuelas_fc2@uni.edu.pe\n\n\nProcedimiento Para Realizar Ayudant\u00eda Acad\u00e9mica\n\u00bfCu\u00e1l es el procedimiento a seguir para que un estudiante de pregrado de la Facultad de Ciencias de la UNI pueda realizar ayudant\u00eda academica?\nLos estudiantes que deseen realizar ayudant\u00eda acad\u00e9mica deben ponerse en contacto con el departamento de su Escuela Profesional correspondiente para obtener m\u00e1s informaci\u00f3n. A continuaci\u00f3n se detallan las direcciones de correo electr\u00f3nico seg\u00fan la escuela profesional:\nF\u00edsica, Qu\u00edmica o Ciencia de la Computaci\u00f3n: escuelas_fc1@uni.edu.pe\nMatem\u00e1ticas o Ingenier\u00eda F\u00edsica: escuelas_fc2@uni.edu.pe\n\nProcedimiento Para Solicitar Constancia De Ayudantia Acad\u00e9mica\n\u00bfQu\u00e9 procedimiento debe seguir un estudiante de pregrado de la Facultad de Ciencias de la UNI para solicitar su constancia de Ayudantia acad\u00e9mica?\nEl tr\u00e1mite se realiza con el Director de Escuela correspondiente. El estudiante puede solicitar informaci\u00f3n a las siguientes direcciones de correo electr\u00f3nico seg\u00fan su escuela profesional.\nPara F\u00edsica, Qu\u00edmica o Ciencia de la Computaci\u00f3n: escuelas_fc1@uni.edu.pe\nPara Matem\u00e1ticas o Ingenier\u00eda F\u00edsica: escuelas_fc2@uni.edu.pe\nEl horario de atenci\u00f3n de las oficinas de Escuelas Profesionales es de lunes a viernes de 8:30 a.m a 4:00 p.m\n\nHorarios De Cursos\n\u00bfD\u00f3nde puede un estudiante visualizar la lista de cursos y sus respectivos horarios para el ciclo academico actual o el pr\u00f3ximo a empezar?\nLa lista completa de los cursos que ser\u00e1n impartidos en el ciclo academico (semestre) junto con sus horarios y profesores correspondientes es publicado con respectiva anticipaci\u00f3n a la matricula dentro de la secci\u00f3n [\"Matr\u00edcula y Procedimientos\" de la p\u00e1gina web de la Facultad de Ciencias](https://fc.uni.edu.pe/estadistica/documentos/). Adem\u00e1s, cada estudiante tambien puede encontrar informaci\u00f3n sobre los cursos y horarios en el modulo de Matricula dentro de la plataforma intranet-alumnos.\n\nPlan De Estudios\n\u00bfQu\u00e9 es el plan de estudios para los alumnos de la Facultad de Ciencias de la Universidad Nacional de Ingenier\u00eda?\nEl plan de estudios de la Facultad de Ciencias (FC) de la Universidad Nacional de Ingenier\u00eda (UNI) constituye la estructura curricular que organiza las asignaturas, cr\u00e9ditos y otros componentes acad\u00e9micos de cada programa de pregrado.\nEste plan establece los cursos que los estudiantes deben completar para culminar su carrera y egresar, distribuidos a lo largo de diez semestres acad\u00e9micos. El plan de estudios contempla:\n\n- Cursos obligatorios: Asignaturas fundamentales que todos los estudiantes de una determinada carrera deben cursar, con el objetivo de adquirir los conocimientos esenciales de su disciplina.\n\n- Cursos electivos: Asignaturas que los estudiantes pueden seleccionar de acuerdo con sus intereses, con el fin de especializarse o profundizar en \u00e1reas espec\u00edficas de su formaci\u00f3n.\n\n- Cr\u00e9ditos acad\u00e9micos: Unidad de medida que refleja la carga acad\u00e9mica de cada curso. El plan de estudios establece un n\u00famero m\u00ednimo de cr\u00e9ditos que el estudiante debe aprobar para culminar su carrera.\n\nEl plan de estudios de las carreras ofrecidas por la Facultad de Ciencias se encuentra disponible en la p\u00e1gina web oficial de la Facultad. Adem\u00e1s, los estudiantes matriculados pueden consultar su avance curricular en el plan de estudios correspondiente a trav\u00e9s de la plataforma INTRALU.\n\nProcedimiento Para Solicitar Una Constancia De Matricula En La Facultad De Ciencias De La Uni\n\u00bfQu\u00e9 procedimiento debe seguir un estudiante para solicitar una constancia de Matricula en ingles o en espa\u00f1ol?\nPara solicitar una constancia de matr\u00edcula en ingl\u00e9s o en espa\u00f1ol, el estudiante deber seguir los siguientes pasos:\n\n1. Enviar un correo a estadistica_fc@uni.edu.pe solicitando una orden de pago para la CONSTANCIA DE MATR\u00cdCULA. En el mensaje, deber\u00e1 incluir sus datos personales: n\u00famero de DNI, apellidos, nombres, correo institucional y/o alternativo.\n\n2. La oficina de estad\u00edstica (AERA) le enviar\u00e1 la orden de pago por el monto correspondiente al correo electr\u00f3nico del estudiante.\n\n3. Realize el pago en alguna sucursal del BCP o a trav\u00e9s aplicaci\u00f3n movil del banco. En la app selecciona \"Pagar servicios\", elige la Universidad Nacional de Ingenier\u00eda, luego la opci\u00f3n de pago para estudiantes, e ingresa su n\u00famero de DNI. La app mostrar\u00e1 la orden de pago con el monto exacto para realizar el pago.\n\n4. Luego, deber\u00e1 enviar la solicitud correspondiente a mesa de partes de la facultad de ciencias al correo mesadepartes_fc@uni.edu.pe. Es importante que se asegure de indicar en la solicitud si desea la CONSTANCIA DE MATR\u00cdCULA en ingl\u00e9s o espa\u00f1ol. El modelo para esta solicitud est\u00e1 disponible dentro de la secci\u00f3n [\"MATR\u00cdCULA Y PROCEDIMIENTOS\" en la p\u00e1gina web de la Facultad de Ciencias](https://fc.uni.edu.pe/estadistica/documentos/).\n\n5. Por \u00faltimo, la constancia se enviar\u00e1 al correo institucional del estudiante.\n\nCalendario De Actividades Acad\u00e9micas\n\u00bfQu\u00e9 es el calendario de actividades acad\u00e9micas de la Facultad de Ciencias de la UNI y d\u00f3nde se publica?\nEl Calendario de Actividades Acad\u00e9micas es un documento oficial que establece las fechas y horarios de las principales actividades acad\u00e9micas durante un per\u00edodo acad\u00e9mico (ciclo semestral). Este calendario incluye informaci\u00f3n clave, como:\n- Fechas para la presentaci\u00f3n de solicitudes de traslado interno, reincorporaci\u00f3n y reserva de matr\u00edcula.\n- Fechas de inicio y finalizaci\u00f3n de clases.\n- Fechas para la matr\u00edcula regular, de ingresantes y matr\u00edcula rezagada.\n- Fechas de ex\u00e1menes parciales, finales y sustitutorios.\n- Fechas para el retiro parcial y retiro total de asignaturas.\n- Entre otras actividades relevantes para los estudiantes.\nSe recomienda revisar el calendario completo para conocer todos los detalles.\n\nEl calendario de actividades acad\u00e9micas es publicado en las seccion [Matr\u00edcula y Procedimientos de la Pagina Web de la Facultad de Ciencias](https://fc.uni.edu.pe/estadistica/documentos/)\nEscuelas Profesionales de la Facultad de Ciencias de la UNI\n\nInformaci\u00f3n de Contacto:\nSeg\u00fan la escuela profesional (carrera universitaria), el correo de contacto es el siguiente:\n\nPara F\u00edsica, Qu\u00edmica o Ciencia de la Computaci\u00f3n: escuelas_fc1@uni.edu.pe\nPara Matem\u00e1ticas o Ingenier\u00eda F\u00edsica: escuelas_fc2@uni.edu.pe\n\nHorario de Atenci\u00f3n de Escuelas Profesionales: De Lunes a Viernes de 8:30 a.m a 4:00 p.m\n\n\u00c1rea de Estad\u00edstica y Registros Acad\u00e9micos de la Facultad de Ciencias de la UNI\n\nInformaci\u00f3n de Contacto de la oficina de estad\u00edstica (AERA)\nE-mail: estadistica_fc@uni.edu.pe\n\nHorario de Atenci\u00f3n de la oficina de estad\u00edstica (AERA):\nDe Lunes a Viernes de 8:00 a.m. a 4:00 p.m."



#print(context)

#print(count_num_tokens(context))
#print("ids_faqs:", ids_faqs[0:15])


#split_file_questions_refomulated(dir_path, filtered_questions_reformulated_rouge)

#a = "\u00bfCuales son los requisitos y el proceso de matr\u00edcula regular para alumnos de pregrado en la Facultad de Ciencias de la Universidad Nacional de Ingenier\u00eda?"
#print(a)
#filtered_reformulated_question_list = flat_questions_reformulate(filtered_questions_reformulated_rouge_list)

#save_json("./faq", f"filtered_reformulated_question_list", filtered_reformulated_question_list)

