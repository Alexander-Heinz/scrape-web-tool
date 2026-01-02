"""
Test file for the web scraper tool, MCP server, and LLM integration.
"""

import asyncio
import os
from web_scraper import get_page_content, count_word_on_page
from search import search_github_docs


def test_get_page_content():
    """Test that get_page_content returns more than 1000 characters for the minsearch repo."""
    url = "https://github.com/alexeygrigorev/minsearch"
    content = get_page_content(url)
    
    print(f"Retrieved {len(content)} characters from {url}")
    
    assert len(content) > 1000, f"Expected more than 1000 characters, got {len(content)}"
    print("✓ Test passed: Content length is greater than 1000 characters")
    
    return content


def test_count_word_on_datatalks():
    """Test that the word 'data' appears more than 50 times on datatalks.club."""
    url = "https://datatalks.club/"
    word = "data"
    
    count = count_word_on_page(url, word)
    
    print(f"Found {count} occurrences of '{word}' on {url}")
    
    assert count > 50, f"Expected more than 50 occurrences of '{word}', got {count}"
    print(f"✓ Test passed: '{word}' appears more than 50 times ({count} times)")
    
    return count


def test_search_returns_md_files():
    """Test that search returns results ending with .md or .mdx."""
    query = "demo"
    results = search_github_docs("https://github.com/jlowin/fastmcp", query)
    
    print(f"Search for '{query}' in FastMCP returned {len(results)} results")
    
    assert len(results) > 0, "Expected at least one search result"
    
    # Check that all results end with .md or .mdx
    for doc in results:
        filename = doc['filename']
        assert filename.endswith('.md') or filename.endswith('.mdx'), \
            f"Expected filename to end with .md or .mdx, got: {filename}"
        print(f"  - {filename}")
    
    print("✓ Test passed: All search results end with .md or .mdx")
    
    return results[0]['filename']


def test_search_any_github_repo():
    """Test that search works on any GitHub repository."""
    # Test with minsearch repo
    results = search_github_docs("alexeygrigorev/minsearch", "vector")
    
    print(f"Search for 'vector' in minsearch returned {len(results)} results")
    
    assert len(results) > 0, "Expected at least one search result"
    
    for doc in results:
        print(f"  - {doc['filename']}")
    
    print("✓ Test passed: Can search any GitHub repository")
    
    return results


async def test_mcp_tools_available():
    """Test that MCP tools are properly exposed."""
    from fastmcp import Client
    from server import mcp
    
    async with Client(mcp) as client:
        tools = await client.list_tools()
        tool_names = [t.name for t in tools]
        
        print(f"Available MCP tools: {tool_names}")
        
        assert "fetch_page" in tool_names, "fetch_page tool not found"
        assert "count_word" in tool_names, "count_word tool not found"
        assert "search_docs" in tool_names, "search_docs tool not found"
        
        print("✓ Test passed: All MCP tools are available")
        
        return tool_names


async def test_mcp_tool_call():
    """Test that MCP tools can be called correctly."""
    from fastmcp import Client
    from server import mcp
    
    async with Client(mcp) as client:
        # Test count_word tool
        result = await client.call_tool("count_word", {
            "url": "https://datatalks.club/",
            "word": "data"
        })
        
        # Extract the result
        count = None
        if hasattr(result, 'content') and result.content:
            for item in result.content:
                if hasattr(item, 'text'):
                    count = int(item.text)
                    break
        
        print(f"MCP count_word result: {count}")
        
        assert count is not None, "Could not get result from MCP tool"
        assert count > 50, f"Expected count > 50, got {count}"
        
        print("✓ Test passed: MCP tool call works correctly")
        
        return count


async def test_llm_integration():
    """Test the LLM integration with MCP tools."""
    api_key = os.environ.get("OPENAI_API_KEY")
    
    if not api_key:
        print("⚠ Skipping LLM test: OPENAI_API_KEY not set")
        return None
    
    from main import chat_with_assistant, get_openai_client
    
    openai_client = get_openai_client()
    
    # Test a simple query that should use a tool
    test_query = "How many times does the word 'data' appear on datatalks.club?"
    
    print(f"Testing LLM with query: '{test_query}'")
    
    response = await chat_with_assistant(test_query, openai_client)
    
    print(f"LLM Response: {response[:200]}..." if len(response) > 200 else f"LLM Response: {response}")
    
    # Check that response mentions a number (the count)
    assert any(char.isdigit() for char in response), "Expected LLM response to contain a number"
    
    print("✓ Test passed: LLM integration works correctly")
    
    return response


def run_sync_tests():
    """Run all synchronous tests."""
    print("=" * 50)
    print("Running synchronous tests...")
    print("=" * 50)
    
    print("\nTest 1: get_page_content")
    print("-" * 30)
    test_get_page_content()
    
    print("\nTest 2: count_word_on_datatalks")
    print("-" * 30)
    test_count_word_on_datatalks()
    
    print("\nTest 3: search_returns_md_files")
    print("-" * 30)
    test_search_returns_md_files()
    
    print("\nTest 4: search_any_github_repo")
    print("-" * 30)
    test_search_any_github_repo()


async def run_async_tests():
    """Run all async tests."""
    print("\n" + "=" * 50)
    print("Running async tests...")
    print("=" * 50)
    
    print("\nTest 5: mcp_tools_available")
    print("-" * 30)
    await test_mcp_tools_available()
    
    print("\nTest 6: mcp_tool_call")
    print("-" * 30)
    await test_mcp_tool_call()
    
    print("\nTest 7: llm_integration")
    print("-" * 30)
    await test_llm_integration()


if __name__ == "__main__":
    run_sync_tests()
    asyncio.run(run_async_tests())
    
    print("\n" + "=" * 50)
    print("All tests completed!")
    print("=" * 50)
