from utils import get_completion_from_messages


from dotenv import load_dotenv
import openai
import os

def set_openai_key():
    API_KEY = os.getenv("API_KEY")
    openai.api_key = API_KEY

load_dotenv()

set_openai_key()

prompt = """
        Analiza detalladamente el prompt proporcionado a continuación y la respuesta generada por el modelo, e identifica las preguntas que no cumplen con lo mencionado en el prompt. 
        Menciona que preguntas y por que no cumplen con lo establecido en el prompt
        
        
        prompt: Tu tarea es generar al menos 20 preguntas practicas y únicas que aborden diversos temas relevantes para los estudiantes de la Facultad de Ciencias de la Universidad Nacional de Ingenieria, basadas en la información proporcionada  (delimitada por tres comillas invertidas).
Prioriza generar preguntas más generales y menos específicas que abarquen temas extensos bien desarrollados y explicitamante descritos en la informacion proporcionada.
Ademas asegurate que las preguntas tengan una respuesta sustancial y completa basandose únicamente en la información proporcionada (delimitada por tres comillas invertidas).

Finalmente, presenta las 20 preguntas de la siguiente manera:
1. pregunta...
2. pregunta...
...

Fragmento de texto: ```Reincorporacion
                REINCORPORACIÓN
            (del Reglamento de Matrícula Aprobado R.R. Nº 0570 del 29.03.2022 y modificado con la R.R. N° 2292 del 04.11.22) 

Art. 11°  Para el presente reglamento se entiende por: 
 
a.  Reincorporación: Es el procedimiento que restablece al estudiante la condición de estudiante activo, quien realizó Retiro Total, solicitó Reserva de Matrícula o Licencia, o dejó de matricularse un semestre académico o más, teniendo como plazo límite tres (03) años o seis (06) periodos académicos consecutivos o alternos. En caso de periodos académicos alternos estos no excederán de cinco (05) años contados a partir del primer periodo académico en el que se dejó de matricularse. Es procedente si no tiene sanción vigente y no ha superado el plazo máximo de Reserva de Matrícula. 
La reincorporación se presenta según el calendario oficial, a través de la Plataforma SIGA-DIRCE. 
 
Procedimiento de Reincorporación  
 
Art. 61° El estudiante deberá tramitar su solicitud de reincorporación en la plataforma de la DIRCE según formato, con una anticipación no menor de diez (10) días útiles antes de la semana de matrícula y según el Calendario Académico de la Universidad; para lo cual deberá realizar el pago correspondiente a través de la Caja UNI o bancos autorizados. 
 
Art. 62° El director de la Escuela Profesional correspondiente revisa la ficha académica de cada estudiante, evalúa y autoriza o rechaza la solicitud de reincorporación ingresada y ordena a la DIRCE, si corresponde, la actualización del Plan de Estudios y la convalidación de asignaturas por dicho cambio. 
 
Art. 63° Una vez reincorporado el estudiante, y de ser el caso realizado el cambio de Plan y las convalidaciones, el procedimiento de matrícula se realizará de manera regular. Si hubiere rezago, la atención será por la OERA. 

El procedimiento para generar la orden de pago es el siguiente (Actualizado por DIRCE): 
 
    1.  El estudiante que realiza el proceso de reincorporación deberá generar una orden de pago, el costo por tramite de reincorporación es S/. 42.00 + S/. 10.00 por cada periodo no estudiado. Para ello, el alumno debe ingresar a intranet-alumno (Portal INTRALU) para generar la orden de pago. revisar manual de pagos UNI 
        El mismo sistema por defecto indicará al estudiante la cantidad a pagar, en base a lo explicado en el párrafo anterior. 
    
    2.  Una vez realizado el pago, el alumno dentro de las fechas señaladas para este proceso (ver calendario académico) ingresará a la Plataforma de intranet-alumno y subirá la solicitud y el recibo de pago.```

    
    respuesta: 1. ¿Qué se entiende por reincorporación según el Reglamento de Matrícula de la Universidad Nacional de Ingeniería?
2. ¿Cuál es el plazo máximo para solicitar la reincorporación de un estudiante que dejó de matricularse en la universidad?
3. ¿Cuál es el procedimiento que debe seguir un estudiante para solicitar la reincorporación según el Reglamento de Matrícula?
4. ¿Qué institución dentro de la universidad se encarga de revisar y autorizar la solicitud de reincorporación de un estudiante?
5. ¿Qué sucede una vez que un estudiante es reincorporado y se realiza el cambio de Plan de Estudios y convalidación de asignaturas?
6. ¿Cuál es el costo por el trámite de reincorporación de un estudiante en la Universidad Nacional de Ingeniería?
7. ¿Cómo puede un estudiante generar la orden de pago para el trámite de reincorporación?
8. ¿Qué sistema debe utilizar un estudiante para generar la orden de pago para la reincorporación?
9. ¿Qué sucede una vez que un estudiante realiza el pago por el trámite de reincorporación?
10. ¿Cuál es el procedimiento que debe seguir un estudiante luego de realizar el pago por la reincorporación?
11. ¿Qué documentos debe subir un estudiante a la Plataforma de intranet-alumno luego de realizar el pago por la reincorporación?
12. ¿Cuál es el papel de la DIRCE en el proceso de reincorporación de un estudiante en la Universidad Nacional de Ingeniería?
13. ¿Qué función cumple el director de la Escuela Profesional en el proceso de reincorporación de un estudiante?
14. ¿Cuál es el plazo mínimo de anticipación que debe tener un estudiante para solicitar la reincorporación?
15. ¿Qué sucede si un estudiante tiene sanciones vigentes al momento de solicitar la reincorporación?
16. ¿Qué costo adicional debe pagar un estudiante por cada periodo no estudiado al solicitar la reincorporación?
17. ¿Qué acciones debe realizar la OERA en caso de que un estudiante tenga rezago al momento de la reincorporación?
18. ¿Qué plataforma debe utilizar un estudiante para tramitar su solicitud de reincorporación?
19. ¿Qué información debe revisar el director de la Escuela Profesional al evaluar la solicitud de reincorporación de un estudiante?
20. ¿Cuál es el objetivo principal de la reincorporación de un estudiante en la Universidad Nacional de Ingeniería?
    """

messages =  [{'role':'user', 'content':prompt}]
response = get_completion_from_messages(
    messages, 
    temperature=0,
    model="gpt-3.5-turbo-0125" 
    #model= "gpt-4-1106-preview"
)
print("response:", response)