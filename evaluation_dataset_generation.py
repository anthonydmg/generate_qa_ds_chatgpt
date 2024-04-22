from utils import get_completion_from_messages, list_json_to_txt, load_json


from dotenv import load_dotenv
import openai
import os
import re
import math
def set_openai_key():
    API_KEY = os.getenv("API_KEY")
    openai.api_key = API_KEY

load_dotenv()

set_openai_key()

examples = [
{
"input": """Preguntas:
1. ¿Cuál es el número mínimo de créditos que los estudiantes de la Facultad de Ciencias de la Universidad Nacional de Ingeniería deben matricularse por semestre para conservar su condición de estudiante regular?
2. ¿Qué excepción se establece para los estudiantes que les falten menos créditos para culminar su carrera en cuanto a la cantidad mínima de créditos a matricular por semestre para conservar su condición de estudiante regular?
3. ¿Cuáles son las consecuencias para un estudiante de la Facultad de Ciencias de la Universidad Nacional de Ingeniería al desaprobar una misma materia por tercera vez?
4. ¿Qué sucede si un estudiante de la Facultad de Ciencias de la Universidad Nacional de Ingeniería desaprueba una misma materia por cuarta vez?""",

"response":"""
1. ¿Cuál es el número mínimo de créditos que los estudiantes de la Facultad de Ciencias de la Universidad Nacional de Ingeniería deben matricularse por semestre para conservar su condición de estudiante regular?
    - ¿Podrían informarme sobre la carga académica mínima requerida por semestre para mantenerme como estudiante regular en la Facultad de Ciencias?
    - ¿Me podrían decir cuántos créditos necesito inscribir cada semestre para no perder mi estatus de estudiante activo en la Facultad de Ciencias?
    - Estoy tratando de planificar mi horario, ¿cuál es la cantidad mínima de créditos que debo tomar para seguir siendo considerado un estudiante regular en la Facultad de Ciencias?
    - Como estudiante de la Facultad de Ciencias, ¿me podrían aclarar cuál es el mínimo de créditos que debo matricular para no caer en condición de irregular?
    - ¿Cuál es el límite inferior de créditos que debo cursar este semestre en la Facultad de Ciencias para mantener mi condición de estudiante regular?

2. ¿Qué excepción se establece para los estudiantes que les falten menos créditos para culminar su carrera en cuanto a la cantidad mínima de créditos a matricular por semestre para conservar su condición de estudiante regular?
    - Si estoy a punto de graduarme y me faltan pocos créditos, ¿existe alguna política especial respecto al mínimo de créditos que debo matricular para seguir siendo estudiante regular?
    - ¿Hay alguna flexibilidad en la cantidad mínima de créditos a matricular para aquellos de nosotros que estamos en el último tramo de nuestra carrera con pocos créditos restantes?
    - Como estudiante cercano a la graduación con menos créditos por completar, ¿cuál sería el mínimo de créditos que necesito inscribir para mantener mi estatus de estudiante regular?
    - ¿Podrían explicarme si hay alguna excepción en la carga académica mínima para estudiantes que están por terminar su carrera y les quedan pocos créditos?
    - En caso de que me falten solo unos créditos para finalizar mi carrera, ¿cuál es la política de la universidad respecto al mínimo de créditos que debo matricular para no perder mi condición de estudiante regular?
    
3. ¿Cuáles son las consecuencias para un estudiante de la Facultad de Ciencias de la Universidad Nacional de Ingeniería al desaprobar una misma materia por tercera vez?
    - ¿Qué penalizaciones enfrento si repruebo un curso por tercera ocasión en la Facultad de Ciencias?
    - ¿Podrían explicarme las repercusiones académicas de fallar tres veces la misma asignatura en Ciencias?
    - ¿Qué sucede en términos de mi estatus académico si no logro aprobar una materia después de tres intentos en la Universidad Nacional de Ingeniería?
    - ¿Cuál es el protocolo de la facultad si un estudiante no supera una clase en el tercer intento?
    - ¿Existen sanciones específicas para quienes desaprueban un curso tres veces consecutivas en la Facultad de Ciencias

4. ¿Qué sucede si un estudiante de la Facultad de Ciencias de la Universidad Nacional de Ingeniería desaprueba una misma materia por cuarta vez?
    - ¿Cuáles son las consecuencias de reprobar cuatro veces la misma asignatura en la Facultad de Ciencias?
    - ¿Qué medidas toma la universidad frente a un estudiante que no aprueba una materia en su cuarto intento?
    - ¿Puedo ser expulsado si desapruebo el mismo curso por cuarta vez en la Universidad Nacional de Ingeniería?
    - ¿Qué opciones académicas me quedan después de desaprobar una materia cuatro veces?
    - ¿Cómo afecta a mi carrera universitaria el desaprobar por cuarta vez un curso en la Facultad de Ciencias?"""
},
{
"input": """Preguntas:
1. ¿Cuál es el objetivo del Programa de Tutoría obligatorio para los estudiantes de la Facultad de Ciencias de la Universidad Nacional de Ingeniería que se encuentran en riesgo académico?
2. ¿En qué consiste el Programa de Tutoría para Estudiantes en Riesgo Académico de la Facultad de Ciencias de la Universidad Nacional de Ingeniería?
3. ¿Qué se entiende por estudiante en riesgo académico y qué medidas se les exige a estos estudiantes antes de poder matricularse nuevamente?
4. ¿Cuáles son los dos tipos de matrícula por oportunidad que se pueden realizar en la Facultad de Ciencias de la Universidad Nacional de Ingeniería?
""",
"response": """
1. ¿Cuál es el objetivo del Programa de Tutoría obligatorio para los estudiantes de la Facultad de Ciencias de la Universidad Nacional de Ingeniería que se encuentran en riesgo académico?
    - ¿Podrían explicarme la finalidad del Programa de Tutoría para alumnos en situación de riesgo académico en la Facultad de Ciencias?
    - ¿Qué busca lograr el Programa de Tutoría obligatorio con los estudiantes que tienen dificultades académicas en la Universidad Nacional de Ingeniería?
    - ¿En qué consiste y qué pretende el Programa de Tutoría para estudiantes que están bajo rendimiento académico en la Facultad de Ciencias?
    - ¿Cuáles son los beneficios y metas del Programa de Tutoría para los alumnos con bajo desempeño académico en la Universidad Nacional de Ingeniería?
    - ¿Qué se espera alcanzar con la implementación del Programa de Tutoría para estudiantes en riesgo de la Facultad de Ciencias?

2. ¿En qué consiste el Programa de Tutoría para Estudiantes en Riesgo Académico de la Facultad de Ciencias de la Universidad Nacional de Ingeniería?
    - ¿Podrían explicarme cómo funciona el Programa de Tutoría para aquellos de nosotros que estamos es riesgo académico en la Facultad de Ciencias?
    - Estoy preocupado por mi situación de estudiante en riesgo académico, ¿me podrían detallar qué apoyo ofrece el Programa de Tutoría para Estudiantes en Riesgo Académico?
    - Como estudiante que en riesgo académico, me gustaría saber más sobre el Programa de Tutoría de la Facultad de Ciencias. ¿Qué servicios y recursos proporciona?
    - ¿Qué tipo de ayuda puedo esperar del Programa de Tutoría si me encuentro en riesgo académico en la Universidad Nacional de Ingeniería?
    - Me interesa mejorar mi condicion de estudiante en riesgo académico, ¿en qué consiste exactamente el apoyo que brinda el Programa de Tutoría para estudiantes como yo?

3. ¿Qué se entiende por estudiante en riesgo académico y qué medidas se les exige a estos estudiantes antes de poder matricularse nuevamente?
    - ¿Cómo se determina si un estudiante está en riesgo académico y qué pasos debo seguir antes de realizar su próxima matrícula?
    - ¿Podrían informarme sobre los criterios que me clasificarían como un estudiante en riesgo académico y qué implicaría en mi siguiente matricula? 
    - Me gustaría comprender mejor qué significa estar en riesgo académico y qué exigencias debo cumplir antes de evitar poder matricularme.
    - ¿Cuáles son las circunstancias para que un estudiante se considere en riesgo académico y que condiciones se le imponen para que pueda matricularse a la universidad?
    - Me interesa saber qué es un estudiante en riesgo académico y si se le exige algún requisito adicional para matricularse en el siguiente ciclo.

4. ¿Cuáles son los dos tipos de matrícula por oportunidad que se pueden realizar en la Facultad de Ciencias de la Universidad Nacional de Ingeniería?
    - ¿Podrían informarme sobre las opciones de matrícula por oportunidad disponibles en la Facultad de Ciencias?
    - Estoy interesado en conocer las variantes de matrícula por oportunidad que ofrece la Facultad de Ciencias, ¿me podrían asesorar al respecto?
    - ¿Qué modalidades de matrícula por oportunidad existen en la Facultad de Ciencias y en qué se diferencian?
    - Como estudiante, quisiera saber cuáles son las alternativas de matrícula por oportunidad en la Facultad de Ciencias, ¿me pueden ayudar?
    - ¿Cuál es la información disponible sobre los tipos de matrícula por oportunidad en la Facultad de Ciencias y cómo puedo acceder a ella?
""",
},
{
"input": """Preguntas:
1. ¿Qué requisitos debe cumplir un estudiante para realizar una Matrícula Regular en la Facultad de Ciencias de la Universidad Nacional de Ingeniería?
2. ¿Quién debe autorizar la Matrícula Rezagada en la Facultad de Ciencias de la Universidad Nacional de Ingeniería?
3. ¿Cuáles son los cuatro tipos de matrícula por tratamiento que se pueden encontrar en la Universidad Nacional de Ingeniería?
4. ¿Qué condiciones deben cumplirse para que un estudiante sea considerado para una matrícula condicionada?
""",
"response": """
1. ¿Qué requisitos debe cumplir un estudiante para realizar una Matrícula Regular en la Facultad de Ciencias de la Universidad Nacional de Ingeniería?
    - ¿Podrían detallarme los requisitos necesarios para inscribirme en una Matrícula Regular en la Facultad de Ciencias?
    - Me gustaría saber qué necesito para poder matricularme de manera regular en la Facultad de Ciencias, ¿me pueden orientar?
    - ¿Cuáles son los pasos y condiciones que debo cumplir para efectuar una Matrícula Regular en la Facultad de Ciencias?
    - Estoy planeando mi matrícula y necesito conocer los requisitos para la Matrícula Regular en la Facultad de Ciencias, ¿pueden asesorarme?
    - Como futuro estudiante de la Facultad de Ciencias, me interesa saber qué se requiere para realizar una Matrícula Regular, ¿podrían informarme?

2. ¿Quién debe autorizar la Matrícula Rezagada en la Facultad de Ciencias de la Universidad Nacional de Ingeniería?
    - ¿A qué autoridad debo dirigirme para obtener la aprobación de una Matrícula Rezagada en la Facultad de Ciencias?
    - Me gustaría saber quién es el responsable de autorizar las Matrículas Rezagadas en la Facultad de Ciencias, ¿podrían informarme?
    - ¿Quién concede la autorización de una Matrícula Rezagada en la Facultad de Ciencias?
    - Necesito saber a quién solicitar la autorización para una Matrícula Rezagada en la Facultad de Ciencias, ¿me pueden orientar?
    - ¿Podrían decirme quién tiene la facultad de autorizar mi Matrícula Rezagada en la Facultad de Ciencias?

3. ¿Cuáles son los cuatro tipos de matrícula por tratamiento que se pueden encontrar en la Universidad Nacional de Ingeniería?
    - ¿Podrían informarme sobre las diferentes categorías de matrícula por tratamiento que ofrece la UNI?
    - Estoy tratando de entender las opciones de matrícula por tratamiento en la UNI, ¿me pueden explicar cuáles son?
    - ¿Me podrían detallar los distintos tipos de matrícula por tratamiento que existen en la Universidad Nacional de Ingeniería?
    - Necesito saber los cuatro tipos de matrícula por tratamiento en la UNI, ¿dónde puedo encontrar esa información?
    - ¿Cuál es la clasificación de las matrículas por tratamiento en la UNI y qué características tiene cada una?

4. ¿Qué condiciones deben cumplirse para que un estudiante sea considerado para una matrícula condicionada?
    - ¿Podrían decirme qué requisitos debo cumplir para ser considerado para una matrícula condicionada en la universidad?
    - Estoy interesado en la matrícula condicionada, ¿cuáles son los criterios de elegibilidad?
    - ¿Cuáles son las condiciones específicas para obtener una matrícula condicionada en mi universidad?
    - ¿Qué necesito para ser elegible para una matrícula condicionada y dónde puedo verificar si cumplo con esos requisitos?
    - Me gustaría saber más sobre la matrícula condicionada, ¿pueden explicarme los requisitos necesarios para acceder a ella?
"""
},
{
    "input": """
Preguntas:
        1. ¿Qué sucede si un estudiante desaprueba una misma asignatura dos veces?
        2. ¿Cuál es el límite de asignaturas desaprobadas por tercera vez que un estudiante puede matricularse después de haber cumplido una suspensión por bajo rendimiento académico?
        3. ¿Qué es la matrícula preferencial y quiénes pueden solicitarla en la Universidad Nacional de Ingeniería?
        4. ¿Cómo se define el Grupo Cero y cuál es su función dentro del proceso de matrícula en la UNI?
""",
    "response" : """
1. ¿Qué sucede si un estudiante desaprueba una misma asignatura dos veces?
    - ¿Cuáles son las consecuencias de reprobar el mismo curso dos veces en la universidad?
    - ¿Podrían informarme sobre el protocolo de la universidad si fallo en una asignatura por segunda vez?
    - Estoy preocupado por haber desaprobado una materia dos veces, ¿qué medidas toma la universidad en estos casos?
    - ¿Qué procedimientos sigue la universidad si no logro aprobar una asignatura después de dos intentos?
    - ¿Cuál es la política de la UNI respecto a los estudiantes que no aprueban una materia en dos ocasiones?

2. ¿Cuál es el límite de asignaturas desaprobadas por tercera vez que un estudiante puede matricularse después de haber cumplido una suspensión por bajo rendimiento académico?
    - Después de una suspensión académica, ¿hay un límite de cursos que puedo matricularme si los he desaprobado tres veces?
    - ¿Podrían decirme cuántas asignaturas desaprobadas puedo llevar he sido suspendido por bajo rendimiento y las he reprobado tres veces?
    - ¿Cuál es el número máximo de asignaturas que puedo matricular nuevamente tras una suspensión y haberlas desaprobado tres veces?
    - ¿Existe un límite en la cantidad de cursos que puedo llevar después de una suspensión por haberlos reprobado tres veces?
    - Tras regresar de una suspensión académica, ¿me podrían informar cuántas asignaturas que he desaprobado previamente en tres ocasiones puedo tomar?

3. ¿Qué es la matrícula preferencial y quiénes pueden solicitarla en la Universidad Nacional de Ingeniería?
    - ¿Me podrían informar acerca de la matrícula preferencial y los criterios para acceder a ella en la UNI?
    - ¿En qué consiste exactamente la matrícula preferencial y cuáles son los requisitos para que un estudiante de la UNI pueda solicitarla?
    - ¿Podrían detallarme qué es la matrícula preferencial y qué estudiantes están habilitados para pedirla en la Universidad Nacional de Ingeniería?
    - ¿Cuál es la definición de matrícula preferencial y qué perfil debe tener un estudiante de la UNI para ser elegible?
    - ¿Cómo funciona el sistema de matrícula preferencial en la UNI y qué estudiantes tienen derecho a aplicar?

4. ¿Cómo se define el Grupo Cero y cuál es su función dentro del proceso de matrícula en la UNI?
    - ¿Me podrían explicar qué es el Grupo Cero y qué papel juega en el proceso de matriculación en la UNI?
    - ¿Cuál es la finalidad del Grupo Cero en el contexto de la matrícula y cómo afecta a la matrícula de los estudiantes en la UNI?
    - ¿Podrían describir las responsabilidades y actividades del Grupo Cero durante la matrícula en la UNI?
    - ¿Qué significa ser parte del Grupo Cero y cómo se relaciona esto con mi proceso de matrícula en la UNI?
    - ¿Cómo puedo beneficiarme del Grupo Cero si estoy en proceso de matricularme en la UNI y qué servicios ofrece?
    
"""
}]

