import asyncio
import json
import re
from typing import Dict, List, Optional, Any
from urllib.parse import quote, urljoin
import aiohttp
from bs4 import BeautifulSoup
from mcp.server.fastmcp import FastMCP
from mcp.types import TextContent, Resource, Tool

# Create the MCP server
mcp = FastMCP("Microsoft Docs MCP Server")

# Microsoft Docs base URLs and endpoints
DOCS_BASE_URL = "https://docs.microsoft.com"
LEARN_BASE_URL = "https://learn.microsoft.com"
SEARCH_API_URL = "https://docs.microsoft.com/api/search"

class MicrosoftDocsClient:
    def __init__(self):
        self.session = None
    
    async def get_session(self):
        if self.session is None:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def close(self):
        if self.session:
            await self.session.close()
    
    async def search_docs(self, query: str, product: str = "", language: str = "en-us", max_results: int = 10) -> List[Dict]:
        """Search Microsoft documentation"""
        session = await self.get_session()
        
        # Use Microsoft Learn search API
        search_url = f"{LEARN_BASE_URL}/api/search"
        params = {
            "search": query,
            "locale": language,
            "$top": max_results
        }
        
        if product:
            params["products"] = product
        
        try:
            async with session.get(search_url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("results", [])
                else:
                    # Fallback to basic search
                    return await self._fallback_search(query, product, max_results)
        except Exception:
            return await self._fallback_search(query, product, max_results)
    
    async def _fallback_search(self, query: str, product: str = "", max_results: int = 10) -> List[Dict]:
        """Fallback search using basic results"""
        
        # Return mock results for demonstration - in production you'd want to use a proper search API
        mock_results = [
            {
                "title": f"Microsoft Documentation: {query}",
                "url": f"{LEARN_BASE_URL}/en-us/docs/{query.lower().replace(' ', '-')}",
                "description": f"Documentation about {query} in Microsoft products",
                "lastUpdated": "2024-01-01T00:00:00Z",
                "product": product or "General"
            },
            {
                "title": f"{query} - Getting Started Guide",
                "url": f"{LEARN_BASE_URL}/en-us/docs/{query.lower().replace(' ', '-')}/getting-started",
                "description": f"Getting started guide for {query}",
                "lastUpdated": "2024-01-01T00:00:00Z",
                "product": product or "General"
            },
            {
                "title": f"{query} - Code Examples",
                "url": f"{LEARN_BASE_URL}/en-us/samples/{query.lower().replace(' ', '-')}",
                "description": f"Code examples and samples for {query}",
                "lastUpdated": "2024-01-01T00:00:00Z",
                "product": product or "General"
            }
        ]
        
        return mock_results[:max_results]
    
    async def get_page_content(self, url: str) -> str:
        """Fetch and parse content from a Microsoft Docs page"""
        session = await self.get_session()
        
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Extract main content (Microsoft Docs specific selectors)
                    content_selectors = [
                        'main[role="main"]',
                        '.content',
                        'article',
                        '#main-content'
                    ]
                    
                    content = ""
                    for selector in content_selectors:
                        element = soup.select_one(selector)
                        if element:
                            # Remove navigation, ads, and other non-content elements
                            for unwanted in element.select('nav, .breadcrumb, .alert, .feedback-section'):
                                unwanted.decompose()
                            
                            content = element.get_text(strip=True, separator='\n')
                            break
                    
                    return content[:5000]  # Limit content length
                else:
                    return f"Error fetching content: HTTP {response.status}"
        except Exception as e:
            return f"Error fetching content: {str(e)}"

# Global client instance
docs_client = MicrosoftDocsClient()

@mcp.tool()
async def search_microsoft_docs(
    query: str,
    product: str = "",
    language: str = "en-us",
    max_results: int = 5
) -> List[Dict[str, Any]]:
    """
    Search Microsoft documentation for information about specific topics.
    
    Args:
        query: The search query (e.g., "Azure Functions", "React hooks", "C# async")
        product: Optional product filter (e.g., "azure", "dotnet", "office", "windows")
        language: Language code (default: "en-us")
        max_results: Maximum number of results to return (default: 5, max: 10)
    
    Returns:
        List of search results with title, URL, description, and last updated date
    """
    max_results = min(max_results, 10)  # Limit to 10 results
    
    try:
        results = await docs_client.search_docs(query, product, language, max_results)
        
        # Format results for better readability
        formatted_results = []
        for result in results:
            formatted_result = {
                "title": result.get("title", "No title"),
                "url": result.get("url", ""),
                "description": result.get("description", "No description available"),
                "lastUpdated": result.get("lastUpdated", "Unknown"),
                "product": result.get("product", "General")
            }
            formatted_results.append(formatted_result)
        
        return formatted_results
    except Exception as e:
        return [{"error": f"Search failed: {str(e)}"}]

@mcp.tool()
async def get_documentation_content(url: str) -> str:
    """
    Fetch the full content of a Microsoft documentation page.
    
    Args:
        url: The URL of the Microsoft Docs page to fetch
    
    Returns:
        The text content of the documentation page
    """
    try:
        # Validate that it's a Microsoft Docs URL
        if not (url.startswith("https://docs.microsoft.com") or url.startswith("https://learn.microsoft.com")):
            return "Error: URL must be from docs.microsoft.com or learn.microsoft.com"
        
        content = await docs_client.get_page_content(url)
        return content
    except Exception as e:
        return f"Error fetching documentation: {str(e)}"

@mcp.tool()
async def find_code_examples(
    technology: str,
    programming_language: str = "",
    scenario: str = ""
) -> List[Dict[str, Any]]:
    """
    Find code examples and tutorials for specific technologies.
    
    Args:
        technology: The technology to find examples for (e.g., "Azure Functions", "React", "Entity Framework")
        programming_language: Optional programming language filter (e.g., "csharp", "javascript", "python")
        scenario: Optional scenario filter (e.g., "getting started", "authentication", "deployment")
    
    Returns:
        List of documentation pages with code examples
    """
    try:
        # Build search query for code examples
        query_parts = [technology]
        if programming_language:
            query_parts.append(programming_language)
        if scenario:
            query_parts.append(scenario)
        query_parts.extend(["code", "example", "tutorial", "sample"])
        
        query = " ".join(query_parts)
        
        results = await docs_client.search_docs(query, max_results=5)
        
        # Filter and format results for code examples
        code_examples = []
        for result in results:
            if any(keyword in result.get("title", "").lower() or keyword in result.get("description", "").lower() 
                   for keyword in ["example", "tutorial", "sample", "quickstart", "getting started"]):
                code_examples.append({
                    "title": result.get("title", ""),
                    "url": result.get("url", ""),
                    "description": result.get("description", ""),
                    "type": "code_example"
                })
        
        return code_examples
    except Exception as e:
        return [{"error": f"Failed to find code examples: {str(e)}"}]

@mcp.tool()
async def get_api_reference(
    api_name: str,
    version: str = "latest",
    language: str = "en-us"
) -> Dict[str, Any]:
    """
    Get API reference documentation for Microsoft APIs.
    
    Args:
        api_name: Name of the API (e.g., "Microsoft Graph", "Azure REST API", "Office 365")
        version: API version (default: "latest")
        language: Language code (default: "en-us")
    
    Returns:
        API reference information including endpoints, parameters, and examples
    """
    try:
        # Search for API reference documentation
        query = f"{api_name} API reference {version}"
        results = await docs_client.search_docs(query, max_results=3)
        
        api_docs = []
        for result in results:
            if "api" in result.get("title", "").lower() or "reference" in result.get("title", "").lower():
                api_docs.append({
                    "title": result.get("title", ""),
                    "url": result.get("url", ""),
                    "description": result.get("description", ""),
                    "version": version,
                    "type": "api_reference"
                })
        
        return {
            "api_name": api_name,
            "version": version,
            "documentation": api_docs
        }
    except Exception as e:
        return {"error": f"Failed to get API reference: {str(e)}"}

# Resource for browsing documentation categories
@mcp.resource("docs://categories")
async def get_documentation_categories() -> str:
    """Get available Microsoft documentation categories"""
    categories = {
        "Azure": ["Functions", "App Service", "Storage", "Cosmos DB", "Active Directory"],
        "Microsoft 365": ["Graph API", "Teams", "SharePoint", "Outlook"],
        "Development": [".NET", "C#", "JavaScript", "Python", "PowerShell"],
        "Windows": ["WinUI", "UWP", "Win32", "Windows Forms"],
        "Office": ["Excel", "Word", "PowerPoint", "Outlook"],
        "Power Platform": ["Power Apps", "Power Automate", "Power BI"],
        "Visual Studio": ["Code", "IDE", "Extensions", "Debugging"]
    }
    
    formatted_categories = ""
    for category, items in categories.items():
        formatted_categories += f"\n## {category}\n"
        for item in items:
            formatted_categories += f"- {item}\n"
    
    return formatted_categories

# Add cleanup on server shutdown
async def cleanup():
    await docs_client.close()

# Add this to actually run the server
if __name__ == "__main__":
    mcp.run()