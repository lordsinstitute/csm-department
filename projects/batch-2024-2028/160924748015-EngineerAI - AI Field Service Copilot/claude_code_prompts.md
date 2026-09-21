# EngineerAI — Claude Code Prompt Playbook (3 Days)

Every prompt below is copy-paste ready. They follow the plan's usage rules: frozen specs first, batches grouped by shared context, one session per layer, precise file lists, and an explicit "no extra abstractions" guard in every generation prompt.

## How to use this playbook

1. **Run Claude Code from the project root** (the folder that will contain `backend/`, `mobile/`, `design/`, `specs/`). Copy `EngineerAI.md` (the plan) into that root first — several prompts tell Claude to read it.
2. **One session per layer.** Start a fresh session at every "SESSION" heading below. Never carry a backend session into Flutter work.
3. **Within a session, run prompts in order.** Later prompts in the same session say "read the files you just created" — that's intentional; don't re-paste file contents.
4. **Manual steps are marked 🔧.** Do them yourself — they are cheaper by hand and burn zero usage.
5. **Never regenerate the manual-edit files**: `specs/contracts.md` (after your review), `design/design_tokens.md`, `prompts.py` wording, `knowledge_base/snippets/*.md` content, `.env`. Tweak these by hand.
6. **When something breaks**, use the Bug-Fix Template (Day 3 section) — paste the actual error, never describe it from memory.

---

# DAY 1 — Foundation

## 🔧 Manual first (no Claude, ~1.5h)

