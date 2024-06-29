from typing import Union

import numpy as np
import torch
import torch.nn.functional as F
from transformers import AutoModel, AutoTokenizer

class EmbeddingModel():
    def __init__(self, model_name: str = 'Alibaba-NLP/gte-large-en-v1.5') -> None:
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name, trust_remote_code=True)

    def get_embedding(self, batch_text: Union[str, list]) -> np.ndarray:
        if not isinstance(batch_text, list):
            batch_text = [batch_text]
        batch_inputs = self.tokenizer(
            batch_text,
            max_length=8192,
            padding='longest',
            truncation=True,
            return_tensors='pt'
        )
        with torch.no_grad():
            outputs = self.model(**batch_inputs)
        embeddings = outputs.last_hidden_state[:, 0]
        embeddings = F.normalize(embeddings, p=2, dim=1)
        return embeddings.numpy()
