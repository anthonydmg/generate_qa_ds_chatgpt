from utils import read_fragment_doc, count_num_tokens, save_json
import re
text = read_fragment_doc("./faq/faq.txt")

pattern_block = r"Tema: (.+?)Pregunta: (.+?)Respuesta:(.+?)(?=Tema: |$)"
bloques = re.findall(pattern_block, text, re.DOTALL)
faq_json = []
for i, bloq in enumerate(bloques):
    tema = bloq[0].strip()
    pregunta = bloq[1].strip()
    respuesta = bloq[2].strip()

    faq_json.append({
        "id": i + 1,
        "question": pregunta,
        "answer": respuesta,
        "topic": tema,
        "num_tokens_answers": count_num_tokens(respuesta) 
    })

print(f"\nUn total de {len(faq_json)} preguntas han sido extraidas")

save_json("./faq", "faq_json", faq_json)

