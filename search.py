"""
Document search implementation using minsearch.
Downloads any GitHub repo, indexes md/mdx files, and provides search functionality.
"""

import os
import zipfile
import urllib.request
from pathlib import Path
from urllib.parse import urlparse
from minsearch import Index


# Constants
DOWNLOAD_DIR = Path(__file__).parent / "downloads"


def parse_github_url(github_url: str) -> tuple[str, str, str]:
    """
    Parse a GitHub URL to extract owner, repo name, and branch.
    
    Supports formats:
    - https://github.com/owner/repo
    - https://github.com/owner/repo/tree/branch
    - owner/repo
    
    Args:
        github_url: GitHub repository URL or owner/repo string.
        
    Returns:
        Tuple of (owner, repo_name, branch)
    """
    # Handle owner/repo format
    if not github_url.startswith("http"):
        parts = github_url.split("/")
        if len(parts) >= 2:
            return parts[0], parts[1], "main"
        raise ValueError(f"Invalid GitHub URL format: {github_url}")
    
    parsed = urlparse(github_url)
    path_parts = parsed.path.strip("/").split("/")
    
    if len(path_parts) < 2:
        raise ValueError(f"Invalid GitHub URL format: {github_url}")
    
    owner = path_parts[0]
    repo = path_parts[1]
    branch = "main"
    
    # Check if branch is specified
    if len(path_parts) >= 4 and path_parts[2] == "tree":
        branch = path_parts[3]
    
    return owner, repo, branch


def get_zip_url(owner: str, repo: str, branch: str) -> str:
    """Get the ZIP download URL for a GitHub repo."""
    return f"https://github.com/{owner}/{repo}/archive/refs/heads/{branch}.zip"


def download_github_repo(github_url: str, force: bool = False) -> Path:
    """
    Download a GitHub repository as a zip file.
    
    Args:
        github_url: GitHub repository URL (e.g., https://github.com/owner/repo)
        force: If True, re-download even if file exists.
        
    Returns:
        Path to the downloaded zip file.
    """
    owner, repo, branch = parse_github_url(github_url)
    
    DOWNLOAD_DIR.mkdir(exist_ok=True)
    zip_filename = f"{owner}-{repo}-{branch}.zip"
    zip_path = DOWNLOAD_DIR / zip_filename
    
    if zip_path.exists() and not force:
        print(f"Zip file already exists at {zip_path}")
        return zip_path
    
    zip_url = get_zip_url(owner, repo, branch)
    print(f"Downloading {owner}/{repo} ({branch}) from {zip_url}...")
    urllib.request.urlretrieve(zip_url, zip_path)
    print(f"Downloaded to {zip_path}")
    return zip_path


def extract_md_files(zip_path: Path) -> list[dict]:
    """
    Extract md and mdx files from the zip archive.
    
    Args:
        zip_path: Path to the zip file.
        
    Returns:
        List of documents with 'filename' and 'content' fields.
    """
    documents = []
    
    with zipfile.ZipFile(zip_path, 'r') as zf:
        for file_info in zf.namelist():
            # Only process .md and .mdx files
            if file_info.endswith('.md') or file_info.endswith('.mdx'):
                # Skip directories
                if file_info.endswith('/'):
                    continue
                    
                # Remove the first part of the path (e.g., "repo-main/")
                parts = file_info.split('/', 1)
                if len(parts) > 1:
                    clean_filename = parts[1]
                else:
                    clean_filename = file_info
                
                # Read the file content
                try:
                    content = zf.read(file_info).decode('utf-8')
                    documents.append({
                        'filename': clean_filename,
                        'content': content
                    })
                except Exception as e:
                    print(f"Error reading {file_info}: {e}")
    
    return documents


def create_search_index(documents: list[dict]) -> Index:
    """
    Create and fit a minsearch index with the given documents.
    
    Args:
        documents: List of documents with 'filename' and 'content' fields.
        
    Returns:
        Fitted minsearch Index.
    """
    index = Index(
        text_fields=["content", "filename"],
        keyword_fields=[]
    )
    index.fit(documents)
    return index


def search(index: Index, query: str, num_results: int = 5) -> list[dict]:
    """
    Search the index for relevant documents.
    
    Args:
        index: The minsearch Index to search.
        query: Search query string.
        num_results: Number of results to return (default 5).
        
    Returns:
        List of matching documents.
    """
    results = index.search(query, num_results=num_results)
    return results


# Cache for indexes by repo
_indexes: dict[str, Index] = {}
_documents: dict[str, list[dict]] = {}


def get_repo_key(github_url: str) -> str:
    """Get a cache key for a GitHub URL."""
    owner, repo, branch = parse_github_url(github_url)
    return f"{owner}/{repo}/{branch}"


def get_index(github_url: str, force: bool = False) -> Index:
    """
    Get or create the search index for a GitHub repo.
    Downloads and indexes if not already done.
    
    Args:
        github_url: GitHub repository URL.
        force: If True, re-download and re-index.
        
    Returns:
        The minsearch Index for the repo.
    """
    key = get_repo_key(github_url)
    
    if key not in _indexes or force:
        zip_path = download_github_repo(github_url, force=force)
        docs = extract_md_files(zip_path)
        print(f"Indexed {len(docs)} documents from {key}")
        _documents[key] = docs
        _indexes[key] = create_search_index(docs)
    
    return _indexes[key]


def search_github_docs(github_url: str, query: str, num_results: int = 5) -> list[dict]:
    """
    Search documentation in a GitHub repository.
    
    Args:
        github_url: GitHub repository URL (e.g., https://github.com/owner/repo)
        query: Search query string.
        num_results: Number of results to return (default 5).
        
    Returns:
        List of matching documents with 'filename' and 'content' fields.
    """
    index = get_index(github_url)
    return search(index, query, num_results)


# Legacy function for backward compatibility
def search_docs(query: str, num_results: int = 5) -> list[dict]:
    """
    Search FastMCP documentation (legacy function).
    
    Args:
        query: Search query string.
        num_results: Number of results to return (default 5).
        
    Returns:
        List of matching documents.
    """
    return search_github_docs("https://github.com/jlowin/fastmcp", query, num_results)


# Legacy function
def download_fastmcp_docs() -> Path:
    """Download FastMCP docs (legacy function)."""
    return download_github_repo("https://github.com/jlowin/fastmcp")


if __name__ == "__main__":
    # Test with different repos
    print("\n=== Testing with FastMCP ===")
    results = search_github_docs("https://github.com/jlowin/fastmcp", "demo")
    print(f"Search results for 'demo' in FastMCP:")
    for i, doc in enumerate(results, 1):
        print(f"{i}. {doc['filename']}")
    
    print("\n=== Testing with minsearch ===")
    results = search_github_docs("alexeygrigorev/minsearch", "vector search")
    print(f"Search results for 'vector search' in minsearch:")
    for i, doc in enumerate(results, 1):
        print(f"{i}. {doc['filename']}")
