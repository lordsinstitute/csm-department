from fastapi import APIRouter, Depends

from app.core.security import get_current_user_id
from app.db.supabase_client import supabase
from app.models.schemas import Machine

router = APIRouter(tags=["machines"])


@router.get("/departments/{department_id}/machines", response_model=list[Machine])
def list_machines(department_id: str, user_id=Depends(get_current_user_id)):
    result = (
        supabase.table("machines")
        .select("*")
        .eq("department_id", department_id)
        .execute()
    )
    return result.data
