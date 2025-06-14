#pip install --no-deps unsloth vllm==0.8.5.post1
#pip install --no-deps bitsandbytes accelerate xformers==0.0.29.post3 peft trl triton cut_cross_entropy unsloth_zoo
#import sys, re, requests; modules = list(sys.modules.keys())
#for x in modules: sys.modules.pop(x) if "PIL" in x or "google" in x else None
#pip install sentencepiece protobuf "datasets>=3.4.1" huggingface_hub hf_transfer
#f = requests.get("https://raw.githubusercontent.com/vllm-project/vllm/refs/heads/main/requirements/common.txt").content
#with open("vllm_requirements.txt", "wb") as file:
#    file.write(re.sub(rb"(transformers|numpy|xformers)[^\n]{1,}\n", b"", f))
#!pip install -r vllm_requirements.txt

for unsloth import FastLanguageModel, is_bfloat16_supported
import torch
max_seq_length = 1024
lora_rank = 64

model, tokenizer = FastLanguageModel.from_pretrained(
    model_name = "Qwen/Qwen2.5-0.5B"
)