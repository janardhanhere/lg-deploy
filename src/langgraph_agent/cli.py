#!/usr/bin/env python
"""
CLI tool to test the LangGraph agent.

Usage:
    python -m langgraph_agent.cli topic=AI
    python -m langgraph_agent.cli topic=AI stream
    python -m langgraph_agent.cli topic=cats
"""

import sys
import os

# Add src to path for imports
src_path = os.path.join(os.path.dirname(__file__), "..")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

import argparse
import asyncio
import json
import logging

from langgraph_agent.graph import create_graph

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s"
)
logger = logging.getLogger("langgraph_agent.cli")


def parse_input_from_args(args: list) -> dict:
    """Parse input from positional arguments like key=value."""
    input_data = {}
    for arg in args:
        if "=" in arg:
            key, value = arg.split("=", 1)
            input_data[key.strip()] = value.strip()
    return input_data


async def test_invoke(input_data: dict):
    """Test graph invocation."""
    logger.info("Creating graph...")
    builder = create_graph()
    graph = builder.compile()  # Compile the graph
    
    logger.info(f"Invoking graph with input: {input_data}")
    result = await graph.ainvoke(input_data)
    
    logger.info("=" * 50)
    logger.info("RESULT:")
    logger.info(json.dumps(result, indent=2))
    logger.info("=" * 50)
    
    return result


async def test_stream(input_data: dict):
    """Test graph streaming."""
    logger.info("Creating graph...")
    builder = create_graph()
    graph = builder.compile()  # Compile the graph
    
    logger.info(f"Streaming graph with input: {input_data}")
    logger.info("=" * 50)
    
    async for mode, chunk in graph.astream(input_data, stream_mode="updates"):
        logger.info(f"[{mode}]")
        logger.info(json.dumps(chunk, indent=2))
        logger.info("-" * 30)
    
    logger.info("=" * 50)
    logger.info("Stream complete")


async def main():
    parser = argparse.ArgumentParser(
        description="CLI tool to test the LangGraph agent"
    )
    parser.add_argument(
        "inputs",
        nargs="*",
        help="Input key=value pairs, e.g., topic=AI"
    )
    parser.add_argument(
        "--stream", "-s",
        action="store_true",
        help="Enable streaming mode"
    )
    parser.add_argument(
        "--json", "-j",
        help="Input as JSON string"
    )
    
    args = parser.parse_args()
    
    if args.json:
        try:
            input_data = json.loads(args.json)
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON: {e}")
            sys.exit(1)
    else:
        input_data = parse_input_from_args(args.inputs)
    
    if not input_data:
        logger.info("Usage: python -m langgraph_agent.cli topic=AI")
        logger.info("       python -m langgraph_agent.cli topic=AI stream")
        sys.exit(0)
    
    if args.stream:
        await test_stream(input_data)
    else:
        await test_invoke(input_data)


if __name__ == "__main__":
    asyncio.run(main())
