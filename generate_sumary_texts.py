import glob
from utils import read_fragment_doc, save_json, format_response_json
import os
import re
import openai
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")
openai.api_key = API_KEY

dir_documents = "./documentos/reglamento_matricula"

documents = glob.glob(f"{dir_documents}/*.txt")
documents.sort()

chapters = {}
for doc in documents:
    chapter_name = re.sub("_parte\d+","", os.path.basename(doc).replace(".txt",""))
    if chapter_name not in chapters:
        chapters[chapter_name] = [doc]
    else:
        chapters[chapter_name].append(doc)


def get_prompt_gen_summary(description,reglamento):
    format_json = """{{resumen del texto...}}"""
    
    prompt = f"""
    Tu tarea es generar un resumen a partir de la información que corresponde {description} del Reglamento de Matrícula de la Facultad de Ciencias descrito abajo.
    Asegúrate que el el resumen no exceda las 180 palabras o 10 oraciones.
    Utiliza el capitulo del reglamento de debajo, delimitado por tres comillas invertidas para el resumen.
    Finalmente, asegúrate de proporcionar el resumen solo en el siguiente formato:
    {format_json}
    Capitulo del Reglamento: ```{reglamento}```
    """
    return prompt


def get_completion_from_messages(messages, model="gpt-3.5-turbo-16k-0613", temperature=0):
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        #max_tokens = 0,
        temperature=temperature, # this is the degree of randomness of the model's output
    )
    return response.choices[0].message["content"]


summary_generated_examples = []

for chapter_name, files in chapters.items():
    texts = [read_fragment_doc(file)  for file in files ]
    chapter_text = "\n".join(texts)
    if "capitulo" in chapter_name:
        description = f'al capitulo {chapter_name.replace("capitulo","")}'
    else:
        description = f'a la sección de {chapter_name.replace("_"," ")}'
    prompt = get_prompt_gen_summary( description= description,reglamento = chapter_text)
    messages =  [{'role':'user', 'content':prompt}]
    response = get_completion_from_messages(messages, temperature=0)
    print("response:", response)
    summary = re.findall("{{.+}}",response)[0]
    summary = summary.lstrip("{{")
    summary = summary.rstrip("}}")
    print("summary:", summary)
    #resp_json = format_response_json(response)
    #summary = resp_json["resumen"]
    summary_generated_examples.append({
        "input": f"Proporciona el resumen relacionado {description} del Reglamento de Matrícula de la Facultad de Ciencias",
        "chapter_name": chapter_name,
        "files": files,
        "output": summary})

save_json("./", "summary_generated", 
summary_generated_examples)