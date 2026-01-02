"""
Test file for the web scraper tool and MCP server.
"""

from web_scraper import get_page_content, count_word_on_page


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


if __name__ == "__main__":
    print("=" * 50)
    print("Running tests...")
    print("=" * 50)
    
    print("\nTest 1: get_page_content")
    print("-" * 30)
    test_get_page_content()
    
    print("\nTest 2: count_word_on_datatalks")
    print("-" * 30)
    count = test_count_word_on_datatalks()
    
    print("\n" + "=" * 50)
    print("All tests passed!")
    print("=" * 50)
