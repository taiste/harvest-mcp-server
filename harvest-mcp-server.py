import os
import json
import httpx
from datetime import datetime
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("harvest-api")

# Get environment variables for Harvest API
HARVEST_ACCOUNT_ID = os.environ.get("HARVEST_ACCOUNT_ID")
HARVEST_API_KEY = os.environ.get("HARVEST_API_KEY")

# Helper function to make Harvest API requests
async def harvest_request(path, params=None, method="GET"):
    if not HARVEST_ACCOUNT_ID or not HARVEST_API_KEY:
        raise ValueError("Missing Harvest API credentials. Set HARVEST_ACCOUNT_ID and HARVEST_API_KEY environment variables.")

    headers = {
        "Harvest-Account-Id": HARVEST_ACCOUNT_ID,
        "Authorization": f"Bearer {HARVEST_API_KEY}",
        "User-Agent": "Harvest MCP Server",
        "Content-Type": "application/json"
    }

    url = f"https://api.harvestapp.com/v2/{path}"

    async with httpx.AsyncClient() as client:
        if method == "GET":
            response = await client.get(url, headers=headers, params=params)
        else:
            response = await client.request(method, url, headers=headers, json=params)

        if response.status_code != 200:
            raise Exception(f"Harvest API Error: {response.status_code} {response.text}")

        return response.json()

@mcp.tool()
async def list_users(is_active: bool = None, page: int = None, per_page: int = None):
    """List all users in your Harvest account.

    Args:
        is_active: Pass true to only return active users and false to return inactive users
        page: The page number for pagination
        per_page: The number of records to return per page (1-2000)
    """
    params = {}
    if is_active is not None:
        params["is_active"] = "true" if is_active else "false"
    else:
        params["is_active"] = "true"
    if page is not None:
        params["page"] = str(page)
    if per_page is not None:
        params["per_page"] = str(per_page)
    else:
        params["per_page"] = 200

    response = await harvest_request("users", params)
    return json.dumps(response, indent=2)

@mcp.tool()
async def get_user_details(user_id: int):
    """Retrieve details for a specific user.

    Args:
        user_id: The ID of the user to retrieve
    """
    response = await harvest_request(f"users/{user_id}")
    return json.dumps(response, indent=2)

@mcp.tool()
async def list_time_entries(user_id: int = None, from_date: str = None, to_date: str = None, is_running: bool = None):
    """List time entries with optional filtering.

    Args:
        user_id: Filter by user ID
        from_date: Only return time entries with a spent_date on or after the given date (YYYY-MM-DD)
        to_date: Only return time entries with a spent_date on or before the given date (YYYY-MM-DD)
        is_running: Pass true to only return running time entries and false to return non-running time entries
    """
    params = {}
    if user_id is not None:
        params["user_id"] = str(user_id)
    if from_date is not None:
        params["from"] = from_date
    if to_date is not None:
        params["to"] = to_date
    if is_running is not None:
        params["is_running"] = "true" if is_running else "false"

    response = await harvest_request("time_entries", params)
    return json.dumps(response, indent=2)

@mcp.tool()
async def create_time_entry(project_id: int, task_id: int, spent_date: str, hours: float, notes: str = None):
    """Create a new time entry.

    Args:
        project_id: The ID of the project to associate with the time entry
        task_id: The ID of the task to associate with the time entry
        spent_date: The date when the time was spent (YYYY-MM-DD)
        hours: The number of hours spent
        notes: Optional notes about the time entry
    """
    params = {
        "project_id": project_id,
        "task_id": task_id,
        "spent_date": spent_date,
        "hours": hours
    }

    if notes:
        params["notes"] = notes

    response = await harvest_request("time_entries", params, method="POST")
    return json.dumps(response, indent=2)

@mcp.tool()
async def stop_timer(time_entry_id: int):
    """Stop a running timer.

    Args:
        time_entry_id: The ID of the running time entry to stop
    """
    response = await harvest_request(f"time_entries/{time_entry_id}/stop", method="PATCH")
    return json.dumps(response, indent=2)

@mcp.tool()
async def start_timer(project_id: int, task_id: int, notes: str = None):
    """Start a new timer.

    Args:
        project_id: The ID of the project to associate with the time entry
        task_id: The ID of the task to associate with the time entry
        notes: Optional notes about the time entry
    """
    params = {
        "project_id": project_id,
        "task_id": task_id,
    }

    if notes:
        params["notes"] = notes

    response = await harvest_request("time_entries", params, method="POST")
    return json.dumps(response, indent=2)

@mcp.tool()
async def list_projects(client_id: int = None, is_active: bool = None):
    """List projects with optional filtering.

    Args:
        client_id: Filter by client ID
        is_active: Pass true to only return active projects and false to return inactive projects
    """
    params = {}
    if client_id is not None:
        params["client_id"] = str(client_id)
    if is_active is not None:
        params["is_active"] = "true" if is_active else "false"

    response = await harvest_request("projects", params)
    return json.dumps(response, indent=2)

@mcp.tool()
async def get_project_details(project_id: int):
    """Get detailed information about a specific project.

    Args:
        project_id: The ID of the project to retrieve
    """
    response = await harvest_request(f"projects/{project_id}")
    return json.dumps(response, indent=2)

@mcp.tool()
async def list_clients(is_active: bool = None):
    """List clients with optional filtering.

    Args:
        is_active: Pass true to only return active clients and false to return inactive clients
    """
    params = {}
    if is_active is not None:
        params["is_active"] = "true" if is_active else "false"

    response = await harvest_request("clients", params)
    return json.dumps(response, indent=2)

@mcp.tool()
async def get_client_details(client_id: int):
    """Get detailed information about a specific client.

    Args:
        client_id: The ID of the client to retrieve
    """
    response = await harvest_request(f"clients/{client_id}")
    return json.dumps(response, indent=2)

@mcp.tool()
async def list_tasks(is_active: bool = None):
    """List all tasks with optional filtering.

    Args:
        is_active: Pass true to only return active tasks and false to return inactive tasks
    """
    params = {}
    if is_active is not None:
        params["is_active"] = "true" if is_active else "false"

    response = await harvest_request("tasks", params)
    return json.dumps(response, indent=2)

if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')
