"""
AI Assistant that uses MCP tools for web scraping and documentation search.
Connects to the MCP server and uses OpenAI to process natural language queries.
"""

import asyncio
import json
import os
from fastmcp import Client
from openai import OpenAI

# Import the MCP server
from server import mcp


def get_openai_client():
    """Get OpenAI client, checking for API key."""
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ValueError(
            "OPENAI_API_KEY environment variable is not set. "
            "Please set it with: export OPENAI_API_KEY='your-api-key'"
        )
    return OpenAI(api_key=api_key)


async def get_available_tools():
    """Get the list of tools from the MCP server in OpenAI format."""
    async with Client(mcp) as client:
        tools = await client.list_tools()
        
        openai_tools = []
        for tool in tools:
            openai_tools.append({
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description or "",
                    "parameters": tool.inputSchema if hasattr(tool, 'inputSchema') else {"type": "object", "properties": {}}
                }
            })
        return openai_tools


async def call_mcp_tool(tool_name: str, arguments: dict):
    """Call an MCP tool and return the result."""
    async with Client(mcp) as client:
        result = await client.call_tool(tool_name, arguments)
        # Extract the text content from the result
        if hasattr(result, 'content') and result.content:
            contents = []
            for item in result.content:
                if hasattr(item, 'text'):
                    contents.append(item.text)
            return "\n".join(contents) if contents else str(result)
        return str(result)


async def chat_with_assistant(user_message: str, openai_client: OpenAI):
    """
    Process a user message through the AI assistant.
    The assistant can use MCP tools to answer questions.
    """
    # Get available tools from MCP server
    tools = await get_available_tools()
    
    # System prompt for the assistant
    system_prompt = """You are a helpful AI assistant with access to the following tools:

1. fetch_page(url): Fetch web page content in markdown format
2. count_word(url, word): Count how many times a word appears on a web page
3. search_docs(github_url, query, num_results): Search documentation in any GitHub repository

Use these tools when needed to answer user questions. Be concise and helpful."""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message}
    ]
    
    # Initial call to OpenAI
    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        tools=tools,
        tool_choice="auto"
    )
    
    assistant_message = response.choices[0].message
    
    # Check if the model wants to call tools
    while assistant_message.tool_calls:
        messages.append(assistant_message)
        
        # Process each tool call
        for tool_call in assistant_message.tool_calls:
            tool_name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)
            
            print(f"  [Calling tool: {tool_name}({arguments})]")
            
            # Call the MCP tool
            try:
                result = await call_mcp_tool(tool_name, arguments)
            except Exception as e:
                result = f"Error calling tool: {e}"
            
            # Add tool result to messages
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": str(result)
            })
        
        # Get next response from OpenAI
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=tools,
            tool_choice="auto"
        )
        assistant_message = response.choices[0].message
    
    return assistant_message.content


async def main():
    """Run the AI assistant."""
    print("=" * 60)
    print("AI Assistant with MCP Tools")
    print("=" * 60)
    print("\nAvailable tools:")
    print("  - fetch_page(url): Fetch web page content")
    print("  - count_word(url, word): Count word occurrences on a page")
    print("  - search_docs(github_url, query): Search any GitHub repository")
    print("\nType 'quit' or 'exit' to stop.\n")
    
    try:
        openai_client = get_openai_client()
    except ValueError as e:
        print(f"Error: {e}")
        return
    
    while True:
        try:
            user_input = input("\nYou: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ('quit', 'exit', 'q'):
                print("Goodbye!")
                break
            
            print("\nAssistant: ", end="", flush=True)
            response = await chat_with_assistant(user_input, openai_client)
            print(response)
            
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except EOFError:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"\nError: {e}")


if __name__ == "__main__":
    asyncio.run(main())
