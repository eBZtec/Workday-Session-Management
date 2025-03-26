from pydantic import BaseModel


class AgentActionSchema(BaseModel):
    action: str
    user: str
    title: str
    message: str