from fastapi import APIRouter, Depends

from app.core.security import get_current_user_id
from app.db.supabase_client import supabase
from app.models.schemas import Department

router = APIRouter(tags=["departments"])


@router.get("/departments", response_model=list[Department])
def list_departments(user_id=Depends(get_current_user_id)):
    result = supabase.table("departments").select("*").execute()
    return result.data
