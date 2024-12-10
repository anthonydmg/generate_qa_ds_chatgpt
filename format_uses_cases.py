from glob import glob
import os
import re
import json

def format_use_cases_dialoges():
    files_names =  glob("./use_cases/case*.txt")
    use_cases_dialogs = []

    for file_path in files_names:
        print("file_path:", file_path)
        base_name =  os.path.basename(file_path[:-4])
        print("base_name:", base_name)
        id_n  = base_name.split('_')[-1]
        print("id_n:", id_n)
        with open(file_path, "r") as f:
            lines = f.readlines()
        text = "\n".join(lines)
        pattern_dialog =  r"(User:.*?)(?=Assistant:|User:|\Z)(Assistant:.*?)(?=User:|Assistant:|\Z)"
        turns = re.findall(pattern_dialog, text, re.DOTALL)
        dialog = []
        for turn in turns:
            user_message = turn[0].replace("User:",'').strip()
            assistant_message = turn[1].replace("Assistant:",'').strip()
            dialog.append({"role":"user", "content": user_message})
            dialog.append({"role":"assistant", "content": assistant_message})
        
        #print("dialog:", dialog)
        use_cases_dialogs.append({
            "id": id_n,
            "file_name": base_name,
            "messages": dialog
        })
    return use_cases_dialogs

if __name__ == "__main__":
    use_cases_dialogs = format_use_cases_dialoges()
    with open("./use_cases/use_cases_dialogs.json", "w") as f:
        json.dump(use_cases_dialogs, f, indent=4)

