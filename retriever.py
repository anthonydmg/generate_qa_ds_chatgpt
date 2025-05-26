import numpy as np
import faiss
import json
from sentence_transformers import SentenceTransformer
from utils import load_json


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
        return embeddings, importance, texts, index
    
    def retrive_texts(self, query, top_k = 10):
        query_embeddings = self.encoder.encode(query, normalized=True)
        distances, indexes = self.index.search(query_embeddings, top_k)
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

if __name__ == "__main__":
    retriever = Retriever()
    query = "¿Cuáles son los pasos y requisitos que un estudiante regular debe seguir para matricularse en el ciclo académico en la UNI?"
    result_texts, scores = retriever.retrive_texts(query, top_k=15)
    #print("result_texts:", result_texts)
    print("scores:", scores)