from fastapi import HTTPException, status

from src.config import config
from src.config.wsm_logger import logger
from src.models.schema.agent_model import AgentActionSchema
from src.services.rabbitmq.rabbitmq_send_message_service import RabbitMQSendMessageService


class AgentActionController:

    @staticmethod
    async def execute(payload: AgentActionSchema):
        try:
            rabbitmq_send_message = RabbitMQSendMessageService(queue_name=config.WSM_AGENT_NOTIFICATION_QUEUE)

            message = payload.model_dump()
            rabbitmq_send_message.send(message)
            logger.info(f"Message {payload} sent successfully")
        except Exception as e:
            logger.error(f"Could not send action {payload.model_dump()}, reason: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Could not send action {payload.model_dump()}, reason: {e}"
            )