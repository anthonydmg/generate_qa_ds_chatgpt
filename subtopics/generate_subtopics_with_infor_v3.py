
from utils import get_completion_from_messages, save_json, set_openai_key, count_tokens, read_fragment_doc
from dotenv import load_dotenv
import tiktoken
import re
import glob
from tqdm import tqdm
load_dotenv()

set_openai_key()

encoding = tiktoken.encoding_for_model('gpt-4-turbo')
#     - Las preguntas deben abarcar los diferentes subtemas mencionados abajo.
# de indicar explicitamente dentro de la informacion el nombre completo de la fuente específica del reglamento o estatuto asociado a cada subtema.

#texto = read_fragment_doc("./documentos/procedimientos/examen_regularizacion.txt")

class TopicsExtractor():
    def __init__(self, 
        model= "gpt-4-1106-preview",
        dir_documents = "./documentos"):
        self.model = model
        self.dir_documents = dir_documents

    def get_prompt_extract_topics(self, texto):
        prompt = f"""
Tu tarea consiste en extraer información relevante sobre subtemas dirigidos a usuarios como estudiantes, docentes y el público en general de la informacion proporcinada de los reglamentos académicos de la Facultad de Ciencias de la UNI (delimitada por tres comillas invertidas). Debes seguir los siguientes pasos:

Paso 1. Analiza detalladamente la informacion proporcionda (delimitada por tres comillas invertidas) con el fin de identificar temas y subtemas relevantes dirigidos a usuarios como estudiantes, docentes y el público en general. Los cuales deben cumplir los siguiente criterios:
	* Los temas y subtemas deben estar bien desarrollados y explícitamente descritos en la información proporcionada. 
	* Utiliza nombres concisos y descriptivos para los temas, facilitando así su comprensión. 
	* Evita la redundancia de subtemas y limita los subtemas a un nivel.
	
Paso 2. Extrae de manera literal toda la información relacionada con cada subtema, asegurándote de no omitir ningún detalle, informacion adjunta o referenciada (Tablas, articulos, entre otros) y previamente a la informacion menciona explicitamente el nombre completo de la fuente específica reglamento o estatuto asociado de donde proviene la informacion extraida incluyendo el capitulo o nombre de seccion solo si la hubiera.

Paso 3. Presenta los temas y subtemas, junto con su información correspondiente, siguiendo el formato:

1. Tema...
  1.1. Subtema...
    ``` La siguiente informacion proviene ...
        Información detallada ...
        ```
  1.2. Subtema...
    ``` La siguiente informacion proviene ...
        Información detallada ...
        ```
2. Tema...
...

Fragmento de texto: ```{texto}```
"""
        return prompt
    
    def extract_topics_content_from_text(self, texto):
        pattern_topics = r'(\d+\.\s*[^`]+)?\n+\s+(\d+\.\d+\.[^`]+)(`{3}.*?`{3})'

        matches_topics = re.findall(pattern_topics, texto, re.DOTALL)


        found_topics = []

        for match in matches_topics:
            if match[0]!='':
                topic = re.sub(r'^\d+\.\s', '',  match[0]).replace("Tema:","").strip()       

            subtopic = re.sub(r'^\d+\.\d+\.\s','', match[1]).replace("Subtema:","").strip()
            
            content =  match[2].replace("```","").strip()
            
            found_topics.append({
                "topic": topic,
                "subtopic": subtopic,
                "content": content
                })
        return found_topics

    def extract_topics(self, texto):
        prompt = self.get_prompt_extract_topics(texto)
        messages =  [{'role':'user', 'content':prompt}]
        response = get_completion_from_messages(
            messages, 
            temperature=0,
            #model= "gpt-3.5-turbo-0125" 
            model= self.model
            )
        print("response:", response)
        found_topics = self.extract_topics_content_from_text(response)
        return found_topics
    
    def run(self):
        documents = glob.glob(f"{self.dir_documents}/*/*.txt")
        documents.sort()
        #texto = read_fragment_doc("./documentos/procedimientos/examen_regularizacion.txt")
        print("Inicia Extraccion de Temas Relevantes...")
        print("documents:", documents)
        all_found_topics = []
        
        for file_text in tqdm(documents[16:17], desc= "Documentos"):
            print("file_text:", file_text)
            text = read_fragment_doc(file_text)
            found_topics = self.extract_topics(text)
            found_topics = [{**t, "source": file_text} for t in found_topics]
            all_found_topics.extend(found_topics)
        
        save_json("./", "topics", all_found_topics)


if __name__ == "__main__":
    topics_extractor = TopicsExtractor(
            dir_documents = "./documentos",
            model= "gpt-4-1106-preview")
 
    topics_extractor.run()
