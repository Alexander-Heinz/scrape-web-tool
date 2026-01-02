"""
Test file for the web scraper tool.
"""

from web_scraper import get_page_content


def test_get_page_content():
    """Test that get_page_content returns more than 1000 characters for the minsearch repo."""
    url = "https://github.com/alexeygrigorev/minsearch"
    content = get_page_content(url)
    
    print(f"Retrieved {len(content)} characters from {url}")
    
    assert len(content) > 1000, f"Expected more than 1000 characters, got {len(content)}"
    print("✓ Test passed: Content length is greater than 1000 characters")
    
    return content


if __name__ == "__main__":
    content = test_get_page_content()
    print(f"\nTotal characters returned: {len(content)}")
