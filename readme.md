[![MseeP.ai Security Assessment Badge](https://mseep.net/pr/taiste-harvest-mcp-server-badge.png)](https://mseep.ai/app/taiste-harvest-mcp-server)

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
- Get unsubmitted timesheets (time entries not yet submitted for approval)

### Projects
- List projects with filtering options (by client, is_active, updated_since, page, per_page)
- Retrieve detailed project information
- Create new projects
- Update existing projects (also used to archive: pass `is_active=False`)
- Delete projects (destructive — also deletes the project's time entries and expenses, though invoices are retained; archiving is recommended instead)

### Task Assignments
- List task assignments (account-wide or scoped to a project)
- Retrieve detailed task assignment information
- Create new task assignments (link a task to a project)
- Update existing task assignments
- Delete task assignments (only when no time entries are logged against them)

### User Assignments
- List user assignments (account-wide or scoped to a project)
- Retrieve detailed user assignment information
- Create new user assignments (link a user to a project)
- Update existing user assignments
- Delete user assignments (only when no time entries or expenses are logged against them)

### Clients
- List clients with filtering options
- Retrieve detailed client information

### Tasks
- List available tasks with filtering options

### Estimates
- List estimates with filtering options (by client, state, date range, updated_since)
- Retrieve detailed estimate information
- Look up an estimate by its user-facing number (e.g. "79")
- List messages associated with an estimate
- Create new estimates with line items
- Update existing estimates (add/update/delete line items via `_destroy`)
- Change estimate state (send, accept, decline, re-open) without sending email
- Send estimate messages (emails the estimate to recipients)
- Delete estimates

## Setup Instructions

### Prerequisites
- Python 3.10 or higher
- Harvest account with API access
- Harvest API key and Account ID

### Integrating with Claude Desktop
1. Create or edit your Claude Desktop configuration file:
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Windows (MSIX installs — the default from [claude.ai/download](https://claude.ai/download)): `%LOCALAPPDATA%\Packages\Claude_pzs8sxrjxfjjc\LocalCache\Roaming\Claude\claude_desktop_config.json`
   - Windows (older/non-MSIX installs): `%APPDATA%\Claude\claude_desktop_config.json`

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
- "Get my unsubmitted timesheets from this month"
- "Show me unsubmitted time entries for user [user_id]"
- "Show me all accepted estimates from this quarter"
- "Find the estimate numbered [number]"
- "Create a draft estimate for client [client_id] with these line items..."
- "Mark estimate [id] as sent"
- "Email estimate [id] to client@example.com"
- "Create a new project called [name] for client [client_id], billed by Project, no budget"
- "Archive project [project_id]"
- "Assign task [task_id] to project [project_id] as billable"
- "Make user [user_id] a project manager on project [project_id]"
- "List everyone assigned to project [project_id]"

## Customization

You can modify the server code to add more functionality or customize the existing tools to better suit your workflow. The server uses FastMCP, which makes it easy to add new tools by simply adding new functions with the `@mcp.tool()` decorator.

## Troubleshooting

- **API Errors**: Make sure your Harvest API key and Account ID are correct and have the necessary permissions.
- **Connection Issues**: Verify that your Claude Desktop configuration has the correct path to the server script.
- **Missing Dependencies**: Ensure you've installed all required packages in your Python environment.

## Read-Only Mode

You can run the server in read-only mode by setting the `HARVEST_READ_ONLY` environment variable to `true`. This disables all write operations (creating time entries, starting/stopping timers, creating/updating/deleting estimates, changing estimate state, sending estimate messages, and creating/updating/deleting projects, task assignments, and user assignments) while keeping all read operations available.

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
                "HARVEST_API_KEY": "api_key",
                "HARVEST_READ_ONLY": "true"
            }
        }
    }
}
```

When read-only mode is enabled, any attempt to call a write tool will return an error message explaining that the server is in read-only mode and how to enable write access.

## Security Notes

This server requires your Harvest API credentials to function. Make sure to:
- Keep your API key secure
- Do not share your claude_desktop_config.json file
- Consider using a dedicated API key with limited permissions for this integration
