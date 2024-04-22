import pandas as pd
import ast
from scipy import spatial
import os
import pandas as pd
import openai

from dotenv import load_dotenv
def set_openai_key():
    API_KEY = os.getenv("API_KEY")
    openai.api_key = API_KEY

load_dotenv()

set_openai_key()

GPT_MODEL = "gpt-3.5-turbo"
EMBEDDING_MODEL = "text-embedding-3-small"

embeddings_path = "topics.csv"

df = pd.read_csv(embeddings_path)

df["embedding"] = df['embedding'].apply(ast.literal_eval)
print(df)

def strings_ranked_by_relatedness(
    query,
    df,
    relatedness_fn=lambda x, y: 1 - spatial.distance.cosine(x, y),
    top_n = 5
):
    """Returns a list of strings and relatednesses, sorted from most related to least."""
    query_embedding_response = openai.embeddings.create(
        model=EMBEDDING_MODEL,
        input=query,
    )
    query_embedding = query_embedding_response.data[0].embedding
    strings_and_relatednesses = [
        (row["text"], relatedness_fn(query_embedding, row["embedding"]))
        for i, row in df.iterrows()
    ]
    strings_and_relatednesses.sort(key=lambda x: x[1], reverse=True)
    strings, relatednesses = zip(*strings_and_relatednesses)
    return strings[:top_n], relatednesses[:top_n]

query = "En cuantos creditos se puede matricular un estudiante?"
sub_texts, relatednesses = strings_ranked_by_relatedness(query, df, top_n=2)
for string, relatednesses in zip(sub_texts, relatednesses):
    print(f"{relatednesses=:.3f}")
    print("text:", string)


