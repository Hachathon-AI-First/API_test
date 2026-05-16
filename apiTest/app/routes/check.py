from fastapi import APIRouter

router = APIRouter()

@router.get("/mcp-test")
async def mcp_test():
    return {"message": "Rota MCP de teste funcionando"}
