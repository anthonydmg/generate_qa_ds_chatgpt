import glob
from utils import read_fragment_doc, save_json
import os
import re
dir_documents = "./documentos/reglamento_matricula"

documents = glob.glob(f"{dir_documents}/*.txt")
documents.sort()

texts_generated_examples = []
input_prompt_gen_chapter = """Proporciona el texto relacionado con el fragmento identificado como RM-{id:05d}. 
Este fragmento corresponde a la parte {portion_num} del capitulo {chapter_num} del Reglamento de Matrícula de la Facultad de Ciencias.
"""

input_prompt_gen_fragment = """Proporciona el texto relacionado con el fragmento identificado como RM-{id:05d}
Este fragmento corresponde a {short_description} del Reglamento de Matrícula de la Facultad de Ciencias
"""

for id , file_text in enumerate(documents):
     
    text = read_fragment_doc(file_text)

    file_name = os.path.basename(file_text)
    if "capitulo" in file_name:
        chapter_name = re.findall("capitulo\d+", file_name)[0]
        chapter_num = chapter_name.replace("capitulo","")
        part_name = re.findall("parte\d+", file_name)[0]
        portion_num = part_name.replace("parte","")
        input = input_prompt_gen_chapter.format(id = id, chapter_num = chapter_num, portion_num = portion_num)
    else:
        input = input_prompt_gen_fragment.format(id = id,short_description = "las disposiciones transitorias y finales")

    texts_generated_examples.append({ 
        "input": input, 
        "output": text})

print(texts_generated_examples[0])

save_json("./", "texts_generated", texts_generated_examples)
    