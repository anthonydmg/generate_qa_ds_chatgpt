import pandas as pd
from utils import count_num_tokens, get_completion_from_messages, load_json, save_json, read_fragment_doc
from sentence_transformers import SentenceTransformer
from scipy import spatial
import ast
import re
import time
from unsloth import FastLanguageModel
import torch

def conversation_to_text(messages):
    txt = ""
    for m in messages:
        role = "Usuario" if m["role"] == "user" else "Asistente"
        txt = txt + "\n" + role + ": "+ m["content"]
    return txt

class EmbeddingEncoder:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(EmbeddingEncoder, cls).__new__(cls)
            cls._instance.init(*args, **kwargs)
        return cls._instance

    def init(self, model_name="jinaai/jina-embeddings-v2-base-es"):
        if model_name:
            self.model_name = model_name
            self.model_emb = SentenceTransformer(model_name, trust_remote_code=True)
        else:
            self.model_name = None
            self.model_emb = SentenceTransformer(model_name, trust_remote_code=True)

    def encode(self, query):
        embeddings = self.model_emb.encode(query)
        return embeddings

class Retriever:
    def init(self, path_df_kb):
        self.model_emb = EmbeddingEncoder()
        self.df_kb = pd.read_csv(path_df_kb)
        self.df_kb["embedding"] = self.df_kb['embedding'].apply(ast.literal_eval)

    def get_best_texts_by_relatedness(
        self,
        query,
        df,
        context = None,
        relatedness_fn=lambda x, y: 1 - spatial.distance.cosine(x, y),
        top_n = 5,
        weighted_source = {
            "faq": 1, "topic-specific-document": 0.8100, "regulation": 0.75, "general_information": 1.10},
        weigthed_embeddings = {"query": 0.68, "context": 0.32} 
    ):
        """Returns a list of strings and relatednesses, sorted from most related to least."""
        query_embedding = self.create_embedding(query, self.embedding_model)
        
        if context is not None:
            context_embedding = self.create_embedding(context, self.embedding_model)

            strings_and_relatednesses = [
                (row["text"], (weigthed_embeddings["query"]* relatedness_fn(query_embedding, row["embedding"]) + 
                               weigthed_embeddings["context"] * relatedness_fn(context_embedding, row["embedding"])
                               ) * weighted_source[row["type_source"]])
                for i, row in df.iterrows()
            ]
        
        else:
            strings_and_relatednesses = [
                (row["text"], relatedness_fn(query_embedding, row["embedding"]) * weighted_source[row["type_source"]])
                for i, row in df.iterrows()
            ]
        
        strings_and_relatednesses.sort(key=lambda x: x[1], reverse=True)
        strings, relatednesses = zip(*strings_and_relatednesses)
        return strings[:top_n], relatednesses[:top_n]
    
    def create_embedding(self, query):
            embeddings = self.model_emb.encode(query)
            return embeddings

class Contextualizer:
    def init(self, model_name="anthonymg/FineContextualizeLlama-3.2-1B"):
        model, tokenizer = FastLanguageModel.from_pretrained(
            model_name = model_name,
            max_seq_length = 2048,
            load_in_4bit = True,
            dtype = None
        )
        model = FastLanguageModel.for_inference(model)
        self.model = model
        self.tokenizer = tokenizer

    def generate(self, query, dialog_context):
        self.model.eval()  # Poner el modelo en modo de evaluación
        prompt = self.formatting_prompt(query, dialog_context)
        with torch.no_grad():
            text = prompt
            inputs = self.tokenizer([
                text,
            ], return_tensors = "pt").to(self.model.device)

            outputs = self.model.generate(
                **inputs,
                max_new_tokens = 256,
                use_cache = True)

            output_text = self.tokenizer.decode(outputs[0, len(inputs[0]):], skip_special_tokens = True)
        return output_text
    
    def formatting_prompt(self, user_message, dialog_context):
        template_prompt = """### Historial de la conversación:
{}

### Consulta actual del usuario:
Usuario: {}

### Instrucciones:
Dado el historial de la conversación y la consulta actual del usuario, reformula la pregunta de manera que pueda entenderse sin necesidad del historial de la conversación.  No responda la pregunta "solo reformúlela si es necesario y, de lo contrario, devuélvala tal como está".

### Pregunta Reformulada:
{}"""
        text = template_prompt.format(conversation_to_text(dialog_context),
                                      user_message, "")
        return text 

