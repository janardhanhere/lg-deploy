#this is where you will write your langgraph agent code

#file structure
src/
  langgraph_agent/
    __init__.py
    agent.py --the main agent file
    .env.example -> .env #rename this file to .env when setting up your environment
    utils/
      __init__.py
      nodes.py -> utils for node operations
      state.py -> utils for state management
      tools.py -> utils for tool integrations
    tests/
      __init__.py
      README.md


