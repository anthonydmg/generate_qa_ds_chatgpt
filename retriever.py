import numpy as np
import faiss
import json
from sentence_transformers import SentenceTransformer
from utils import load_json
from scipy import spatial

INDEX_PATH = "./kb/faiss_index.index"
EMBEDDINGS_PATH = "./kb/embeddings.npy"
IMPORTANCE_PATH = "./kb/importance.npy"
TEXTS_PATH = "./kb/texts.json"

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

    def encode(self, query, normalized = False):
        embeddings = self.model_emb.encode(query)
        print("embeddings:", embeddings.shape)
        if normalized:
            embeddings = self.normalize(embeddings.reshape(1,-1))
        return embeddings
    
    def normalize(self, v):
        return v / np.linalg.norm(v, axis=1, keepdims=True)

class Retriever:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Retriever, cls).__new__(cls)
            cls._instance.__init__(*args, **kwargs)
        return cls._instance
    
    def __init__(self):
        embeddings, importance, texts, index = self.load_data()
        self.embeddings = embeddings
        self.importance = importance
        self.texts = texts
        self.index = index
        self.encoder = EmbeddingEncoder()

    def load_data(self):
        embeddings = np.load(EMBEDDINGS_PATH)
        importance = np.load(IMPORTANCE_PATH)
        texts = load_json(TEXTS_PATH)
        index = faiss.read_index(INDEX_PATH)
        print("index:", index)
        return embeddings, importance, texts, index
    
    def retrive_texts(self, query, top_k = 10):
        query_embeddings = self.encoder.encode(query, normalized=True)
        distances, indexes = self.index.search(query_embeddings, top_k)
        print("initial indexes:", indexes)
        print("distances:", distances)
        importance_k = self.importance[indexes]
        # Reponderar los scores
        distances_weighted = distances * importance_k
        # Reordenar
        sorted_idx = np.argsort(-distances_weighted, axis=1)
        indexes_final = np.take_along_axis(indexes, sorted_idx, axis=1)
        distances_final = np.take_along_axis(distances_weighted, sorted_idx, axis=1)
        print("indexes_final:", indexes_final)
        #print("distances_final:", distances_final)
        result_texts = [self.texts[i] for i in indexes_final[0]]
        return result_texts, distances_final[0]


def strings_ranked_by_relatedness(
        query,
        df,
        relatedness_fn=lambda x, y: 1 - spatial.distance.cosine(x, y),
        top_n = 10,
        weighted_source = {
            "faq": 1, "topic-specific-document": 0.90, "regulation": 0.85, "general_information": 1.0},
    ):
        """Returns a list of strings and relatednesses, sorted from most related to least."""
        encoder = EmbeddingEncoder()
        query_embedding =  encoder.encode(query=query, normalized=False) #self.create_embedding_from_hf(query, self.embedding_model)
        
        strings_and_relatednesses = [
            (i, 
             row["text"], 
             relatedness_fn(query_embedding, row["embedding"]) #* weighted_source[row["type_source"]]
             )
            for i, row in df.iterrows()
        ]
        #print("strings_and_relatednesses:", strings_and_relatednesses[0])
        strings_and_relatednesses.sort(key=lambda x: x[2], reverse=True)
        indexes, strings, relatednesses = zip(*strings_and_relatednesses)
        return indexes[:top_n] ,strings[:top_n], relatednesses[:top_n]

def prev_retrival(query):
    import pandas as pd
    import ast
    df = pd.read_csv("./kb/topics.csv")
    #print(df.head(10))
    df["embedding"] = df['embedding'].apply(ast.literal_eval)
    indexes, strings, relatednesses = strings_ranked_by_relatedness(query, df, top_n=30)
    print("indexes:", indexes)
    print("relatednesses:", relatednesses)
    print(strings[0])
    
if __name__ == "__main__":
    retriever = Retriever()
    query = "Oye, ¿me puedes decir qué requisitos tiene que cumplir un estudiante para matricularse en la Facultad de Ciencias?"
    #query = "Oye, ¿me puedes decir qué requisitos tiene que cumplir un estudiante para matricularse en este ciclo academico de la Facultad de Ciencias?"
    #query = "Oye, me puedes decir ¿Cuales son los requisitos de matrícula para estudiantes en la Facultad de Ciencias?"
    result_texts, scores = retriever.retrive_texts(query, top_k=30)
    #print("result_texts:", result_texts)
    print("scores:", scores)
    print()
    prev_retrival(query)