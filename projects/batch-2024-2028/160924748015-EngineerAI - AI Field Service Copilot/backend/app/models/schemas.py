from datetime import datetime
from typing import Literal, Optional
from uuid import UUID

from pydantic import BaseModel

Status = Literal["draft", "analyzing", "diagnosed", "repairing", "complete"]


# ---- Reference / table row models ----

class Department(BaseModel):
    id: UUID
    name: str


class Machine(BaseModel):
    id: UUID
    department_id: UUID
    name: str
    image_url: Optional[str] = None


class Problem(BaseModel):
    id: UUID
    machine_id: UUID
    name: str
    description: Optional[str] = None


# ---- AI module output / core models ----

class VisionResult(BaseModel):
    visible_issues: list[str]
    damaged_components: list[str]
    severity_estimate: Literal["low", "medium", "high"]
    machine_confirmed: bool


class Hypothesis(BaseModel):
    cause: str
    confidence: float
    reasoning: str


class InvestigationResult(BaseModel):
    hypotheses: list[Hypothesis]


class Question(BaseModel):
    text: str
    question_type: Literal["multiple_choice", "free_text"]
    options: Optional[list[str]] = None


class QuestionSet(BaseModel):
    questions: list[Question]


class AnswerEntry(BaseModel):
    question: str
    answer: str


class AnswersPayload(BaseModel):
    answers: list[AnswerEntry]


class RuledOutHypothesis(BaseModel):
    cause: str
    reason: str


class ReasoningResult(BaseModel):
    root_cause: str
    confidence: float
    explanation: str
    ruled_out: list[RuledOutHypothesis]
    cited_sources: list[str]


class DiagnosisResult(BaseModel):
    hypotheses: list[Hypothesis]
    root_cause: str
    confidence: float
    explanation: str
    ruled_out: list[RuledOutHypothesis]
    cited_sources: list[str]


class RepairStep(BaseModel):
    step_number: int
    instruction: str
    safety_warning: Optional[str] = None


class SparePart(BaseModel):
    part_name: str
    spec: str


class RepairPlan(BaseModel):
    steps: list[RepairStep]
    tools: list[str]
    est_minutes: int
    safety_warnings: list[str]
    spare_parts: list[SparePart]


class ChecklistItem(BaseModel):
    step: str
    checked: bool


class ReportRequest(BaseModel):
    checklist_state: list[ChecklistItem]


# ---- Inspection row ----

class Inspection(BaseModel):
    id: UUID
    user_id: UUID
    machine_id_fk: UUID
    problem_id_fk: UUID
    photo_url: Optional[str] = None
    answers: Optional[AnswersPayload] = None
    vision_result: Optional[VisionResult] = None
    diagnosis: Optional[DiagnosisResult] = None
    repair_plan: Optional[RepairPlan] = None
    checklist_state: Optional[list[ChecklistItem]] = None
    pdf_url: Optional[str] = None
    status: Status
    created_at: datetime
    updated_at: datetime


class InspectionSummary(BaseModel):
    id: UUID
    machine_id_fk: UUID
    problem_id_fk: UUID
    status: Status
    created_at: datetime
    updated_at: datetime


# ---- Request/response wrappers per endpoint ----

class CreateInspectionRequest(BaseModel):
    machine_id: UUID
    problem_id: UUID


CreateInspectionResponse = Inspection


class VisionAnalysisRequest(BaseModel):
    photo_url: str


VisionAnalysisResponse = VisionResult
QuestionsResponse = QuestionSet
AnswersRequest = AnswersPayload
AnswersResponse = AnswersPayload
DiagnoseResponse = DiagnosisResult
RepairPlanResponse = RepairPlan


class ReportResponse(BaseModel):
    pdf_url: str


InspectionListResponse = list[InspectionSummary]
InspectionDetailResponse = Inspection


class ErrorEnvelope(BaseModel):
    error_code: str
    message: str
