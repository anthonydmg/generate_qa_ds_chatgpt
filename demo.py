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

extract_reformulated_questions(text)