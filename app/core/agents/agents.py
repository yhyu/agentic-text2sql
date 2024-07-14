import json
import os
from typing import TypedDict, List

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AnyMessage

from app.core.tools.semantic_search_tools import SemanticSearchTool

class AgentState(TypedDict):
    level: int
    question: List[str]
    table_schemas: List[str]
    database: List[str]
    sql: List[str]
    reflect: List[str]
    accepted: List[str]
    messages: List[List[AnyMessage]]
    revision: int
    max_revision: int


class Agent():
    def __init__(
            self, config_file: str = os.path.join(os.path.dirname(__file__), 'agents.json')) -> None:
        with open(config_file) as f:
            self.agent_config = json.load(f)
        self.llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
        self.semantic_search = SemanticSearchTool(n_results=10)

    def search_engineer_node(self, state: AgentState):
        current_level = state['level']
        candidates = self.semantic_search(state['question'][current_level])
        role_prompt = self.agent_config['search_engineer']
        messages = [
            SystemMessage(content=role_prompt['system']),
            HumanMessage(
                content=f"Based on the following candidate database/table schemas:\n{candidates}\n\n"
                f"Find the relevant database/table schemas to answer the question: {state['question'][current_level]}\n\n"
                f"{role_prompt['expected_output']}")
        ]
        response = self.llm.invoke(messages)
        json_output = json.loads(response.content)

        tables = state['table_schemas'].copy()
        if len(tables) > current_level:
            tables[current_level] = json_output['table_schemas']
        else:
            tables.append(json_output['table_schemas'])

        database = state['database'].copy()
        if len(database) > current_level:
            database[current_level] = json_output['database']
        else:
            database.append(json_output['database'])
        return {"table_schemas": tables, "database": database}

    def senior_sql_writer_node(self, state: AgentState):
        current_level = state['level']
        role_prompt = self.agent_config['senior_sql_writer']
        instruction = f"Based on the following database/table schemas:\n{state['table_schemas'][current_level]}\n\n"
        if len(state['reflect']) > 0:
            instruction += f"Also reflect on these feedbacks:\n{'\n'.join(state['reflect'])}\n\n"
        instruction += f"Write a SQL script to answer the question: {state['question'][current_level]}\n\n{role_prompt['expected_output']}"
        human_message = HumanMessage(content=instruction)
        messages = [SystemMessage(content=role_prompt['system'])]
        for m in state['messages']:
            messages += m
        messages.append(human_message)
        response = self.llm.invoke(messages)
        sqls = state['sql'].copy()
        if len(sqls) > current_level:
            sqls[current_level] = response.content
        else:
            sqls.append(response.content)
    
        history = state['messages'].copy()
        if len(history) > current_level:
            history[current_level][1] = response
        else:
            history.append([human_message, response])
        return {
            "sql": sqls,
            "revision": state['revision']+1,
            "messages": history
        }

    def senior_qa_engineer_node(self, state: AgentState):
        current_level = state['level']
        role_prompt = self.agent_config['senior_qa_engineer']
        messages = [
            SystemMessage(content=role_prompt['system']), 
            HumanMessage(
                content=f"Based on the following database/table schemas:\n{state['table_schemas'][current_level]}\n\n"
                f"And the sql script:\n{state['sql']}\n\n"
                f"Verify the sql script to check if it can complete the task: {state['question'][current_level]}\n\n"
                f"{role_prompt['expected_output']}")
        ]
        response = self.llm.invoke(messages)
        accepted = state['accepted'].copy()
        accepted[current_level] = 'ACCEPTED' in response.content.upper()
        return {"accepted": accepted}

    def chief_dba_node(self, state: AgentState):
        current_level = state['level']
        role_prompt = self.agent_config['chief_dba']
        messages = [
            SystemMessage(content=role_prompt['system']), 
            HumanMessage(
                content=f"Based on the following database/table schemas:\n{state['table_schemas'][current_level]}\n\n"
                f"And the imperfect sql script:\n{state['sql'][current_level]}\n\n"
                f"Provide the usefule and detail recommendation to help the sql writer complete the task: {state['question'][current_level]}\n\n"
                f"{role_prompt['expected_output']}")
        ]
        response = self.llm.invoke(messages)
        reflect = state['reflect'].copy()
        reflect.append(response.content)
        return {"reflect": reflect}

    def search_rewriter_node(self, state: AgentState):
        role_prompt = self.agent_config['search_rewriter']
        messages = [
            SystemMessage(content=role_prompt['system']), 
            HumanMessage(
                content=f"Based on the following previous search queries:\n{'\n'.join(state['question'])}\n\n"
                f"Rewrite the following new search query so that search engine can understand its intention without previous queries:\n"
                f"{state['question'][-1]}\n\n"
                f"{role_prompt['expected_output']}")
        ]
        response = self.llm.invoke(messages)
        questions = state['question'].copy()
        questions[-1] = response.content
        return {"question": questions}

    def user_proxy_node(self, state: AgentState):
        accepted = state['accepted'].copy()
        accepted.append(False)
        return {
            'level': state['level'] + 1,
            'revision': 0,
            'reflect': [],
            'accepted': accepted
        }
