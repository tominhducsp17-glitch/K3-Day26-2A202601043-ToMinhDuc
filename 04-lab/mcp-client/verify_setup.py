#!/usr/bin/env python3
"""
Verification script for Weather Agent setup
Checks if all components are configured correctly
"""
import os
import sys
from pathlib import Path

# Ensure UTF-8 output encoding on Windows
if sys.stdout:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if sys.stderr:
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

def check_environment():
    """Check if .env file exists and is configured"""
    print("[*] Checking environment configuration...")
    
    env_file = Path(".env")
    if not env_file.exists():
        print("[FAIL] .env file not found")
        print("   Run: echo 'GOOGLE_API_KEY=your_key' > .env")
        return False
    
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key or api_key == "your_google_api_key_here":
        print("[FAIL] GOOGLE_API_KEY not configured in .env")
        print("   Get key from: https://aistudio.google.com/apikey")
        return False
    
    print(f"[PASS] GOOGLE_API_KEY configured ({api_key[:10]}...)")
    return True

def check_dependencies():
    """Check if required packages are installed"""
    print("\n[*] Checking dependencies...")
    
    required_packages = [
        ("google.adk", "Google ADK"),
        ("google.generativeai", "Google Generative AI"),
        ("mcp", "MCP"),
        ("fastmcp", "FastMCP"),
        ("dotenv", "python-dotenv"),
        ("httpx", "httpx"),
    ]
    
    all_installed = True
    for package, name in required_packages:
        try:
            __import__(package)
            print(f"[PASS] {name}")
        except ImportError:
            print(f"[FAIL] {name} not installed")
            all_installed = False
    
    return all_installed

def check_agent_structure():
    """Check if agent directory structure is correct"""
    print("\n[*] Checking agent structure...")
    
    required_files = [
        "weather_agent/agent.py",
        "weather_agent/__init__.py",
    ]
    
    all_exist = True
    for file_path in required_files:
        path = Path(file_path)
        if path.exists():
            print(f"[PASS] {file_path}")
        else:
            print(f"[FAIL] {file_path} not found")
            all_exist = False
    
    return all_exist

def check_mcp_server():
    """Check if MCP server is accessible"""
    print("\n[*] Checking MCP server connectivity...")
    
    server_url = "http://localhost:8085/mcp"
    
    try:
        import httpx
        import asyncio
        
        async def test_connection():
            async with httpx.AsyncClient() as client:
                response = await client.get(server_url, timeout=5.0)
                return response.status_code
        
        status_code = asyncio.run(test_connection())
        
        if status_code in [200, 404, 405]:
            print(f"[PASS] MCP server reachable at {server_url} (HTTP {status_code})")
            return True
        else:
            print(f"[WARN] MCP server returned status {status_code}")
            return True
            
    except Exception as e:
        print(f"[INFO] Local MCP server not running yet: {e}")
        print("       (You can start it with: cd ../mcp-server && uv run python weather.py)")
        return True

def check_agent_import():
    """Try to import the agent"""
    print("\n[*] Checking agent import...")
    
    try:
        import warnings
        warnings.filterwarnings("ignore")
        
        from weather_agent import root_agent
        print(f"[PASS] Agent imported successfully: {root_agent.name}")
        print(f"       Model: {root_agent.model}")
        return True
    except Exception as e:
        print(f"[FAIL] Failed to import agent: {e}")
        return False

def main():
    """Run all verification checks"""
    print("=" * 60)
    print("Weather Agent Setup Verification")
    print("=" * 60)
    print()
    
    checks = [
        check_environment(),
        check_dependencies(),
        check_agent_structure(),
        check_mcp_server(),
        check_agent_import(),
    ]
    
    print("\n" + "=" * 60)
    if all(checks):
        print("[SUCCESS] All checks passed!")
        print("\nReady to start!")
        print("   1. In terminal 1: cd ../mcp-server && uv run python weather.py")
        print("   2. In terminal 2: cd mcp-client && uv run adk web")
        print("   3. Open: http://localhost:8000")
        return 0
    else:
        print("[FAIL] Some checks failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())