
from utils import get_completion_from_messages, set_openai_key, count_tokens, read_fragment_doc
from dotenv import load_dotenv
import tiktoken

load_dotenv()

set_openai_key()

encoding = tiktoken.encoding_for_model('gpt-4-turbo')
#     - Las preguntas deben abarcar los diferentes subtemas mencionados abajo.

texto = read_fragment_doc("./documentos/reglamento_matricula/capitulo2_parte1.txt")

prompt = f"""
Analiza la información provista sobre los reglamentos académicos de la Facultad de Ciencias de la UNI (delimitada por tres comillas invertidas) para identificar temas y subtemas relevantes dirigidos a usuarios como estudiantes, docentes y el público en general. 
Asegúrate de que los temas y subtemas estén bien desarrollados y explícitamente descritos en la información proporcionada.
Utiliza nombres concisos y descriptivos para los temas, facilitando así su comprensión. Ademas, evita la redundancia de subtemas.

Finalmente presenta los temas y subtemas de la siguiente manera:

1. Tema...
 1.1. Subtema...
 1.2. Subtema...
 ...
2. Tema..
  ...

Fragmento de texto: ```{texto}```
  
"""

#print(prompt)

print("size input: ",count_tokens(encoding,prompt))
messages =  [{'role':'user', 'content':prompt}]
response = get_completion_from_messages(
    messages, 
    temperature=0,
    #model= "gpt-3.5-turbo-0125" 
    model= "gpt-4-1106-preview"
    )
print(response)
print("size output: ", count_tokens(encoding,response))