# EngineerAI — Frozen Contract

This file is the frozen contract for the entire project (per plan §2–4, §5–7). Backend and Flutter are both generated against it. Do not edit after manual review except by hand.

---

## 1. Supabase Postgres Schema

(plan §3, exact column names; types picked where the plan only implied them — flagged below)

### departments
| column | type |
|---|---|
| id | uuid, primary key, default gen_random_uuid() |
| name | text, not null |

### machines
| column | type |
|---|---|
| id | uuid, primary key, default gen_random_uuid() |
| department_id | uuid, not null, references departments(id) |
| name | text, not null |
| image_url | text, nullable |

### problems
| column | type |
|---|---|
| id | uuid, primary key, default gen_random_uuid() |
| machine_id | uuid, not null, references machines(id) |
| name | text, not null |
| description | text, nullable |

### inspections
| column | type |
|---|---|
| id | uuid, primary key, default gen_random_uuid() |
| user_id | uuid, not null (references auth.users(id)) |
| machine_id_fk | uuid, not null, references machines(id) |
| problem_id_fk | uuid, not null, references problems(id) |
| photo_url | text, nullable |
| answers | jsonb, nullable |
| vision_result | jsonb, nullable |
| diagnosis | jsonb, nullable |
| repair_plan | jsonb, nullable |
| checklist_state | jsonb, nullable |
| pdf_url | text, nullable |
| status | text, not null, default 'draft' (enum: draft / analyzing / diagnosed / repairing / complete) |
| created_at | timestamptz, not null, default now() |
| updated_at | timestamptz, not null, default now() |

DECISION: all `id` columns are `uuid` with `gen_random_uuid()` defaults (Supabase convention); the plan doesn't state a type explicitly. `status` is `text` with the 5 values from the plan's column comment, enforced via a CHECK constraint in the migration (Prompt 1.2), not a Postgres enum type, to keep the migration simple.

---

## 2. JSONB Column Shapes (also the AI module output schemas)

### `inspections.answers` → shape of `AnswersPayload`
| field | type |
|---|---|
| answers | list of { question: string, answer: string } |

Example:
```json
{
  "answers": [
    { "question": "Does the vibration change with motor speed?", "answer": "No, it stays constant." },
    { "question": "Is there any audible grinding or metallic noise?", "answer": "No" }
  ]
}
```

### `inspections.vision_result` → shape of `VisionResult`
| field | type |
|---|---|
| visible_issues | list of string |
| damaged_components | list of string |
| severity_estimate | string (low / medium / high) |
| machine_confirmed | boolean |

Example:
```json
{
  "visible_issues": ["visible surface rust near mounting base", "slight oil residue on housing"],
  "damaged_components": ["motor mounting bracket"],
  "severity_estimate": "medium",
  "machine_confirmed": true
}
```

### `inspections.diagnosis` → combined shape of `InvestigationResult` + `ReasoningResult`
| field | type |
|---|---|
| hypotheses | list of { cause: string, confidence: float (0-1), reasoning: string } |
| root_cause | string |
| confidence | float (0-1) |
| explanation | string |
| ruled_out | list of { cause: string, reason: string } |
| cited_sources | list of string (knowledge snippet titles) |

Example:
```json
{
  "hypotheses": [
    { "cause": "Rotor imbalance", "confidence": 0.6, "reasoning": "Vibration is constant across speeds, consistent with imbalance rather than misalignment." },
    { "cause": "Loose mounting bolts", "confidence": 0.3, "reasoning": "Visible surface rust near the mounting base suggests bolts may have loosened." },
    { "cause": "Bearing wear", "confidence": 0.1, "reasoning": "No grinding or metallic noise reported, making this less likely." }
  ],
  "root_cause": "Rotor imbalance",
  "confidence": 0.72,
  "explanation": "The constant-speed vibration pattern and absence of bearing noise point to rotor imbalance rather than a mounting or bearing issue. A balancing check is recommended before reassembly.",
  "ruled_out": [
    { "cause": "Bearing wear", "reason": "No grinding or metallic noise reported by technician." }
  ],
  "cited_sources": ["Rotor Imbalance", "Loose Mounting Bolts"]
}
```

DECISION: the plan's schema comment for `diagnosis` lists only "hypotheses, root cause, confidence, explanation", but Prompt 5.1 persists hypotheses under `diagnosis` and Prompt 5.2 additionally persists `ruled_out` and `cited_sources` into the same column. This spec merges all five into one `diagnosis` object rather than adding a second JSONB column, since the plan explicitly says reasoning writes into the existing `diagnosis` field.

