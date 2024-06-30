# Agentic RAG for open domain text-to-query
The experiment try to answer open domain business questions described in natural language through SQL queries to retrieve data from business databases.

## Prerequisites
- The experiment leverage [CrewAI](https://www.crewai.com/) framework to build the agentic RAG pipeline.
- [Spider](https://yale-lily.github.io/spider) dataset is used to test the pipeline.
- [Chroma](https://www.trychroma.com/) is used as a vector database.
- Text embedding model: [gte-large-en-v1.5](https://huggingface.co/Alibaba-NLP/gte-large-en-v1.5). (Chroma also supports default built-in text embedding model which is [SentenceTransformer](https://www.sbert.net/) all-MiniLM-L6-v2 model.)
- LLM: OpenAI [gpt-3.5-turbo](https://platform.openai.com/docs/models/gpt-3-5-turbo)
- The experiment runs on CPU only, no GPU is required.

## Prepare experiment environment
Install packages.
```
pip install --no-cache-dir -r requirements.txt
```

Setup environment.
```
python setup_env.py
```

## Try it out
Try the [text2sql](https://github.com/yhyu/agentic-text2sql/blob/main/text2sql.ipynb) notebook.