- ✅ **Already done: Supabase project + Gemini key + OpenRouter key, all in your .env.** Remaining checks on those accounts:
  - Supabase: confirm **anonymous sign-in is enabled** (Auth → Providers) and the .env has URL + anon key + service key + JWT secret.
  - Gemini: open AI Studio's **rate-limit view** and write down your project's actual RPM/RPD for gemini-2.5-flash (public numbers fluctuate; the dashboard is the truth).
  - OpenRouter: **set a hard spend cap**. It is the automatic fallback when the Gemini free quota exhausts — Gemini returns 429 and the client retries the same request on OpenRouter with the same model. (Optional: a one-time $10 credit also permanently raises OpenRouter's free-model cap to 1,000 req/day.)
- **The .env lives at the project root (`EngineerAI/.env`) — leave it there.** The prompts point Claude at that path, and config.py will load it from the root explicitly. Make sure the root `.gitignore` covers `.env`. Never paste key values into a Claude Code prompt — the prompts below tell Claude to read the variable NAMES from the file, never to echo the values.
- Write `design/design_tokens.md` by hand (~30 min): color palette (primary/surface/error/success), type scale (4–5 sizes), spacing scale (4/8/16/24/32), button + card style notes, tone ("industrial, calm, high-contrast, big touch targets").
- Run `flutter create mobile` yourself (don't spend Claude usage on scaffolding a tool does for free).

---

## SESSION 1 — Freeze the contracts (backend + frontend both depend on this)

### Prompt 1.1 — Draft the frozen spec

```text
Read EngineerAI.md (the project plan) in this folder.

Create ONE file: specs/contracts.md. It is the frozen contract for the entire project — everything else will be generated against it. Include, in this order:

1. The Supabase Postgres schema from plan §3: departments, machines, problems, inspections — exact column names and types.
2. The exact JSON shape of every JSONB column on inspections (answers, vision_result, diagnosis, repair_plan, checklist_state): field names, types, and ONE realistic example value each. These shapes are also the AI module output schemas.
3. All 12 REST endpoints from plan §4: method, path, request body, response body. One shared error envelope: {error_code, message}.
4. A named list of Pydantic models (field name + type only, no code): VisionResult, Hypothesis, InvestigationResult, QuestionSet, AnswersPayload, ReasoningResult, RepairPlan, ChecklistItem, ReportRequest, plus request/response wrappers per endpoint.
5. A 1:1 list of Dart model classes mirroring the same.

Rules: markdown only, no code. Do NOT invent fields, endpoints, or models beyond the plan. Where the plan is ambiguous, pick the simplest option and flag it on one line starting with "DECISION:" so I can review.
```

### 🔧 Manual: review `specs/contracts.md` (~15 min)

Read every DECISION line, fix anything wrong **by hand**. From here on this file is frozen — no prompt may modify it.

### Prompt 1.2 — Migration SQL

```text
Read specs/contracts.md (frozen — do not change it).

Create ONE file: backend/migrations/001_init.sql, runnable top-to-bottom in the Supabase SQL editor on a fresh project. Contents:

1. CREATE TABLE for departments, machines, problems, inspections — exactly per the contract.
2. Enable RLS on inspections with policies: authenticated users (including anonymous) can select/insert/update only rows where auth.uid() = user_id. Reference tables: select for any authenticated user.
3. Storage: create private buckets inspection-photos and inspection-reports; policies on storage.objects so authenticated users can read/write only paths starting with their own auth.uid()/ in inspection-photos, and read-only their own folder in inspection-reports.
4. Seed: department "Industrial Equipment"; machine "Electric Motor" under it; problems Vibration, Overheating, Noise, Won't Start with one-line descriptions.

Rules: no triggers, no functions, no extra indexes beyond PK/FK — the backend sets updated_at itself. One file only.
```

### 🔧 Manual: run the SQL in the Supabase SQL editor, verify the 4 tables + seed rows + 2 buckets exist.

---

## SESSION 2 — Backend skeleton + knowledge base (fresh session)

### Prompt 2.1 — FastAPI skeleton

```text
Read specs/contracts.md (frozen contract) and EngineerAI.md §2 for the folder structure.

A real .env already exists at the PROJECT ROOT (./.env, next to EngineerAI.md) with my Supabase, Gemini, and OpenRouter keys. Read it ONLY to learn the exact variable names — NEVER print, log, echo, or copy the values anywhere. config.py must read those exact names and load that root .env via an explicit path resolved relative to the config.py source file (so it works from any working directory), with real environment variables taking precedence (production/Railway sets vars directly and has no .env). backend/.env.example mirrors the same names with placeholder values. Ensure .gitignore covers .env and backend/llm_cache/.

Build the FastAPI skeleton. Create EXACTLY these files and nothing else:

backend/requirements.txt
backend/Dockerfile
backend/.env.example
backend/app/main.py
backend/app/core/config.py            # pydantic-settings reading env vars
backend/app/core/security.py          # FastAPI dependency verifying the Supabase JWT (HS256, SUPABASE_JWT_SECRET), returns user_id
backend/app/db/supabase_client.py     # one supabase-py client using the service key
backend/app/models/schemas.py         # ALL Pydantic models from the contract (requests, responses, AI outputs)
backend/app/api/routes/departments.py # GET /departments
backend/app/api/routes/machines.py    # GET /departments/{id}/machines
backend/app/api/routes/problems.py    # GET /machines/{id}/problems
backend/app/api/routes/inspections.py # POST /inspections (create draft row, status=draft), GET /inspections (user's history), GET /inspections/{id}. All AI endpoints (vision-analysis, questions, answers, diagnose, repair-plan, report) as stubs returning 501.

Also in main.py: one global exception handler returning the {error_code, message} envelope; CORS fully open (mobile client).

Dockerfile: python slim base, install requirements, uvicorn entrypoint, and this exact layer so Chroma's ONNX embedding model is baked into the image (it otherwise downloads ~80MB at runtime):
RUN python -c "from chromadb.utils.embedding_functions import DefaultEmbeddingFunction; DefaultEmbeddingFunction()(['warmup'])"

Rules: NO repositories, NO service interfaces, NO dependency-injection framework, NO async ORM — plain functions and FastAPI dependencies. Keep each route file under ~80 lines.
Acceptance: uvicorn starts clean; with a valid Supabase JWT, curl GET /departments returns the seeded row; without a JWT, 401.
```

### Prompt 2.2 — Knowledge snippets (draft for manual edit)

```text
Create exactly 20 markdown files in backend/app/knowledge_base/snippets/ — synthetic service-manual knowledge for electric motor troubleshooting. Distribution:

- 4 vibration: misalignment, rotor imbalance, bearing wear, loose mounting bolts
- 4 overheating: overload, blocked ventilation/dirty fins, winding insulation fault, low/unbalanced supply voltage
- 4 abnormal noise: bearing failure, electrical hum (single-phasing), rotor rub, loose cover/components
- 4 won't-start: supply/fuse/breaker, failed start capacitor, seized bearing, tripped thermal overload
- 2 safety: lockout-tagout procedure, electrical safety checks before opening a motor
- 2 reference: common spare parts for small industrial motors; standard toolkit for motor repair

Each file: YAML frontmatter (title, problem_tags: [list], source: "EngineerAI KB"), then 150–250 words structured as: Symptom, Likely cause, How to confirm, Fix, Parts/tools. Write like a service-manual excerpt for a technician — specific and dry, no marketing tone. Kebab-case filenames matching titles. Exactly 20 files, nothing else.
```

### 🔧 Manual: skim/edit the 20 snippets for technical accuracy (~30 min). They are now frozen.

### Prompt 2.3 — Chroma index + knowledge service

```text
Read backend/app/knowledge_base/snippets/ (20 files) and backend/app/main.py.

Create exactly two files and wire one thing:

backend/app/knowledge_base/build_index.py   # parse frontmatter + body of every snippet, embed whole files (no chunk splitting — they are small) into an in-memory Chroma collection using DefaultEmbeddingFunction, storing title/source/problem_tags as metadata
backend/app/services/knowledge_service.py   # query(text: str, problem_name: str, k: int = 3) -> list[{content, title, source}]; prefer snippets whose problem_tags match problem_name, fill remaining slots by pure similarity

Wire build_index into main.py's lifespan so the index rebuilds at every startup.

Rules: in-memory Chroma client (no persist directory), no LLM calls, no caching layer.
Acceptance: app starts; a test query "motor vibrates at high speed" with problem_name "Vibration" returns 3 vibration-tagged snippets.
```

---

## SESSION 3 — LLM client + all prompt templates (fresh session)

### Prompt 3.1 — llm_client + prompts.py

```text
Read specs/contracts.md, backend/app/models/schemas.py, and backend/app/core/config.py. My real keys are in the root .env (config.py already loads it) — read it ONLY for the variable names, NEVER echo the values.

Create exactly two files, extend config.py with the provider settings, and add the new flags (LLM_CACHE) to backend/.env.example:

backend/app/services/llm_client.py
- One async function: call_llm(system_prompt: str, user_content, schema: type[BaseModel], fixture_key: str | None = None) -> BaseModel
- Speaks the OpenAI chat-completions wire format via httpx (60s timeout) — no provider adapter classes, the format is identical on both providers. Provider config lives in config.py, built from the EXISTING .env variable names:
  * PRIMARY: my Gemini key -> base URL https://generativelanguage.googleapis.com/v1beta/openai/, model gemini-2.5-flash (free tier)
  * FALLBACK: my OpenRouter key -> base URL https://openrouter.ai/api/v1, model google/gemini-2.5-flash (same model, paid)
- Provider fallback: on 429 (the expected case — Gemini free-tier quota exhausted), 5xx, or timeout from the primary, retry the SAME request once against the OpenRouter fallback
- Passes the Pydantic schema as response_format json_schema (strict) so output is constrained at the source
- user_content may be a string OR a multimodal list including an image as a base64 data URL part
- On schema validation failure: ONE retry appending "Return ONLY valid JSON matching the schema."; on second failure raise LLMParseError
- Read-through disk cache when LLM_CACHE=on (default: off): key = sha256(model + system prompt + serialized user content, with any image part replaced by the sha256 of its bytes); hit -> return the stored JSON with ZERO api calls; miss -> live call, then save to backend/llm_cache/{key}.json (gitignore that folder)
- fixture_key is accepted and stored for later (demo fallback comes on Day 3) — for now it does nothing

backend/app/services/prompts.py
- Plain module-level string templates only (SYSTEM_X + USER_X per module) for: vision, investigation, question, reasoning, repair, report_summary
- Each template states the module's role, the exact output fields (matching schemas.py), and concrete quality rules:
  * vision: set machine_confirmed=false unless the photo clearly shows an electric motor; describe only what is visible
  * investigation: 3–5 hypotheses with confidence 0–1 and one-line reasoning each
  * question: 2–4 questions targeting ONLY the lowest-confidence hypotheses; multiple-choice where possible
  * reasoning: pick one root cause, cite the retrieved snippet titles used, list ruled_out with reasons, explanation in plain English for a technician
  * repair: max 10 imperative steps, safety warning attached to any step involving power or moving parts, realistic est_minutes, spare_parts only if actually needed
  * report_summary: 3–4 sentences for a maintenance manager

Rules: f-string/.format templating only — no prompt-builder classes, no LangChain, no per-provider adapters. These two files + config.py + .env.example are the ONLY files you create or edit.
```

*(After this, `prompts.py` wording is a manual-edit file — tune it by hand during Day 3 testing. Dev workflow: run with LLM_CACHE=on from the start — every UI iteration replays cached responses at zero API cost; only new/changed prompts hit the live free tier.)*

---

## SESSION 4 — Flutter skeleton (fresh session)

### Prompt 4.1 — App skeleton, theme, state, selection screens

```text
Read design/design_tokens.md and specs/contracts.md. The Flutter project already exists at mobile/ (flutter create is done).

Create exactly these files:

mobile/lib/core/theme/colors.dart, typography.dart, spacing.dart  # constants straight from design_tokens.md — no values invented
mobile/lib/core/api_client.dart      # Dio client; base URL from --dart-define API_BASE_URL; interceptor attaching the current Supabase JWT
mobile/lib/models/                   # one Dart class per model in specs/contracts.md, hand-written fromJson/toJson
mobile/lib/state/auth_notifier.dart  # Riverpod: supabase_flutter anonymous sign-in + session stream
mobile/lib/state/inspection_session.dart  # Riverpod Notifier accumulating the draft inspection: inspectionId, machine/problem ids, photoUrl, answers, visionResult, diagnosis, repairPlan, checklist state — mirrors the backend inspections row
mobile/lib/state/catalog_providers.dart   # FutureProviders: departments, machines(deptId), problems(machineId), history
mobile/lib/shared_widgets/selection_grid.dart, progress_stepper.dart, primary_button.dart, info_card.dart
mobile/lib/router.dart               # go_router with every route from plan §8; screens not yet built get a labeled placeholder
mobile/lib/main.dart                 # Supabase.initialize, ProviderScope, MaterialApp.router themed from the token files
mobile/lib/features/auth/splash_screen.dart          # logo + single "Continue" button -> anonymous sign-in -> Home
mobile/lib/features/home/home_screen.dart            # "Start Inspection" + "History" buttons
mobile/lib/features/selection_screens/department_screen.dart, machine_screen.dart, problem_screen.dart  # ALL THREE are thin wrappers around SelectionGrid fed by the catalog providers; selection stored in the session notifier

Update pubspec.yaml deps: flutter_riverpod, go_router, dio, supabase_flutter, image_picker (used tomorrow).

Also delete the default test/widget_test.dart that `flutter create` generated (it references the counter-app MyApp and will break `flutter analyze` once main.dart is replaced) — replace it with a trivial smoke test that just builds the app, or remove it entirely.

Rules: NO freezed/json_serializable/build_runner, NO repository layer, NO localization scaffolding, no colors or text styles outside the theme files.
Acceptance: flutter analyze is clean; on device, Continue signs in anonymously and I can tap Home -> Department -> Machine -> Problem with data loaded from my running backend.
```

### 🔧 Day 1 checkpoint (manual): backend running locally, app taps through splash → problem selection against live endpoints. If broken, use the Bug-Fix Template.

---

# DAY 2 — Core Build

## SESSION 5 — Backend AI modules (fresh session, 3 prompts in order)

### Prompt 5.1 — Vision + Investigation + Question + Answers

```text
Read specs/contracts.md, backend/app/services/prompts.py, llm_client.py, knowledge_service.py, and app/models/schemas.py. Do NOT modify prompts.py or schemas.py — if a schema looks wrong, stop and tell me instead of changing it.

Create these services and replace the matching 501 stubs in backend/app/api/routes/inspections.py:

backend/app/services/vision_service.py
- POST /inspections/{id}/vision-analysis: download the row's photo from Supabase Storage with the service key, base64 data-URL it, call_llm with the vision prompts, persist vision_result JSONB, set status=analyzing, return VisionResult

backend/app/services/investigation_service.py + question_service.py
- POST /inspections/{id}/questions: investigation prompt (vision_result + problem) -> hypotheses; persist them under diagnosis JSONB; then question prompt (lowest-confidence hypotheses) -> QuestionSet; return it

Also implement POST /inspections/{id}/answers: persist answers JSONB, no LLM call.

Rules: each service is one module with one public async function — no classes, no base classes. On LLMParseError, return that module's safe generic fallback (plan §18) instead of a 500.
Acceptance: give me a numbered curl sequence (create -> vision with a real photo_url -> questions -> answers) with expected response shapes so I can verify before touching Flutter.
```

### Prompt 5.2 — Diagnose (Knowledge + Reasoning) + Repair

```text
Same ground rules: read the existing services and contract; do not edit prompts.py or schemas.py.

Create backend/app/services/reasoning_service.py and repair_service.py, and replace the two stubs:

POST /inspections/{id}/diagnose
- knowledge_service.query(problem + top hypothesis text) for top-3 snippets
- reasoning prompt with: vision_result, answers, retrieved chunks, hypotheses
- persist full diagnosis JSONB (root_cause, confidence, explanation, ruled_out, cited_sources), status=diagnosed, return it

POST /inspections/{id}/repair-plan
- repair prompt with root cause + the same retrieved snippets (re-query is fine)
- persist repair_plan JSONB (steps, tools, est_minutes, safety_warnings, spare_parts), status=repairing, return it

Acceptance: curl commands + expected shapes; the diagnosis explanation must mention the cited snippet titles.
```

### Prompt 5.3 — Report (PDF)

```text
Create backend/app/services/report_service.py and replace the report stub:

POST /inspections/{id}/report
- Body: {checklist_state: [...]} — persist it to the row first (data-loss safety per plan §18)
- Build the PDF with ReportLab flowables, simple single stylesheet: header (app name, date, inspection id), machine + problem, the inspection photo (downloaded from Storage, scaled to page width), root cause + confidence + explanation, repair steps rendered with their checklist tick state, spare parts + tools, safety warnings box, cited sources footer
- Upload to inspection-reports/{user_id}/{inspection_id}/report.pdf with the service key, persist pdf_url, status=complete, return {pdf_url}

Rules: no LLM call, no custom canvas drawing, one file.
Acceptance: the curl returns a pdf_url whose file opens as a valid PDF containing every section.
```

### 🔧 Manual: run the full curl sequence for the Vibration problem with a real motor photo. Backend is now feature-complete.

---

## SESSION 6 — Flutter screens (fresh session, 3 prompts in order)

### Prompt 6.1 — Photo capture + shared loading screen

```text
Read mobile/lib (state/, shared_widgets/, router.dart, core/api_client.dart) and specs/contracts.md. Reuse the existing session notifier and widgets — do not create parallel state.

Build:

mobile/lib/features/photo_capture/photo_capture_screen.dart
- image_picker camera + gallery with maxWidth: 1280, imageQuality: 80 (compression is mandatory)
- preview with Retake / Use Photo
- on confirm: POST /inspections if no inspectionId yet, upload bytes DIRECTLY to Supabase Storage at inspection-photos/{uid}/{inspectionId}/photo.jpg via supabase_flutter, store URL in the session notifier, navigate to the vision loading route

mobile/lib/features/diagnosis_loading/analysis_loading_screen.dart
- ONE reusable loading screen used by BOTH vision and diagnosis routes: takes a list of cycling status lines and an async task; animated engineer-style status text; on success navigate to the given next route; on failure show a retry button (re-run the task)
- Vision branch: if the result has machine_confirmed == false, show a dialog explaining the photo wasn't clear enough and route back to Photo Capture

Rules: no new packages. Acceptance: flutter analyze clean; on device: capture -> upload -> vision-analysis -> lands on the questions route.
```

### Prompt 6.2 — Guided questions + Root cause

```text
Build two screens, reusing existing widgets and theme files exactly (no new colors/styles):

mobile/lib/features/guided_questions/guided_questions_screen.dart
- fetches POST /inspections/{id}/questions on entry (via the loading pattern already in the codebase)
- one question per step with ProgressStepper; multiple-choice as tappable options, free-text fallback field
- answers accumulate in the session notifier; on last answer: POST answers, then navigate to diagnosis loading (which calls diagnose)

mobile/lib/features/root_cause/root_cause_screen.dart
- root cause title + confidence badge, plain-English explanation, cited snippet titles as small chips, ruled-out alternatives in a collapsed expansion section, CTA button -> Repair Instructions (triggers repair-plan call via the loading pattern)
```

### Prompt 6.3 — Repair instructions + checklist + report

```text
Build three screens, reusing existing widgets/theme:

mobile/lib/features/repair_instructions/repair_instructions_screen.dart
- header: est. time + tools; numbered steps with inline safety-warning banners; spare parts section at the bottom (part name, spec); CTA "Start Repair"

mobile/lib/features/repair_checklist/repair_checklist_screen.dart
- tappable check-off list with progress bar; state lives ONLY in the session notifier — zero API calls per tap
- CTA "Generate Report": enabled when all checked; if not all checked, allow proceeding via a confirm dialog

mobile/lib/features/report_preview/report_screen.dart
- calls POST /inspections/{id}/report with the checklist_state from the notifier (via the loading pattern)
- success state: "Report ready" with Open and Share buttons — pick ONE package (url_launcher or share_plus), add it, justify in one line

Acceptance: full flow photo -> PDF works on device against the local backend.
```

### 🔧 Day 2 checkpoint (manual): run the Vibration flow end-to-end, photo → PDF. **Fallback trigger: if this isn't working by ~8pm, use Prompt X.2 (endpoint merge).**

---

# DAY 3 — Integration, Deploy, Polish

## 🔧 Manual first: run all 4 problem flows end-to-end locally. Write down every bug as: screen/endpoint, expected, actual, error text.

## SESSION 7 — Bug fixing (fresh session; reuse this template per bug or small bug batch)

### Prompt X.1 — Bug-Fix Template (use all day)

```text
Bug: [one sentence — what happened, on which screen/endpoint].
Expected: [one sentence].
Error/log output:
[paste the ACTUAL error text or response body]

Read only the files involved in this path. Propose the minimal fix and apply it. Do NOT refactor, rename, reformat, or touch prompts.py, knowledge_base/snippets/, design tokens, or specs/contracts.md. If the real fix belongs in one of those manual files, tell me what to change and I'll do it by hand.
```

*(Batch 2–3 related bugs into one message when they share files. Prompt-wording and snippet-content problems: fix by hand, don't prompt.)*

### Prompt X.2 — Endpoint-merge fallback (ONLY if the Day-2 trigger fired)

```text
Per plan §4 fallback: without changing any service module code, merge endpoints in backend/app/api/routes/inspections.py:
1. POST /inspections/{id}/vision-analysis now also runs investigation + question generation and returns {vision_result, questions}.
2. POST /inspections/{id}/diagnose now also runs repair-plan and returns {diagnosis, repair_plan}.
Update mobile/lib call sites (loading screens / session notifier) to match — remove the now-redundant calls. Keep the old routes working if trivial; delete them if not. Smallest possible diff.
```

## SESSION 8 — Error-hardening + History screens (fresh session)

### Prompt 8.1 — Error-handling pass

```text
Read backend/app/api/routes/, backend/app/services/, mobile/lib/core/api_client.dart, and the loading screen.

One error-hardening pass — change only what's listed:
1. Backend: every AI endpoint catches LLMParseError -> that module's safe fallback response; any other exception -> the global {error_code, message} envelope with a correct status code. Verify the report endpoint persists checklist_state BEFORE PDF generation so a PDF failure is retry-only.
2. Flutter: Dio interceptor does ONE automatic retry on timeout/connection errors, then surfaces a "Connection lost — tap to retry" banner state (no raw exceptions to the UI). Every loading screen's failure state has a working retry.
3. Confirm the machine_confirmed==false retake branch works end to end.

Rules: no new abstractions, no logging framework. List what you changed per file when done.
```

### Prompt 8.2 — History + Inspection detail

```text
Build, reusing info_card, theme, and catalog_providers:

mobile/lib/features/history/history_screen.dart        # GET /inspections list: machine, problem, date, status chip; tap -> detail
mobile/lib/features/history/inspection_detail_screen.dart  # read-only replay from GET /inspections/{id}: photo, diagnosis summary, repair steps with saved checklist ticks, "Open PDF" if pdf_url exists

Rules: no pagination, no pull-to-refresh, no search. Acceptance: flutter analyze clean; a completed inspection from today appears and replays.
```

### Prompt 8.3 — Demo fallback (golden fixtures)

```text
Read backend/app/services/llm_client.py and the service call sites in backend/app/services/.

Add a last-resort demo fallback — smallest possible diff:
1. New env var DEMO_FALLBACK (default false).
2. New folder backend/app/demo_fixtures/ (empty for now — I will populate it by copying the best responses out of backend/llm_cache/ after final testing, named {fixture_key}.json).
3. In call_llm: if the primary call, the provider fallback, AND the JSON retry all fail, and DEMO_FALLBACK=true and a fixture file matching fixture_key exists, load, validate against the schema, and return it instead of raising.
4. Update each AI service call site to pass a deterministic fixture_key: "{module}_{problem-slug}" (e.g. "vision_vibration", "reasoning_wont-start").

With DEMO_FALLBACK=false, behavior is byte-identical to today. Only llm_client.py and the fixture_key arguments at call sites may change.
Acceptance: with LLM_API_KEY set to an invalid value, DEMO_FALLBACK=true, and fixtures in place, a full inspection flow completes end-to-end.
```

### 🔧 Manual (after the final Day-3 test pass): copy the best cached responses from `backend/llm_cache/` into `backend/app/demo_fixtures/` as `{fixture_key}.json` for all 4 problems; deploy with `DEMO_FALLBACK=true`, `LLM_CACHE=off`; prove the fallback once locally with a garbage API key.

## 🔧 Manual: deploy to Railway (create service, set env vars, ≥1GB RAM). If the build/deploy fails, use:

### Prompt X.3 — Deploy troubleshooting template

```text
Deploying backend/ to Railway via its Dockerfile. Failure log:
[paste the actual build or runtime log]

Diagnose and apply the smallest possible fix. Do not restructure the Dockerfile beyond what this specific error requires — the embedding-model warm-up RUN layer must stay.
```

## 🔧 Manual: `flutter run --dart-define=API_BASE_URL=https://<railway-url>` on the device; smoke test; `flutter build apk --release` (debug keystore fallback is fine).

## SESSION 9 — UI polish (fresh session, ONE batched prompt — collect items first)

### Prompt 9.1 — Polish batch

```text
UI polish pass — small visual edits only, no structural changes. Read design/design_tokens.md first and stay strictly inside its values.

Fix exactly this list:
1. [e.g. Root cause screen: confidence badge overflows on long cause names]
2. [e.g. Checklist: checked items should also strike through]
3. [e.g. Empty state for History when no inspections]
4. [...]

Rules: touch only the files these items live in; no widget refactors; no new dependencies; no changes outside this list.
```

### Prompt 9.2 — Stretch (P2, only if everything else is done): exec summary in PDF

```text
Add an optional executive-summary paragraph to the PDF report:
- In report_service.py, before assembly, one call_llm using the existing report_summary template in prompts.py, output schema {summary: str} (add ReportSummary to schemas.py — the only schema change allowed).
- Render it as the first section after the header. If the LLM call fails for any reason, skip the section silently — report generation must never fail because of it.
Only edit report_service.py and schemas.py.
```

## 🔧 Manual finish line (no Claude)

- Run the written manual test script: all 4 flows + bad-photo retake + airplane-mode-mid-flow.
- Prep 4–6 motor test photos (one per problem + one bad).
- **Record the backup demo video on the deployed build.**
- Rehearse the demo script. Do not clear app data on the demo device afterward.

---

## Quick reference — session map

| Session | Layer | Prompts | Day |
|---|---|---|---|
| 1 | Specs + SQL | 1.1, 1.2 | 1 |
| 2 | Backend skeleton + KB | 2.1, 2.2, 2.3 | 1 |
| 3 | LLM client + prompt templates | 3.1 | 1 |
| 4 | Flutter skeleton | 4.1 | 1 |
| 5 | Backend AI modules | 5.1, 5.2, 5.3 | 2 |
| 6 | Flutter feature screens | 6.1, 6.2, 6.3 | 2 |
| 7 | Bug fixing | X.1 (template), X.2 (fallback) | 3 |
| 8 | Hardening + History + Demo fallback | 8.1, 8.2, 8.3 | 3 |
| 9 | Polish + stretch | 9.1, 9.2 | 3 |

Templates X.1 and X.3 are reusable any time. Total: ~17 planned prompts + templated fixes — well inside Pro limits if you resist re-generating manual-edit files and always paste real error output instead of describing it.

**API-cost ground rules while building**: primary = Gemini API free tier (same gemini-2.5-flash as the demo); LLM_CACHE=on for all local dev so UI work costs zero calls; ~5 live calls per full inspection flow; OpenRouter fires automatically only when Gemini answers 429 (quota exhausted) — keep its spend cap set. Expected total API spend for the 3 days: $0 while the free quota holds, a few cents per inspection on OpenRouter overflow.
