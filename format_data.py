from utils import load_json, save_json

data_qa = load_json("./answers_generated.json")
qa_pairs = [qa for block_qas in data_qa for qa in block_qas["question_answer_pairs"] ]

instruction_examples = [{
    "instruction": "Imagina que eres un asistente virtual especializado en brindar información sobre la Facultad de Ciencias, incluyendo reglamentos, procedimientos, trámites académicos y cualquier información general relacionada. Por favor, responde a la siguiente pregunta",
    "input": qa["pregunta"],
    "output": qa["respuesta"]
} for qa in qa_pairs]

data_tg = load_json("./texts_generated.json")
data_tg = [ {"instruction": tg["input"], "output": tg["output"]} for tg in data_tg]
#instruction_examples.extend(data_tg)

data_sg = load_json("./summary_generated.json")
data_sg = [ {"instruction": sg["input"], "output": sg["output"]} for sg in data_sg]

#instruction_examples.extend(data_sg)

save_json("./","instruction_only_qa_regulation", instruction_examples)