class EvalDatasetGenerator:
    def __init__(self, question_answers_file):
        #self.question_answers_file = question_answers_file
        self.question_answers = load_json(question_answers_file)
    
    def format_examples_text(self, examples):
        text = ""
        for example in examples:
            input = example["input"]
            response = example["response"].strip()
            template = f"{input}\nNuevas formas de consultas generadas:\n{response}"
            text = text + "\n" + template
        return text
    
    def get_prompt_few_shot_gen_distinct_questions(self, questions):
        questions_text = list_json_to_txt(questions)
        
        examples_text =  self.format_examples_text(examples)

        prompt = f"""
Se te proporcionara una lista de preguntas.
Tu tarea consiste en generar cinco consultas distintas y únicas que un estudiante universitario podría utilizar para obtener información o asesoramiento sobre cada uno de los temas enumerados a continuación. Prioriza utilizar la perspectiva de un estudiante en búsqueda de información o asesoramiento.
Presenta cada pregunta original seguida de cinco formas diferentes y únicas de consultarla, enfocándote en la perspectiva de un estudiante en búsqueda de información o asesoramiento. Sigue el siguiente formato:
1. Aquí la Pregunta Original
    - Aquí la Forma 1 de consulta
    - Aquí la Forma 2 de consulta
    - Aquí la Forma 3 de consulta
    - Aquí la Forma 4 de consulta
    - Aquí la Forma 5 de consulta

{examples_text}

Preguntas: {questions_text}

Nuevas formas de consultas generadas:"""
        print(prompt)
        return prompt        

    def get_prompt_gen_distinct_questions(self, questions):
        questions_text = list_json_to_txt(questions)
        prompt = f"""
            Tu tarea consiste en generar cinco consultas distintas y únicas que un estudiante universitario podría utilizar para obtener información o asesoramiento sobre cada uno de los temas enumerados a continuación. Prioriza utilizar la perspectiva de un estudiante en búsqueda de información o asesoramiento.
            Preguntas:
                {questions_text}
            A continuación, presenta cada pregunta original seguida de cinco formas diferentes y únicas de consultarla, enfocándote en la perspectiva de un estudiante en búsqueda de información o asesoramiento. Sigue el siguiente formato:
            1. Aquí la Pregunta Original
                - Aquí la Forma 1 de consulta
                - Aquí la Forma 2 de consulta
                - Aquí la Forma 3 de consulta
                - Aquí la Forma 4 de consulta
                - Aquí la Forma 5 de consulta
        """
        return prompt

    def extract_new_distinct_questions(self, response):
        pattern = '\d+\.\s+(¿[^\?]*\?)\s+(.*?)(?=\d+\.|\Z)'
        matches = re.findall(pattern, response, re.DOTALL)
        new_questions = []
        for origin_question, text_distinc_questions in matches:
            #print("\norigin_question:", origin_question)
            distinct_questions = re.findall('-\s+(¿[^\?]*\?)', text_distinc_questions)
            #print("\ndistinc_questions:", distinct_questions)
            new_questions.append({"question": origin_question, "distinct_questions": distinct_questions})

        return new_questions


    def gen_distinct_questions(self, questions):
        prompt = self.get_prompt_few_shot_gen_distinct_questions(questions)
        print("\n\nprompt:", prompt)
        messages =  [{'role':'user', 'content':prompt}]
        response = get_completion_from_messages(
        messages, 
        temperature=0,
        #model="gpt-3.5-turbo-0125" 
        #model= "gpt-4-1106-preview"
        )
        print("\n\nresponse:", response)
        new_questions = self.extract_new_distinct_questions(response)
        return new_questions

    def run(self):
        for questions_block in self.question_answers[10:12]:
            question_answer_pairs = questions_block["question_answer_pairs"]
            questions = [ qa["question"] for qa in question_answer_pairs]
            len_questions = len(questions)
            batch_size = 4

            if len_questions > batch_size:
                num_batch = math.ceil(len(questions) / batch_size)
            else:
               num_batch = 1
           
            for i in range(num_batch):
                start = batch_size * i
                print("start:", start)
                if i + 1 < num_batch:
                    end = batch_size * (i + 1)
                    b_questions = questions[start:end]
                else:
                    b_questions = questions[start:]
            
                new_questions = self.gen_distinct_questions(b_questions)
                



eval_gen_dataset = EvalDatasetGenerator(
    question_answers_file = "./answers_generated.json")

eval_gen_dataset.run()
