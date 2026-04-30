"""Policy MCP client stub."""

from tools.rag_retriever import retrieve_policy


class PolicyMCPClient:
    def retrieve_policy(self, query: str) -> list[str]:
        return retrieve_policy(query)
