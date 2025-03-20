# Harvest MCP Server

This MCP (Model Context Protocol) server provides integration with the Harvest time tracking and project management API. It allows Claude and other MCP-compatible AI assistants to interact with your Harvest account, helping you manage time entries, projects, clients, and more.

## Features

The server provides the following functionality:

### Users

- List users
- Get user details

### Time Entries
- List time entries with filtering options
- Create new time entries
- Start/stop timers
- Query time entry details

### Projects
- List projects with filtering options
- Retrieve detailed project information

### Clients
- List clients with filtering options
- Retrieve detailed client information

### Tasks
- List available tasks with filtering options

## Setup Instructions

### Prerequisites
- Python 3.10 or higher
- Harvest account with API access
- Harvest API key and Account ID

### Integrating with Claude Desktop

1. Create or edit your Claude Desktop configuration file:
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`

2. Add the Harvest MCP server configuration:
   ```json
    {
        "mcpServers": {
            "harvest": {
                "command": "uv",
                "args": [
                  "run",
                  "--directory",
                  "change_directory",
                  "harvest-mcp-server.py"
                ],
                "env": {
                    "HARVEST_ACCOUNT_ID": "account_id",
                    "HARVEST_API_KEY": "api_key"
                }
            }
        }
    }
   ```

3. Restart Claude Desktop.

4. Verify the integration by looking for the hammer icon in Claude's interface.

## Example Queries

Once connected, you can ask Claude about your Harvest data with queries like:

- "Show me my time entries from last week"
- "List all my active projects"
- "Start a timer for project [project_id] and task [task_id]"
- "Show me all active clients"
- "List all available tasks"

## Customization

You can modify the server code to add more functionality or customize the existing tools to better suit your workflow. The server uses FastMCP, which makes it easy to add new tools by simply adding new functions with the `@mcp.tool()` decorator.

## Troubleshooting

- **API Errors**: Make sure your Harvest API key and Account ID are correct and have the necessary permissions.
- **Connection Issues**: Verify that your Claude Desktop configuration has the correct path to the server script.
- **Missing Dependencies**: Ensure you've installed all required packages in your Python environment.

## Security Notes

This server requires your Harvest API credentials to function. Make sure to:
- Keep your API key secure
- Do not share your claude_desktop_config.json file
- Consider using a dedicated API key with limited permissions for this integration
