from fastapi import APIRouter, Query, HTTPException, Depends
from typing import Union, List
from pydantic import BaseModel
import json
from src.controllers.report.report_controller import ReportController
from src.services.auth_service import AuthService

auth_service = AuthService()

router = APIRouter(dependencies=[Depends(auth_service.get_current_user)])

class FilterItem(BaseModel):
    field: str
    operator: str
    value: Union[str, int, float, bool]

class AuditQueryRequest(BaseModel):
    filters: List[FilterItem]
    page: int = 1
    page_size: int = 10

@router.get("/")
async def report(filter: str = Query(...), page: int = 1, page_size: int = 10):
    """
    GET com filtro como string JSON no parâmetro `filter`
    """
    try:
        filter_parsed = json.loads(filter)
        result = await ReportController.execute(filter_parsed, page, page_size)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erro no filtro: {e}")

"""
@router.post("/query")
async def report_post(payload: AuditQueryRequest):
    
    #POST com corpo JSON estruturado
    
    try:
        result = await ReportController.execute(
            filter=payload.filters,
            page=payload.page,
            page_size=payload.page_size
        )
        return {
            "pagination": {
                "page": payload.page,
                "page_size": payload.page_size
            },
            "results": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno: {e}")
"""