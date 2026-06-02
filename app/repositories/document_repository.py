"""
All database operations for the Document model.

The repository pattern keeps DB queries out of route handlers and services.
Services call the repository. Routes call services. Nothing leaks.
"""
import logging
from typing import List, Optional
from datetime import datetime