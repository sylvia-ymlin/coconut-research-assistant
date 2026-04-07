"""LLM adapter for HelloAgents."""

from hello_agents import HelloAgentsLLM

LLMClient = HelloAgentsLLM


def create_llm_client(**kwargs) -> LLMClient:
    """Create the application LLM client."""

    return HelloAgentsLLM(**kwargs)
