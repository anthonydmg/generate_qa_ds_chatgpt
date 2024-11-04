from glob import glob
from utils import load_json, save_json

path_directory = "./conversational_faq" # conv_sim_faq_1_derived_20_to_29
#files = glob(f"{path_directory}/conversations_simulated_*.json")
files = glob(f"{path_directory}/openline-reformulated/conv_sim_faq_*.json") + glob(f"{path_directory}/openline-derived/conv_sim_faq_*.json")
files.sort()
#files.sort(key= lambda name: int(name[:-5].split("_")[-1]))

conversational_dataset = []
id = 0
for file_path in files:                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             
    print("file_path:", file_path)
    data = load_json(file_path)
    for conv in data:
        id +=1
        conversational_dataset.append({
            "id": id ,
            "messages": [{
                "role": m["role"], 
                "recovered_texts": m["recovered_texts"],
                "content":m["content"],
                "need_context": m["need_context"] == True,
                "reformulated_question":  m["content"] if not m["need_context"] and  m["role"] == "user" else m["reformulated_question"]
                } for m in conv["messages"]]
        })

print(f"Numero de conversaciones finales {len(conversational_dataset)}")
save_json(path_directory + "/data","conversational_dataset", conversational_dataset)
    #print(data)
