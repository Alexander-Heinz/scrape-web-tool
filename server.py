"""
MCP Server for web scraping and documentation search.
Exposes web scraping and search functions as MCP tools.
"""

from fastmcp import FastMCP
from web_scraper import get_page_content, count_word_on_page
from search import search_github_docs

# Create the MCP server
mcp = FastMCP("Web Scraper and Documentation Search MCP Server")


@mcp.tool
def fetch_page(url: str) -> str:
    """
    Fetch the content of a web page in markdown format using Jina Reader.
    
    Args:
        url: The URL of the web page to fetch.
        
    Returns:
        The page content in markdown format.
    """
    return get_page_content(url)


@mcp.tool
def count_word(url: str, word: str) -> int:
    """
    Count how many times a specific word appears on a web page.
    
    Args:
        url: The URL of the web page to analyze.
        word: The word to count (case-insensitive).
        
    Returns:
        The number of times the word appears on the page.
    """
    return count_word_on_page(url, word)


@mcp.tool
def search_docs(github_url: str, query: str, num_results: int = 5) -> list[dict]:
    """
    Search documentation in any GitHub repository.
    
    Downloads the repository (if not cached), indexes all markdown files,
    and searches for relevant content.
    
    Args:
        github_url: GitHub repository URL (e.g., 'https://github.com/owner/repo' or 'owner/repo')
        query: The search query string.
        num_results: Number of results to return (default 5).
        
    Returns:
        List of matching documents with 'filename' and 'content' fields.
    """
    results = search_github_docs(github_url, query, num_results)
    # Return simplified results for better readability
    return [
        {
            "filename": doc["filename"],
            "content": doc["content"][:500] + "..." if len(doc["content"]) > 500 else doc["content"]
        }
        for doc in results
    ]


if __name__ == "__main__":
    mcp.run()
