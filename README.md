# AI Web Scraper & Documentation Assistant

A powerful toolset for web scraping and documentation search, featuring an AI Assistant powered by OpenAI and the Model Context Protocol (MCP).

## 🚀 Features

- **Web Scraper**: Converts any URL into clean Markdown using Jina Reader.
- **Universal Documentation Search**: Search **any** GitHub repository's documentation (README, .md, .mdx files) with semantic search powered by `minsearch`.
- **MCP Server**: FastMCP server exposing tools for LLMs to consume.
- **AI Assistant**: A built-in CLI assistant that uses OpenAI and the MCP tools to answer natural language queries.

## 🛠️ Installation

This project uses [`uv`](https://github.com/astral-sh/uv) for dependency management.

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/Alexander-Heinz/scrape-web-tool.git
    cd scrape-web-tool
    ```

2.  **Install dependencies:**
    ```bash
    uv sync
    ```

## 🤖 Usage

### 1. AI Assistant (Recommended)

Interact with the tools using natural language.

```bash
export OPENAI_API_KEY='your-api-key'
uv run python main.py
```

**Example queries:**
- *"What is the main topic of https://example.com?"*
- *"Count how many times 'python' appears on https://www.python.org"*
- *"Search the fastmcp repo for how to create a server"*
- *"Find information about 'vector search' in alexeygrigorev/minsearch"*

### 2. MCP Server

Run the MCP server to use these tools in other MCP-compatible clients (like Claude Desktop).

```bash
uv run python server.py
# Or via FastMCP CLI
uv run fastmcp run server.py:mcp
```

### 3. Core Libraries

You can also use the Python modules directly in your code.

**Web Scraper (`web_scraper.py`):**
```python
from web_scraper import get_page_content

markdown = get_page_content("https://example.com")
print(markdown)
```

**GitHub Search (`search.py`):**
```python
from search import search_github_docs

# Search any repo (owner/repo)
results = search_github_docs("jlowin/fastmcp", "tools")
print(results[0]['content'])
```

## 🧪 Testing

Run the comprehensive test suite to verify functionality:

```bash
uv run python test.py
```

## 🏗️ Architecture

- **`main.py`**: AI Assistant client (OpenAI integration).
- **`server.py`**: FastMCP server definition.
- **`web_scraper.py`**: Logic for fetching and processing web pages.
- **`search.py`**: Logic for downloading GitHub repos and indexing markdown files.

## 📦 Dependencies

- **fastmcp**: Framework for building MCP servers.
- **requests**: HTTP client for scraping.
- **minsearch**: Minimalistic search engine for documentation.
- **openai**: For the AI Assistant integration.
