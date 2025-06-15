from glob import glob
from utils import load_json, save_json

path_directory = "./conversational_faq" # conv_sim_faq_1_derived_20_to_29
#files = glob(f"{path_directory}/conversations_simulated_*.json")
files = glob(f"{path_directory}/openline-questions/conv_sim_derived_*.json") #+ glob(f"{path_directory}/openline-derived/conv_sim_faq_*.json")
files.sort()
#files.sort(key= lambda name: int(name[:-5].split("_")[-1]))

conversational_dataset = []
id = 0
for file_path in files:                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             
    print("file_path:", file_path)
    data = load_json(file_path)
    print("len(data):",len(data))
    for conv in data:
        id +=1
        conversational_dataset.append({
            "id": id ,
            "messages": [{
                "role": m["role"], 
                "recovered_texts": m["recovered_texts"],
                "content":m["content"],
                #"need_context": m["need_context"] == True,
                "reformulated_question": m["reformulated_question"]
                } for m in conv["messages"]]
        })

print(f"Numero de conversaciones finales {len(conversational_dataset)}")
save_json(path_directory + "/data","conversational_dataset", conversational_dataset)



from datasets import DatasetDict, Dataset, load_dataset
from huggingface_hub import login

#login(token="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")

# Cargar tu dataset
#dataset = load_dataset("json", data_files= "conversational_faq/data/conversational_dataset.json")


# Guardar el dataset en el Hub
#dataset.push_to_hub("anthonymg/aera_conversational_dataset")
    #print(data)

#from datasets import DatasetDict, Dataset, load_dataset
#from huggingface_hub import login
#dataset = load_dataset("anthonymg/aera_conversational_dataset")
#print(dataset)
