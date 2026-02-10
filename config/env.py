"""
Environment configuration for News Trading Bot V1.0

This file loads MT5 credentials from environment variables.
Create a .env file in the project root with:

MT5_LOGIN=your_account_number
MT5_PASSWORD=your_password
MT5_SERVER=YourBroker-Demo

IMPORTANT: Never commit .env file to version control!
"""

import os
from pathlib import Path
from typing import Optional

# Try to load .env file if it exists
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)
except ImportError:
    # python-dotenv not installed, skip
    pass


def get_mt5_credentials() -> tuple[Optional[int], Optional[str], Optional[str]]:
    """
    Get MT5 credentials from environment variables
    
    Returns:
        Tuple of (login, password, server) or (None, None, None)
    
    Note:
        If credentials are not set, the bot will connect to
        the already-logged-in MT5 terminal (recommended method)
    """
    login = os.getenv('MT5_LOGIN')
    password = os.getenv('MT5_PASSWORD')
    server = os.getenv('MT5_SERVER')
    
    if login:
        login = int(login)
    
    return login, password, server


if __name__ == "__main__":
    login, password, server = get_mt5_credentials()
    
    if login:
        print(f"MT5 Credentials loaded:")
        print(f"  Login: {login}")
        print(f"  Password: {'*' * len(password) if password else 'Not set'}")
        print(f"  Server: {server}")
    else:
        print("No MT5 credentials in environment")
        print("Bot will connect to already-logged-in MT5 terminal")
