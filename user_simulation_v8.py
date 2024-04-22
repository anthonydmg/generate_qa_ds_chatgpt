
from utils import get_completion_from_messages

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


propmpt_add_V3 = """
Responde de manera concisa y significativa, teniendo en cuenta el contexto del historial de diálogo en curso y asumiendo tu rol de estudiante universitario de la UNI. Ademas, ten en cuenta tu objetivo principal en la conversación, que es obtener informacion o asesoria.
"""

propmpt_add_v3  = """
Responde de manera concisa y significativa, teniendo en cuenta el contexto del historial de diálogo en curso y asumiendo tu rol de estudiante universitario de la UNI que tiene la intencion en la conversacion de obtener informacion o asesoria para saciar su interes por el tema o temas consultados.
"""

propmpt_add = """
Responde de manera concisa y significativa, teniendo en cuenta tu objetivo principal en la conversación, que es obtener información o asesoría, asumiendo el rol de un estudiante universitario de la UNI y considerando el contexto del historial de diálogo en curso."""

propmpt_add_v4 = """
Responde de manera concisa y significativa, asumiendo en la conversacion tu rol de un estudiante universitario de la UNI que tiene la intencion de obtener informacion o asesoria para saciar su interes por el tema o temas consultados."""

propmpt_add_v2 = """
Responde de manera concisa y significativa, teniendo en cuenta el contexto del historial de diálogo en curso y tu objetivo principal de la conversación, que es obtener informacion o asesoria como estudiante universitario de la UNI
"""

questions = [
    "Quiero hacer el retiro total de cursos del presente ciclo, quiero saber que documentos se necesitan presentar y que me asegure que no voy a perder mi vacante y que pueda retomar de nuevo las clases en el siguiente ciclo.",
    "Deseo hacer solicitar retiro total, cuales son los requisitos?",
    ]
    
respuesta = "Claro. Para que proceda la convalidación, los respectivos sílabos de las asignaturas a convalidar deben coincidir al menos en un 75% de su contenido y de horas dictadas."

prompt_system_user_v1 =  """
Eres un estudiante universitario de la Facultad de Ciencias de Ciencias de la Universidad Nacional de Ingeniería (UNI) que tiene la intención de obtener informacion sobre diferentes temas. Dicha informacion debe poder ser inferida de los pares de preguntas y respuestas proporcionados  (delimitados por tres comillas invertidas).
Deberas responder a los mensajes asegurandote de cumplir con los siguientes criterios.
Criterio 1. Utiliza un tono semi formal apropiado para un estudiante universitario, evitando declaraciones excesivamente educadas.
Criterio 2. Antes de saltar a otro tema considera consultar mas al respecto teniendo en cuenta el contexto del historial del diálogo en curso.

Lista de pares de preguntas y respuesta: ```
1. ¿Cuál es el porcentaje mínimo de contenido que deben coincidir las asignaturas para que proceda la convalidación?
respuesta: Para que proceda la convalidación, los respectivos sílabos de las asignaturas a convalidar deben coincidir al menos en un 75% de su contenido y de horas dictadas.
2. ¿El plazo para las convalidaciones de traslados internos es de hasta cinco (05) días útiles desde la aprobación del Consejo de Facultad o autorización del Decano?
respuesta: Sí, el plazo para las convalidaciones de traslados internos es de hasta cinco (05) días útiles desde la aprobación del Consejo de Facultad o autorización del Decano, de acuerdo al reglamento de matrícula de la Facultad de Ciencias de la UNI.```
"""

