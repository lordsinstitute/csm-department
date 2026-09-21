from fastapi import APIRouter, Depends

from app.core.security import get_current_user_id
from app.db.supabase_client import supabase
from app.models.schemas import Problem

router = APIRouter(tags=["problems"])


@router.get("/machines/{machine_id}/problems", response_model=list[Problem])
def list_problems(machine_id: str, user_id=Depends(get_current_user_id)):
    result = (
        supabase.table("problems")
        .select("*")
        .eq("machine_id", machine_id)
        .execute()
    )
    return result.data
