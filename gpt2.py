from transformers import GPT2LMHeadModel, GPT2Tokenizer
import torch
import numpy as np
from tqdm import trange

#from transformers import GPT2Config, OpenAIGPTConfig, XLNetConfig, TransfoXLConfig, XLMConfig, CTRLConfig

class GPT2:

    def __init__(self):
        # parameters
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.n_gpu = torch.cuda.device_count()
        self.seed = 42
        self.stop_token = None
        self.num_samples = 1
        self.sample_length = 200

        # ??? parameters
        self.temperature = 1.0
        self.top_k = 0
        self.top_p = 0.9

        # set seed
        np.random.seed(self.seed)
        torch.manual_seed(self.seed)
        if self.n_gpu > 0:
            torch.cuda.manual_seed_all(self.seed)

        # models
        # ('gpt2', 'gpt2-medium', 'gpt2-large', 'distilgpt2', 'openai-gpt', 'xlnet-base-cased', 'xlnet-large-cased', 'transfo-xl-wt103', 'xlm-mlm-en-2048', 'xlm-mlm-ende-1024', 'xlm-mlm-enfr-1024', 'xlm-mlm-enro-1024', 'xlm-mlm-tlm-xnli15-1024', 'xlm-mlm-xnli15-1024', 'xlm-clm-enfr-1024', 'xlm-clm-ende-1024', 'xlm-mlm-17-1280', 'xlm-mlm-100-1280', 'ctrl')
        self.model = GPT2LMHeadModel.from_pretrained('gpt2')
        self.tokenizer = GPT2Tokenizer.from_pretrained('gpt2')
        self.model.to(self.device)
        self.model.eval()

    def generate(self, history, sample_length=100, num_samples=1):
        context = self.tokenizer.encode(history, add_special_tokens=False)

        # generator
        context = torch.tensor(context, dtype=torch.long, device=self.device)
        context = context.unsqueeze(0).repeat(num_samples, 1)
        generated = context
        with torch.no_grad():
            for _ in trange(sample_length):
                inputs = {'input_ids': generated}
                outputs = self.model(**inputs)  # Note: we could also use 'past' with GPT-2/Transfo-XL/XLNet/CTRL (cached hidden-states)
                next_token_logits = outputs[0][0, -1, :] / (self.temperature if self.temperature > 0 else 1.)

                # reptition penalty from CTRL (https://arxiv.org/abs/1909.05858)
                #for _ in set(generated.view(-1).tolist()):
                #    next_token_logits[_] /= repetition_penalty
                        
                filtered_logits = self.top_k_top_p_filtering(next_token_logits)
                if self.temperature == 0: #greedy sampling:
                    next_token = torch.argmax(filtered_logits).unsqueeze(0)
                else:
                    next_token = torch.multinomial(torch.nn.functional.softmax(filtered_logits, dim=-1), num_samples=1)
                generated = torch.cat((generated, next_token.unsqueeze(0)), dim=1)

        # print
        out = generated[0, len(context):].tolist()
        text = self.tokenizer.decode(out, clean_up_tokenization_spaces=True, skip_special_tokens=True)
        text = text[: text.find(self.stop_token) if self.stop_token else None]
        return text


    def top_k_top_p_filtering(self, logits, filter_value=-float('Inf')):
        assert logits.dim() == 1  # batch size 1 for now - could be updated for more but the code would be less clear
        new_top_k = min(self.top_k, logits.size(-1))  # Safety check
        if new_top_k > 0:
            # Remove all tokens with a probability less than the last token of the top-k
            indices_to_remove = logits < torch.topk(logits, new_top_k)[0][..., -1, None]
            logits[indices_to_remove] = filter_value

        if self.top_p > 0.0:
            sorted_logits, sorted_indices = torch.sort(logits, descending=True)
            cumulative_probs = torch.cumsum(torch.nn.functional.softmax(sorted_logits, dim=-1), dim=-1)

            # Remove tokens with cumulative probability above the threshold
            sorted_indices_to_remove = cumulative_probs > self.top_p
            # Shift the indices to the right to keep also the first token above the threshold
            sorted_indices_to_remove[..., 1:] = sorted_indices_to_remove[..., :-1].clone()
            sorted_indices_to_remove[..., 0] = 0

            indices_to_remove = sorted_indices[sorted_indices_to_remove]
            logits[indices_to_remove] = filter_value
        return logits





