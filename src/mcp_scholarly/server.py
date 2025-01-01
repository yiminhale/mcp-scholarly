import asyncio

from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server import NotificationOptions, Server
import mcp.server.stdio
import arxiv

server = Server("mcp-scholarly")
client = arxiv.Client()


@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """
    List available tools.
    Each tool specifies its arguments using JSON Schema validation.
    """
    return [
        types.Tool(
            name="search-arxiv",
            description="Search arxiv for articles related to the given keyword.",
            inputSchema={
                "type": "object",
                "properties": {
                    "keyword": {"type": "string"},
                },
                "required": ["keyword"],
            },
        )
    ]


@server.call_tool()
async def handle_call_tool(
        name: str, arguments: dict | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """
    Handle tool execution requests.
    Tools can modify server state and notify clients of changes.
    """
    if name != "search-arxiv":
        raise ValueError(f"Unknown tool: {name}")

    if not arguments:
        raise ValueError("Missing arguments")

    keyword = arguments.get("keyword")

    if not keyword:
        raise ValueError("Missing keyword")

    # Notify clients that resources have changed
    await server.request_context.session.send_resource_list_changed()

    search = arxiv.Search(query=keyword, max_results=10, sort_by=arxiv.SortCriterion.SubmittedDate)

    results = client.results(search)

    all_results = list(results)

    formatted_results = []

    for result in all_results:
        title = result.title
        summary = result.summary
        links = "||".join([link.href for link in result.links])
        pdf_url = result.pdf_url

        article_data = "\n".join([
            f"Title: {title}",
            f"Summary: {summary}",
            f"Links: {links}",
            f"PDF URL: {pdf_url}",
        ])

        formatted_results.append(article_data)

    return [
        types.TextContent(
            type="text",
            text=f"Search articles for {keyword}:\n"
                 + "\n\n\n".join(formatted_results)
        ),
    ]


async def main():
    # Run the server using stdin/stdout streams
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="mcp-scholarly",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )
