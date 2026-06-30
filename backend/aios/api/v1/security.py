"""AIOS Security Endpoints."""

import structlog
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query

logger = structlog.get_logger(__name__)

router = APIRouter()

# In-memory store for now
_audit_logs: dict = {}
_users: dict = {}


@router.get("/audit-log")
async def list_audit_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    action: Optional[str] = None,
    user_id: Optional[str] = None,
) -> List[dict]:
    """List audit logs."""
    logs = list(_audit_logs.values())
    if action:
        logs = [l for l in logs if l.get("action") == action]
    if user_id:
        logs = [l for l in logs if l.get("user_id") == user_id]
    return logs[skip : skip + limit]


@router.post("/audit-log", status_code=201)
async def create_audit_log(log_entry: dict) -> dict:
    """Create an audit log entry."""
    import uuid
    from datetime import datetime
    
    log_id = str(uuid.uuid4())
    log_data = {
        "id": log_id,
        "action": log_entry.get("action"),
        "user_id": log_entry.get("user_id"),
        "resource": log_entry.get("resource"),
        "details": log_entry.get("details", {}),
        "ip_address": log_entry.get("ip_address"),
        "timestamp": datetime.utcnow().isoformat(),
    }
    _audit_logs[log_id] = log_data
    return log_data


@router.get("/users")
async def list_users() -> List[dict]:
    """List all users."""
    return list(_users.values())


@router.post("/users", status_code=201)
async def create_user(user: dict) -> dict:
    """Create a new user."""
    import uuid
    from datetime import datetime
    
    from aios.core.security import get_password_hash
    
    user_id = str(uuid.uuid4())
    user_data = {
        "id": user_id,
        "username": user.get("username"),
        "email": user.get("email"),
        "hashed_password": get_password_hash(user.get("password", "")),
        "roles": user.get("roles", ["user"]),
        "is_active": True,
        "created_at": datetime.utcnow().isoformat(),
    }
    _users[user_id] = user_data
    logger.info("User created", user_id=user_id, username=user.get("username"))
    return {k: v for k, v in user_data.items() if k != "hashed_password"}
