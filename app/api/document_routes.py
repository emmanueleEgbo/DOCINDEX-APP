"""
Document API routes.

Route handlers are intentionally thin:
  - Validate input (Pydantic handles this automatically)
  - Call the service
  - Return the response or raise HTTPException

All business logic and DB logic lives in services and repositories.
"""
import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

