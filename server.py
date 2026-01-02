"""
MCP Server for web scraping tool using FastMCP.
Exposes the web scraping functions as MCP tools.
"""

from fastmcp import FastMCP
from web_scraper import get_page_content, count_word_on_page

# Create the MCP server
mcp = FastMCP("Web Scraper MCP Server")


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


if __name__ == "__main__":
    mcp.run()
