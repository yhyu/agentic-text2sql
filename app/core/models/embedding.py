import os
from typing import Union

import numpy as np
import torch
import torch.nn.functional as F
from transformers import AutoModel, AutoTokenizer
from chromadb import Documents, EmbeddingFunction, Embeddings


class EmbeddingModel(EmbeddingFunction):
    model_name = os.environ.get('EMBEDDING_MODEL', 'Alibaba-NLP/gte-large-en-v1.5')
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModel.from_pretrained(model_name, trust_remote_code=True)

    def __call__(self, input: Documents) -> Embeddings:
        return self.get_embedding(input)

    def get_embedding(self, batch_text: Union[str, list], batch_size=32) -> np.ndarray:
        all_embeddings = None
        if not isinstance(batch_text, list):
            batch_text = [batch_text]
        for batch in range(0, len(batch_text), batch_size):
            batch_inputs = self.tokenizer(
                batch_text[batch:batch+batch_size],
                max_length=8192,
                padding='longest',
                truncation=True,
                return_tensors='pt'
            )
            with torch.no_grad():
                outputs = self.model(**batch_inputs)
            embeddings = outputs.last_hidden_state[:, 0]
            embeddings = F.normalize(embeddings, p=2, dim=1)
            if all_embeddings is None:
                all_embeddings = embeddings
            else:
                all_embeddings = torch.cat((all_embeddings, embeddings), axis=0)
        return all_embeddings.tolist()
