#!/usr/bin/env python3
"""
Command Line Interface for DMancipate DM Chatbot.

This module provides a lightweight CLI client for interacting with the DMancipate
DM chatbot API. It accepts an action and prompt as arguments and makes HTTP requests
to the running API server.

This CLI is completely independent of the DMancipate server code and only requires
basic HTTP client dependencies.
"""

import argparse
import json
import sys
import requests
from typing import Optional


class DMancipateCLI:
    """CLI client for DMancipate DM chatbot."""
    
    ALLOWED_ACTIONS = ["talk", "attack", "skill_check", "use_item", "look", "pick_up", "ask", "reset", "review", "use_skill"]
    DEFAULT_HOST = "localhost"
    DEFAULT_PORT = 5000
    
    def __init__(self, host: str = DEFAULT_HOST, port: int = DEFAULT_PORT):
        """Initialize the CLI client with API server details."""
        self.base_url = f"http://{host}:{port}"
    
    def send_request(self, action: str, prompt: str) -> Optional[str]:
        """
        Send a request to the DMancipate API.
        
        Args:
            action: The action to perform (must be one of ALLOWED_ACTIONS except 'reset')
            prompt: The prompt/message to send to the DM
            
        Returns:
            The response from the API, or None if there was an error
        """
        if action not in self.ALLOWED_ACTIONS or action == "reset":
            print(f"Error: Invalid action '{action}' for chat request.")
            print(f"Allowed actions: {', '.join([a for a in self.ALLOWED_ACTIONS if a != 'reset'])}")
            return None
        
        # Prepare the request payload
        payload = {
            "prompt": prompt,
            "action": action,
            "enable_stream": "False"  # CLI doesn't use streaming
        }
        
        try:
            # Make the API request
            response = requests.post(
                f"{self.base_url}/chat",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=600  # 10 minute timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get("result", "No response received")
            else:
                error_data = response.json() if response.headers.get("content-type") == "application/json" else {}
                error_msg = error_data.get("error", f"HTTP {response.status_code}")
                print(f"Error: {error_msg}")
                return None
                
        except requests.exceptions.ConnectionError:
            print(f"Error: Could not connect to DMancipate API at {self.base_url}")
            print("Make sure the DMancipate server is running.")
            return None
        except requests.exceptions.Timeout:
            print("Error: Request timed out. The DM might be thinking too hard!")
            return None
        except requests.exceptions.RequestException as e:
            print(f"Error: Request failed - {e}")
            return None
        except json.JSONDecodeError:
            print("Error: Invalid response from server")
            return None
    
    def reset_campaign(self) -> bool:
        """
        Reset the campaign by deleting all game history.
        
        Returns:
            True if reset was successful, False otherwise
        """
        try:
            # Make the DELETE request to reset campaign history
            response = requests.delete(
                f"{self.base_url}/chat",
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ {data.get('message', 'Campaign history reset successfully')}")
                return True
            else:
                error_data = response.json() if response.headers.get("content-type") == "application/json" else {}
                error_msg = error_data.get("error", f"HTTP {response.status_code}")
                print(f"Error: {error_msg}")
                return False
                
        except requests.exceptions.ConnectionError:
            print(f"Error: Could not connect to DMancipate API at {self.base_url}")
            print("Make sure the DMancipate server is running.")
            return False
        except requests.exceptions.Timeout:
            print("Error: Request timed out during reset operation")
            return False
        except requests.exceptions.RequestException as e:
            print(f"Error: Reset request failed - {e}")
            return False
        except json.JSONDecodeError:
            print("Error: Invalid response from server during reset")
            return False
    
    def check_health(self) -> bool:
        """
        Check if the API server is running and healthy.
        
        Returns:
            True if the server is healthy, False otherwise
        """
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="DMancipate CLI - Interact with your DM chatbot",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  dmancipate talk "Hello DM, what do I see around me?"
  dmancipate attack "I swing my sword at the goblin"
  dmancipate skill_check "I try to pick the lock"
  dmancipate look "I examine the mysterious door"
  dmancipate ask "What are the stats for a goblin?"
  dmancipate reset  # Deletes all campaign history

Available actions: talk, attack, skill_check, use_item, look, pick_up, ask, reset, review, use_skill
        """
    )
    
    parser.add_argument(
        "action",
        choices=DMancipateCLI.ALLOWED_ACTIONS,
        help="The action to perform"
    )
    
    parser.add_argument(
        "prompt",
        nargs="?" if "reset" in sys.argv else None,
        help="The message/prompt to send to the DM (not required for reset action)"
    )
    
    parser.add_argument(
        "--host",
        default=DMancipateCLI.DEFAULT_HOST,
        help=f"API server host (default: {DMancipateCLI.DEFAULT_HOST})"
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=DMancipateCLI.DEFAULT_PORT,
        help=f"API server port (default: {DMancipateCLI.DEFAULT_PORT})"
    )
    
    parser.add_argument(
        "--check-health",
        action="store_true",
        help="Check if the API server is running and exit"
    )
    
    args = parser.parse_args()
    
    # Initialize CLI client
    cli = DMancipateCLI(host=args.host, port=args.port)
    
    # Health check mode
    if args.check_health:
        if cli.check_health():
            print("✅ DMancipate API is running and healthy!")
            sys.exit(0)
        else:
            print("❌ DMancipate API is not responding")
            sys.exit(1)
    
    # Check if API is available before making the request
    if not cli.check_health():
        print("❌ DMancipate API is not responding. Make sure the server is running.")
        sys.exit(1)
    
    # Handle reset command separately
    if args.action == "reset":
        print("🗑️  Resetting campaign history...")
        print("⚠️  This will delete all game history. This action cannot be undone.")
        print("-" * 50)
        
        if cli.reset_campaign():
            print("🎯 Campaign has been reset to a fresh state!")
        else:
            sys.exit(1)
    else:
        # Validate that prompt is provided for non-reset actions
        if not args.prompt:
            print("Error: Prompt is required for this action.")
            print("Use 'dmancipate --help' for usage information.")
            sys.exit(1)
            
        # Send the regular chat request
        print(f"🎲 Sending '{args.action}' action to DM...")
        print(f"📝 Prompt: {args.prompt}")
        print("⏳ Waiting for DM response...")
        print("-" * 50)
        
        response = cli.send_request(args.action, args.prompt)
        
        if response:
            print("🎯 DM Response:")
            print(response)
        else:
            sys.exit(1)


if __name__ == "__main__":
    main() 