# WARNING: you are on the master branch, please refer to the examples on the branch that matches your `cortex version`

# This file includes code which was modified from https://github.com/huggingface/transformers/blob/master/examples/run_generation.py

from __future__ import absolute_import, division, print_function, unicode_literals

import torch
import torch.nn.functional as F
#from transformers import GPT2Tokenizer, GPT2LMHeadModel
from transformers import AutoTokenizer, AutoModelWithLMHead
from tqdm import trange
import math
import nltk

def top_k_top_p_filtering(logits, top_k=0, top_p=0.0, filter_value=-float("Inf")):
    """ Filter a distribution of logits using top-k and/or nucleus (top-p) filtering
        Args:
            logits: logits distribution shape (vocabulary size)
            top_k > 0: keep only top k tokens with highest probability (top-k filtering).
            top_p > 0.0: keep the top tokens with cumulative probability >= top_p (nucleus filtering).
                Nucleus filtering is described in Holtzman et al. (http://arxiv.org/abs/1904.09751)
        From: https://gist.github.com/thomwolf/1a5a29f6962089e871b94cbd09daf317
    """
    assert (
        logits.dim() == 1
    )  # batch size 1 for now - could be updated for more but the code would be less clear
    top_k = min(top_k, logits.size(-1))  # Safety check
    if top_k > 0:
        # Remove all tokens with a probability less than the last token of the top-k
        indices_to_remove = logits < torch.topk(logits, top_k)[0][..., -1, None]
        logits[indices_to_remove] = filter_value

    if top_p > 0.0:
        sorted_logits, sorted_indices = torch.sort(logits, descending=True)
        cumulative_probs = torch.cumsum(F.softmax(sorted_logits, dim=-1), dim=-1)

        # Remove tokens with cumulative probability above the threshold
        sorted_indices_to_remove = cumulative_probs > top_p
        # Shift the indices to the right to keep also the first token above the threshold
        sorted_indices_to_remove[..., 1:] = sorted_indices_to_remove[..., :-1].clone()
        sorted_indices_to_remove[..., 0] = 0

        indices_to_remove = sorted_indices[sorted_indices_to_remove]
        logits[indices_to_remove] = filter_value
    return logits


def sample_sequence(
    model,
    length,
    context,
    device,
    num_samples=1,
    temperature=1,
    top_k=0,
    top_p=0.9,
    repetition_penalty=1.0
):
    context = torch.tensor(context, dtype=torch.long, device=device)
    context = context.unsqueeze(0).repeat(num_samples, 1)
    generated = context
    with torch.no_grad():
        for _ in trange(length):

            inputs = {"input_ids": generated}
            outputs = model(
                **inputs
            )  # Note: we could also use 'past' with GPT-2/Transfo-XL/XLNet/CTRL (cached hidden-states)
            next_token_logits = outputs[0][0, -1, :] / (temperature if temperature > 0 else 1.0)

            # reptition penalty from CTRL (https://arxiv.org/abs/1909.05858)
            for _ in set(generated.view(-1).tolist()):
                next_token_logits[_] /= repetition_penalty

            filtered_logits = top_k_top_p_filtering(next_token_logits, top_k=top_k, top_p=top_p)
            if temperature == 0:  # greedy sampling:
                next_token = torch.argmax(filtered_logits).unsqueeze(0)
            else:
                next_token = torch.multinomial(F.softmax(filtered_logits, dim=-1), num_samples=1)
            generated = torch.cat((generated, next_token.unsqueeze(0)), dim=1)
    return generated


class GPT2:
    def __init__(self, model_scale):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        #self.tokenizer = GPT2Tokenizer.from_pretrained("distilgpt2")
        #self.model = GPT2LMHeadModel.from_pretrained("distilgpt2")
        if model_scale == 0:
            self.tokenizer = AutoTokenizer.from_pretrained("distilgpt2")
            self.model = AutoModelWithLMHead.from_pretrained("distilgpt2")
        elif model_scale == 1:
            self.tokenizer = AutoTokenizer.from_pretrained("gpt2")
            self.model = AutoModelWithLMHead.from_pretrained("gpt2")
        elif model_scale == 2:
            self.tokenizer = AutoTokenizer.from_pretrained("gpt2-medium")
            self.model = AutoModelWithLMHead.from_pretrained("gpt2-medium")
        elif model_scale == 3:
            self.tokenizer = AutoTokenizer.from_pretrained("gpt2-large")
            self.model = AutoModelWithLMHead.from_pretrained("gpt2-large")
        else:
            self.tokenizer = AutoTokenizer.from_pretrained("gpt2-xl")
            self.model = AutoModelWithLMHead.from_pretrained("gpt2-xl")
        
        self.model.eval()
        self.model.to(self.device)

    def generate_texts(self, prefix, length, num_samples):
        #indexed_tokens = self.tokenizer.encode(prefix)
        #output = sample_sequence(self.model, length=length, context=indexed_tokens, num_samples=num_samples,device=self.device)
        #return self.tokenizer.decode(
        #    output[0, 0:].tolist(), clean_up_tokenization_spaces=True, skip_special_tokens=True
        #)
        input_ids = torch.tensor(self.tokenizer.encode(prefix), device=self.device).unsqueeze(0)
        outputs = self.model.generate(max_length=length, num_beams=5, input_ids=input_ids, bos_token_id=self.tokenizer.bos_token_id, eos_token_ids=self.tokenizer.eos_token_id, num_return_sequences=num_samples)
        result = []
        for i in range(num_samples):
            text = self.tokenizer.decode(outputs[i], skip_special_tokens=True)
            result.append(text)
            print(text)
        return result

    def generate_text(self, prefix, length):
        texts = self.generate_texts(prefix, length, 1)
        if (len(texts[0]) > len(prefix)):
            return texts[0][len(prefix):]
        else:
            return ""

    def _score_probability(self, sentence):
        # https://github.com/huggingface/transformers/issues/473
        tokenize_input = self.tokenizer.tokenize(sentence)
        tensor_input = torch.tensor([self.tokenizer.convert_tokens_to_ids(tokenize_input)])
        tensor_input = tensor_input.to(self.device)
        outputs = self.model(tensor_input, labels=tensor_input)
        loss, _ = outputs[:2]
        return math.exp(loss)

    def score_probability(self, sentence):
        input_ids = torch.tensor([self.tokenizer.encode(sentence)])
        input_ids = input_ids.to(self.device)
        
        prob = 0.0
        with torch.no_grad():
            index=0
            outputs = self.model(input_ids=input_ids)
            logits = outputs[0][0]
            probs = torch.softmax(logits, 1)
            for index in range(0, len(input_ids[0])):
                token_id = input_ids[0][index]
                probability = probs[index - 1][token_id].item()
                #print(f"Probability for the token \"{tokenizer.decode(token_id.item())}\" is {probability}")
                prob += probability
        #print("\n")   
        return probability

    #def predict(self, payload):
    #    indexed_tokens = self.tokenizer.encode(payload["text"])
    #    output = sample_sequence(self.model, self.num_words, indexed_tokens, device=self.device)
    #    return self.tokenizer.decode(
    #        output[0, 0:].tolist(), clean_up_tokenization_spaces=True, skip_special_tokens=True
    #    )