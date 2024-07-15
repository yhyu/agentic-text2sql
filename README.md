# Agentic RAG for open domain text-to-query
The experiment try to answer open domain business questions described in natural language through SQL queries to retrieve data from business databases.

## Prerequisites
- The experiment leverage [CrewAI](https://www.crewai.com/), [AutoGen](https://microsoft.github.io/autogen/) and [LangChain - LangGraph](https://www.langchain.com/langgraph) frameworks to build the agentic RAG pipeline.
- [Spider](https://yale-lily.github.io/spider) dataset is used to test the pipeline.
- [Chroma](https://www.trychroma.com/) is used as a vector database.
- Text embedding model: [gte-large-en-v1.5](https://huggingface.co/Alibaba-NLP/gte-large-en-v1.5). (Chroma also supports default built-in text embedding model which is [SentenceTransformer](https://www.sbert.net/) all-MiniLM-L6-v2 model.)
- LLM: OpenAI [gpt-3.5-turbo](https://platform.openai.com/docs/models/gpt-3-5-turbo)
- The experiment runs on CPU only, no GPU is required.

## Prepare experiment environment
Install packages for CrewAI experiment.
```
pip install --no-cache-dir -r requirements/crewai.txt
```

Install packages for AutoGen experiment.
```
pip install --no-cache-dir -r requirements/autogen.txt
```

Install packages for LangGraph experiment.
```
pip install --no-cache-dir -r requirements/langgraph.txt
```

Setup environment.
```
python setup_env.py
```

## Try it out
* CrewAI: try [text2sql_crewai](https://github.com/yhyu/agentic-text2sql/blob/main/text2sql_crewai.ipynb) notebook.
* AutoGen: try [text2sql_autogen](https://github.com/yhyu/agentic-text2sql/blob/main/text2sql_autogen.ipynb) notebook.
* LangGraph: try [text2sql_langgraph](https://github.com/yhyu/agentic-text2sql/blob/main/text2sql_langgraph.ipynb) notebook.

## Mutli-turns Agentic RAG
The multi-turns experiment is served by [FastAPI](https://fastapi.tiangolo.com/), you can also use other framworks that you familiar with.  
Before you launch the service, install required packages:
```
pip install --no-cache-dir -r requirements/fastapi.txt
```

Run the command to start the multi-turns agentic RAG service:
```
chmod a+x run_multiturns.sh
export OPENAI_API_KEY="your-openai-api-key"
./run_multiturns.sh
```

### Multi-turns Request and Response
The multi-turns experiment is created using [LangGraph](https://www.langchain.com/langgraph) framework. Here is the graph looks like.  
[Multi-turns Agentic RAG](https://github.com/yhyu/agentic-text2sql/blob/main/graph.png?raw=true)
In the multi-turns agentic RAG, __session_id__ is used to track conversations. __session_id__ is created in the first response, succeeded requests have to use the same __session_id__ to identify the same conversation. For instance:  
First request:
```
curl -X POST  http://127.0.0.1:8000/v1/rag/query \
-H 'accept: application/json' \
-H 'Content-Type: application/json' \
-d '{
"request_id": "1234",
"query": "How many routes does American Airlines operate?"
}'
```
First response:
```json
{
    "request_id":"1234",
    "response_id":"c56f90ccf67544a4b25c8290432e90d0",
    "results":{
        "database":"flight_4",
        "sql":"SELECT COUNT(*) AS total_routes\nFROM routes\nWHERE alid = (SELECT alid FROM airlines WHERE name = 'American Airlines');",
        "value":[[2352]]
    },
    "session_id":"c56f90ccf67544a4b25c8290432e90d0"
}
```
Second request:
```
curl -X POST  http://127.0.0.1:8000/v1/rag/query \
-H 'accept: application/json' \
-H 'Content-Type: application/json' \
-d '{
"request_id": "2234",
"query": "How about Ryanair?",
"session_id": "c56f90ccf67544a4b25c8290432e90d0"
}'
```
Second response:
```json
{
    "request_id":"1234",
    "response_id":"361039f19e4d4b45957b0e2f413a1ba2",
    "results":{
        "database":"flight_4",
        "sql":"SELECT COUNT(*) AS total_routes\nFROM routes\nJOIN airlines ON routes.alid = airlines.alid\nWHERE airlines.name = 'Ryanair';",
        "value":[[2484]]
    },
    "session_id":"c56f90ccf67544a4b25c8290432e90d0"
}
```
Third request:
```
curl -X POST  http://127.0.0.1:8000/v1/rag/query \
-H 'accept: application/json' \
-H 'Content-Type: application/json' \
-d '{
"request_id": "3234",
"query": "What is the country of the former?",
"session_id": "c56f90ccf67544a4b25c8290432e90d0"
}'
```
Third response:
```json
{
    "request_id":"1234",
    "response_id":"259e86c55bee46c690a1c7b8d961d255",
    "results":{
        "database":"flight_4",
        "sql":"SELECT country\nFROM airlines\nWHERE name = 'American Airlines';",
        "value":[["United States"]]
    },
    "session_id":"c56f90ccf67544a4b25c8290432e90d0"
}
```