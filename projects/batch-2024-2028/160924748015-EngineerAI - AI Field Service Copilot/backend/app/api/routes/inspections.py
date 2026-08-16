from fastapi import APIRouter, Depends, HTTPException

from app.core.security import get_current_user_id
from app.db.supabase_client import supabase
from app.models.schemas import (
    AnswersPayload,
    CreateInspectionRequest,
    Inspection,
    InspectionSummary,
    ReportRequest,
)

router = APIRouter(tags=["inspections"])


@router.post("/inspections", response_model=Inspection)
def create_inspection(body: CreateInspectionRequest, user_id=Depends(get_current_user_id)):
    row = {
        "user_id": str(user_id),
        "machine_id_fk": str(body.machine_id),
        "problem_id_fk": str(body.problem_id),
        "status": "draft",
    }
    result = supabase.table("inspections").insert(row).execute()
    return result.data[0]


@router.get("/inspections", response_model=list[InspectionSummary])
def list_inspections(user_id=Depends(get_current_user_id)):
    result = (
        supabase.table("inspections")
        .select("id,machine_id_fk,problem_id_fk,status,created_at,updated_at")
        .eq("user_id", str(user_id))
        .execute()
    )
    return result.data


@router.get("/inspections/{inspection_id}", response_model=Inspection)
def get_inspection(inspection_id: str, user_id=Depends(get_current_user_id)):
    result = (
        supabase.table("inspections")
        .select("*")
        .eq("id", inspection_id)
        .eq("user_id", str(user_id))
        .execute()
    )
    if not result.data:
        raise HTTPException(status_code=404, detail="Inspection not found")
    return result.data[0]


@router.post("/inspections/{inspection_id}/vision-analysis")
def vision_analysis(inspection_id: str, user_id=Depends(get_current_user_id)):
    raise HTTPException(status_code=501, detail="Not implemented")


@router.post("/inspections/{inspection_id}/questions")
def questions(inspection_id: str, user_id=Depends(get_current_user_id)):
    raise HTTPException(status_code=501, detail="Not implemented")


@router.post("/inspections/{inspection_id}/answers")
def answers(inspection_id: str, body: AnswersPayload, user_id=Depends(get_current_user_id)):
    raise HTTPException(status_code=501, detail="Not implemented")


@router.post("/inspections/{inspection_id}/diagnose")
def diagnose(inspection_id: str, user_id=Depends(get_current_user_id)):
    raise HTTPException(status_code=501, detail="Not implemented")


@router.post("/inspections/{inspection_id}/repair-plan")
def repair_plan(inspection_id: str, user_id=Depends(get_current_user_id)):
    raise HTTPException(status_code=501, detail="Not implemented")


@router.post("/inspections/{inspection_id}/report")
def report(inspection_id: str, body: ReportRequest, user_id=Depends(get_current_user_id)):
    raise HTTPException(status_code=501, detail="Not implemented")
