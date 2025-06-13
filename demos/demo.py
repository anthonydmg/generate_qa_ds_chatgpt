import re

text = """Pregunta Original 1: ¿Cómo solicitar un certificado de décimo o quinto superior en la Facultad de Ciencias de la UNI?

Preguntas Generadas:
1. ¿Cuál es el proceso para obtener una constancia de quinto o tercio superior en la Facultad de Ciencias de la UNI?
2. ¿Dónde se puede solicitar un certificado de quinto superior en la Facultad de Ciencias de la UNI?
3. ¿Cuáles son los pasos para tramitar un certificado de décimo superior en la Facultad de Ciencias de la UNI?
4. ¿Qué requisitos se necesitan para obtener un certificado de quinto superior en la Facultad de Ciencias de la UNI?
5. ¿Cuál es el procedimiento para solicitar un certificado de tercio superior en la Facultad de Ciencias de la UNI?
6. ¿Cómo se puede obtener un certificado de décimo superior en la Facultad de Ciencias de la UNI?
7. ¿Dónde se encuentra la oficina encargada de emitir certificados de quinto superior en la Facultad de Ciencias de la UNI?
8. ¿Qué documentación se requiere para solicitar un certificado de tercio superior en la Facultad de Ciencias de la UNI?

Pregunta Original 2: ¿Cuáles son los requisitos y el proceso de matrícula para nuevos ingresantes de pregrado en la Facultad de Ciencias de la Universidad Nacional de Ingeniería?

Preguntas Generadas:
1. ¿Qué pasos deben seguir los nuevos ingresantes de pregrado para matricularse en la Facultad de Ciencias de la UNI?
2. ¿Dónde se pueden encontrar los requisitos para la matrícula de nuevos ingresantes en la Facultad de Ciencias de la UNI?
3. ¿Cuál es el procedimiento para realizar la matrícula como nuevo ingresante en la Facultad de Ciencias de la UNI?
4. ¿Cuáles son los documentos necesarios para la matrícula de nuevos ingresantes en la Facultad de Ciencias de la UNI?
5. ¿Cómo se puede completar el proceso de matrícula para nuevos ingresantes en la Facultad de Ciencias de la UNI?
6. ¿Dónde se puede obtener información sobre la matrícula de nuevos ingresantes en la Facultad de Ciencias de la UNI?
7. ¿Cuál es el cronograma de actividades para la matrícula de nuevos ingresantes en la Facultad de Ciencias de la UNI?
8. ¿Qué pasos se deben seguir para realizar la matrícula como nuevo ingresante en la Facultad de Ciencias de la UNI?

Pregunta Original 3: ¿Cuál es el procedimiento que debe seguir un estudiante para reservar su matrícula?

Preguntas Generadas:
1. ¿Cómo se puede solicitar la reserva de matrícula en la Facultad de Ciencias de la UNI?
2. ¿Cuáles son los pasos para reservar la matrícula como estudiante de la Facultad de Ciencias de la UNI?
3. ¿Dónde se puede encontrar el formulario para solicitar la reserva de matrícula en la Facultad de Ciencias de la UNI?
4. ¿Qué documentos se necesitan para realizar la reserva de matrícula en la Facultad de Ciencias de la UNI?
5. ¿Cuál es el plazo para solicitar la reserva de matrícula en la Facultad de Ciencias de la UNI?
6. ¿Cómo se puede justificar la solicitud de reserva de matrícula en la Facultad de Ciencias de la UNI?
7. ¿Dónde se puede obtener información sobre la reserva de matrícula en la Facultad de Ciencias de la UNI?
8. ¿Cuál es el periodo máximo de reserva de matrícula para los estudiantes de la Facultad de Ciencias de la UNI?"""

# Usar expresiones regulares para extraer las preguntas originales y generadas