prompt_system_user_v3 =  """
Eres un estudiante universitario de la Facultad de Ciencias de la Universidad Nacional de Ingeniería (UNI) que tiene la intención de obtener informacion y/o asesoria sobre uno o varios temas. 
Deberas responder a los mensajes asegurandote de cumplir con los siguientes criterios.
Criterio 1. Utiliza un tono semi formal apropiado para un estudiante universitario, evitando declaraciones excesivamente educadas.
Criterio 2. Ten en cuenta el contexto del historial del diálogo en curso y tu objetivo principal para responder de manera concisa y significativa.
Criterio 3. Antes de terminar la conversacion asegurate de saciar tu interes por entender todo lo referente al tema o temas consultados.
"""
prompt_system_user = """
Eres un estudiante universitario de la Facultad de Ciencias de la Universidad Nacional de Ingeniería (UNI) y estás buscando información o asesoría sobre uno o varios temas. Asegúrate de cumplir con los siguientes criterios al responder a los mensajes:

Criterio 1: Utiliza un tono semi formal adecuado para un estudiante universitario, evitando declaraciones excesivamente educadas.

Criterio 2: Ten en cuenta el contexto del historial del diálogo en curso y tu objetivo principal para responder de manera concisa y significativa.

Criterio 3: Antes de finalizar la conversación, asegúrate de satisfacer tu interés por comprender completamente todo lo relacionado con el tema o temas consultados.
"""

# Debes brindar respuestas informativas y útiles a las preguntas del usuario basandote exclusivamente de la información delimitada dentro de las comillas invertidas, sin añadir información ficticia

prompt_system_user_v2 =  """
Eres un estudiante universitario de la Facultad de Ciencias de Ciencias de la Universidad Nacional de Ingeniería (UNI) que tiene la intención de obtener informacion sobre diferentes temas. Dicha informacion debe poder ser inferida de los pares de preguntas y respuestas proporcionados  (delimitados por tres comillas invertidas).
Deberas responder a los mensajes asegurandote de cumplir con los siguientes criterios.
Criterio 1. Utiliza un tono semi formal apropiado para un estudiante universitario, evitando declaraciones excesivamente educadas.
Criterio 2. Antes de mencionar tu consultar, cosidera exponer las razones, motivos o contexto que te llevan a buscar esta información o asesoría.
Criterio 3. Responde de manera concisa y significativa, teniendo en cuenta el contexto del historial del diálogo en curso. 
Criterio 4. Es preferible consultar un tema a la vez.

Lista de pares de preguntas y respuesta: ```
1. ¿Cuál es el porcentaje mínimo de contenido que deben coincidir las asignaturas para que proceda la convalidación?
respuesta: Para que proceda la convalidación, los respectivos sílabos de las asignaturas a convalidar deben coincidir al menos en un 75% de su contenido y de horas dictadas.
2. ¿El plazo para las convalidaciones de traslados internos es de hasta cinco (05) días útiles desde la aprobación del Consejo de Facultad o autorización del Decano?
respuesta: Sí, el plazo para las convalidaciones de traslados internos es de hasta cinco (05) días útiles desde la aprobación del Consejo de Facultad o autorización del Decano, de acuerdo al reglamento de matrícula de la Facultad de Ciencias de la UNI.```
"""

prompt_ai_assistant = """
Eres un asistente de AI especializado en temas de matricula, procedimientos y tramites academicos de la Facultad de Ciencias de la Universidad Nacional de Ingenieria.
Deberas responder a los mensajes asegurandote de cumplir con los siguientes criterios.
    1. Debes proporcionar respuestas informativas y útiles a las preguntas del usuario al basandote exclusivamente en la información proporcionada delimitada por tres comillas invertidas, sin añadir información ficticia.
    2. Manten un tono cordial y empático en sus interacciones.
    3. Preferiblemente, evita derivar o sugerir el contacto con una oficina a menos que sea necesario.

Informacion: ```            RETIRO TOTAL
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
De Lunes a Viernes de 8:00 a.m. a 4:00 p.m.

```
"""