### `inspections.repair_plan` → shape of `RepairPlan`
| field | type |
|---|---|
| steps | list of { step_number: int, instruction: string, safety_warning: string or null } |
| tools | list of string |
| est_minutes | int |
| safety_warnings | list of string (general/aggregate warnings) |
| spare_parts | list of { part_name: string, spec: string } |

Example:
```json
{
  "steps": [
    { "step_number": 1, "instruction": "Power down and lock out the motor per LOTO procedure.", "safety_warning": "Ensure the motor is fully de-energized before proceeding." },
    { "step_number": 2, "instruction": "Remove the coupling guard and inspect rotor balance.", "safety_warning": null }
  ],
  "tools": ["socket wrench set", "dial indicator", "balancing weights"],
  "est_minutes": 45,
  "safety_warnings": ["Lock out power before any physical inspection or repair."],
  "spare_parts": [
    { "part_name": "balancing weight kit", "spec": "for NEMA 56 frame motors" }
  ]
}
```

DECISION: repair steps are structured objects (`step_number`, `instruction`, `safety_warning`) rather than plain strings, so a step-level warning can be attached per prompts.py's rule ("safety warning attached to any step involving power or moving parts"), while `safety_warnings` holds only general/aggregate warnings not tied to one step.

### `inspections.checklist_state` → shape of `ChecklistItem` list
The column value is a JSON array (per plan §3 comment `[{step, checked}]`), not a wrapping object.

| field | type |
|---|---|
| step | string |
| checked | boolean |

Example:
```json
[
  { "step": "Power down and lock out the motor per LOTO procedure.", "checked": true },
  { "step": "Remove the coupling guard and inspect rotor balance.", "checked": false }
]
```

---

## 3. REST API (12 endpoints, plan §4)

Shared error envelope (all non-2xx responses):
| field | type |
|---|---|
| error_code | string |
| message | string |

### 1. `GET /departments`
- Request body: none
- Response body: list of Department `{ id, name }`

### 2. `GET /departments/{id}/machines`
- Request body: none
- Response body: list of Machine `{ id, department_id, name, image_url }`

### 3. `GET /machines/{id}/problems`
- Request body: none
- Response body: list of Problem `{ id, machine_id, name, description }`

### 4. `POST /inspections`
- Request body: `{ machine_id: uuid, problem_id: uuid }`
- Response body: Inspection (draft row) `{ id, user_id, machine_id_fk, problem_id_fk, photo_url: null, answers: null, vision_result: null, diagnosis: null, repair_plan: null, checklist_state: null, pdf_url: null, status: "draft", created_at, updated_at }`

### 5. `POST /inspections/{id}/vision-analysis`
- Request body: `{ photo_url: string }`
- Response body: VisionResult

DECISION: the plan doesn't state how `photo_url` reaches the `inspections` row before Vision Module runs (photos upload client → Storage directly, bypassing FastAPI). This spec has the client pass `photo_url` in this endpoint's request body; the backend persists it to the row, then downloads it with the service key per Prompt 5.1.

