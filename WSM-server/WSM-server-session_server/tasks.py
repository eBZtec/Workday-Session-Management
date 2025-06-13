import argparse
from enum import Enum
import asyncio

from src.tasks import task_configure_grace_logon_hours


class TasksDefined(str, Enum):
    GRACE_LOGON_TASK = "GRACE_LOGON_TASK"


async def task_executor():
    parser = argparse.ArgumentParser(
        description="WSM task executor."
    )
    parser.add_argument(
        "-n",
        "--name",
        type=str,
        choices=[s.value for s in TasksDefined],
        required=True,
        help=f"Task name to execute: {', '.join(s.value for s in TasksDefined)}"
    )
    args = parser.parse_args()

    if args.name == TasksDefined.GRACE_LOGON_TASK:
        await task_configure_grace_logon_hours.execute()


if __name__ == "__main__":
    asyncio.run(task_executor())