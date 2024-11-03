from utils import load_json, save_json
from sklearn.model_selection import train_test_split

def format_conv_to_single_turn(conv_dataset):
    #conv_dataset = load_json(path_dataset_conv)
    single_turn_dataset = [] 
    for conv in conv_dataset:
        conv_id = conv["id"]
        messages = conv["messages"]
        for index, m in enumerate(messages):
            if m["role"] == "user":
                dialog_context = messages[0:index]
                retrieved_texts =  m["recovered_texts"]
                user_message = m["content"]
                expected_response = messages[index + 1]["content"]

                single_turn_dataset.append({
                    "conv_id": conv_id,
                    "dialog_context": dialog_context,
                    "retrieved_texts": retrieved_texts,
                    "user_message": user_message,
                    "expected_response": expected_response
                })
    
    return single_turn_dataset


def prepare_datasets(full_dataset):
    conv_dataset = load_json(full_dataset)

    train_val, test = train_test_split(conv_dataset, test_size=0.2, random_state=42)

    train, val = train_test_split(train_val, test_size= 0.25, random_state=42)

    dir_data = "./conversational_faq/data/"

    for data, name_set in zip([train, val, test],["train","val", "test"]):
        save_json(dir_data, f"{name_set}_conversational_dataset", data)
        single_turn_dataset = format_conv_to_single_turn(data)
        save_json(dir_data, f"{name_set}_single_turn_dataset", single_turn_dataset)

if __name__ == "__main__":
    path_dataset_conv = "./conversational_faq/data/conversational_dataset.json"
    prepare_datasets(path_dataset_conv)