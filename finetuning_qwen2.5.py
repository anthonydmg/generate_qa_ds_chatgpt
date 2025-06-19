from unsloth import FastLanguageModel, is_bf16_supported
import torch

max_seq_length = 4096
lora_rank = 64
dtype = None

model, tokenizer = FastLanguageModel.from_pretrained(
    model_name = "./models/Qwen2.5-0.5B",
    max_seq_length = max_seq_length,
    load_in_4bit = True,
    dtype = dtype
    #fast_inference = True,
    #max_lora_rank = lora_rank,
    #gpu_memory_utilization = 0.5
)

model = FastLanguageModel.get_peft_model(
    model,
    r = lora_rank,
    target_modules=[
        "q_proj", "k_proj", "v_proj", "o_proj",
        "gate_proj", "up_proj", "down_proj",
    ],
    lora_alpha = lora_rank,
    lora_dropout = 0,
    bias = "none",
    use_gradient_checkpointing = "unsloth",
    random_state = 42,
    use_rslora = False,
    loftq_config = None    
)

from unsloth.chat_templates import get_chat_template
from datasets import load_dataset

tokenizer = get_chat_template(
    tokenizer,
    chat_template = "qwen-2.5"
)

def formatting_prompts_func(examples):
    convos = examples["conversations"]
    texts = [tokenizer.apply_chat_template(convo, tokenize = False, add_generation_prompt = False) for convo in convos]
    return {"text": texts}


dataset = load_dataset("./models/FineTome-100k", split="train")
print(dataset[0])


from unsloth.chat_templates import standardize_sharegpt
dataset = standardize_sharegpt(dataset)
dataset = dataset.map(formatting_prompts_func, batched=True)
print(dataset[0])

print(dataset[0]['text'])

from unsloth import is_bf16_supported
from trl import SFTTrainer
from transformers import TrainingArguments, DataCollatorForSeq2Seq
trainer = SFTTrainer(
    model = model,
    tokenizer = tokenizer,
    train_dataset = dataset,
    dataset_text_field = "text",
    max_seq_length = max_seq_length,
    data_collator = DataCollatorForSeq2Seq(tokenizer = tokenizer),
    dataset_num_proc = 2,
    packing = False, # Can make training 5x faster for short sequences.
    args = TrainingArguments(
        per_device_train_batch_size = 2,
        gradient_accumulation_steps = 4,
        warmup_steps=5,
        max_steps=60,
        learning_rate= 2e-4,
        fp16= not is_bf16_supported(),
        bf16= is_bf16_supported(),
        logging_steps=1,
        optim = "adamw_8bit",
        weight_decay = 0.01,
        lr_scheduler_type = "linear",
        seed = 3407,
        output_dir = "outputs"
    ),
)

from unsloth.chat_templates import train_on_responses_only
trainer = train_on_responses_only(
    trainer,
    instruction_part= "<|im_start|>user\n",
    response_part= "<|im_start|>assistant\n",
)

print(tokenizer.decode(trainer.train_dataset[5]["input_ids"]))


space = tokenizer(" ", add_special_tokens= False).input_ids[0]
print(tokenizer.decode([space if x == -100 else x for x in trainer.train_dataset[5]["labels"]]))


# @title Show current memory stats
gpu_stats = torch.cuda.get_device_properties(0)
start_gpu_memory = round(torch.cuda.max_memory_reserved() / 1024 / 1024 / 1024, 3)
max_memory = round(gpu_stats.total_memory / 1024 / 1024 / 1024, 3)
print(f"GPU = {gpu_stats.name}. Max memory = {max_memory} GB.")
print(f"{start_gpu_memory} GB of memory reserved.")


trainer_stats = trainer.train()