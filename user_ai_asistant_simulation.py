
from utils import get_completion_from_messages, load_json

import openai
import json
from dotenv import load_dotenv
import os
import time
import re
load_dotenv()

def set_openai_key():
    API_KEY = os.getenv("API_KEY")
    openai.api_key = API_KEY

set_openai_key()


def conversation_to_text(messages):
    txt = ""
    for m in messages:
        txt = txt + "\n" + m["role"] + ": "+ m["content"]
    return txt


information = """            RETIRO TOTAL
    (del Reglamento de Matrícula Aprobado R.R. Nº 0570 del 29.03.2022 y modificado con la R.R. N° 2292 del 04.11.22) 

Art. 11° Para el presente reglamento se entiende por: 
 
d. Retiro Total: (R.R. N° 2292-2022) Es el procedimiento mediante el cual el estudiante, o persona acreditada con carta poder simple, solicita la anulación total de su matrícula en un periodo académico, con el cumplimiento de los requisitos para este trámite. 

Procedimiento de Retiro Total 
 
Art. 67° (R.R. N° 2292-2022) El Retiro Total puede ser solicitado hasta una semana antes de los exámenes parciales, a través de la plataforma SIGA-DIRCE y procede de oficio, con excepción a lo establecido en el Artículo 68° para los estudiantes en riesgo académico. 
Vencido el periodo para ingresar solicitudes, DIRCE informará a las Facultades sobre los retiros totales registrados. 
 
Art. 68° (R.R.  N°  2292-2022) No procede el Retiro Total cuando el estudiante ha rendido todas las evaluaciones regulares de alguna de las asignaturas en la que se encuentra matriculado o si tiene algún curso desaprobado dos veces o más al periodo académico regular precedente. 
De  manera  excepcional,  un  estudiante  puede  solicitar  el  retiro  total,  en  casos  debidamente justificados,  por causa de  enfermedad grave  ascendiente  o  descendiente  (en  primer grado)  y 
certificado por el Centro Médico de la UNI, MINSA o ESSALUD, hasta una semana antes de los exámenes finales, el mismo que será evaluado por el Consejo Directivo de la Escuela Profesional correspondiente. 
 
Art. 69° (R.R. N° 2292-2022) El Retiro Total se computa para efectos de un Retiro Definitivo como una reserva de matrícula. El Retiro Total es de oficio por fallecimiento del estudiante. 

Pasos para solicitar el Retiro Total a través de la plataforma SIGA-DIRCE:

1. El alumno accederá a la intranet de alumnos utilizando su código UNI y la clave correspondiente.
2. Dentro de la intranet de alumnos, seleccionará la opción "Mis Trámites" en el menú de navegación ubicado en la parte izquierda de la pantalla. Al hacer clic en dicho menú, se desplegarán varias opciones, entre las cuales deberá seleccionar "Retiro Total".
3. Completará el formulario desplegado en la plataforma para la solicitud de retiro total, donde deberá llenar la siguiente información:
    - Motivo por el cual desea realizar el retiro total, que puede ser: Viaje al extranjero, Accidente limitante, Enfermedad limitante o Asumir emergencia familiar limitante.
    - Descripción del motivo por el que desea realizar el retiro.
    - Número de ciclos que estará ausente.
    - Adjuntar documentos sustentatorios para el motivo de retiro total.
4. Una vez completado el formulario, seleccionará "Enviar Solicitud".

Al enviar la solicitud, podrá visualizarla junto con la fecha de envío, así como también la respuesta correspondiente, la cual estará disponible una vez que se haya procesado su solicitud.

Para obtener más detalles sobre el proceso, consulta el Manual de Retiro Total publicado en la sección de MATRÍCULA Y PROCEDIMIENTOS en la Página Web de la Facultad de Ciencias."


Nota1: En el caso del retiro total o aprobado el retiro total excepcional, el alumno debe tener en cuenta que previamente a la siguiente matrícula deberá realizar el trámite de REINCORPORACIÓN. 
 
Nota2: Las solicitudes de retiro total excepcional, son previamente aprobadas por el director de la Escuela Profesional y finalmente por la dirección de Registro Central y Estadística (DIRCE).

Nota3 : El retiro total es gratuito.


REINCORPORACIÓN
            (del Reglamento de Matrícula Aprobado R.R. Nº 0570 del 29.03.2022 y modificado con la R.R. N° 2292 del 04.11.22) 

Art. 11°  Para el presente reglamento se entiende por: 
 
a.  Reincorporación: Es el procedimiento que restablece al estudiante la condición de estudiante activo, quien realizó Retiro Total, solicitó Reserva de Matrícula o Licencia, o dejó de matricularse un semestre académico o más, teniendo como plazo límite tres (03) años o seis (06) periodos académicos consecutivos o alternos. En caso de periodos académicos alternos estos no excederán de cinco (05) años contados a partir del primer periodo académico en el que se dejó de matricularse. Es procedente si no tiene sanción vigente y no ha superado el plazo máximo de Reserva de Matrícula. 
La reincorporación se presenta según el calendario oficial, a través de la Plataforma SIGA-DIRCE. 
 
Procedimiento de Reincorporación  
 
Art. 61° El estudiante deberá tramitar su solicitud de reincorporación en la plataforma de la DIRCE según formato, con una anticipación no menor de diez (10) días útiles antes de la semana de matrícula y según el Calendario Académico de la Universidad; para lo cual deberá generar una orden de pago y realizar el pago correspondiente a través de la Caja UNI o bancos autorizados. 
 
Art. 62° El director de la Escuela Profesional correspondiente revisa la ficha académica de cada estudiante, evalúa y autoriza o rechaza la solicitud de reincorporación ingresada y ordena a la DIRCE, si corresponde, la actualización del Plan de Estudios y la convalidación de asignaturas por dicho cambio. 
 
Art. 63° Una vez reincorporado el estudiante, y de ser el caso realizado el cambio de Plan y las convalidaciones, el procedimiento de matrícula se realizará de manera regular. Si hubiere rezago, la atención será por la OERA. 

El procedimiento para generar la orden de pago es el siguiente (Actualizado por DIRCE): 
 
    1.  El estudiante que realiza el proceso de reincorporación deberá generar una orden de pago, el costo por tramite de reincorporación es S/. 42.00 + S/. 10.00 por cada periodo no estudiado. Para ello, el alumno debe ingresar a intranet-alumno (Portal INTRALU) para generar la orden de pago. revisar manual de pagos UNI publicado en la seccion MATRÍCULA Y PROCEDIMIENTOS de la Pagina Web de la Facultad de Ciencias para mas detalles sobre el proceso.
        El mismo sistema por defecto indicará al estudiante la cantidad a pagar, en base a lo explicado en el párrafo anterior. 
    
    2.  Una vez realizado el pago, el alumno dentro de las fechas señaladas para este proceso (ver calendario académico) ingresará a la Plataforma de intranet-alumno y subirá la solicitud y el recibo de pago. (ver modelo de solicitud publicado en la seccion MATRÍCULA Y PROCEDIMIENTOS en la pagina web de la Facultad de Ciencias)
    
Para obtener detalles sobre el proceso de presentación de la solicitud y el recibo de pago, así como para enviar la solicitud de REINCORPORACIÓN, revisar el Manual de Reincorporación publicado en la sección 'MATRÍCULA Y PROCEDIMIENTOS' de la página web de la Facultad de Ciencias

AERA

El Área de Estadística y Registros Académicos  de la Facultad de Ciencias es un órgano de apoyo administrativo, encargado de centralizar, verificar y custodiar la documentación académica de la Facultad.

Actividades que realiza AERA:

1. Procesos de matrícula
Planificar, atender y supervisar los procedimientos de la matrícula en cada semestre Académico de acuerdo al Reglamento de Matrícula de estudiantes de Antegrado vigente.

    - Matrícula (ingresantes, regular, condicionada y rezagada).
    - Reincorporación.
    - Grupo cero de Matrícula.
    - Matrícula Condicionada.
    - Matrícula Preferencial.
    - Reserva de Matrícula.
    - Retiros (Parciales, Totales y Definitivos).

2. Procesos de evaluación
Supervisar e informar el cumplimiento de los procedimientos que regulan el sistema de calificación de acuerdo al Reglamento de Evaluación para estudiantes de Antegrado vigente.
    - Supervisar el registro de notas de prácticas, exámenes y solucionario.
    - Supervisión en la atención de los reclamos de notas de los estudiantes.
    - Informar sobre las faltas en la entrega oportuna de notas por parte de los docentes.
    - Gestionar el registro de nota del Examen de Regularización.

3. Otras Actividades
- Coordinar el trámite de los carnés universitarios.
- Elaborar las Constancias de Notas y/o Matrícula.
- Verificar la información de los Certificados de notas, Constancias de Egresado y Constancias de No Adeudos emitidas por la DIRCE.
- Entrega reportes y estadísticas a las diferentes oficinas de la Facultad para su evaluación y toma de decisiones.
- Realizar el estudio de las deudas por Decreto Legislativo 739 (Derecho de la Enseñanza) e informar al estudiante para que cumplan con la cancelación respectiva.

Informacion de Contacto de la oficina de AERA
E-mail: estadistica_fc@uni.edu.pe

Hoario de Atencion de la oficina de AERA:
De Lunes a Viernes de 8:00 a.m. a 4:00 p.m."""


