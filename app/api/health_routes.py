from fastapi import APIRouter, Depends, HTTPException, status


health_check_router = APIRouter(prefix="/v1/health_check", tags=["health_check"])


@health_check_router.get("")
async def health_check():
    return {
        "service": "DocMind API",
        "version": "1.0.0",
        "docs": "/docs",
    }