### 6. `POST /inspections/{id}/questions`
- Request body: none (uses the row's persisted `vision_result`)
- Response body: QuestionSet

### 7. `POST /inspections/{id}/answers`
- Request body: AnswersPayload
- Response body: AnswersPayload (echoes what was persisted)

DECISION: the plan doesn't specify a return shape for this persist-only call; echoing the persisted payload avoids inventing an extra confirmation wrapper.

### 8. `POST /inspections/{id}/diagnose`
- Request body: none (uses persisted `vision_result` + `answers`)
- Response body: the full `diagnosis` object (hypotheses, root_cause, confidence, explanation, ruled_out, cited_sources)

### 9. `POST /inspections/{id}/repair-plan`
- Request body: none (uses persisted `diagnosis`)
- Response body: RepairPlan

### 10. `POST /inspections/{id}/report`
- Request body: ReportRequest `{ checklist_state: list of ChecklistItem }`
- Response body: `{ pdf_url: string }`

### 11. `GET /inspections`
- Request body: none
- Response body: list of InspectionSummary `{ id, machine_id_fk, problem_id_fk, status, created_at, updated_at }`

DECISION: history returns a lightweight summary, not the full row with JSONB blobs, matching the History screen's needs (machine, problem, date, status chip per plan §8–9).

### 12. `GET /inspections/{id}`
- Request body: none
- Response body: full Inspection row (all columns, including all JSONB fields expanded per their shapes above)

---

## 4. Pydantic Models (backend, field name + type only)

**Reference/table row models**
- Department: id: UUID, name: str
- Machine: id: UUID, department_id: UUID, name: str, image_url: Optional[str]
- Problem: id: UUID, machine_id: UUID, name: str, description: Optional[str]
- Inspection: id: UUID, user_id: UUID, machine_id_fk: UUID, problem_id_fk: UUID, photo_url: Optional[str], answers: Optional[AnswersPayload], vision_result: Optional[VisionResult], diagnosis: Optional[DiagnosisResult], repair_plan: Optional[RepairPlan], checklist_state: Optional[list[ChecklistItem]], pdf_url: Optional[str], status: str, created_at: datetime, updated_at: datetime
- InspectionSummary: id: UUID, machine_id_fk: UUID, problem_id_fk: UUID, status: str, created_at: datetime, updated_at: datetime

**AI module output / core models (named in Prompt 1.1)**
- VisionResult: visible_issues: list[str], damaged_components: list[str], severity_estimate: str, machine_confirmed: bool
- Hypothesis: cause: str, confidence: float, reasoning: str
- InvestigationResult: hypotheses: list[Hypothesis]
- Question: text: str, question_type: str (multiple_choice / free_text), options: Optional[list[str]]
- QuestionSet: questions: list[Question]
- AnswersPayload: answers: list[{question: str, answer: str}]
- RuledOutHypothesis: cause: str, reason: str
- ReasoningResult: root_cause: str, confidence: float, explanation: str, ruled_out: list[RuledOutHypothesis], cited_sources: list[str]
- DiagnosisResult: hypotheses: list[Hypothesis], root_cause: str, confidence: float, explanation: str, ruled_out: list[RuledOutHypothesis], cited_sources: list[str]
- RepairStep: step_number: int, instruction: str, safety_warning: Optional[str]
- SparePart: part_name: str, spec: str
- RepairPlan: steps: list[RepairStep], tools: list[str], est_minutes: int, safety_warnings: list[str], spare_parts: list[SparePart]
- ChecklistItem: step: str, checked: bool
- ReportRequest: checklist_state: list[ChecklistItem]

**Request/response wrappers per endpoint**
- CreateInspectionRequest: machine_id: UUID, problem_id: UUID
- CreateInspectionResponse: Inspection
- VisionAnalysisRequest: photo_url: str
- VisionAnalysisResponse: VisionResult
- QuestionsResponse: QuestionSet
- AnswersRequest: AnswersPayload
- AnswersResponse: AnswersPayload
- DiagnoseResponse: DiagnosisResult
- RepairPlanResponse: RepairPlan
- ReportResponse: pdf_url: str
- InspectionListResponse: list[InspectionSummary]
- InspectionDetailResponse: Inspection
- ErrorEnvelope: error_code: str, message: str

---

## 5. Dart Model Classes (frontend, 1:1 mirror of §4)

- Department: id, name
- Machine: id, departmentId, name, imageUrl
- Problem: id, machineId, name, description
- Inspection: id, userId, machineId, problemId, photoUrl, answers, visionResult, diagnosis, repairPlan, checklistState, pdfUrl, status, createdAt, updatedAt
- InspectionSummary: id, machineId, problemId, status, createdAt, updatedAt
- VisionResult: visibleIssues, damagedComponents, severityEstimate, machineConfirmed
- Hypothesis: cause, confidence, reasoning
- InvestigationResult: hypotheses
- Question: text, questionType, options
- QuestionSet: questions
- AnswerEntry: question, answer
- AnswersPayload: answers
- RuledOutHypothesis: cause, reason
- ReasoningResult: rootCause, confidence, explanation, ruledOut, citedSources
- DiagnosisResult: hypotheses, rootCause, confidence, explanation, ruledOut, citedSources
- RepairStep: stepNumber, instruction, safetyWarning
- SparePart: partName, spec
- RepairPlan: steps, tools, estMinutes, safetyWarnings, spareParts
- ChecklistItem: step, checked
- ReportRequest: checklistState
- CreateInspectionRequest: machineId, problemId
- VisionAnalysisRequest: photoUrl
- ReportResponse: pdfUrl
- ErrorEnvelope: errorCode, message
