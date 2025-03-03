#!/usr/bin/env python3
"""
Command-line interface for the blog post generator
"""
import sys
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add the parent directory to the path so we can import the modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.gen_blog import main

if __name__ == "__main__":
    main()
