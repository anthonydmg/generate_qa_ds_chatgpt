import tiktoken

from utils import load_json
import openai
import os
import pandas as pd

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

def halved_by_delimiter(string, delimiter = "\n") -> list[str, str]:
    """Split a string in two, on a delimiter, trying to balance tokens on each side."""
    chunks = string.split(delimiter)
    if len(chunks) == 1:
        return [string, ""]  # no delimiter found
    elif len(chunks) == 2:
        return chunks  # no need to search for halfway point
    else:
        total_tokens = count_num_tokens(string)
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
    string = "\n\n".join([title,text])
    num_tokens_in_text = count_num_tokens(string)
    print("num_tokens_in_text:", num_tokens_in_text)
    if num_tokens_in_text <= max_tokens:
        return [text]
    elif max_recursion == 0:
        return truncated_text(string, model=model, max_tokens=max_tokens)
    else:
        for delimiter in ["\n\n", "\n", "."]:
            left, right = halved_by_delimiter(string, delimiter=delimiter)
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
                    results.extend(half_strings)
                return results
    
    return [truncated_text(string, model=model, max_tokens=max_tokens)]


MAX_TOKENS = 1600

text_subsections = []
general_topics_subsections = []

topics = load_json("topics_finals.json")
faqs = load_json("faq/faq_json.json")

for topic in topics:
    title = topic["topic"]
    content = topic["content"]
    print("title:", title)
    section = (title, content)
    subsections = split_text_into_subsections(section, max_tokens=MAX_TOKENS)
    text_subsections.extend(subsections)
    general_topics_subsections.extend([title] * len(subsections))

embeddings = []

for faq in faqs:
    text_faq = faq["topic"].title() + "\n" + faq["question"] + "\n" + faq["answer"]
    text_subsections.append(text_faq)
    general_topics_subsections.append(faq["topic"])

EMBEDDING_MODEL = "text-embedding-3-small"
BATCH_SIZE = 50
for batch_start in range(0, len(text_subsections), BATCH_SIZE):
    batch_end = min(batch_start + BATCH_SIZE, len(text_subsections))
    batch = text_subsections[batch_start:batch_end]
    print(f"Batch {batch_start} to {batch_end-1}")
    response = openai.embeddings.create(model=EMBEDDING_MODEL, input= batch)
    for i, be in enumerate(response.data):
        assert i == be.index  # double check embeddings are in same order as input
    batch_embeddings = [e.embedding for e in response.data]
    embeddings.extend(batch_embeddings)

df = pd.DataFrame({"topic": general_topics_subsections, "text": text_subsections, "embedding": embeddings})

SAVE_PATH = "./kb/topics.csv"

df.to_csv(SAVE_PATH, index=False)