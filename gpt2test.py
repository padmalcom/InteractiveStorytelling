history = """My name is Jonas and I have been hunting dinosaurs my entire life. One day during a tough hunt I met my wife Lilly. She was the love of my life
and when I saw her the first time I could not focus on the triceratops who was just attacking me. He """

""" import gpt_2_simple as gpt2
import os
       
if not os.path.isdir("./models/124M"):
    gpt2.download_gpt2(model_name="124M")
session = gpt2.start_tf_sess()
gpt2.load_gpt2(session, model_name="124M")


gpo=gpt2.generate(session, temperature=0.1,prefix=history, model_name="124M",length=400,return_as_list=True,nsamples=3,batch_size=3,top_p=0.99)
for index, candidate in enumerate(gpo):
    length = len(history)
    print(str(index) + " before: " + candidate)
    candidate = candidate[length:]
    print(str(index) + " after: " + candidate) """

from transformers import GPT2LMHeadModel, GPT2Tokenizer
import torch
import numpy as np
from tqdm import trange

from transformers import GPT2Config, OpenAIGPTConfig, XLNetConfig, TransfoXLConfig, XLMConfig, CTRLConfig

def top_k_top_p_filtering(logits, top_k=0, top_p=0.0, filter_value=-float('Inf')):
    assert logits.dim() == 1  # batch size 1 for now - could be updated for more but the code would be less clear
    top_k = min(top_k, logits.size(-1))  # Safety check
    if top_k > 0:
        # Remove all tokens with a probability less than the last token of the top-k
        indices_to_remove = logits < torch.topk(logits, top_k)[0][..., -1, None]
        logits[indices_to_remove] = filter_value

    if top_p > 0.0:
        sorted_logits, sorted_indices = torch.sort(logits, descending=True)
        cumulative_probs = torch.cumsum(torch.nn.functional.softmax(sorted_logits, dim=-1), dim=-1)

        # Remove tokens with cumulative probability above the threshold
        sorted_indices_to_remove = cumulative_probs > top_p
        # Shift the indices to the right to keep also the first token above the threshold
        sorted_indices_to_remove[..., 1:] = sorted_indices_to_remove[..., :-1].clone()
        sorted_indices_to_remove[..., 0] = 0

        indices_to_remove = sorted_indices[sorted_indices_to_remove]
        logits[indices_to_remove] = filter_value
    return logits

# parameters
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
n_gpu = torch.cuda.device_count()
seed = 0
stop_token = None
num_samples = 1
sample_length = 200

# ??? parameters
temperature = 1.0
top_k = 0
top_p = 0.9

# set seed
np.random.seed(seed)
torch.manual_seed(seed)
if n_gpu > 0:
    torch.cuda.manual_seed_all(seed)

# models
# ('gpt2', 'gpt2-medium', 'gpt2-large', 'distilgpt2', 'openai-gpt', 'xlnet-base-cased', 'xlnet-large-cased', 'transfo-xl-wt103', 'xlm-mlm-en-2048', 'xlm-mlm-ende-1024', 'xlm-mlm-enfr-1024', 'xlm-mlm-enro-1024', 'xlm-mlm-tlm-xnli15-1024', 'xlm-mlm-xnli15-1024', 'xlm-clm-enfr-1024', 'xlm-clm-ende-1024', 'xlm-mlm-17-1280', 'xlm-mlm-100-1280', 'ctrl')
model = GPT2LMHeadModel.from_pretrained('gpt2')
tokenizer = GPT2Tokenizer.from_pretrained('gpt2')
model.to(device)
model.eval()

context = tokenizer.encode(history, add_special_tokens=False)

# generator
context = torch.tensor(context, dtype=torch.long, device=device)
context = context.unsqueeze(0).repeat(num_samples, 1)
generated = context
with torch.no_grad():
    for _ in trange(sample_length):
        inputs = {'input_ids': generated}
        outputs = model(**inputs)  # Note: we could also use 'past' with GPT-2/Transfo-XL/XLNet/CTRL (cached hidden-states)
        next_token_logits = outputs[0][0, -1, :] / (temperature if temperature > 0 else 1.)

        # reptition penalty from CTRL (https://arxiv.org/abs/1909.05858)
        #for _ in set(generated.view(-1).tolist()):
        #    next_token_logits[_] /= repetition_penalty
                
        filtered_logits = top_k_top_p_filtering(next_token_logits, top_k=top_k, top_p=top_p)
        if temperature == 0: #greedy sampling:
            next_token = torch.argmax(filtered_logits).unsqueeze(0)
        else:
            next_token = torch.multinomial(torch.nn.functional.softmax(filtered_logits, dim=-1), num_samples=1)
        generated = torch.cat((generated, next_token.unsqueeze(0)), dim=1)

# print
out = generated[0, len(context):].tolist()
text = tokenizer.decode(out, clean_up_tokenization_spaces=True, skip_special_tokens=True)
text = text[: text.find(stop_token) if stop_token else None]
print(text)