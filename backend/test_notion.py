"""
Quick test to verify Notion API key and database connection.
Run from the backend directory with the venv active:
    python test_notion.py
"""
import os
from dotenv import load_dotenv
from notion_client import Client
from notion_client.errors import APIResponseError

load_dotenv()

api_key = os.environ.get("NOTION_API_KEY")
database_id = os.environ.get("NOTION_DATABASE_ID")

print("=== Notion Connection Test ===\n")

# 1. Check env vars are set
if not api_key:
    print("FAIL  NOTION_API_KEY is not set in .env")
    exit(1)
if not database_id:
    print("FAIL  NOTION_DATABASE_ID is not set in .env")
    exit(1)

print(f"OK    NOTION_API_KEY found  ({api_key[:8]}...)")
print(f"OK    NOTION_DATABASE_ID found  ({database_id})\n")

client = Client(auth=api_key)

# 2. Check the API key is valid
print("Checking API key...")
try:
    client.users.me()
    print("OK    API key is valid\n")
except APIResponseError as e:
    print(f"FAIL  Invalid API key: {e.code} - {e.message}")
    exit(1)

# 3. Check the database is accessible
print("Checking database access...")
try:
    db = client.databases.retrieve(database_id=database_id)
    title = db.get("title", [{}])
    db_name = title[0].get("plain_text", "(untitled)") if title else "(untitled)"
    print(f"OK    Database found: '{db_name}'\n")
except APIResponseError as e:
    if e.code == "object_not_found":
        print("FAIL  Database not found or not shared with your integration.")
        print("\nTo fix this:")
        print("  1. Open the database in Notion")
        print("  2. Click '...' (top-right) → 'Connections'")
        print("  3. Search for your integration and click 'Confirm'")
    elif e.code == "unauthorized":
        print("FAIL  Integration does not have access to this database.")
    else:
        print(f"FAIL  {e.code}: {e.message}")
    exit(1)

# 4. Check database has expected properties
print("Checking database properties...")
props = db.get("properties", {})
required = ["Title", "Category", "Channel", "URL", "Date Watched"]
missing = [p for p in required if p not in props]

if missing:
    print(f"WARN  Missing properties: {', '.join(missing)}")
    print("      The app may fail when writing pages.")
else:
    print(f"OK    All required properties found: {', '.join(required)}\n")

print("=== All checks passed. Notion is connected. ===")
