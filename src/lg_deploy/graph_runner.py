"""
GraphRunner for executing LangGraph agents.

This module provides a GraphRunner class that compiles and executes
LangGraph workflows. It serves as the bridge between the deployment
system and the LangGraph agent.
"""

import logging
from typing import Any, Dict
from langgraph.graph.state import CompiledStateGraph

from langgraph_agent.graph import create_graph


logger = logging.getLogger('lg_deploy.graph_runner')


class GraphRunner:
    """
    Executes LangGraph workflows.
    
    This class is responsible for:
    - Compiling the LangGraph agent
    - Running executions with provided input state
    - Returning results from the graph execution
    """
    
    def __init__(self):
        """Initialize the GraphRunner by compiling the graph."""
        self._graph: CompiledStateGraph = create_graph().compile()
        logger.info("GraphRunner initialized with compiled graph")
    
    async def run(self, input_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the graph with the provided input state.
        
        Args:
            input_state: A dictionary containing the initial state for the graph.
                        For the default agent, this should include 'topic'.
        
        Returns:
            A dictionary containing the final state after graph execution.
        
        Raises:
            Exception: If graph execution fails.
        """
        logger.info(f"Starting graph execution with input: {input_state}")
        
        try:
            # Execute the compiled graph
            result = await self._graph.ainvoke(input_state)
            
            logger.info(f"Graph execution completed with result: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Graph execution failed: {e}")
            raise
    
    def run_sync(self, input_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the graph synchronously (for testing).
        
        Args:
            input_state: A dictionary containing the initial state for the graph.
        
        Returns:
            A dictionary containing the final state after graph execution.
        """
        logger.info(f"Starting synchronous graph execution with input: {input_state}")
        
        try:
            # Execute the compiled graph synchronously
            result = self._graph.invoke(input_state)
            
            logger.info(f"Synchronous graph execution completed with result: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Synchronous graph execution failed: {e}")
            raise
