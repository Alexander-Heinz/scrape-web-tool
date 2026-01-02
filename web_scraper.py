"""
Web scraping tool using Jina Reader to get page content in markdown format.
"""

import requests


def get_page_content(url: str) -> str:
    """
    Download the content of any web page using Jina Reader.
    
    Jina Reader converts web pages to clean markdown by prepending r.jina.ai to the URL.
    
    Args:
        url: The URL of the web page to scrape.
        
    Returns:
        The page content in markdown format.
        
    Raises:
        requests.RequestException: If the request fails.
    """
    jina_url = f"https://r.jina.ai/{url}"
    response = requests.get(jina_url)
    response.raise_for_status()
    return response.text


def count_word_on_page(url: str, word: str) -> int:
    """
    Count how many times a specific word appears on a web page.
    
    Args:
        url: The URL of the web page to analyze.
        word: The word to count (case-insensitive).
        
    Returns:
        The number of times the word appears on the page.
    """
    content = get_page_content(url)
    return content.lower().count(word.lower())


if __name__ == "__main__":
    # Quick test
    test_url = "https://github.com/alexeygrigorev/minsearch"
    content = get_page_content(test_url)
    print(f"Content length: {len(content)} characters")
    print("\nFirst 500 characters:")
    print(content[:500])
