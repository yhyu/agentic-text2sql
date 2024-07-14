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
./run_multiturns.sh
```

### Multi-turns Request and Response
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
    "response_id":"e6e6526dc6024e9fb988898a56e9d3a6",
    "results":{
        "database":"flight_4",
        "sql":"SELECT COUNT(*) AS total_routes\nFROM routes\nWHERE alid = (SELECT alid FROM airlines WHERE name = 'American Airlines');"
    },
    "session_id":"fa9ddb1ee7c440318ab1bb25bf7999ee"
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
"session_id": "fa9ddb1ee7c440318ab1bb25bf7999ee"
}'
```
Second response:
```json
{
    "request_id":"2234",
    "response_id":"c8b4e665bf484389a81b6ee471d02bfc",
    "results":{
        "database":"flight_4","sql":
        "SELECT COUNT(*) AS total_routes\nFROM routes\nJOIN airlines ON routes.alid = airlines.alid\nWHERE airlines.name = 'Ryanair';"
    },
    "session_id":"fa9ddb1ee7c440318ab1bb25bf7999ee"
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
"session_id": "fa9ddb1ee7c440318ab1bb25bf7999ee"
}'
```
Third response:
```json
{
    "request_id":"3234",
    "response_id":"46b7b1df6eff494bb992955dd43657dd",
    "results":{
        "database":"flight_4",
        "sql":"SELECT country\nFROM airlines\nWHERE name = 'American Airlines';"
    },
    "session_id":"fa9ddb1ee7c440318ab1bb25bf7999ee"
}
```