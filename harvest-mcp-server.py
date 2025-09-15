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

if not HARVEST_ACCOUNT_ID or not HARVEST_API_KEY:
    raise ValueError(
        "Missing Harvest API credentials. Set HARVEST_ACCOUNT_ID and HARVEST_API_KEY environment variables."
    )


# Helper function to make Harvest API requests
async def harvest_request(path, params=None, method="GET"):
    headers = {
        "Harvest-Account-Id": HARVEST_ACCOUNT_ID,
        "Authorization": f"Bearer {HARVEST_API_KEY}",
        "User-Agent": "Harvest MCP Server",
        "Content-Type": "application/json",
    }

    url = f"https://api.harvestapp.com/v2/{path}"

    async with httpx.AsyncClient() as client:
        if method == "GET":
            response = await client.get(url, headers=headers, params=params)
        else:
            response = await client.request(method, url, headers=headers, json=params)

        if response.status_code not in [200, 201, 204]:
            raise Exception(
                f"Harvest API Error: {response.status_code} {response.text}"
            )

        # Handle empty responses (like DELETE operations)
        if response.status_code == 204 or not response.text:
            return None

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
async def list_time_entries(
    user_id: int = None,
    from_date: str = None,
    to_date: str = None,
    is_running: bool = None,
    is_billable: bool = None,
):
    """List time entries with optional filtering.

    Args:
        user_id: Filter by user ID
        from_date: Only return time entries with a spent_date on or after the given date (YYYY-MM-DD)
        to_date: Only return time entries with a spent_date on or before the given date (YYYY-MM-DD)
        is_running: Pass true to only return running time entries and false to return non-running time entries
        is_billable: Pass true to only return billable time entries and false to return non-billable time entries
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
    if is_billable is not None:
        params["is_billable"] = "true" if is_billable else "false"

    response = await harvest_request("time_entries", params)
    return json.dumps(response, indent=2)


@mcp.tool()
async def create_time_entry(
    project_id: int, task_id: int, spent_date: str, hours: float, notes: str = None
):
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
        "hours": hours,
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
    response = await harvest_request(
        f"time_entries/{time_entry_id}/stop", method="PATCH"
    )
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


@mcp.tool()
async def get_unsubmitted_timesheets(
    user_id: int = None,
    from_date: str = None,
    to_date: str = None,
    page: int = None,
    per_page: int = None,
):
    """Get unsubmitted timesheets (time entries that haven't been submitted for approval).

    This function queries for time entries that are not yet closed/submitted, which typically
    means they are still editable and haven't been submitted for approval or invoicing.

    Args:
        user_id: Filter by specific user ID (optional)
        from_date: Only return time entries with a spent_date on or after the given date (YYYY-MM-DD)
        to_date: Only return time entries with a spent_date on or before the given date (YYYY-MM-DD)
        page: The page number for pagination
        per_page: The number of records to return per page (1-2000)
    """
    params = {}
    if user_id is not None:
        params["user_id"] = str(user_id)
    if from_date is not None:
        params["from"] = from_date
    if to_date is not None:
        params["to"] = to_date
    if page is not None:
        params["page"] = str(page)
    if per_page is not None:
        params["per_page"] = str(per_page)
    else:
        params["per_page"] = "200"

    # Get all time entries first
    response = await harvest_request("time_entries", params)

    # Filter for unsubmitted entries (those that are not closed)
    unsubmitted_entries = []
    if "time_entries" in response:
        for entry in response["time_entries"]:
            # Time entries that are not closed are considered unsubmitted
            if not entry.get("is_closed", False):
                unsubmitted_entries.append(entry)

    # Create a response structure similar to the original API response
    filtered_response = {
        "time_entries": unsubmitted_entries,
        "per_page": response.get("per_page", len(unsubmitted_entries)),
        "total_pages": 1,  # Simplified since we're filtering client-side
        "total_entries": len(unsubmitted_entries),
        "next_page": None,
        "previous_page": None,
        "page": response.get("page", 1),
        "links": response.get("links", {})
    }

    return json.dumps(filtered_response, indent=2)


@mcp.tool()
async def list_estimates(
    client_id: int = None,
    updated_since: str = None,
    from_date: str = None,
    to_date: str = None,
    state: str = None,
    page: int = None,
    per_page: int = None,
):
    """List estimates with optional filtering.

    Args:
        client_id: Filter by client ID
        updated_since: Only return estimates updated after the given date and time (ISO 8601 format)
        from_date: Only return estimates with an issue_date on or after the given date (YYYY-MM-DD)
        to_date: Only return estimates with an issue_date on or before the given date (YYYY-MM-DD)
        state: Filter by estimate state (draft, sent, accepted, declined)
        page: The page number for pagination
        per_page: The number of records to return per page (1-2000)
    """
    params = {}
    if client_id is not None:
        params["client_id"] = str(client_id)
    if updated_since is not None:
        params["updated_since"] = updated_since
    if from_date is not None:
        params["from"] = from_date
    if to_date is not None:
        params["to"] = to_date
    if state is not None:
        params["state"] = state
    if page is not None:
        params["page"] = str(page)
    if per_page is not None:
        params["per_page"] = str(per_page)
    else:
        params["per_page"] = "200"

    response = await harvest_request("estimates", params)
    return json.dumps(response, indent=2)


@mcp.tool()
async def get_estimate_details(estimate_id: int):
    """Get detailed information about a specific estimate.

    Args:
        estimate_id: The ID of the estimate to retrieve
    """
    response = await harvest_request(f"estimates/{estimate_id}")
    return json.dumps(response, indent=2)


@mcp.tool()
async def create_estimate(
    client_id: int,
    subject: str = None,
    notes: str = None,
    currency: str = None,
    issue_date: str = None,
    purchase_order: str = None,
    tax: float = None,
    tax2: float = None,
    line_items: str = None,
):
    """Create a new estimate.

    Args:
        client_id: The ID of the client for whom the estimate is being created (required)
        subject: The estimate subject
        notes: Any additional notes to include on the estimate
        currency: The currency used by the estimate (defaults to client's currency)
        issue_date: Date the estimate was issued (YYYY-MM-DD, defaults to today)
        purchase_order: The purchase order number
        tax: First tax percentage (0-100)
        tax2: Second tax percentage (0-100)
        line_items: JSON string of line items array. Each item should have: kind (required), description (optional), unit_price (required), quantity (optional, defaults to 1), taxed (optional, defaults to false), taxed2 (optional, defaults to false). Example: '[{"kind": "Service", "description": "Web Development", "unit_price": 100.0, "quantity": 10, "taxed": false}]'
    """
    params = {"client_id": client_id}

    if subject is not None:
        params["subject"] = subject
    if notes is not None:
        params["notes"] = notes
    if currency is not None:
        params["currency"] = currency
    if issue_date is not None:
        params["issue_date"] = issue_date
    if purchase_order is not None:
        params["purchase_order"] = purchase_order
    if tax is not None:
        params["tax"] = tax
    if tax2 is not None:
        params["tax2"] = tax2

    if line_items is not None:
        try:
            parsed_line_items = json.loads(line_items)
            params["line_items"] = parsed_line_items
        except json.JSONDecodeError:
            raise ValueError("line_items must be a valid JSON string")

    response = await harvest_request("estimates", params, method="POST")
    return json.dumps(response, indent=2)


@mcp.tool()
async def update_estimate(
    estimate_id: int,
    client_id: int = None,
    subject: str = None,
    notes: str = None,
    currency: str = None,
    issue_date: str = None,
    purchase_order: str = None,
    tax: float = None,
    tax2: float = None,
    line_items: str = None,
):
    """Update an existing estimate.

    Args:
        estimate_id: The ID of the estimate to update (required)
        client_id: The ID of the client for whom the estimate is being created
        subject: The estimate subject
        notes: Any additional notes to include on the estimate
        currency: The currency used by the estimate
        issue_date: Date the estimate was issued (YYYY-MM-DD)
        purchase_order: The purchase order number
        tax: First tax percentage (0-100)
        tax2: Second tax percentage (0-100)
        line_items: JSON string of line items array. Each item should have: kind (required), description (optional), unit_price (required), quantity (optional, defaults to 1), taxed (optional, defaults to false), taxed2 (optional, defaults to false). Example: '[{"kind": "Service", "description": "Web Development", "unit_price": 100.0, "quantity": 10, "taxed": false}]'
    """
    params = {}

    if client_id is not None:
        params["client_id"] = client_id
    if subject is not None:
        params["subject"] = subject
    if notes is not None:
        params["notes"] = notes
    if currency is not None:
        params["currency"] = currency
    if issue_date is not None:
        params["issue_date"] = issue_date
    if purchase_order is not None:
        params["purchase_order"] = purchase_order
    if tax is not None:
        params["tax"] = tax
    if tax2 is not None:
        params["tax2"] = tax2

    if line_items is not None:
        try:
            parsed_line_items = json.loads(line_items)
            params["line_items"] = parsed_line_items
        except json.JSONDecodeError:
            raise ValueError("line_items must be a valid JSON string")

    response = await harvest_request(f"estimates/{estimate_id}", params, method="PATCH")
    return json.dumps(response, indent=2)


@mcp.tool()
async def delete_estimate(estimate_id: int):
    """Delete an estimate. This action is not reversible.

    Args:
        estimate_id: The ID of the estimate to delete
    """
    response = await harvest_request(f"estimates/{estimate_id}", method="DELETE")
    if response is None:
        return json.dumps({"message": "Estimate successfully deleted"}, indent=2)
    return json.dumps(response, indent=2)


@mcp.tool()
async def add_line_item_to_estimate(
    estimate_id: int,
    kind: str,
    unit_price: float,
    description: str = None,
    quantity: int = None,
    taxed: bool = None,
    taxed2: bool = None,
):
    """Add a new line item to an existing estimate.

    Args:
        estimate_id: The ID of the estimate to add the line item to (required)
        kind: The category name for the line item (required, e.g., "Service", "Product")
        unit_price: The unit price for this line item (required)
        description: Optional description of the line item
        quantity: The quantity for this line item (defaults to 1)
        taxed: Whether this line item is subject to the first tax (defaults to false)
        taxed2: Whether this line item is subject to the second tax (defaults to false)
    """
    # First, get the current estimate to preserve existing line items
    current_estimate = await harvest_request(f"estimates/{estimate_id}")

    # Build the new line item
    new_line_item = {
        "kind": kind,
        "unit_price": unit_price
    }

    if description is not None:
        new_line_item["description"] = description
    if quantity is not None:
        new_line_item["quantity"] = quantity
    if taxed is not None:
        new_line_item["taxed"] = taxed
    if taxed2 is not None:
        new_line_item["taxed2"] = taxed2

    # Get existing line items or initialize empty list
    existing_line_items = current_estimate.get("line_items", [])

    # Add the new line item to the existing ones
    updated_line_items = existing_line_items + [new_line_item]

    # Update the estimate with the new line items array
    params = {"line_items": updated_line_items}

    response = await harvest_request(f"estimates/{estimate_id}", params, method="PATCH")
    return json.dumps(response, indent=2)


@mcp.tool()
async def update_line_item_in_estimate(
    estimate_id: int,
    line_item_id: int,
    kind: str = None,
    unit_price: float = None,
    description: str = None,
    quantity: int = None,
    taxed: bool = None,
    taxed2: bool = None,
):
    """Update an existing line item in an estimate.

    Args:
        estimate_id: The ID of the estimate containing the line item (required)
        line_item_id: The ID of the line item to update (required)
        kind: The category name for the line item (e.g., "Service", "Product")
        unit_price: The unit price for this line item
        description: Description of the line item
        quantity: The quantity for this line item
        taxed: Whether this line item is subject to the first tax
        taxed2: Whether this line item is subject to the second tax
    """
    # First, get the current estimate to preserve other line items
    current_estimate = await harvest_request(f"estimates/{estimate_id}")

    # Get existing line items
    existing_line_items = current_estimate.get("line_items", [])

    # Find and update the specific line item
    updated_line_items = []
    line_item_found = False

    for item in existing_line_items:
        if item.get("id") == line_item_id:
            line_item_found = True
            # Update the line item with new values
            updated_item = {"id": line_item_id}

            # Use new values if provided, otherwise keep existing
            updated_item["kind"] = kind if kind is not None else item.get("kind")
            updated_item["unit_price"] = unit_price if unit_price is not None else item.get("unit_price")

            if description is not None:
                updated_item["description"] = description
            elif "description" in item:
                updated_item["description"] = item["description"]

            if quantity is not None:
                updated_item["quantity"] = quantity
            elif "quantity" in item:
                updated_item["quantity"] = item["quantity"]

            if taxed is not None:
                updated_item["taxed"] = taxed
            elif "taxed" in item:
                updated_item["taxed"] = item["taxed"]

            if taxed2 is not None:
                updated_item["taxed2"] = taxed2
            elif "taxed2" in item:
                updated_item["taxed2"] = item["taxed2"]

            updated_line_items.append(updated_item)
        else:
            # Keep other line items unchanged
            updated_line_items.append(item)

    if not line_item_found:
        raise ValueError(f"Line item with ID {line_item_id} not found in estimate {estimate_id}")

    # Update the estimate with the modified line items array
    params = {"line_items": updated_line_items}

    response = await harvest_request(f"estimates/{estimate_id}", params, method="PATCH")
    return json.dumps(response, indent=2)


@mcp.tool()
async def delete_line_item_from_estimate(estimate_id: int, line_item_id: int):
    """Delete a line item from an estimate.

    Args:
        estimate_id: The ID of the estimate containing the line item (required)
        line_item_id: The ID of the line item to delete (required)
    """
    # First, get the current estimate to preserve other line items
    current_estimate = await harvest_request(f"estimates/{estimate_id}")

    # Get existing line items
    existing_line_items = current_estimate.get("line_items", [])

    # Build updated line items array with the _destroy flag for the item to delete
    updated_line_items = []
    line_item_found = False

    for item in existing_line_items:
        if item.get("id") == line_item_id:
            line_item_found = True
            # Mark this item for deletion
            updated_line_items.append({
                "id": line_item_id,
                "_destroy": True
            })
        else:
            # Keep other line items unchanged
            updated_line_items.append(item)

    if not line_item_found:
        raise ValueError(f"Line item with ID {line_item_id} not found in estimate {estimate_id}")

    # Update the estimate with the modified line items array
    params = {"line_items": updated_line_items}

    response = await harvest_request(f"estimates/{estimate_id}", params, method="PATCH")
    return json.dumps(response, indent=2)


if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport="stdio")
