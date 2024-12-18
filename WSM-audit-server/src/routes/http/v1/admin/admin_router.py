from typing import Union, List
from src.controllers.report.report_controller import ReportController
from fastapi import APIRouter
import json

router = APIRouter()


@router.get("/")
async def report(filter: str, page:int = 1, page_size:int = 10):
    filter = json.loads(filter)
    result =await ReportController.execute(filter,page,page_size)
    return result