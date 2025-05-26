import tiktoken

from utils import load_json, save_json
import openai
import os
import pandas as pd
from sentence_transformers import SentenceTransformer
import numpy as np
import faiss

from dotenv import load_dotenv

def set_openai_key():
    API_KEY = os.getenv("API_KEY")
    openai.api_key = API_KEY

load_dotenv()

set_openai_key()

GPT_MODEL = "gpt-3.5-turbo"

def count_num_tokens(text, model = GPT_MODEL):
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))
import re

def halved_by_delimiter(string, delimiter = "\n") -> list[str, str]:
    """Split a string in two, on a delimiter, trying to balance tokens on each side."""
    chunks = string.split(delimiter)
    #print("delimiter:", repr(delimiter))
    #print("num chunks:", len(chunks))
    #print("len chunks:", [count_num_tokens(c) for c in chunks])
    if len(chunks) == 1:
        return [string, ""]  # no delimiter found
    elif len(chunks) == 2:
        return chunks  # no need to search for halfway point
    else:
        total_tokens = count_num_tokens(string)
        #print("\n\ntotal_tokens:", total_tokens)
        halfway = total_tokens // 2
        best_diff = halfway
        for i, chunk in enumerate(chunks):
            left = delimiter.join(chunks[: i + 1])
            left_tokens = count_num_tokens(left)
            diff = abs(halfway - left_tokens)
            if diff >= best_diff:
                break
            else:
                best_diff = diff
        left = delimiter.join(chunks[:i])
        right = delimiter.join(chunks[i:])
        return [left, right]
    

def truncated_text(
        text,
        model,
        max_tokens,
        print_warning = True
):
    """Trucate a text to a maximum number of tokens"""
    encoding = tiktoken.encoding_for_model(model)
    encoded_text= encoding.encode(text)
    truncated_text = encoding.decode(encoded_text[:max_tokens])
    if print_warning and len(encoded_text) > max_tokens:
        print(f"Warning: Trucanted text from {len(encoded_text)} token to {max_tokens} tokens.")
    return truncated_text

def merge_splits(self, splits, separator, max_size = 600):
    # We now want to combine these smaller pieces into medium size
    # chunks to send to the LLM.
    separator_len = self._length_function(separator)

    docs = []
    current_doc = []
    total = 0
    for d in splits:
        num_tokens = count_num_tokens(d)
        if (
            total + num_tokens > max_size
        ):
            if total > max_size:
                print(
                    f"Created a chunk of size {total}, ",
                    f"which is longer than the specified {max_size}"
                )
            if len(current_doc) > 0:
                doc = "\n".join(current_doc) #self._join_docs(current_doc, separator)
                if doc is not None:
                    docs.append(doc)
                # Keep on popping if:
                # - we have a larger chunk than in the chunk overlap
                # - or if we still have any chunks and the length is long
                while total > self._chunk_overlap or (
                    total + num_tokens > max_size
                    and total > 0
                ):
                    total -= self._length_function(current_doc[0]) + (
                        separator_len if len(current_doc) > 1 else 0
                    )
                    current_doc = current_doc[1:]
        current_doc.append(d)
        total += num_tokens 
    doc = self._join_docs(current_doc, separator)
    if doc is not None:
        docs.append(doc)

def split_text_into_subsections(
        section,
        max_tokens,
        model = GPT_MODEL,
        max_recursion = 5
):
    """
    Split text into list subsections, each with no more than max_tokens
    """
    title, text = section
    string = "\n".join([title,text])
    num_tokens_in_text = count_num_tokens(text)
    #print("\n\nnum_tokens_in_text:", num_tokens_in_text)
    if num_tokens_in_text <= max_tokens:
        return [string]
    elif max_recursion == 0:
        print(f"Warning: Created a chunk of {num_tokens_in_text} tokens, which is longer than the specified {max_tokens} max tokens")
        return [string]
        
        #return truncated_text(string, model=model, max_tokens=max_tokens)
    else:
        for delimiter in ["\n\n\n","\n\n", "\n", "."]:
            left, right = halved_by_delimiter(text, delimiter=delimiter)
            #print("delimiter:", repr(delimiter))
            #print("left tokens:",  count_num_tokens(left))
            #print("right tokens:",  count_num_tokens(right))
            #print("title tokens:",  count_num_tokens(title))
            #print("\nleft:", left)
            #print("\n\nright:", right)
            
            if left == "" or right == "":
                continue
            else:
                results = []
                for half in [left, right]:
                    half_subsection = (title, half)
                    half_strings = split_text_into_subsections(
                        half_subsection,
                        max_tokens=max_tokens,
                        model=model,
                        max_recursion=max_recursion - 1,
                    )
                    #print("add half_strings:", len(half_strings))
                    #return [text]
                    #half_strings[1] = "\n".join([title,half_strings[1]])
                    if len(results) == 1 and count_num_tokens(left) < 100 and (count_num_tokens(half_strings[0] +"\n" + left) < max_tokens):
                        results[0] = delimiter.join([results[0], half_strings[0][len(title):].strip()])
                        half_strings = half_strings[1:] if len(half_strings)> 1 else [] 

                    results.extend(half_strings)
                    
                
                return results
    
    return [truncated_text(string, model=model, max_tokens=max_tokens)]


