import uuid
from contextvars import ContextVar

from sqlalchemy.ext.asyncio import AsyncSession

session_context: ContextVar[AsyncSession | None] = ContextVar("session", default=None)
org_id_context: ContextVar[uuid.UUID | None] = ContextVar("org_id", default=None)

def get_current_session() -> AsyncSession:
    # Get the current active database session
    session = session_context.get()
    if not session:
        raise RuntimeError("No active session found in context.")
    return session

def get_current_org_id() -> uuid.UUID:
    # Get the current active org ID from context
    org_id = org_id_context.get()
    if not org_id:
        raise RuntimeError("No organization ID found in context.")
    return org_id