class UserAISim:
    def __init__(self, first_message, model = "gpt-3.5-turbo-0613") -> None:
        
        prompt_system_role_user = self.get_prompt_system_role()
        prompt_start = self.get_prompt_start()
        
        self.messages = [
            {'role':'system', 'content': prompt_system_role_user},
            {'role': 'user', 'content': prompt_start},
            {"role": "assistant", "content": first_message}]
        self.model = model
    
    def get_prompt_system_role(self):
        prompt_system_role_user = """
Eres un estudiante universitario de la Facultad de Ciencias de la Universidad Nacional de Ingeniería (UNI) y estás buscando información o asesoría sobre uno o varios temas. Asegúrate de cumplir con los siguientes criterios al responder a los mensajes:

Criterio 1: Utiliza un tono semi formal adecuado para un estudiante universitario, evitando declaraciones excesivamente educadas.

Criterio 2: Ten en cuenta el contexto del historial del diálogo en curso y tu objetivo principal para responder de manera concisa y significativa.

Criterio 3: Antes de finalizar la conversación, asegúrate de satisfacer tu interés por comprender completamente todo lo relacionado con el tema o temas consultados.
"""
        return prompt_system_role_user

    def get_prompt_start(self):
        prompt_start = """Responde de manera concisa y significativa, teniendo en cuenta tu objetivo principal en la conversación, que es obtener información o asesoría, asumiendo el rol de un estudiante universitario de la UNI y considerando el contexto del historial de diálogo en curso."""
        return prompt_start


    def generate_response(self, message):
        self.messages.append({"role": "user", "content": message})
        
        response_user_ai = get_completion_from_messages(
            self.messages,
            model=self.model)
        
        self.messages.append({"role": "assistant", "content": response_user_ai})
        
        return response_user_ai

