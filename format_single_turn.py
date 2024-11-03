from utils import load_json, save_json

def format_conv_to_single_turn(path_dataset_conv):
    conv_dataset = load_json(path_dataset_conv)
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


if __name__ == "__main__":
    path_dataset_conv = "./conversational_faq/data/conversational_dataset.json"
    single_turn_dataset = format_conv_to_single_turn(path_dataset_conv)

    save_json("./conversational_faq/data", "single_turn_dataset", single_turn_dataset)


