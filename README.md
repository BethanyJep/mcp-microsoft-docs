# Microsoft Docs MCP Server

A Model Context Protocol (MCP) server that provides access to Microsoft documentation to help you code better.

## Features

This MCP server provides the following tools:

### 🔍 **search_microsoft_docs**
Search across Microsoft documentation with optional product filtering.

**Usage:**
- `query`: Search term (e.g., "Azure Functions", "React hooks", "C# async")
- `product`: Optional product filter (e.g., "azure", "dotnet", "office", "windows")
- `language`: Language code (default: "en-us")
- `max_results`: Maximum results to return (default: 5, max: 10)

### 📄 **get_documentation_content**
Fetch the full content of any Microsoft documentation page.

**Usage:**
- `url`: URL from docs.microsoft.com or learn.microsoft.com

### 💻 **find_code_examples**
Find code examples and tutorials for specific technologies.

**Usage:**
- `technology`: Technology to find examples for (e.g., "Azure Functions", "React")
- `programming_language`: Optional language filter (e.g., "csharp", "javascript", "python")
- `scenario`: Optional scenario filter (e.g., "getting started", "authentication")

### 🔌 **get_api_reference**
Get API reference documentation for Microsoft APIs.

**Usage:**
- `api_name`: Name of the API (e.g., "Microsoft Graph", "Azure REST API")
- `version`: API version (default: "latest")
- `language`: Language code (default: "en-us")

### 📚 **docs://categories**
Browse available Microsoft documentation categories (resource).

## Installation

1. Install dependencies:
```bash
pip install mcp requests beautifulsoup4 aiohttp
```

2. Configure your MCP client with this server by adding to `.vscode/mcp.json`:
```json
{
    "inputs": [],
    "servers": {
       "microsoft-docs-mcp": {
           "command": "python3",
           "args": ["server.py"],
           "type": "stdio",
           "cwd": "/path/to/mcp-microsoft-docs"
       }
    }
}
```

## Example Usage

### Search for Azure Functions documentation:
```
search_microsoft_docs("Azure Functions", product="azure")
```

### Find React code examples:
```
find_code_examples("React", programming_language="javascript", scenario="getting started")
```

### Get Microsoft Graph API reference:
```
get_api_reference("Microsoft Graph")
```

### Browse documentation categories:
```
Access the docs://categories resource
```

## Development

The server uses:
- **FastMCP** for the MCP server implementation
- **aiohttp** for async HTTP requests
- **BeautifulSoup** for HTML parsing
- **requests** for HTTP requests

## License

MIT License