class AIAssistant:
    def __init__(
            self, 
            information,
            model = "gpt-3.5-turbo-0613") -> None:
        
        prompt_system_role_assistant = self.get_prompt_system_role(information)
        
        self.messages = [
            {'role':'system', 'content': prompt_system_role_assistant}]
        self.model = model
    
    def get_prompt_system_role(self, information):
        prompt_system_role_assistant = f"""
Eres un asistente de AI especializado en temas de matricula, procedimientos y tramites academicos de la Facultad de Ciencias de la Universidad Nacional de Ingenieria.
Deberas responder a los mensajes asegurandote de cumplir con los siguientes criterios.
    1. Debes proporcionar respuestas informativas y útiles a las preguntas del usuario al basandote exclusivamente en la información proporcionada delimitada por tres comillas invertidas, sin añadir información ficticia.
    2. Manten un tono cordial y empático en sus interacciones.
    3. Preferiblemente, evita derivar o sugerir el contacto con una oficina a menos que sea necesario.

Informacion: ```{information}```
"""
        return prompt_system_role_assistant

    def generate_response(self, message):
        self.messages.append({"role": "user", "content": message})
        
        response_ai_assistant = get_completion_from_messages(
            self.messages,
            model=self.model)
        
        self.messages.append({"role": "assistant", "content": response_ai_assistant})
        
        return response_ai_assistant
    

questions_topics = load_json("./questions_generated_topics_finals.json")
opening_lines = [
    "Quiero hacer el retiro total de cursos del presente ciclo, quiero saber que documentos se necesitan presentar y que me asegure que no voy a perder mi vacante y que pueda retomar de nuevo las clases en el siguiente ciclo.",
    "Deseo hacer solicitar retiro total, cuales son los requisitos?",
    ]

for questions_about_topic in questions_topics[:1]:
    questions = questions_about_topic["questions"]
    information = questions_about_topic["context"]
    #opening_lines = [question["question"] for question in questions]
    
    for i, question in enumerate(questions[0:1]):
        print(f"\n\nConversacion {i + 1}.......................................................\n\n")

        ai_assistant = AIAssistant(information = information)
        user_ai_sim = UserAISim(first_message = question)
        
        print("\nUser:", question)
        response_ai_assistant = ai_assistant.generate_response(message = question)
        print("\nAssitant:", response_ai_assistant)
        
        for i in range(2):
            response_user_ai = user_ai_sim.generate_response(message=response_ai_assistant)

            print("\nUser:", response_user_ai)
            
            time.sleep(2)

            response_ai_assistant = ai_assistant.generate_response(message = response_user_ai)

            print("\nAssitant:", response_ai_assistant)
            
            time.sleep(2)