class AnswerGenerator:
    def init(self, model_name="anthonymg/FineAeritoLlama-3.2-1B"):
        model, tokenizer = FastLanguageModel.from_pretrained(
            model_name = model_name,
            max_seq_length = 4096,
            load_in_4bit = True,
            dtype = None
        )
        model = FastLanguageModel.for_inference(model)
        self.model = model
        self.tokenizer = tokenizer

    def generate(self, query, dialog_context, retrieved_texts):
        self.model.eval()  # Poner el modelo en modo de evaluación
        prompt = self.formatting_prompt(query, dialog_context, retrieved_texts)
        with torch.no_grad():
            text = prompt
            inputs = self.tokenizer([
                text,
            ], return_tensors = "pt").to(self.model.device)

            outputs = self.model.generate(
                **inputs,
                max_new_tokens = 256,
                use_cache = True)

            output_text = self.tokenizer.decode(outputs[0, len(inputs[0]):], skip_special_tokens = True)
        return output_text
    
    def formatting_prompt(self, user_message, dialog_context, retrieved_texts):
        retrieved_information = "\n\n".join([ text["text"] for text in retrieved_texts[:5]])

        template_prompt = """### Contexto de la conversación:
{}

### Información Recuperada:
{}

### Consulta actual del usuario:
Usuario: {}

### Instrucciones:
Eres Aerito un asistente de AI especializado en temas de matricula, procedimientos y tramites académicos de la Facultad de Ciencias de la Universidad Nacional de Ingeniería de Peru. Responde a la consulta actual del usuario utilizando el contexto de la conversación y la información recuperadoa.

### Respuesta:
{}"""   
        text = template_prompt.format(conversation_to_text(dialog_context),
                                    retrieved_information,
                                    user_message, "")
        return text 

class AIAssistant:
    def __init__(
            self, 
            path_df_kb = "./kb/topics.csv",
            contextualization_model = "anthonymg/FineContextualizeLlama-3.2-1B",
           ):
        
        self.df_kb = pd.read_csv(path_df_kb)
        self.df_kb["embedding"] = self.df_kb['embedding'].apply(ast.literal_eval)

        self.contexts = [None]
        self.recovered_texts = [None]
        self.reformulated_question = [None]
        self.retriever = Retriever(path_df_kb)
        self.contextualizer = Contextualizer(model_name = contextualization_model)
        self.answer_generator = AnswerGenerator()
        self.history = []
        self.recovered_texts = []
        self.reformulated_messages = []
    
    def contar_tokens_history(self, historial):
        total_tokens = 0
        for turno in historial:
            # Concatena el rol y el contenido
            texto = f"{turno['role']}: {turno['content']}"
            # Cuenta los tokens
            total_tokens += len(self.answer_generator.tokenizer.encode(texto, add_special_tokens=False))
        return total_tokens

    def update_context(self, new_turn, limit_tokens = 2048):
        self.history.append(new_turn)
        while self.contar_tokens_history(self.history) > limit_tokens:
            self.history.pop(0)
    
    def reset_context(self):
        self.history = []
        self.recovered_texts = []
        self.reformulated_messages = []

    def format_text_history_chat(self, history_chat):
        text = ""
        for message in history_chat:
            text += f'\n{message["role"]}:{message["content"]}'    
        return text

    def get_reformulated_contextual_query(self, query, history_chat_messages):
        reformulated_query = self.contextualizer.generate(query, history_chat_messages)
        return reformulated_query

    def generate_response(self, message):
        query = message
        reformulated_query = self.get_reformulated_contextual_query(query = query, history_chat_messages = self.history)

        info_texs, relatednesses = self.retriever.get_best_texts_by_relatedness(reformulated_query)
        
        print("\nrelatednesses:", relatednesses)
        self.recovered_texts.append([{"text": text, "relatedness": relatedness } for text , relatedness in zip(info_texs, relatednesses)])

        ## Filter low relatednesess
        cut_idx = len(relatednesses)
        for i in range(len(relatednesses)):
            if relatednesses[i] < 0.40:
                cut_idx = i
                print(f"\nSimilarity lower than threshold {relatednesses[i]}, idx {cut_idx}")
                break

        info_texs = info_texs[:cut_idx]
        relatednesses = relatednesses[:cut_idx]

        num_tokens_context_dialog =  self.contar_tokens_history(self.history)
        print("\nnum_tokens_context_dialog:", num_tokens_context_dialog)
        max_tokens_response = 850

        general_contact_information = read_fragment_doc("./documentos/informacion_general_contacto.txt")
        
        response_ai_assistant = self.answer_generator.generate(query=query, dialog_context = self.history, retrieved_texts= info_texs + [general_contact_information])

        response_ai_assistant = response_ai_assistant.replace("```","").strip()

        self.history.append({"role": "user", "content": message})
        self.reformulated_messages.append(reformulated_query)
        self.history.append({"role": "assistant", "content": response_ai_assistant})
        self.reformulated_messages.append(None)
        self.recovered_texts.append(None)

        return response_ai_assistant
    
    def get_history_dialog(self, include_context = True):
        if include_context:
            history_dialog = []
            dialog_data = zip(self.history, self.recovered_texts, self.reformulated_messages)
            
            for message, texts, reformulated_question in dialog_data:
                history_dialog.append({
                    "role": message["role"],
                    "content": message["content"],
                    "recovered_texts": texts,
                    "reformulated_question": reformulated_question,
                })
                
            return history_dialog
        else:
            return self.history
        
if __name__ == "__main__":
    assistant = AIAssistant()
    query = "hola"
    ai_response = assistant.answer_generator(query)
    print(ai_response)