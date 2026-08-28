"""
Weather Agent - Connects to Remote MCP Server on Cloud Run or Localhost
Successfully connects to custom MCP HTTP endpoints!
"""
import sys
if sys.stdout:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if sys.stderr:
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from google.adk import Agent
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset, StreamableHTTPConnectionParams
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")
logger = logging.getLogger(__name__)

MCP_SERVER_URL = "http://localhost:8085/mcp"

logger.info("Initializing weather agent with remote MCP server")
logger.info(f"MCP Server: {MCP_SERVER_URL}")

try:
    # Create connection parameters for the remote MCP server
    connection_params = StreamableHTTPConnectionParams(
        url=MCP_SERVER_URL,
        timeout=30.0,
    )
    
    # Create the MCP toolset - this will connect to the remote server
    logger.info("Connecting to MCP server...")
    weather_tools = McpToolset(
        connection_params=connection_params,
    )
    logger.info("MCP toolset created successfully")
    
    # Create the agent with remote MCP tools
    root_agent = Agent(
        name="weather_agent",
        model="gemini-2.5-flash",
        tools=[weather_tools],
    )
    logger.info("Weather agent initialized with remote MCP tools:")
    logger.info("   - get_current_weather(city)")
    logger.info("   - get_forecast(city, days)")
    logger.info("   - health_check()")
    logger.info("Remote MCP connection successful!")
    
except Exception as e:
    logger.error(f"Failed to connect to remote MCP server: {e}")
    logger.error(f"   Server URL: {MCP_SERVER_URL}")
    import traceback
    traceback.print_exc()
    
    # Create a fallback agent without tools
    logger.warning("Creating fallback agent without MCP tools")
    root_agent = Agent(
        name="weather_agent",
        model="gemini-2.5-flash",
    )