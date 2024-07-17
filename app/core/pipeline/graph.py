from typing import Any
from uuid import uuid4 as guid

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver

from app.core.agents.agents import Agent, AgentState
from app.core.configs.config import logger
from app.core.utils import Singleton


class Graph(metaclass=Singleton):

    graph = None
    builder = None
    agents = Agent()
    memory = SqliteSaver.from_conn_string(":memory:")
    thread_id: str = None

    def __init__(self) -> None:
        self.rebuild()

    def __call__(
            self, question: str, thread_id: str = None,
            max_revision: int = 2) -> Any:
        if thread_id:
            init_state = None
            thread = {"configurable": {"thread_id": thread_id}}
            if not self.graph.get_state(thread).next:
                return {
                    'thread_id': '',
                    'state': None
                }
            else:
                current_state = self.graph.get_state(thread).values
                current_state['question'].append(question.strip())
                self.graph.update_state(thread, current_state)
        else:
            thread_id = str(guid().hex)
            init_state = {
                'level': 0,
                'question': [question],
                'table_schemas': [],
                'database': [],
                'sql': [],
                'accepted': [False],
                'reflect': [],
                'messages': [],
                'revision': 0,
                'max_revision': max_revision,
            }
            thread = {"configurable": {"thread_id": thread_id}}

        for s in self.graph.stream(init_state, thread):
            logger.debug(s)
        return {
            'state': self.graph.get_state(thread).values,
            'thread_id': thread_id if self.graph.get_state(thread).next else ''
        }

    def build(self) -> None:
        # add nodes
        self.builder.add_node("search_engineer", self.agents.search_engineer_node)
        self.builder.add_node("sql_writer", self.agents.senior_sql_writer_node)
        self.builder.add_node("qa_engineer", self.agents.senior_qa_engineer_node)
        self.builder.add_node("chief_dba", self.agents.chief_dba_node)
        self.builder.add_node("user_proxy", self.agents.user_proxy_node)
        self.builder.add_node("search_rewriter", self.agents.search_rewriter_node)

        # add edges
        self.builder.add_edge("search_engineer", "sql_writer")
        self.builder.add_edge("sql_writer", "qa_engineer")
        self.builder.add_edge("chief_dba", "sql_writer")
        self.builder.add_edge("search_rewriter", "search_engineer")

        # add conditional edges
        self.builder.add_conditional_edges(
            "qa_engineer", 
            lambda state: 'continue' if state['accepted'][state['level']] == True or state['revision'] >= state['max_revision'] else 'reflect', 
            {'continue': 'user_proxy', 'reflect': 'chief_dba'}
        )
        self.builder.add_conditional_edges(
            "user_proxy", 
            lambda state: 'end' if len(state['question'][-1]) == 0 or 'exit' == state['question'][-1].lower() else 'explore', 
            {'end': END, 'explore': 'search_rewriter'}
        )

        # set entry point
        self.builder.set_entry_point("search_engineer")

        # compile graph
        self.graph = self.builder.compile(
            checkpointer=self.memory,
            interrupt_before=["user_proxy"],
        )

    def rebuild(self):
        self.builder = StateGraph(AgentState)
        self.build()