from utils import filtered_questions_reformulated_rouge, flat_questions_reformulate, join_reformulated_questions, load_json, save_json


#reformulated_faqs = load_json("./faq/reformulated_faqs.json")


#reformulated_faqs_joined = join_reformulated_questions(reformulated_faqs)

#save_json("./faq", "reformulated_faqs_joined", reformulated_faqs_joined)


reformulated_faqs_joined = load_json("./faq/reformulated_faqs_joined.json")

threshold_rouge = 0.80
filtered_questions_reformulated = filtered_questions_reformulated_rouge(reformulated_faqs_joined, threshold_rouge)

save_json(f"./faq/reformulated_{threshold_rouge}", f"filtered_questions_reformulated_rouge_{threshold_rouge}", filtered_questions_reformulated)

filtered_questions_reformulated_rouge_list = load_json(f"./faq/reformulated_{threshold_rouge}/filtered_questions_reformulated_rouge_{threshold_rouge}.json")

filtered_reformulated_question_list = flat_questions_reformulate(filtered_questions_reformulated_rouge_list)

print("Numero de preguntas finales:", len(filtered_reformulated_question_list))

save_json(f"./faq/reformulated_{threshold_rouge}", f"filtered_reformulated_question_list", filtered_reformulated_question_list)
