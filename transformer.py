# Implementation based on Andrej Karpathy repo https://github.com/karpathy/nanoGPT and
# his youtube video https://www.youtube.com/watch?v=kCc8FmEb1nY


import torch
import torch.nn as nn
import torch.nn.functional as F
from dataclasses import dataclass
import numpy as np
import json

# @dataclass
# class Config:
#     """Contains all hyperparameters"""
#     batch_size: int # how many independent sequences will we process in parallel
#     block_size: int # the maximum context length for predictions
#     max_iters: int
#     eval_interval: int
#     learning_rate: float
#     device: str
#     eval_iters: int
#     n_embed: int
#     n_head: int
#     n_layer: int
#     dropout: float

@dataclass
class BigConfig():
    batch_size: int = 64
    block_size: int = 256
    max_iters: int = 5000
    eval_interval: int = 500
    learning_rate: float = 3e-4
    device: str = 'cuda' if torch.cuda.is_available() else 'cpu'
    eval_iters: int = 200
    n_embed: int = 384
    n_head: int = 6
    n_layer: int = 6
    dropout: float = 0.2
    bias = False

@dataclass
class Config():
    batch_size: int = 32
    block_size: int = 8
    max_iters: int = 5000
    eval_interval: int = 500
    learning_rate: float = 1e-3
    device: str = 'cuda' if torch.cuda.is_available() else 'cpu'
    eval_iters: int = 200
    n_embed: int = 32
    n_head: int = 2
    n_layer: int = 4
    dropout: float = 0.2
    bias = False

torch.manual_seed(1337)

file_path = 'dataset.json'

# Open the file and load its contents
with open(file_path, 'r') as json_file:
    # Read the file content
    file_content = json_file.read()

    # Split the content by newline to get individual JSON objects
    json_objects = file_content.split('\n')

data = []
# Process each JSON object
for json_object in json_objects:
    if json_object.strip() == '':
        continue  # Skip empty lines
    
    # Parse the JSON object
    data.append(json.loads(json_object))

X = []

for i in data:
    flatten_matrix = np.array(i['matrix']).flatten().tolist()
    X.append(i['vector'] + flatten_matrix)
    # Y.append(np.array(i['matrix']).flatten())
print('mirame', X[0:10])
# Here are all the unique characters that occur in the text 
# chars = sorted(list(set(text)))
vocab_size = len(data[0]['vector'] + data[0]['matrix'])
# create a mapping from characters to integers and vice versa
# stoi = {ch:i for i, ch in enumerate(chars)}
# itos = {i:ch for i, ch in enumerate(chars)}

# encode = lambda s: [stoi[c] for c in s] # convert string to list of integers
# decode = lambda l: ''.join([itos[i] for i in l]) # convert list of integers to string

# train and test splits 
data = torch.tensor(X, dtype=torch.long)
n = int(0.9*len(data)) # first 90% will be train, rest val
train_data, val_data = data[:n], data[n:]

# data loading
def get_batch(split, config):
    # generate a small batch of data of inputs x and targets y
    data = train_data if split == 'train' else val_data
    # print(len(data) - config.block_size,'1ro')
    # print(config.batch_size,'2do')

    ix = torch.randint(len(data) - config.block_size, (config.batch_size),)
    x = torch.stack([data[i:i+config.block_size] for i in ix])
    y = torch.stack([data[i+1:i+config.block_size+1] for i in ix])
    x, y = x.to(config.device), y.to(config.device)
    return x, y

@torch.no_grad()
def estimate_loss(config, model):
    out = {}
    model.eval()
    for split in ['train', 'val']:
        losses = torch.zeros(config.eval_iters)
        for k in range(config.eval_iters):
            X, Y = get_batch(split, config)
            logits, loss = model(X, Y)
            losses[k] = loss.item()
        out[split] = losses.mean()
    model.train()
    return out

class Head(nn.Module):
    """ One Head of self-attention """

    def __init__(self, config: Config, head_size):
        super().__init__()
        self.key = nn.Linear(config.n_embed, head_size, bias=config.bias)
        self.query = nn.Linear(config.n_embed, head_size, bias=config.bias)
        self.value = nn.Linear(config.n_embed, head_size, bias=config.bias)
        self.dropout = nn.Dropout(config.dropout)
        self.flash_attention_dropout = config.dropout
        self.flash = hasattr(torch.nn.functional, 'scaled_dot_product_attention')
        if not self.flash:
            print("WARNING: using slow attention. Flash Attention requires PyTorch >= 2.0")
            # causal mask to ensure that attention is only applied to the left in the input sequence
            self.register_buffer('tril', torch.tril(torch.ones(config.block_size, config.block_size)))

    def forward(self, x):
        B, T, C  = x.shape # batch size, sequence lenght, embedding dimensionality (n_embed)
        k = self.key(x)   # (B, T, C)
        q = self.query(x) # (B, T, C)
        v = self.value(x) # (B, T, C)
        # Compute attention scores ("affinities")
        
        if self.flash:
            # efficient attention using Flash Attention CUDA kernels
            out = torch.nn.functional.scaled_dot_product_attention(q, k, v, attn_mask=None, dropout_p=self.flash_attention_dropout if self.training else 0, is_causal=True)
        else:
            # manual implementation of attention
            weights = q @ k.transpose(-2, -1) * C**(-0.5) # (B, T, C) @ (B, C, T) -> (B, T, T)
            weights = weights.masked_fill(self.tril[:T, :T] == 0, float('-inf')) # (B, T, T)
            weights = F.softmax(weights, dim=-1) # (B, T, T)
            weights = self.dropout(weights) 
            # Perform the weighted aggregation of the values
            out = weights @ v # (B, T, T) @ (B, T, C) -> (B, T, C)

        return out

