from glob import glob
from utils import load_json, save_json

path_directory = "./conversational_data"
files = glob(f"{path_directory}/conversations_simulated_*.json")
files.sort(key= lambda name: int(name[:-5].split("_")[-1]))

conversational_dataset = []
id = 0
for file_path in files:
    data = load_json(file_path)
    for conv in data:
        id +=1
        conversational_dataset.append({
            "id": id ,
            "messages": [{"role": m["role"], "content":m["content"]} for m in conv["messages"]]
        })

print(f"Numero de conversaciones finales {len(conversational_dataset)}")
save_json(path_directory,"conversational_dataset", conversational_dataset)
    #print(data)