MAX_TOKENS = 800

text_subsections = []
general_topics_subsections = []
type_sources = []

topics = load_json("topics_finals.json")
faqs = load_json("faq/faq_json.json")

for topic in topics:
    title = topic["topic"]
    content = topic["content"]
    print("title:", title)
    section = (title, content)
    subsections = split_text_into_subsections(section, max_tokens=MAX_TOKENS)
    print(f"Divido en {len(subsections)} secciones")
    print("len tokens:", [count_num_tokens(c) for c in subsections])
    text_subsections.extend(subsections)
    general_topics_subsections.extend([title] * len(subsections))
    
    type_source = "general_information" 
    if "documentos/otros/informacion_general" in topic["source"]:
        type_source = "general_information" 
    elif "reglamento_matricula" in topic["source"]:
        type_source = "regulation"
    else:
        type_source = "topic-specific-document"

    type_sources.extend([type_source] * len(subsections))


print("\nNumero de secciones encontradas:", len(text_subsections))

for faq in faqs:
    text_faq = faq["topic"].title() + "\n" + faq["question"] + "\n" + faq["answer"]
    text_subsections.append(text_faq)
    general_topics_subsections.append(faq["topic"])
    type_sources.append("faq")
print("\nNumero de secciones encontradas:", len(text_subsections))


EMBEDDING_MODEL_OPENAI = "text-embedding-3-small"

EMBEDDING_MODEL_HF = "jinaai/jina-embeddings-v2-base-es"

model_hf = None

def create_embeddings_from_hugginface(inputs, model_hf = EMBEDDING_MODEL_HF):
    #if model_hf is None:
    #    print("\nLoad Model")
    #    model_hf = SentenceTransformer(model_name, trust_remote_code=True)
    
    embeddings = model_hf.encode(inputs)
    #print(type(embeddings))
    #embeddings = embeddings.numpy()
    #print(type(embeddings))
    print("embeddings shape:", embeddings.shape)
    embeddings_str = [np.array2string(embeddings[i], separator=",") for i in range(embeddings.shape[0])]
    #print(embeddings_str)
    return embeddings_str, embeddings

def create_embeddings_from_openai(inputs, model_name = EMBEDDING_MODEL_OPENAI):
    response = openai.embeddings.create(model=model_name, input= inputs)
    for i, be in enumerate(response.data):
        assert i == be.index  # double check embeddings are in same order as input
    batch_embeddings = [e.embedding for e in response.data]
    return batch_embeddings

""" from utils import read_fragment_doc
text = read_fragment_doc("./documentos/matricula/matricula_condicionada.txt")

subsections = split_text_into_subsections(
        section = ("Traslado Interno", text),
        max_tokens = 600,
        model = GPT_MODEL,
        max_recursion = 5
)

print("Len subsections:", len(subsections))

for i in range(len(subsections)):
    print(f"Num tokens {count_num_tokens(subsections[i])} subsection {i}")
    print("subsection:",subsections[i] )
     """

EMBEDDING_MODEL = "text-embedding-3-small"
BATCH_SIZE = 10


weighted_source = {
            "faq": 1, "topic-specific-document": 0.85, "regulation": 0.75, "general_information": 1.0}

print("\nNumero de secciones encontradas:", len(text_subsections))
embeddings_str = []
embeddings = []
model_hf = SentenceTransformer(EMBEDDING_MODEL_HF, trust_remote_code=True)

for batch_start in range(0, len(text_subsections), BATCH_SIZE):
    batch_end = min(batch_start + BATCH_SIZE, len(text_subsections))
    batch = text_subsections[batch_start:batch_end]
    print(f"Batch {batch_start} to {batch_end-1}")
    batch_embeddings_str, batch_embeddings = create_embeddings_from_hugginface(inputs=batch, model_hf = model_hf)
    embeddings_str.extend(batch_embeddings_str)
    embeddings.extend(batch_embeddings)

df = pd.DataFrame({"type_source": type_sources ,"topic": general_topics_subsections, "text": text_subsections, "embedding": embeddings_str})

embeddings = np.array(embeddings).astype(np.float32)
print("embeddings.shape:",embeddings.shape)
# normalización (para similitud coseno)
embeddings = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)
print("embeddings.shape:",embeddings.shape)

importance = [weighted_source[ts] for ts in type_sources ]
## Guardar embeddings
np.save("./kb/embeddings.npy", embeddings)
np.save("./kb/importance.npy", importance)

save_json("./kb","texts", text_subsections)

index = faiss.IndexFlatIP(768)
index.add(embeddings)
faiss.write_index(index, "./kb/faiss_index.index")

print("Cantidad de Textos:", len(df))
print(df.head(15))
SAVE_PATH = "./kb/topics.csv"

df.to_csv(SAVE_PATH, index=False)
