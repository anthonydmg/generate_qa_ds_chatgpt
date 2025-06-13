from utils import get_completion_from_messages


from dotenv import load_dotenv
import openai
import os

def set_openai_key():
    API_KEY = os.getenv("API_KEY")
    openai.api_key = API_KEY

load_dotenv()

set_openai_key()

prompt = """Dado el historial del chat proporcionado entre tres comillas invertidas y la última pregunta del usuario, reformula la pregunta de manera que dependa completamente del contexto del historial del chat y no se entienda sin él

Historial del chat: ```
user:¿Cuál es el plazo límite para solicitar el retiro total?
assistant:El plazo límite para solicitar el retiro total es hasta una semana antes de los exámenes parciales, a través de la plataforma SIGA-DIRCE (intranet-alumnos). En casos excepcionales debidamente justificados, como enfermedad grave de ascendiente o descendiente en primer grado certificada por el Centro Médico de la UNI, MINSA o ESSALUD, se puede solicitar hasta una semana antes de los exámenes finales, sujeto a evaluación por el Consejo Directivo de la Escuela Profesional correspondiente. Recuerda consultar el calendario académico para las fechas específicas.
user:¿Qué tipo de documentación se requiere para justificar un retiro total por enfermedad grave de un familiar en primer grado?
assistant:Para justificar un retiro total por enfermedad grave de un familiar en primer grado, se requiere presentar un certificado médico emitido por el Centro Médico de la UNI, MINSA o ESSALUD que certifique la gravedad de la enfermedad. Este certificado debe contener la información necesaria que respalde la situación, como el diagnóstico, la gravedad de la enfermedad y la relación de parentesco con el estudiante. Además, es importante adjuntar este documento sustentatorio al completar el formulario de solicitud de retiro total en la plataforma intranet-alumnos. Recuerda seguir los pasos detallados en el procedimiento para enviar la solicitud correctamente.
user:¿Es necesario presentar algún otro tipo de documentación adicional junto con el certificado médico para justificar el retiro total por enfermedad grave de un familiar en primer grado?
assistant:No es necesario presentar otro tipo de documentación adicional junto con el certificado médico para justificar el retiro total por enfermedad grave de un familiar en primer grado. El certificado médico emitido por el Centro Médico de la UNI, MINSA o ESSALUD que certifique la gravedad de la enfermedad y la relación de parentesco con el estudiante es suficiente para respaldar la solicitud de retiro total en este caso. Recuerda adjuntar este documento al completar el formulario de solicitud en la plataforma intranet-alumnos.```

Último mensaje del usuario: ```¡Gracias por la información! ¿Hay algún plazo específico para presentar la solicitud de retiro total una vez que se cuenta con el certificado médico?```    """

messages =  [{'role':'user', 'content':prompt}]

response = get_completion_from_messages(
    messages, 
    temperature=0,
    model="gpt-3.5-turbo-0125" 
    #model= "gpt-4-1106-preview"
)
print("response:", response)