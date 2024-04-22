
from utils import get_completion_from_messages, set_openai_key, count_tokens, read_fragment_doc
from dotenv import load_dotenv
import tiktoken

load_dotenv()

set_openai_key()

encoding = tiktoken.encoding_for_model('gpt-4-turbo')
#     - Las preguntas deben abarcar los diferentes subtemas mencionados abajo.

texto = read_fragment_doc("./documentos/reglamento_matricula/capitulo1_parte1.txt")

prompt = f"""
Analiza detalladamente los reglamentos académicos de la Facultad de Ciencias de la UNI (delimitada por tres comillas invertidas) con el fin de identificar y presentar de manera clara y concisa los temas y subtemas relevantes dirigidos a usuarios como estudiantes, docentes y el público en general.

Asegúrate de estructurar los temas y subtemas de manera coherente y comprensible, evitando la redundancia y limitando los subtemas a dos niveles de profundidad.

Luego, extrae de manera literal toda la información relacionada con cada subtema, asegurándote de no omitir ningún detalle relevante y de proporcionar la fuente específica del reglamento o estatuto asociado a cada subtema.

Finalmente, presenta los temas y subtemas identificados, junto con su información correspondiente, siguiendo un formato organizado y fácil de entender.

Fragmento de texto: ```{texto}```
  
"""

#print(prompt)

print("size input: ",count_tokens(encoding,prompt))
messages =  [{'role':'user', 'content':prompt}]
response = get_completion_from_messages(
    messages, 
    temperature=0,
    model= "gpt-3.5-turbo-0125" 
    #model= "gpt-4-1106-preview"
    )
print(response)
print("size output: ", count_tokens(encoding,response))

