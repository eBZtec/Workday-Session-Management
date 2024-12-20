from fastapi import APIRouter

from src.controllers.agent.agent_action_controller import AgentActionController
from src.models.schema.agent_model import AgentActionSchema

router = APIRouter()


@router.post("/action")
async def action(payload: AgentActionSchema):
    await AgentActionController.execute(payload)