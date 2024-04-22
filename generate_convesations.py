import os
from utils import generate_random_groups_qa, get_completion_from_messages, format_convesations_data, load_json, save_json, set_openai_key
from tqdm import tqdm

from dotenv import load_dotenv


load_dotenv()

set_openai_key()

sample_group_qa = """1. ¿Cuál es el porcentaje mínimo de contenido que deben coincidir las asignaturas para que proceda la convalidación?
respuesta: Para que proceda la convalidación, los respectivos sílabos de las asignaturas a convalidar deben coincidir al menos en un 75% de su contenido y de horas dictadas.
2. ¿El plazo para las convalidaciones de traslados internos es de hasta cinco (05) días útiles desde la aprobación del Consejo de Facultad o autorización del Decano?
respuesta: Sí, el plazo para las convalidaciones de traslados internos es de hasta cinco (05) días útiles desde la aprobación del Consejo de Facultad o autorización del Decano, de acuerdo al reglamento de matrícula de la Facultad de Ciencias de la UNI."""

class ConversationGenerator:
    def __init__(self, file_qa = "./answers_generated.json", model = "gpt-4-1106-preview") -> None:
        self.model = model
        self.file_qa = file_qa
    
    def format_group_qa_to_enum_list(self, group_qa):
        text_qas = ''
        for i , qa in enumerate(group_qa):
            text_qas = text_qas + "\n"+ f'{i + 1}. {qa["question"]}\nrespuesta: {qa["answer"]}'
        return text_qas
    
    def get_prompt_gen_conversations(self, group_qa):
        text_group_qa = self.format_group_qa_to_enum_list(group_qa)
        #     5. En las interacciones, el usuario no necesariamente iniciará con un saludo o expresará gratitud durante la conversación.
        #     10. Enriquece las conversaciones mediante interacciones naturales, como saludos, despedidas, confirmaciones y solicitudes de ayuda, entre otros elementos. No es necesario que el usuario inicie cada conversación con un saludo ni que exprese agradecimiento obligatoriamente en todas las conversaciones.
        #     10. Enriquece las conversaciones mediante interacciones naturales, como saludos, despedidas, confirmaciones y solicitudes de ayuda, entre otros elementos. No es necesario que el usuario inicie cada conversación con un saludo ni que exprese agradecimiento obligatoriamente en todas las conversaciones.
