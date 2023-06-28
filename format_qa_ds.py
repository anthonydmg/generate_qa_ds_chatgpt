from utils import load_json, save_json

data = load_json("./answers_generated.json")
qa_pairs = [qa for block_qas in data for qa in block_qas["question_answer_pairs"] ]

save_json("./","registration_regulation_qa", qa_pairs)