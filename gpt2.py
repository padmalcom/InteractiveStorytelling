from __future__ import absolute_import, division, print_function, unicode_literals

from tqdm import trange
import torch
import torch.nn.functional as F
import numpy as np
from transformers import GPT2Config
from transformers import AutoModelWithLMHead, AutoTokenizer
import math

class GPT2:

    def set_seed(self, seed, n_gpu):
        np.random.seed(seed)
        torch.manual_seed(seed)
        if n_gpu > 0:
            torch.cuda.manual_seed_all(seed)

    def _top_k_top_p_filtering(self, logits):
        top_k = 0
        top_p = 0.9
        filter_value=-float('Inf')
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

            # scatter sorted tensors to original indexing
            indices_to_remove = sorted_indices_to_remove.scatter(dim=1, index=sorted_indices, src=sorted_indices_to_remove)
            logits[indices_to_remove] = filter_value
        return logits

    def __sample_sequences__(self, model, length, context, num_samples):
        context = torch.tensor(context, dtype=torch.long, device=self.device)
        context = context.unsqueeze(0).repeat(num_samples, 1)
        generated = context
        result = []
        with torch.no_grad():
            for _ in trange(length):

                inputs = {'input_ids': generated}

                outputs = model(**inputs)  # Note: we could also use 'past' with GPT-2/Transfo-XL/XLNet/CTRL (cached hidden-states)
                next_token_logits = outputs[0][:, -1, :]

                # repetition penalty from CTRL (https://arxiv.org/abs/1909.05858)
                for i in range(num_samples):
                    for _ in set(generated[i].tolist()):
                        next_token_logits[i, _] /= 1.0
                    
                filtered_logits = self._top_k_top_p_filtering(next_token_logits)
                if self.temperature == 0: # greedy sampling:
                    next_token = torch.argmax(filtered_logits, dim=-1).unsqueeze(-1)
                else:
                    next_token = torch.multinomial(F.softmax(filtered_logits, dim=-1), num_samples=1)
                generated = torch.cat((generated, next_token), dim=1)
                result.append(generated)
        return result

    def __init__(self, model_scale=0, dummy=False):
        if not dummy:
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            self.n_gpu = torch.cuda.device_count()
            self.set_seed(42, self.n_gpu)
            self.num_samples = 1
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

            #add pad token
            self.tokenizer.pad_token = '<PAD>'
            self.model.resize_token_embeddings(len(self.tokenizer))
            
            self.model.to(self.device)
            self.model.eval()
            self.temperature = 1.0
            self.is_dummy = False
        else:
            self.is_dummy = True

    def generate_texts(self, prefix, length, num_samples):

        if self.is_dummy:
            return ["This is a dummy text."]

        context_tokens = self.tokenizer.encode(prefix, add_special_tokens=False)

        out = self.__sample_sequences__(model=self.model, context=context_tokens, length=length, num_samples=num_samples)

        for t in out:
            t = t[:, len(context_tokens):].tolist()
            result = []
            for o in t:
                text = self.tokenizer.decode(o, clean_up_tokenization_spaces=True)
                result.append(text)

        return result

    def generate_text(self, prefix, length):
        texts = self.generate_texts(prefix, length, 1)
        if (len(texts) > 0):
            return texts[0]
        else:
            return ""

    # smaller result is more probable
    def score_probability(self, sentence):
        # https://github.com/huggingface/transformers/issues/1009
        """tokenize_input = self.tokenizer.tokenize(sentence)
        tensor_input = torch.tensor([ [self.tokenizer.eos_token_id]  +  self.tokenizer.convert_tokens_to_ids(tokenize_input)])
        tensor_input = tensor_input.to(self.device)
        with torch.no_grad():
            outputs = self.model(tensor_input, labels=tensor_input)
            _, logits = outputs[:2] # first parameter is loss

        lp = 0.0
        for i in range(len(tokenize_input)):
            masked_index = i
            predicted_score = logits[0, masked_index].cpu()
            #predicted_prob = F.softmax(np.array(predicted_score))
            predicted_prob = F.softmax(predicted_score)
            predicted_prob = np.array(predicted_prob)
            lp += np.log(predicted_prob[self.tokenizer.convert_tokens_to_ids([tokenize_input[i]])[0]])
        return lp """

        # https://github.com/huggingface/transformers/issues/473
        tokenize_input = self.tokenizer.tokenize(sentence)
        tensor_input = torch.tensor([self.tokenizer.convert_tokens_to_ids(tokenize_input)])
        tensor_input = tensor_input.to(self.device)
        outputs = self.model(tensor_input, labels=tensor_input)
        loss, _ = outputs[:2]
        return math.exp(loss)