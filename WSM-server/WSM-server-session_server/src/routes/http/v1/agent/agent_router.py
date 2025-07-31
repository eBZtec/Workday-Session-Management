from fastapi import APIRouter, Depends

from src.controllers.agent.agent_action_controller import AgentActionController
from src.models.schema.agent_model import AgentActionSchema
from src.services.auth_service import AuthService

auth_service  = AuthService()

router = APIRouter(dependencies=[Depends(auth_service.get_current_user)])


@router.post("/action")
async def action(payload: AgentActionSchema):
    await AgentActionController.execute(payload)