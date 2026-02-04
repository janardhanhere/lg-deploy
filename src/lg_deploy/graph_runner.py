"""
GraphRunner for executing LangGraph agents.

This module provides a GraphRunner class that compiles and executes
LangGraph workflows. It serves as the bridge between the deployment
system and the LangGraph agent.

Supports multiple streaming modes:
- stream_mode="values": Full state after each node
- stream_mode="updates": Only state updates per node
- stream_mode="messages": LLM message chunks
- astream_events: All events with metadata
"""

import logging
import uuid
from typing import Any, Dict, AsyncIterator, Literal
from langgraph.graph.state import CompiledStateGraph
from langgraph.checkpoint.memory import MemorySaver

from langgraph_agent.graph import create_graph


logger = logging.getLogger('lg_deploy.graph_runner')

StreamMode = Literal["values", "updates", "messages"]


class GraphRunner:
    """
    Executes LangGraph workflows.
    
    This class is responsible for:
    - Compiling the LangGraph agent
    - Running executions with provided input state
    - Supporting multiple streaming modes
    - Managing thread-based memory with checkpointers
    
    Attributes:
        checkpointer: Memory saver for thread-based persistence.
        _graph: Compiled LangGraph state machine.
    """
    
    def __init__(self, use_memory_checkpointer: bool = True):
        """
        Initialize the GraphRunner by compiling the graph.
        
        Args:
            use_memory_checkpointer: If True, uses in-memory checkpointer for
                                     thread-based state persistence. Set to False
                                     for stateless operations.
        """
        self._checkpointer = None
        if use_memory_checkpointer:
            self._checkpointer = MemorySaver()
            logger.info("GraphRunner initialized with MemorySaver checkpointer")
        else:
            logger.info("GraphRunner initialized without checkpointer (stateless)")
        
        self._graph: CompiledStateGraph = create_graph().compile(
            checkpointer=self._checkpointer
        )
        logger.info("GraphRunner initialized with compiled graph")
    
    async def run(
        self, 
        input_state: Dict[str, Any],
        thread_id: str | None = None
    ) -> Dict[str, Any]:
        """
        Execute the graph with the provided input state (non-streaming).
        
        Args:
            input_state: A dictionary containing the initial state for the graph.
                        For the default agent, this should include 'topic'.
            thread_id: Optional thread ID for stateful execution. If provided,
                      the graph will resume from the previous state of this thread.
                      If not provided, a new thread_id will be auto-generated.
        
        Returns:
            A dictionary containing the final state after graph execution.
        
        Raises:
            Exception: If graph execution fails.
        """
        config = self._make_config(thread_id)
        logger.info(f"Starting graph execution with input: {input_state}, thread_id: {thread_id}")
        
        try:
            result = await self._graph.ainvoke(input_state, config=config)
            logger.info(f"Graph execution completed with result: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Graph execution failed: {e}")
            raise
    
    def run_sync(
        self, 
        input_state: Dict[str, Any],
        thread_id: str | None = None
    ) -> Dict[str, Any]:
        """
        Execute the graph synchronously (for testing).
        
        Args:
            input_state: A dictionary containing the initial state for the graph.
            thread_id: Optional thread ID for stateful execution.
                      If not provided, a new thread_id will be auto-generated.
        
        Returns:
            A dictionary containing the final state after graph execution.
        """
        config = self._make_config(thread_id)
        logger.info(f"Starting synchronous graph execution with input: {input_state}")
        
        try:
            result = self._graph.invoke(input_state, config=config)
            logger.info(f"Synchronous graph execution completed with result: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Synchronous graph execution failed: {e}")
            raise
    
    async def astream(
        self,
        input_state: Dict[str, Any],
        thread_id: str | None = None,
        stream_mode: StreamMode = "values"
    ) -> AsyncIterator[Dict[str, Any]]:
        """
        Stream graph execution with the specified stream mode.
        
        Args:
            input_state: A dictionary containing the initial state for the graph.
            thread_id: Optional thread ID for stateful execution.
                      If not provided, a new thread_id will be auto-generated.
            stream_mode: Streaming mode:
                - "values": Full state after each node completion
                - "updates": Only state updates (changed values) per node
                - "messages": LLM message chunks
        
        Yields:
            A dictionary containing the streamed output based on stream_mode.
        
        Raises:
            Exception: If graph execution fails.
        """
        config = self._make_config(thread_id)
        logger.info(f"Starting streaming execution with input: {input_state}, stream_mode: {stream_mode}")
        
        try:
            async for chunk in self._graph.astream(input_state, config=config, stream_mode=stream_mode):
                yield chunk
        except Exception as e:
            logger.error(f"Streaming execution failed: {e}")
            raise
    
    async def astream_events(
        self,
        input_state: Dict[str, Any],
        thread_id: str | None = None,
        version: Literal["v1", "v2"] = "v2"
    ) -> AsyncIterator[Dict[str, Any]]:
        """
        Stream all graph events with full metadata.
        
        This is useful for debugging, logging, and custom event handling.
        
        Args:
            input_state: A dictionary containing the initial state for the graph.
            thread_id: Optional thread ID for stateful execution.
                      If not provided, a new thread_id will be auto-generated.
            version: Event format version. Use "v2" for latest format.
        
        Yields:
            A dictionary containing event data with metadata.
        
        Raises:
            Exception: If graph execution fails.
        """
        config = self._make_config(thread_id)
        logger.info(f"Starting event streaming with input: {input_state}, version: {version}")
        
        try:
            async for chunk in self._graph.astream_events(input_state, config=config, version=version):
                yield chunk
        except Exception as e:
            logger.error(f"Event streaming failed: {e}")
            raise
    
    def get_state(self, thread_id: str) -> Dict[str, Any] | None:
        """
        Get the current state of a thread.
        
        Args:
            thread_id: The thread ID to get state for.
        
        Returns:
            The current state of the thread, or None if not found.
        """
        if not self._checkpointer:
            logger.warning("Cannot get state: no checkpointer configured")
            return None
        
        config = self._make_config(thread_id)
        try:
            state = self._graph.get_state(config)
            return state.values if state else None
        except Exception as e:
            logger.error(f"Failed to get state for thread {thread_id}: {e}")
            return None
    
    def delete_thread(self, thread_id: str) -> bool:
        """
        Delete all state for a thread.
        
        Args:
            thread_id: The thread ID to delete.
        
        Returns:
            True if deletion was successful, False otherwise.
        """
        if not self._checkpointer:
            logger.warning("Cannot delete thread: no checkpointer configured")
            return False
        
        try:
            self._checkpointer.delete_thread(thread_id)
            logger.info(f"Deleted thread: {thread_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete thread {thread_id}: {e}")
            return False
    
    def _make_config(self, thread_id: str | None) -> Dict[str, Any]:
        """
        Create a configuration dictionary for graph execution.
        
        When using a checkpointer, a thread_id is required. If not provided,
        one will be auto-generated.
        
        Args:
            thread_id: Optional thread ID.
        
        Returns:
            A configuration dictionary for the graph.
        """
        # Ensure we have a thread_id for checkpointer compatibility
        if thread_id is None:
            thread_id = f"thread_{uuid.uuid4().hex[:8]}"
        
        return {"configurable": {"thread_id": thread_id}}
