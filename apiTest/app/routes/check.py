from typing import Optional
from uuid import uuid4

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/check", tags=["check"])


class MCPCreateRequest(BaseModel):
    name: str
    agent_name: str
    description: Optional[str] = None


class MCPResponse(BaseModel):
    mcp_id: str
    name: str
    agent_name: str
    status: str
    created: bool


@router.post("/mcp", response_model=MCPResponse)
def test_create_mcp(payload: MCPCreateRequest):
    """Rota para testar a criação de um MCP com um agente automatizado."""
    if not payload.name or not payload.agent_name:
        raise HTTPException(status_code=400, detail="Nome do MCP e agente são obrigatórios")

    mcp_id = str(uuid4())
    return MCPResponse(
        mcp_id=mcp_id,
        name=payload.name,
        agent_name=payload.agent_name,
        status="created",
        created=True,
    )