def extract_reformulated_questions(text):
    matches = re.findall(r'Pregunta Original (\d+): (.+?)(?=Pregunta Original|\Z)', text, re.DOTALL)
    
    original_questions = []
    generated_questions = []
    # Iterar sobre los resultados
    for match in matches:
        pregunta_original_numero = match[0]
        pregunta_original = match[1].strip()
        preguntas_generadas = re.findall(r'\d+\. (.+)', pregunta_original)
        pregunta_original = pregunta_original.split('\n')[0].strip()
        print("Pregunta Original:", pregunta_original)
        print("Preguntas Generadas:", preguntas_generadas)
        print()

        original_questions.append(pregunta_original)
        generated_questions.append(preguntas_generadas)
    
    return original_questions, generated_questions

a = "\n\nReincorporaci\u00f3n Despu\u00e9s De Una Una Reserva De Matricula\n\u00bfQu\u00e9 procedimiento debe seguir un estudiante que desea reincorporarse despu\u00e9s de haber reservado su matricula por uno o mas periodos acad\u00e9micos?\nEl estudiante que desee realizar su reincorporaci\u00f3n deber\u00e1 gestionarla antes de las fechas de matr\u00edcula dentro del plazo establecido en el calendario de actividades acad\u00e9micas. Para ello, debera realizar los siguientes pasos.\n    1. Acceder a la plataforma intranet-alumnos con su c\u00f3digo UNI y clave correspondiente.\n    2. Luego, seleccionar la opci\u00f3n \"Tr\u00e1mites y Pagos\" para acceder al m\u00f3dulo de pagos del Portal INTRALU.\n    3. En el m\u00f3dulo de pagos, seleccionar el tr\u00e1mite correspondiente y generar un nuevo pago siguiendo las indicaciones en la plataforma. Mas detalles del proceso consultar el Manual de Pagos publicado en la secci\u00f3n [\"MATR\u00cdCULA Y PROCEDIMIENTOS\" de la Pagina Web de la Facultad de Ciencias](https://fc.uni.edu.pe/documentos/).\n\nUna vez generada la orden de pago, el alumno debe realizar el pago en una sucursal del BCP o utilizando la aplicaci\u00f3n m\u00f3vil del BCP. \nDespu\u00e9s de completar el pago, el estudiante debe enviar su solicitud de reincorporaci\u00f3n a trav\u00e9s de la Plataforma de Intranet-Alumnos dentro de los plazos establecidos (consultar el calendario acad\u00e9mico). Para ello accede a la plataforma, elige \"Reincorporaci\u00f3n de Estudiantes\" en \"Mis Tr\u00e1mites\", completa el formulario con la solicitud y el comprobante de pago, y env\u00eda la solicitud.\nAl completar el envi\u00f3 de la solicitud por la plataforma se visualizara la solicitud enviada, la fecha de envio y estado actual de la solicitud.\nUna vez aprobada y realizada la reincorporaci\u00f3n, el estudiante podr\u00e1 realizar su matr\u00edcula de manera regular.\n\nFecha De Pago De Autoseguro\n\u00bfHasta que fecha se debe realizar el pago por concepto de autoseguro estudiantil para que un estudiante pueda realizar la matr\u00edcula regular al ciclo academico en la Facultad de Ciencias de la UNI?\nLos estudiantes deben realizar el pago del autoseguro estudiantil antes de las fechas de matr\u00edcula, dentro del plazo m\u00e1ximo establecido en el calendario de actividades acad\u00e9micas correspondiente al periodo acad\u00e9mico. Si no se cumple con este plazo m\u00e1ximo, es probable que la matr\u00edcula no pueda realizarse de manera regular y deba gestionarse como rezagada. El estudiante puede verificar esta situaci\u00f3n al comprobar si su matr\u00edcula se habilita o no en las fechas de matr\u00edcula regular. Si la matr\u00edcula no se habilita en estas fechas, es necesario que el estudiante se comunique con la oficina de estad\u00edstica (AERA) al correo estadistica_fc@uni.edu.pe o revise el procedimiento para gestionar su matr\u00edcula rezagada.\nEl calendario de actividades acad\u00e9micas es publicado en la secci\u00f3n \"MATR\u00cdCULA Y PROCEDIMIENTOS\", puede acceder a esta secci\u00f3n mediante el siguiente enlace: https://fc.uni.edu.pe/documentos/\n\nProcedimiento Para Solicitar Una Constancia De Matricula\n\u00bfQu\u00e9 procedimiento debe seguir un estudiante para solicitar una constancia de Matricula en ingles o en espa\u00f1ol?\nPara solicitar una constancia de matr\u00edcula en ingl\u00e9s o en espa\u00f1ol, el estudiante deber seguir los siguientes pasos:\n\n1. Enviar un correo a estadistica_fc@uni.edu.pe solicitando una orden de pago para la CONSTANCIA DE MATR\u00cdCULA. En el mensaje, deber\u00e1 incluir sus datos personales: n\u00famero de DNI, apellidos, nombres, correo institucional y/o alternativo.\n\n2. La oficina de estad\u00edstica (AERA) le enviar\u00e1 la orden de pago por el monto de S/. 100.00 (dato correspondiente al a\u00f1o 2024) a su correo electr\u00f3nico.\n\n3. El alumno deber\u00e1 realizar el pago en alguna sucursal del BCP o a trav\u00e9s aplicaci\u00f3n movil del banco. En la app selecciona \"Pagar servicios\", elige la Universidad Nacional de Ingenier\u00eda, luego la opci\u00f3n de pago para estudiantes, e ingresa su n\u00famero de DNI. La app mostrar\u00e1 la orden de pago con el monto exacto para realizar el pago.\n\n4. Luego, el estudiante deber\u00e1 dejar en mesa de partes de la facultad el comprobante de pago y la solicitud correspondiente, o enviarlos por correo electr\u00f3nico a mesadepartes_fc@uni.edu.pe. Es importante que se asegure de indicar en la solicitud si desea la CONSTANCIA DE MATR\u00cdCULA en ingl\u00e9s o espa\u00f1ol. El modelo para esta solicitud est\u00e1 disponible en la secci\u00f3n [\"MATR\u00cdCULA Y PROCEDIMIENTOS\" en la p\u00e1gina web de la Facultad de Ciencias](https://fc.uni.edu.pe/documentos/).\n\n5. Por \u00faltimo, AERA enviar\u00e1 un correo para notificarle que la constancia est\u00e1 lista para ser recogida en el horario de atenci\u00f3n de Lunes a Viernes, de 08:00 a 13:00 y de 14:00 a 16:00.\n\nEstado De Tramites\n\u00bfComo un estudiante de la UNI puede ver el estado de sus tramites?\nEl estado de las solicitudes presentadas trav\u00e9s de la plataforma intranet-alumnos, puede ser visualizadas en la misma plataforma. Para otros tramites puede usar el n\u00famero de expediente correspondiente para realizar el seguimiento, ingresando a http://stduni.uni.pe/modalum\nEscuelas Profesionales de la Facultad de Ciencias de la UNI\n\nInformaci\u00f3n de Contacto:\nSeg\u00fan la escuela profesional (carrera universitaria), el correo de contacto es el siguiente:\n\nPara F\u00edsica, Qu\u00edmica o Ciencia de la Computaci\u00f3n: escuelas_fc1@uni.edu.pe\nPara Matem\u00e1ticas o Ingenier\u00eda F\u00edsica: escuelas_fc2@uni.edu.pe\n\nHorario de Atenci\u00f3n: De Lunes a Viernes de 8:30 a.m a 4:00 p.m\n\n\u00c1rea de Estad\u00edstica y Registros Acad\u00e9micos de la Facultad de Ciencias de la UNI\n\nInformaci\u00f3n de Contacto de la oficina de estad\u00edstica (AERA)\nE-mail: estadistica_fc@uni.edu.pe\n\nHorario de Atenci\u00f3n de la oficina de estad\u00edstica (AERA):\nDe Lunes a Viernes de 8:00 a.m. a 4:00 p.m."

print(a)

#extract_reformulated_questions(text)