#     El asistente debe responder adecuadamente con respuestas informativas y útiles a las consultas del usuario inferiendo las respuestas de los pares de preguntas y respuestas proporcionados, evitando inventar información adicional.

        prompt = f"""
Se proporcionará una lista de dos pares de preguntas y respuestas relacionadas con matrículas, trámites y procedimientos académicos de la Facultad de Ciencias de la Universidad Nacional de Ingeniería (UNI). 
Tu tarea es generar 8 conversaciones realistas entre un asistente de IA especializado en estos temas y un usuario.

Antes de generar las conversaciones, asegúrate de cumplir cada uno de los siguientes criterios:
    1. Las conversaciones deben ser por turnos entre el agente de IA y el usuario, siendo el usuario el que siempre comenzará la conversación.
    2. Las conversaciones deben tener al menos 3 turnos para cada hablante en la conversación.
    3. El usuario debe manejar un tono semiformal y natural de un estudiante universitario.
    4. El usuario no debe referenciar directamente a ningun reglamento.
    5. El usuario no necesariamente iniciará con un saludo, y tampoco necesariamente expresará su agradecimiento por la ayuda en su ultimo turno en la conversación.
    6. El asistente debe mantener un tono cordial y empático en sus interacciones. Ante despedidas, confirmaciones o agradecimientos, debe responder adecuadamente y siempre mencionar que si tiene alguna otra duda, no dude en consultar.
    7. Enfócate en crear diferentes conversaciones donde el usuario tenga la intención de obtener información que puedan ser inferida de los pares de preguntas y respuestas proporcionados  (delimitados por tres comillas invertidas).
    8. Evita repetir preguntas de manera idéntica en distintas conversaciones. Sé creativo y original en la forma de consultar por información del usuario, usando enfoques tanto directos como indirectos. Considera agregar un contexto proporcionado por el usuario antes de manifestar su duda.
    9. El asistente debe brindar respuestas informativas y útiles a las preguntas del usuario al inferir la información de los pares de preguntas y respuestas proporcionados, sin añadir información ficticia.
    10. En caso no sea posible proveer una respuesta completa con la información proporcionada o se mencione problemas con procesos de matricula sugiere consultar con la oficina del Area de Estadistica y Registros Academicos de la Facultad de ciencias (AERA).
    11. En caso sea sumamente necesario puedes usar la siguiente informacion adicional de la Facultad de Ciencias para complementar alguna respuesta:
        - La facultad de ciencias cuenta con pagina web.
        - En la sección de Matrícula y Procedimientos (dentro de Aera) de la pagina web de la facultad se publica:
            * Manuales/diagramas de diferentes procesos de matricula, procedimientos y tramites academicos.
            * El calendario académico
            * Modelos para solicitudes de diferentes procesos academicos.
        - Las vacantes disponibles de los cursos a matriculase se visualizan en la plataforma de intranet-alumno (DIRCE)
    12. Considera agregar un contexto proporcionado por el usuario antes de manifestar su duda.

Conversación 1:
            user: ...
            assistant: ...
            user: ...
            ...
    
Lista de pares de preguntas y respuestas: ```{sample_group_qa}```
    
Conversaciones generadas:

    Conversación 1:
            user: tengo una pregunta sobre la convalidación de asignaturas. ¿Cuál es el porcentaje mínimo de contenido que deben coincidir las asignaturas para que proceda la convalidación?
            assistant: Para que proceda la convalidación, los respectivos sílabos de las asignaturas a convalidar deben coincidir al menos en un 75% de su contenido y de horas dictadas.
            user: Entiendo, tambien me gustaría saber ¿Cuál es el plazo para convalidaciones de traslados internos?.
            assistant: El período disponible para realizar convalidaciones de traslados internos se extiende hasta cinco (5) días hábiles contados a partir de la aprobación por parte del Consejo de Facultad o la autorización del Decano, conforme a lo establecido en el reglamento de matrícula de la Facultad de Ciencias de la UNI.
            user: ok
            assistant: Si tienes más preguntas en el futuro o necesitas ayuda, no dudes en preguntar. ¡Buena suerte con todo!
    
    Conversación 2:
    	    user: Hola, buenas tardes.
            assistant: ¡Hola!, ¿En qué puedo ayudarte hoy?
            user: tengo una consulta. Quiero solicitar la convalidacion de un curso pero no estoy seguro si hay un minimo de porcentaje de similitud entre los cursos.
            assistant: Para que la convalidación pueda llevarse a cabo, es necesario que los contenidos y la carga horaria de las asignaturas respectivas coincidan en al menos un 75%.
            user:  He llevado un curso de Programación II en otra facultad que tiene 3 créditos y quisiera convalidarlo con el curso de Programación Orientada a Objetos que tiene 4 créditos. Según mi estimación, coinciden entre un 60% a 70%. ¿Habrá alguna manera de solicitar su convalidación?
            assistant: La decisión se toma conforme al reglamento de Matrícula de la Facultad de Ciencias, que establece un mínimo del 75% de coincidencia en contenido y horas dictadas para su convalidación. Te sugiero consultar con la oficina del Área de Estadística y Registros Académicos (AERA) para obtener más información sobre posibles apelaciones.
            user: ok
            assistant: Si tienes más preguntas, no dudes en preguntar. Estoy aquí para ayudar.
            user: ok 
            assistant: Perfecto. Si en el futuro tienes más preguntas, no dudes en comunicarte. ¡Que tengas un buen día!
            
    Conversación 3:
    	    user: Estoy tramitando mi traslado interno de la escuela de matemáticas a la de ciencias de la computación. Me dijeron que una vez que sea aprobado, puedo convalidar varios cursos. ¿Cuántos días tengo como plazo límite para realizar este proceso?
    	    assistant: El plazo disponible para llevar a cabo convalidaciones luego de un traslado interno es de hasta cinco (5) días hábiles, comenzando a contar desde la aprobación por parte del Consejo de Facultad o la autorización del Decano. Esta información se basa en lo establecido en el reglamento de matrícula de la Facultad de Ciencias de la UNI.
    	    user: entonces si aprueban mi traslado interno mañana lunes tendria, hasta el proximo lunes para tramitarlo.
    	    assistant: Los días hábiles se contabilizan de lunes a viernes, excluyendo los días festivos a nivel nacional o regional. Si tu traslado interno es aprobado un lunes, dispondrás de un periodo de 5 días hábiles a partir de ese día para llevar a cabo las convalidaciones. Este plazo se cumplirá en el próximo viernes, siempre y cuando no haya feriados en ese lapso.
    	    user: a ya entiendo y que requisito deben cumplir los cursos para que se puedan convalidar?
    	    assistant:  Para que la convalidación pueda llevarse a cabo, es necesario que los contenidos y la carga horaria de los cursos respectivos coincidan en al menos un 75%.
    	    user: ok
            assistant: Si tienes alguna otra duda, no dudes en consultarme. ¡Estoy aquí para ayudar!
    	    user: no eso es todo lo que queria saber
    	    assistant: Entendido. Si en el futuro surge alguna pregunta o necesitas asistencia, no dudes en volver. ¡Buena suerte con todo!
    	    
    Conversación 4:
            user: una consulta. Quiero solicitar la convalidacion del curso de fisica ii pero no estoy seguro si hay un minimo de porcentaje de similitud requerido entre los cursos.
            assistant: Para que la convalidación pueda llevarse a cabo, es necesario que los contenidos y la carga horaria de las asignaturas respectivas coincidan en al menos un 75%.
            user: como ya me aprobaron mi traslado interno, queria saber hasta cuando puedo realizar las convalidaciones de cursos.
            assistant:  El período disponible para realizar convalidaciones de traslados internos se extiende hasta cinco (5) días hábiles contados a partir de la aprobación por parte del Consejo de Facultad o la autorización del Decano, conforme a lo establecido en el reglamento de matrícula de la Facultad de Ciencias de la UNI.
            user: ok, gracias.
            assistant: ¡De nada! Si tienes alguna otra duda, no dudes en preguntar. Estoy aquí para ayudarte.
            user: ok, adios.
            assistant: ¡Adiós! Si tienes más preguntas en el futuro, no dudes en volver. ¡Hasta luego!
            
    Conversación 5:
            user: : queria que me ayudes con esta duda. Estaba considerando la posibilidad de trasladarme a la escuela de física dentro de la misma facultad y me gustaría saber qué cursos podría convalidar.
            assistant: Las asignaturas a convalidar deben coincidir al menos en un 75% de su contenido y de horas dictadas, para que proceda la convalidación.
            user: entonces, si el curso que lleve tiene 4 creditos igual lo puedo convalidar con uno 5 creditos.
            assistant: Es correcto, mientras coincidan en al menos un 75% de su contenido y de horas dictadas, la convalidacion puede llevarse a acabo.
            user: y si la simitud que se encuentra es del 70%, tengo alguna opcion de apelar a la esa decisión o es definitiva?
            assistant: Según el reglamento de Matrícula de la Facultad de Ciencias, se requiere un mínimo del 75% para la convalidación. Sin embargo, puedes considerar hablar con la oficina del Área de Estadística y Registros Académicos (AERA) para obtener información detallada sobre posibles apelaciones y opciones disponibles para tu situación. ¡No dudes en buscar más orientación si lo necesitas!
            user: esta bien.
            assistant:  tienes alguna otra duda, no dudes en consultar. Estoy aquí para ayudarte.
   	   
    Conversación 6:
            user:Me aprobaron mi traslado interno el miércoles de la semana pasada, pero el jueves fue feriado nacional. Entonces, ¿Todavía tendría hasta el jueves para realizar la convalidación de cursos?
            assistant:  Según el reglamento de matrícula de la Facultad de Ciencias de la UNI, el plazo para las convalidaciones de traslados internos es de hasta cinco días hábiles desde la aprobación del Consejo de Facultad o la autorización del Decano. Dado que te aprobaron el traslado interno el miércoles de la semana pasada y el jueves fue feriado nacional, el primer día hábil sería el miércoles. Luego contaríamos el viernes, lunes, martes y miércoles. Por lo tanto, el plazo de cinco días hábiles se agotaría el miércoles de esta semana, y deberías completar la convalidación hasta ese día para cumplir con el reglamento establecido. 
            user: genial, ahora me queda mucho mas claro gracias.
            assistant:  ¡De nada! tienes alguna otra duda, no dudes en consultar. Estoy aquí para ayudarte.
            user: En caso de que me pase de ese plazo, ¿podría solicitar alguna prórroga?
            assistant: Entiendo tu preocupación. Sin embargo, los plazos deben cumplirse según lo establecido en el reglamento. Si llegara a pasarte, te recomendaría que te pongas en contacto con la oficina del Área de Estadística y Registros Académicos (AERA) lo antes posible. Explica tu situación detalladamente y pregunta si existe algún procedimiento para solicitar una prórroga en caso de que necesites más tiempo para completar la convalidación.
            user: esta bien, lo tendre en mente,  Gracias por la ayuda.
            assistant: No hay de qué. Recuerda que si tienes más preguntas en el futuro, puedes contactarme. 
           
    Conversación 7:
            user: tengo una duda, no estoy seguro si puedo convalidar el curso de Fisica I que lleve antes de trasladarme a la Facultad de Ciencias.
            assistant:  Para que la convalidación sea efectiva, es necesario que el silabus y la carga horaria del curso de Física I que cursaste previamente, antes de tu traslado, coincidan en al menos un 75% con el curso que deseas convalidar.
            user: mmm...
            assistant: ¿Hay algo específico sobre temas relacionados a la Facultad de ciencias, que incluyen incluyen procesos de matricula, procemientos y tranmites, entre otros que quisieras saber?. Estoy aquí para ayudar con cualquier pregunta adicional que puedas tener sobre estos temas.
            user: dime como esta el clima hoy.
            assistant: Lo siento, solo puedo ayudarte con temas relacionados a la Facultad de ciencias, los cuales incluyen procesos de matricula, procemientos y tranmites, entre otros.
            user: ok
            assistant: Recuerda que si tienes más preguntas en el futuro, puedes contactarme. 

    Conversación 8:
            user: una duda, acabo de trasladarme a la escuela de ingenieria fisica me diferon que puedo convalidar algunos cursos. Cuanto tiempo tengo para hacerlo?
            assistant: En el caso de traslados internos, el plazo para realizar convalidaciones se extiende hasta cinco (5) días hábiles, contados a partir de la aprobación por parte del Consejo de Facultad o la autorización del Decano. Esto está establecido en el reglamento de matrícula de la Facultad de Ciencias de la UNI.     
            user: Como ya han pasado 6 días desde que aprobaron mi traslado interno, ¿puedo solicitar la convalidación de los cursos?
            assistant: Entiendo tu situación y tu interés en solicitar la convalidación de cursos después de tu traslado interno. Según los reglamentos de la Facultad de Ciencias, el plazo para las convalidaciones es de hasta cinco (05) días hábiles desde la aprobación del Consejo de Facultad o la autorización del Decano. Dado que ya han pasado 6 días desde la aprobación, te recomendaría verificar si el plazo de los 5 días hábiles (sin contar feriados ni fines de semana) no ha caducado. En caso de que no haya expirado, puedes proceder con la convalidación de cursos antes de que concluya el plazo.
            user:  Ok, también estaba en duda en esto. ¿Existe algún requisito para que los cursos se puedan convalidar?
            assistant:  Para que la convalidación proceda, es necesario que los silabus y la carga horaria de los cursos respectivos coincidan en al menos un 75%.
            user:  entonces el curso de fisica iii que lleve en la antes de mi trasaldo puede convalidarse
            assistant: Es posible la convalidacion, si es que los silabus y la carga horaria de los cursos respectivos coincidan en al menos un 75%.
        
Lista de preguntas y respuestas: ```{text_group_qa}```

Conversaciones generadas:

"""
        return prompt
    
    def generate_conversations(self, group_qa):
        prompt = self.get_prompt_gen_conversations(group_qa)
        messages =  [{'role':'user', 'content':prompt}]
        response = get_completion_from_messages(
            messages, 
            temperature=0,
            model="gpt-4-1106-preview"
            )
        print("\nresponse:", response)
        conversations = format_convesations_data(response)

        if len(conversations) < 8:
            print("\nFaltan generar conversaciones\n")
            #content = prompt + "\n" + response
            messages =  [{'role':'user', 'content':prompt}]
            response = get_completion_from_messages(
                messages, 
                temperature=0, 
                model="gpt-4-1106-preview"
            )
            print("\nresponse:", response)
            next_conversations = format_convesations_data(response)
            num_missing_conv = 8 - len(conversations) 
            conversations = conversations + next_conversations[-num_missing_conv:]

        return conversations
       
    def run(self):
        groups_qa = generate_random_groups_qa(self.file_qa)
        all_conversations_generated = []
      
        if os.path.exists("./conversations_generated.json"):
            all_conversations_generated = load_json("./conversations_generated.json")
            prev_groups_qa = [conversation["metadata"]["group_qa"] for  conversation in all_conversations_generated]
            reset_point = len(set(g_qa[0]["question"] + " " +  g_qa[1]["question"] for g_qa in  prev_groups_qa))
            print("reset_point:", reset_point)
        else:
            reset_point = 0
        
        print(f"Restuarando generación en la iteración {reset_point+1} ...\n")
        num_conv_generated = len(all_conversations_generated)
        progress_bar = tqdm(len(groups_qa[reset_point:152]), desc= "Generando Conversaciones" )
       
        for group_qa in groups_qa[reset_point:152]:
              conversations = self.generate_conversations(group_qa)
              conversations = [{**conv, "metadata": {"group_qa": group_qa}}  for conv in conversations]
              all_conversations_generated.extend(conversations)
      

              num_conv_generated += len(conversations)
              progress_bar.set_postfix({"total_preguntas": num_conv_generated})
              progress_bar.update(1)

        save_json("./", "conversations_generated", all_conversations_generated)
        

convesation_generator = ConversationGenerator(file_qa= "./answers_generated.json")

convesation_generator.run()