class MultiHeadAttention(nn.Module):
    """Multiple heads of self-attention in parallel"""

    def __init__(self, config: Config, head_size):
        super().__init__()
        self.heads = nn.ModuleList([Head(config, head_size) for _ in range(config.n_head)])
        self.proj = nn.Linear(config.n_embed, config.n_embed)
    
    def forward(self, x):
        out = torch.cat([h(x) for h in self.heads], dim=-1)
        out = self.proj(out)
        return out 

class FeedFoward(nn.Module):
    def __init__(self, config: Config):
        super().__init__()
        # GELU instead of RELU because RELU can suffer from "problems where significant 
        # amount of neuron in the network become zero and don’t practically do anything. 
        # GELU "is smoother near zero and "is differentiable in all ranges, 
        # and allows to have gradients(although small) in negative range" 
        self.net = nn.Sequential(
            nn.Linear(config.n_embed, 4 * config.n_embed, bias=config.bias),
            nn.GELU(),
            nn.Linear(4 * config.n_embed, config.n_embed, bias=config.bias),
            nn.Dropout(config.dropout)
        )

    def forward(self, x):
        return self.net(x)

class Block(nn.Module):
    """ Transformer block: communication followed by computation """

    def __init__(self, config):
        # n_embed: embedding dimension, n_head: the number of heads we'd like
        super().__init__()
        head_size = config.n_embed // config.n_head
        self.sa = MultiHeadAttention(config, head_size)
        self.ffwd = FeedFoward(config)
        self.ln1 = nn.LayerNorm(config.n_embed)
        self.ln2 = nn.LayerNorm(config.n_embed)

    def forward(self, x):
        # x + represents residual connections 
        x = x + self.sa(self.ln1(x))
        x = x + self.ffwd(self.ln2(x))
        return x

class Transformer(nn.Module):
    def __init__(self, config: Config):
        super().__init__()
        # each token directly reads off the logits for the next token from a lookup table
        self.token_embedding_table = nn.Embedding(vocab_size, config.n_embed)
        self.position_embedding_table = nn.Embedding(config.block_size, config.n_embed)
        self.blocks = nn.Sequential(*[Block(config) for _ in range(config.n_layer)])
        self.ln_f = nn.LayerNorm(config.n_embed) # final layer norm
        self.lm_head = nn.Linear(config.n_embed, vocab_size)
        self.config = config

    def forward(self, idx, targets=None):
        B, T = idx.shape

        # idx and targets are both (B, T) tensor of integers
        tok_emb = self.token_embedding_table(idx) # (B, T, C)
        pos_emb = self.position_embedding_table(torch.arange(T, device=idx.device)) # (T, C)
        x = tok_emb + pos_emb # (B, T, C)
        x = self.blocks(x) # (B, T, C)
        x = self.ln_f(x) # (B, T, C)
        # Logits are the raw predictions which come out of the last layer of the neural network.
        logits = self.lm_head(x) # (B, T, vocab_size)

        if targets is None:
            loss = None 
        else:
            B, T, C = logits.shape
            logits = logits.view(B*T, C)
            targets = targets.view(B*T)
            loss = F.cross_entropy(input=logits, target=targets)

        return logits, loss

    @torch.no_grad()
    def generate(self, idx, max_new_tokens):
        """
        Take a conditioning sequence of indices idx (LongTensor of shape (B,T)) and complete
        the sequence max_new_tokens times, feeding the predictions back into the model each time.
        Most likely you'll want to make sure to be in model.eval() mode of operation for this.
        """
        for _ in range(max_new_tokens):
            # if the sequence context is growing too long we must crop it at block_size
            idx_cond = idx if idx.size(1) <= self.config.block_size else idx[:, -self.config.block_size:]
            # forward the model to get the logits for the index in the sequence
            logits, loss = self(idx_cond)
            # pluck the logits at the final step
            logits = logits[:, -1, :]  # Becomes (B, C)
            # apply softmax to convert logits to (normalized) probabilities
            probs = F.softmax(logits, dim=-1)
            # sample from the distribution
            idx_next = torch.multinomial(probs, num_samples=1)
            # append sampled index to the running sequence
            idx = torch.cat((idx, idx_next), dim=1) # (B, T+1)
        return idx

config = Config()
print(config.device)
model = Transformer(config)
n = model.to(config.device)

# Create the optimizer
optimizer = torch.optim.Adam(model.parameters(), lr=config.learning_rate)

for iter in range(config.max_iters):
    # Every once in a while evaluate the loss on train and val sets
    if iter % config.eval_interval == 0 or iter == config.max_iters - 1:
        losses = estimate_loss(config, model)
        print(f"step {iter}: train loss {losses['train']:.4f}, val loss {losses['val']:.4f}") 
    
    # Sample a batch of data
    xb, yb = get_batch('train', config)

    # Evaluate the loss 
    logits, loss = model(xb, yb)
    optimizer.zero_grad(set_to_none=True)
    loss.backward()
    optimizer.step()

# Generate from the model
context = torch.zeros((1,1), dtype=torch.long, device=config.device)
# print(decode(n.generate(context, max_new_tokens=500)[0].tolist()))