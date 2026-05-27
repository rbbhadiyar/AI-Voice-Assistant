from langchain_tavily import TavilySearch

search_tool = TavilySearch(max_results=3)

def web_search(query: str) -> str:
    results = search_tool.invoke(query)
    if isinstance(results, dict) and "results" in results:
        return "\n".join([r["content"] for r in results["results"]])
    return str(results)
