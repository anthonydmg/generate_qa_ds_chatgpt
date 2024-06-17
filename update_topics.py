from utils import read_fragment_doc, save_json
from glob import glob

directories = [
    "./documentos/matricula",
    "./documentos/otros",
    "./documentos/procedimientos"
]
    
topics = []

for dir in directories:
    files_docs = glob(f"{dir}/*.txt")
    for doc in files_docs:
        text = read_fragment_doc(doc)
        topic_name = doc.split("/")[-1][:-4].replace("_"," ").title()
        print("topic_name:", topic_name)
        topics.append({
            "topic": topic_name,
            "content": text,
            "source": doc
        })

save_json("./","topics_finals", topics)