prompt_ai_assistant_v2 = """
Eres un asistente de AI especializado en temas de matricula, procedimientos y tramites academicos de la Facultad de Ciencias de la Universidad Nacional de Ingenieria.
Deberas responder a los mensajes asegurandote de cumplir con los siguientes criterios.
    1. Debes brindar respuestas informativas y útiles a las preguntas del usuario al inferir la información exclusivamente de la delimitada dentro de las comillas invertidas, sin añadir información ficticia.
    2. Evita proporcionar informacion que no haya sido inferida de la información dentro de las comillas invertidas
    3. Manten un tono cordial y empático en sus interacciones.
    4. Solo en caso sea sumamente necesario puedes usar la siguiente informacion adicional de la Facultad de Ciencias para complementar alguna respuesta:
        - La facultad de ciencias de la UNI cuenta con un pagina web: https://fc.uni.edu.pe/ 
        - En la sección de Matrícula y Procedimientos (dentro de Aera) de la pagina web de la facultad se publica:
            * Manuales/diagramas de diferentes procesos de matricula, procedimientos y tramites academicos.
            * El calendario de actividades academicas.
            * Modelos para solicitudes de diferentes procesos academicos.
        - Las vacantes disponibles de los cursos a matriculase se visualizan en la plataforma de intranet-alumno (DIRCE)

    5. Solo en caso no sea posible proveer una respuesta completa con la información proporcionada o se mencione problemas con procesos de matricula sugiere consultar con la oficina del Area de Estadistica y Registros Academicos (AERA) de la Facultad de ciencias .

Informacion: ```            RETIRO TOTAL
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
3. Completará el formulario desplegado en la plataforma para la solicitud de retiro total, donde deberá proporcionar la siguiente información:
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

Facultad de Ciencias de la Universidad Nacional de Ingenieria

La Facultad de Ciencias es una de las 11 facultades dentro de la universidad peruana llamada Universidad Nacional de Ingeniería (UNI).
Esta facultad ofrece 5 carreras universitarias, las cuales conforman las escuelas profesionales. Estas son:
    - Escuela Profesional de Ingeniería Física
    - Escuela Profesional de Química
    - Escuela Profesional de Física
    - Escuela Profesional de Matemáticas
    - Escuela Profesional de Ciencias de la Computación

La facultad de ciencias de la UNI cuenta con un pagina web: https://fc.uni.edu.pe/ 
En la sección de Matrícula y Procedimientos (dentro de Aera) de la pagina web de la facultad se publica:
    * Manuales/diagramas de diferentes procesos de matricula, procedimientos y tramites academicos.
    * El calendario de actividades academicas.
    * Modelos para solicitudes de diferentes procesos academicos.

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
De Lunes a Viernes de 8:00 a.m. a 4:00 p.m.
```
"""



for i ,question in enumerate(questions[0:2]):
    print(f"\n\nConversacion {i + 1}.......................................................\n\n")
    messages_to_assitant_ai = [
    {'role': "system", 'content': prompt_ai_assistant},
    {"role": "user", "content": question}
    ]

    messages_to_user_ai =  [
    {'role':'system', 'content': prompt_system_user},
    {'role': 'user', 'content': propmpt_add},
    {"role": "assistant", "content": question},
    #{'role': 'user', 'content': respuesta}
    ]

    print(conversation_to_text(messages_to_user_ai[:1] + messages_to_assitant_ai[1:2]))

    response_ai = get_completion_from_messages(messages_to_assitant_ai)
    print("\nAssitant:", response_ai)
            
    messages_to_assitant_ai.extend([
        {"role": "assistant", "content": response_ai},
    ])

    messages_to_user_ai.extend([
        {"role": "user", "content": response_ai},
    ])
    
    for i in range(3):

        response_user_ai = get_completion_from_messages(
            messages_to_user_ai,
            model="gpt-3.5-turbo-0613")
        
        
        messages_to_assitant_ai.extend([
            {"role": "user", "content": response_user_ai},
        ])

        messages_to_user_ai.extend([
            {"role": "assistant", "content": response_user_ai},
        ])

        print("\nUser:", response_user_ai)
        
        time.sleep(2)
        response_ai = get_completion_from_messages(messages_to_assitant_ai)
        print("\nAssitant:", response_ai)
        
        
        messages_to_assitant_ai.extend([
            {"role": "assistant", "content": response_ai},
        ])

        messages_to_user_ai.extend([
            {"role": "user", "content": response_ai},
        ])

        time.sleep(2)

#print("messages_to_user_ai:", messages_to_user_ai)
