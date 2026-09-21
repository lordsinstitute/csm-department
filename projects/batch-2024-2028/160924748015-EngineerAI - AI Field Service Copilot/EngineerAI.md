# EngineerAI — AI Field Service Copilot: 3-Day Hackathon Implementation Plan

## Context

EngineerAI is a guided (non-chat) mobile inspection copilot for industrial technicians, scoped for a 3-day hackathon build using Claude Code Pro. MVP covers one department (Industrial Equipment), one machine (Electric Motor), and four problems (Vibration, Overheating, Noise, Won't Start). The plan below is optimized for two hard constraints: **solo developer, 3 days**, and **limited Claude Code Pro usage** — every architectural choice favors low infrastructure surface area, small independent generation batches, and manual editing for anything that's a "value tweak" rather than a structural change.

Decisions locked in with the user before writing this plan:
- **RAG content**: authored synthetic knowledge snippets (not real manuals) — fast, controllable, ships in ~1 hour.
- **Deployment**: cloud-deployed backend + installable app (not local-only demo).
- **Accounts**: Supabase project + OpenRouter key not yet created — budgeted into Day 1 start.
- **UI workflow**: skip Figma; write a short manual design-tokens brief, then generate Flutter screens directly from it.

---

## 1. Overall Architecture

Single FastAPI monolith (not microservices) sits between the Flutter app and three external systems: Supabase (Postgres + Auth + Storage), one OpenAI-compatible LLM endpoint for all AI calls (Gemini 2.5 Flash — **primary: the Gemini API's free tier** via its OpenAI-compatible endpoint, **fallback: the same model paid via OpenRouter**), and a local ChromaDB collection embedded in the backend for RAG. The 7 "AI modules" (Vision, Investigation, Question, Knowledge, Reasoning, Repair, Report) are logical Python service classes inside one deployable, not separate services — this is the single biggest complexity cut for a solo 3-day build.

```
Flutter App ──(Supabase Auth SDK, direct)──> Supabase Auth
     │                                              
     ├──(direct upload, anon key + RLS)──> Supabase Storage (photos)
     │
     └──(REST + JWT)──> FastAPI Backend
                             ├──> Supabase Postgres (single `inspections` row per session)
                             ├──> Supabase Storage (service key, PDF upload)
                             ├──> LLM endpoint (Gemini 2.5 Flash: Gemini API free tier ▸ OpenRouter fallback) — vision, investigation, question, reasoning, repair
                             └──> ChromaDB (local, rebuilt at startup from bundled markdown snippets)
```

Key simplification: the photo upload goes **client → Supabase Storage directly**, not through FastAPI — avoids proxying large binary uploads through the backend and cuts an endpoint.

---

## 2. Folder Structure

```
backend/
  app/
    core/            config.py, security.py (Supabase JWT verification)
    api/routes/       departments.py, machines.py, problems.py, inspections.py
    services/
      llm_client.py            # single OpenRouter wrapper, used by all modules
      prompts.py                # ALL prompt templates in one file — manual-edit target
      vision_service.py
      investigation_service.py
      question_service.py
      knowledge_service.py       # Chroma query wrapper
      reasoning_service.py
      repair_service.py
      report_service.py          # ReportLab PDF assembly
    models/schemas.py            # Pydantic request/response + AI output schemas
    db/supabase_client.py
    knowledge_base/
      snippets/*.md               # authored knowledge chunks — manual-edit target
      build_index.py               # embeds snippets into Chroma at startup
    reports/templates/            # PDF branding assets
  requirements.txt, Dockerfile, .env.example

mobile/
  lib/
    core/theme/        colors.dart, typography.dart, spacing.dart   # design tokens
    core/api_client.dart          # dio setup + auth interceptor
    state/                        # Riverpod providers (inspection session, auth, history)
    models/                       # Dart mirrors of backend schemas
    features/
      auth/ selection_screens/ photo_capture/ guided_questions/
      diagnosis_loading/ root_cause/ repair_instructions/
      repair_checklist/ report_preview/ history/
    shared_widgets/     selection_grid.dart, progress_stepper.dart, buttons.dart, cards.dart
  pubspec.yaml
design/
  design_tokens.md               # the manual design brief (written before any UI generation)
```

---

## 3. Database Schema (Supabase Postgres)

Deliberately denormalized around the workflow: **one `inspections` row holds the entire session state as JSONB**, mirroring the linear guided workflow and cutting join complexity to near zero. Reference tables stay real tables (not hardcoded) so multi-department/multi-machine expansion later is just seed data, not schema work.

```
departments      id, name
machines         id, department_id, name, image_url
problems         id, machine_id, name, description
inspections      id, user_id, machine_id_fk, problem_id_fk,
                 photo_url,
                 answers            jsonb,   -- guided question Q&A
                 vision_result      jsonb,   -- Vision Module output
                 diagnosis          jsonb,   -- hypotheses, root cause, confidence, explanation
                 repair_plan        jsonb,   -- steps, tools, est. time, safety, spare parts
                 checklist_state    jsonb,   -- [{step, checked}] — written once, with the /report call
                 pdf_url,
                 status             text,    -- enum: draft/analyzing/diagnosed/repairing/complete
                 created_at, updated_at
```

RLS: `inspections` scoped to `auth.uid() = user_id`. Storage buckets `inspection-photos` and `inspection-reports`, folder-per-user, RLS matching `auth.uid()`.

---

## 4. API Design (FastAPI)

Auth is handled client-side by `supabase_flutter` directly against Supabase Auth — FastAPI only **verifies** the JWT on protected routes (no auth endpoints to build).

```
GET  /departments
GET  /departments/{id}/machines
GET  /machines/{id}/problems
POST /inspections                        -> create session (machine_id, problem_id)
POST /inspections/{id}/vision-analysis   -> runs Vision Module on photo_url
POST /inspections/{id}/questions         -> Question Module, returns dynamic follow-ups
POST /inspections/{id}/answers           -> persist answers
POST /inspections/{id}/diagnose          -> Investigation + Knowledge + Reasoning Modules
POST /inspections/{id}/repair-plan       -> Repair Module
POST /inspections/{id}/report            -> Report Module, accepts final checklist_state in body, returns pdf_url
GET  /inspections                        -> history list
GET  /inspections/{id}                   -> full detail (replay)
```

12 endpoints total — deliberately one-module-per-endpoint so each backend AI service is independently testable via curl/Postman before Flutter is wired up. **Checklist is local-only state** (Riverpod) while the technician works; the final `checklist_state` is persisted once in the `/report` call body — drops a PATCH endpoint and its per-tap sync wiring. (Trade-off: an inspection abandoned before report generation loses its checkmarks — acceptable for MVP.) **Day-3 fallback**: if time runs short, vision-analysis + questions can be merged into one call, and diagnose + repair-plan into another, to cut round trips without changing the module code. **Pre-decided trigger**: invoke this fallback if the Day-2 checkpoint isn't reached by ~8pm on Day 2 — decide by the clock, not under panic.

---

## 5–7. AI Service Architecture, RAG Pipeline, Prompt Architecture

**AI layer — cost-optimized and provider-agnostic.** One `llm_client.call_llm(system_prompt, user_content, schema)` wrapper used by every module; every module has its own template in `prompts.py`. The client speaks the **OpenAI chat-completions wire format**, which both the Gemini API (via its OpenAI-compatible endpoint `https://generativelanguage.googleapis.com/v1beta/openai/`) and OpenRouter accept — both support `response_format` json_schema and base64 image parts — so the provider is pure configuration:

```
LLM_BASE_URL / LLM_API_KEY / LLM_MODEL                   # primary: Gemini API FREE TIER, gemini-2.5-flash
LLM_FALLBACK_BASE_URL / _API_KEY / _MODEL                # optional: OpenRouter, google/gemini-2.5-flash (paid)
LLM_CACHE=on|off                                         # dev read-through disk cache
DEMO_FALLBACK=true|false                                 # serve golden fixtures if every live path fails
```

- **One model everywhere** (gemini-2.5-flash for all six templates): free tier for dev, and the demo runs exactly what Day-3 testing tuned. No per-task model split — it multiplies the testing surface for zero demo value.
- **Structured output first**: each module's Pydantic schema goes up as `response_format` json_schema, constraining JSON **at the source**; Pydantic validation + one "return ONLY valid JSON" retry remain as backstop, then the module's safe generic fallback.
- **Provider fallback (~15 lines, not a framework)**: on 429/timeout/5xx from the primary, retry the same request once against the fallback triple — same wire format, different base URL.
- **Read-through dev cache**: key = sha256(model + prompts + content, images hashed by bytes) → JSON on disk. All Flutter/UI iteration replays recorded responses at **zero API cost**; editing a prompt changes the key and transparently goes live. This eliminates the bulk of a solo dev's calls, since UI iteration vastly outnumbers prompt iteration.
- **Demo fallback**: `DEMO_FALLBACK=true` serves a pre-recorded golden response (best real outputs from Day-3 testing, copied from the cache) keyed by module + problem when primary, fallback, and retry all fail — the live demo cannot die to a provider outage.
- **Call budget: 5 LLM calls per inspection** (vision 1, investigation 1, question 1, reasoning 1, repair 1 — RAG is local, report is ReportLab = 0; +1 only for the P2 exec summary). Free-tier daily quotas cover dev comfortably (~40–50 full flows/day even at pessimistic limits); fully paid worst case ≈ 1–2¢ per inspection.

Module chain:
1. **Vision** — photo (base64) → `{visible_issues, damaged_components, severity_estimate, machine_confirmed}`
2. **Investigation** — vision result + problem → `{hypotheses: [{cause, confidence, reasoning}]}`
3. **Question** — lowest-confidence hypotheses → 2–4 targeted disambiguating questions
4. **Knowledge (RAG, no LLM call)** — pure vector search, described below
5. **Reasoning** — vision + answers + retrieved chunks + hypotheses → `{root_cause, confidence, explanation, ruled_out}`
6. **Repair** — root cause + retrieved chunks → `{steps, tools, est_minutes, safety_warnings, spare_parts}`
7. **Report** — no LLM required; pure ReportLab assembly of everything already stored (optional: one short LLM call for an executive-summary paragraph, cheap since it's the only free-text field)

**RAG pipeline (zero extra infra)**: 15–20 authored markdown snippets (vibration/overheating/noise/won't-start causes+fixes, safety lockout-tagout, common spare parts/tools) in `knowledge_base/snippets/`. Embedded with **ChromaDB's built-in `DefaultEmbeddingFunction`** (ONNX MiniLM, ~80MB — no external embeddings API, no extra key). **Important**: this model is *not* bundled with the pip package — it downloads on first use at runtime. Bake it into the Docker image with a build-time warm-up step (e.g. `RUN python -c "from chromadb.utils.embedding_functions import DefaultEmbeddingFunction; DefaultEmbeddingFunction()(['warmup'])"`) so container restarts never re-download 80MB mid-judging. Give the Railway service **≥1GB RAM** (onnxruntime footprint). Index rebuilt from the bundled markdown files at container startup (seconds, for 20 docs) rather than relying on a persistent volume — makes the cloud deploy stateless and restart-safe. Query returns top-3 chunks + source filename, used both for reasoning grounding and for citing evidence in the explanation shown to the technician.

**Documented fallback (decide consciously, don't panic-switch)**: with only ~20 snippets already organized by problem type, retrieval can be replaced by **tag matching** (problem + hypothesis keywords → snippets) with zero infra — deletes ChromaDB, onnxruntime, and the model download from the risk surface. Less impressive as a "RAG" talking point for judges, but if the Chroma/onnxruntime deploy fights back for more than ~1 hour on Day 3, switch to tags; only `knowledge_service.py` changes.

**Content authoring split**: Claude Code drafts the first version of the 20 snippets in one batch (cheap, single pass); user manually reviews/edits for technical accuracy (~30 min) — this is a manual-edit file, not a regeneration target.

---

## 8–9. Mobile Navigation & Screen List

`go_router`, linear route stack matching the workflow, backed by one `InspectionSessionNotifier` (Riverpod) that accumulates the draft inspection exactly as the backend's `inspections` row accumulates JSONB — frontend and backend state shapes mirror each other by design.

Screens (many share one generic `SelectionGridScreen` widget, so screen count ≠ build effort):
1. Splash / anonymous auth continue
2. Home (Start Inspection + History)
3. Department Selection (1 card — kept for demo narrative & future scale)
4. Machine Selection (1 card)
5. Problem Selection (4 cards)
6. Photo Capture (image_picker: camera/gallery, preview, retake)
7. Vision Analysis loading (animated engineer-style status text)
8. Guided Questions (one per step, progress indicator)
9. Diagnosis loading
10. Root Cause Analysis (confidence-ranked, explanation, cited evidence, ruled-out alternatives)
11. Repair Instructions (steps, tools, est. time, safety warnings)
12. Interactive Repair Checklist (tappable, progress bar)
13. Spare Parts (section of Repair Instructions, not a separate route)
14. Report Preview / Generate PDF (share/download)
15. Inspection History (list)
16. Inspection Detail (read-only replay)

Screens 3–5 share one template; 7 & 9 share one loading-animation template — realistically **~10 unique UI templates**, not 16.

---

## 10–15. User Journey, Backend/Frontend/AI Workflow, State Management, Data Flow

**Journey**: technician opens app → anonymous session auto-created → taps Start → selects dept/machine/problem (mostly single-tap since MVP has one option each) → snaps photo → app shows "Analyzing image…" while Vision Module runs → 2–4 guided questions appear, tailored to what the photo suggests → "Consulting knowledge base… evaluating hypotheses…" while Investigation+Knowledge+Reasoning run → Root Cause screen shows ranked diagnosis with plain-English explanation citing manual snippets → Repair Instructions with safety warnings and parts list → technician checks off steps on the interactive checklist as they work → taps Generate Report → PDF appears, downloadable/shareable → session appears in History for later reference.

**State management**: Riverpod throughout. One `InspectionSessionNotifier` per active session; `FutureProvider`s for read-only lists (departments/machines/problems/history); a small `AuthNotifier` wrapping the `supabase_flutter` session stream.

**Data flow**: Supabase JWT attached via Dio interceptor on every FastAPI call; photos are **resized/compressed client-side before upload** (`image_picker`'s `maxWidth: 1280, imageQuality: 80` — one line) since raw phone photos run 4–12MB, which would slow venue-wifi uploads and balloon the base64 vision payload/token cost; photo bytes go client→Storage directly (never through FastAPI); backend downloads the photo from its Storage URL (service key) and base64-encodes it for the Gemini vision call (simplest reliable path, avoids depending on the model provider fetching arbitrary URLs).

---

## 16–17. Authentication & Storage Strategy

**Auth**: Supabase **anonymous sign-in**, triggered by a single "Continue" tap — no login/signup UI to build at all. This is the single biggest scope cut in the whole plan; skip building email/password unless all Day-3 stretch goals are already done. Anonymous sessions still get per-user `auth.uid()` for RLS and history scoping. Two gotchas: (1) anonymous sign-in is **off by default** — enable it in the Supabase Auth dashboard on Day 1; (2) the anonymous session lives in app storage, so clearing app data orphans the user's history — fine for MVP, but **don't clear app data on the demo device between rehearsal and judging**.

**Storage**: two buckets, `inspection-photos` (client uploads directly via anon key + RLS policy scoped to `auth.uid()`) and `inspection-reports` (backend uploads via service-role key — the service key never leaves the backend). Folder convention `{user_id}/{inspection_id}/...` for both.

---

## 18. Error Handling

- **Network**: Dio interceptor, one automatic retry, friendly banner ("Connection lost — tap to retry") instead of raw exceptions.
- **AI JSON parsing**: structured output (`response_format` json_schema) constrains the model at the source; every response still validated against its Pydantic schema; one retry with a stricter "JSON only" reminder; final fallback to a safe generic response so the demo never hard-crashes mid-flow.
- **AI provider failure**: primary 429/timeout/5xx → one retry against the fallback provider (same model via OpenRouter); if `DEMO_FALLBACK=true` and every live path fails, serve the pre-recorded golden response for that module + problem — recorded from real Day-3 runs, so the demo completes with genuine output even in a full provider outage.
- **Low-confidence vision**: if the Vision Module can't confirm the machine/issue, UI explicitly asks the technician to retake the photo rather than proceeding into a nonsense diagnosis.
- **Backend**: one global FastAPI exception handler, consistent `{error_code, message}` envelope.
- **Report generation**: since the inspection row is already persisted before the PDF step, a failed report generation is retry-only — no data loss.

---

## 19. Deployment Strategy

- **Backend**: **Railway** (preferred over Render's free tier — Render's spin-down-on-idle creates cold-start risk during live judging). Dockerfile-based deploy; env vars: `LLM_BASE_URL`/`LLM_API_KEY`/`LLM_MODEL` (+ optional fallback triple; `LLM_CACHE=off`, `DEMO_FALLBACK=true` for judging), `SUPABASE_URL`, `SUPABASE_SERVICE_KEY`, `SUPABASE_JWT_SECRET`. Dockerfile includes the **embedding-model warm-up step** (see RAG section) so the ONNX model is baked into the image, and the service gets **≥1GB RAM**. Chroma index rebuilds from bundled markdown at container startup — no persistent volume needed.
- **Data/Auth/Storage**: Supabase cloud project (create Day 1; enable anonymous sign-in).
- **API budget**: primary is the Gemini API **free tier** (AI Studio key, no card — check your project's real limits in AI Studio's rate-limit view on Day 1). Optional insurance: a **one-time $10 OpenRouter credit purchase** funds the paid same-model fallback AND permanently raises OpenRouter's free-model cap from 50 to 1,000 requests/day; set a hard spend cap on that key regardless.
- **Mobile**: Android only for the 3-day window (iOS TestFlight/signing overhead isn't worth it — flagged as an assumption, override if you have an Apple dev account handy). Ship a release APK (`flutter build apk --release`) as the installable deliverable for judges — without a signing config Flutter falls back to the debug keystore, which is fine for judges side-loading an APK; **don't burn time on proper keystore setup** unless a store upload is required. For the **live demo itself**, run via `flutter run` on a physical device against the deployed Railway URL — more reliable in the moment than relying on a fresh install.
- **Config**: `--dart-define=API_BASE_URL=...` so local vs. prod backend is a one-line build flag switch.
- **Demo insurance** (the live path is device → venue wifi → Railway → OpenRouter → Gemini — four failure points you don't control):
  - **Record a backup demo video** the night before, end-to-end on the deployed build.
  - **Prep 4–6 electric-motor test photos in advance** (one per problem type + one deliberately bad photo to show the retake branch) — never depend on photographing anything at the venue.
  - **Golden fixtures + `DEMO_FALLBACK=true`**: after final testing, copy the best real responses from the dev cache into `demo_fixtures/` and deploy with the flag on — prove it works by pointing `LLM_API_KEY` at a garbage value locally and running a full flow.

---

## 20. Testing Strategy

No formal test-suite investment — time is better spent on polish. Instead:
- A handful of pytest smoke tests only on the AI JSON-parsing/validation layer (highest silent-failure risk; ~30 min well spent).
- A curl/Postman collection to sanity-check each of the 12 endpoints standalone during Day 1–2, so backend and Flutter tracks can proceed in parallel without blocking each other.
- A written manual test script: run all 4 problem flows (Vibration/Overheating/Noise/Won't Start) end-to-end before demo day, plus 2 edge cases (bad photo, network drop mid-flow).

---

## 21. Future Improvements

Multi-department/multi-machine expansion (schema already supports it), real manual/PDF ingestion pipeline, offline mode, technician skill-level personalization, multi-language support, escalation-to-senior-engineer workflow, fleet-wide failure analytics, vision model fine-tuned on real defect photos, voice input for hands-free field use.

---

## Claude Code Pro Usage Optimization

- **Freeze specs before generating**: write DB schema, API contract, Pydantic/Dart data models, and `prompts.py` templates as plain markdown/config first (manually or in one cheap Claude Code pass) — generate implementation *against* a frozen contract, never co-design it interactively; interactive co-design is what burns context fastest.
- **Batch by shared context, not by file count**: e.g. request all 7 AI service files + `prompts.py` in one message (they share the same schemas), all 4 selection screens in one message (they share one template), all Dart model classes in one message (they mirror the backend schema 1:1).
- **One session per layer**: close/start a fresh session when switching between unrelated concerns (backend AI services vs. Flutter screens vs. deployment) — don't run one mega-session across the whole 3 days.
- **Reference, don't re-paste**: point Claude Code at file paths it already generated instead of pasting file contents back into chat or asking it to re-search/re-grep its own prior output.
- **Manual-edit files, never regenerate**: `prompts.py` wording, `knowledge_base/snippets/*.md` content, `design_tokens.md` values, `.env` files, and any one-line copy/color/spacing tweak — edit these by hand.
- **Precise prompts**: state the exact file list, paste the frozen schema inline, state acceptance criteria, and explicitly say "no extra abstractions" — open-ended "build the backend" prompts cause exploratory thrashing that costs far more than a scoped one.
- **Verify with terminal, not Claude**: run `flutter analyze` / hot reload / curl checks yourself for routine sanity checks; only ask Claude Code to "run and verify" at real integration checkpoints.

---

## Tech Stack — Validated with Adjustments

Kept as proposed: Flutter, FastAPI, Gemini 2.5 Flash (now primarily via the **Gemini API's free tier + OpenAI-compatible endpoint**, with OpenRouter demoted to optional paid same-model fallback), Supabase (Postgres/Storage/Auth), ReportLab. Two additions, both zero-new-infrastructure:
- **ChromaDB in-process with its built-in ONNX embedding function** (not FAISS, not an external embeddings API) — no separate vector DB service, no extra key, rebuilds from bundled files on every deploy.
- **Flutter**: `riverpod` (state), `go_router` (nav), `image_picker` (camera — simpler/more reliable under time pressure than the raw `camera` plugin), `dio` (HTTP + interceptors), `supabase_flutter` (auth + direct storage upload).

## UI Workflow — Recommendation

Skip Figma. Spend ~20–30 minutes writing `design/design_tokens.md` by hand (color palette, type scale, spacing scale, button/card styles, tone/voice notes, 2–3 reference-app screenshots for visual inspiration if desired) — then have Claude Code generate Flutter screens directly from that brief, screen-batch by screen-batch, reusing shared widgets. Full Figma-first costs the better part of a day and Figma→Flutter translation is never 1:1 (guaranteed rework); generating with zero spec risks visual inconsistency across ~10 screens. The written brief is the cheapest way to buy consistency without the Figma tax.

---

## 3-Day Development Roadmap

Legend: **Priority** P0=must-have, P1=important, P2=stretch. **Owner**: CC=Claude Code, M=Manual, Both=paired. **Claude usage**: rough sessions/messages.

### Day 1 — Foundation (specs frozen, both tracks unblocked)

| Task | Time | Priority | Depends on | Owner | Claude usage |
|---|---|---|---|---|---|
| Create Supabase project (**enable anonymous sign-in**) + **Gemini API key in AI Studio** (free, no card — note your project's limits in the rate-limit view) + optional OpenRouter fallback key (**one-time $10 + hard spend cap**) | 45m | P0 | — | M | None |
| Write `design/design_tokens.md` (colors, type, spacing, tone) | 30m | P0 | — | M | None |
| Define DB schema + Pydantic/Dart data contracts (frozen spec doc) | 45m | P0 | Supabase project | M (with CC drafting first pass) | Low — 1 short session |
| Apply Supabase migration (tables + RLS + seed dept/machine/problems) | 30m | P0 | schema doc | CC generates SQL, M runs it | Low — 1 message |
| FastAPI skeleton: config, JWT verification middleware, static routes (departments/machines/problems) | 1.5h | P0 | schema | CC | Medium — 1 batched session |
| Author 20 RAG knowledge snippets (first draft) | 45m | P0 | — | CC drafts, M edits after | Low — 1 message, then manual edit |
| `build_index.py` — Chroma index build from snippets, startup rebuild | 45m | P0 | snippets drafted | CC | Low |
| `llm_client.py` + `prompts.py` (all 6 prompt templates) + Pydantic AI-output schemas | 2h | P0 | data contracts | CC (batched, single session) | Medium |
| Flutter project skeleton: theme files from design_tokens.md, go_router shell, shared widgets (SelectionGrid, ProgressStepper, buttons/cards) | 2h | P0 | design_tokens.md | CC (batched) | Medium |
| Supabase anonymous auth wiring (Flutter side) | 45m | P0 | Flutter skeleton | CC | Low |
| **Day 1 checkpoint**: static screens (dept/machine/problem selection) navigable against live static endpoints | 30m | P0 | above | Both | — |

### Day 2 — Core Build (AI modules live, full screen set)

| Task | Time | Priority | Depends on | Owner | Claude usage |
|---|---|---|---|---|---|
| Vision Module service + endpoint, tested via curl with sample photo | 1.5h | P0 | llm_client, schemas | CC | Medium |
| Investigation + Question Module services + endpoints | 1.5h | P0 | Vision module | CC | Medium |
| Knowledge (RAG query) + Reasoning Module services + endpoint | 1.5h | P0 | Chroma index, question module | CC | Medium |
| Repair Module service + endpoint | 1h | P0 | Reasoning module | CC | Low-Medium |
| Report Module: ReportLab PDF assembly + storage upload + endpoint | 1.5h | P0 | Repair module | CC | Medium |
| Photo Capture screen (image_picker with `maxWidth`/`imageQuality` compression, preview/retake) + direct-to-Storage upload | 1h | P0 | Flutter skeleton | CC | Low |
| Vision/Diagnosis loading screens (shared animated template) | 45m | P1 | screens shell | CC | Low |
| Guided Questions screen (dynamic list, progress) | 1h | P0 | Question endpoint | CC | Low-Medium |
| Root Cause Analysis screen | 1h | P0 | Reasoning endpoint | CC | Medium |
| Repair Instructions + Spare Parts section | 1h | P0 | Repair endpoint | CC | Medium |
| Interactive Repair Checklist (tap-to-check, local Riverpod state — no per-tap sync) | 45m | P0 | Repair Instructions screen | CC | Low |
| Report Preview / Generate + share/download (sends final checklist_state) | 1h | P0 | Report endpoint | CC | Low-Medium |
| **Day 2 checkpoint**: one full problem flow (e.g. Vibration) works end-to-end locally, photo → PDF | 1h | P0 | everything above | Both | — |

*(History + Inspection Detail screens moved to Day 3 — Day 2 was overloaded at ~15h of task rows.)* **Fallback trigger**: if this checkpoint isn't reached by ~8pm, invoke the endpoint-merge fallback from §4 — decide by the clock, not under panic.

### Day 3 — Integration, Deploy, Polish

| Task | Time | Priority | Depends on | Owner | Claude usage |
|---|---|---|---|---|---|
| Run all 4 problem flows end-to-end locally, log bugs | 1.5h | P0 | Day 2 checkpoint | M (drive), CC (fix) | Low-Medium (targeted fixes) |
| Fix bugs found above | 2h | P0 | bug list | CC for logic, M for prompt/content tuning | Medium |
| History list + Inspection Detail (replay) screens | 1.5h | P1 | GET /inspections endpoints | CC | Medium |
| Error handling pass: retries, low-confidence vision branch, global exception handler | 1h | P0 | — | CC | Low |
| Deploy backend to Railway (env vars, Dockerfile check incl. embedding-model warm-up bake, ≥1GB RAM) | 1h | P0 | backend feature-complete | M (with CC troubleshooting) | Low |
| Point Flutter build at prod API URL via --dart-define, smoke test on device | 45m | P0 | backend deployed | M | None-Low |
| Build release APK (debug-keystore fallback is fine) | 30m | P1 | app stable | M | None |
| UI polish pass (spacing, empty/loading states, icons) | 1.5h | P1 | all screens built | CC (batched small edits) | Low-Medium |
| Prep 4–6 motor test photos (one per problem + one bad photo for retake branch) | 30m | P0 | — | M | None |
| Manual test script: 4 flows + 2 edge cases, final pass | 1h | P0 | deployed build | M | None |
| Record golden demo fixtures from the dev cache + verify DEMO_FALLBACK with an invalid key | 30m | P1 | final test pass | M | None |
| Record backup demo video on the deployed build | 30m | P0 | stable deployed build | M | None |
| Prepare demo script / rehearsal | 1h | P0 | stable build | M | None |
| **Buffer / stretch**: nicer spare-parts UI, history polish, exec-summary LLM paragraph in PDF | remaining | P2 | core complete | CC | Low |

**If time runs out**: the P0 rows alone (through the Day-2 checkpoint plus Day-3 deploy/bugfix/test rows) constitute a complete, demoable, cloud-deployed MVP covering all 4 problems end-to-end — everything marked P1/P2 is additive polish, safe to drop without breaking the demo narrative.

---

## Revision Notes (v2 — 2026-07-12)

Changes from the original plan, all hardening — no architecture changes:

1. **Embedding model baked into Docker image** — Chroma's `DefaultEmbeddingFunction` downloads its ~80MB ONNX model at runtime, not install time; a build-time warm-up step caches it in the image so container restarts never re-download mid-judging. Railway service sized ≥1GB RAM for onnxruntime. Documented a zero-infra tag-matching fallback if the Chroma deploy fights back.
2. **Client-side photo compression** — `image_picker` `maxWidth: 1280, imageQuality: 80`; raw 4–12MB phone photos would slow uploads and balloon the base64 vision payload.
3. **Structured outputs first** — `response_format` json_schema via OpenRouter constrains Gemini to valid JSON at the source; the prompt-retry logic stays as a backstop, not the primary defense.
4. **Checklist PATCH endpoint dropped** (13 → 12 endpoints) — checklist is local Riverpod state, persisted once in the `/report` call body.
5. **Day 2 rebalanced** — History + Inspection Detail (P1) moved to Day 3; Day 2 rows summed to ~15h. Endpoint-merge fallback now has a pre-decided trigger (~8pm Day 2).
6. **Demo insurance added to Day 3 (P0)** — backup demo video, 4–6 pre-shot motor test photos (incl. one bad photo for the retake branch), hard spend cap on the OpenRouter key.
7. **Small Day-1 checklist items made explicit** — enable anonymous sign-in in the Supabase dashboard (off by default); don't clear app data on the demo device between rehearsal and judging (anonymous session = history). Release APK ships on the debug-keystore fallback — no keystore setup time.

## Revision Notes (v3 — 2026-07-12): Cost-Optimized AI Layer

Provider strategy redesigned for a zero/near-zero API budget without changing models or module code:

1. **Primary provider switched to the Gemini API free tier** (Google AI Studio key, no card) via its OpenAI-compatible endpoint — same gemini-2.5-flash the plan already targets, now free for the whole build. Real per-project limits must be read from AI Studio's rate-limit view on Day 1 (public numbers fluctuate); even pessimistic limits (~250 req/day) cover ~40–50 full test inspections daily at 5 calls each.
2. **OpenRouter demoted to optional paid fallback** — same model, same wire format, different base URL. A one-time $10 credit purchase doubles as insurance (funds the fallback) and permanently raises OpenRouter's free-model cap from 50 to 1,000 req/day.
3. **Client is provider-agnostic by configuration**: `LLM_BASE_URL/LLM_API_KEY/LLM_MODEL` + optional fallback triple; fallback fires on 429/timeout/5xx. No adapter classes — both endpoints speak OpenAI chat-completions with json_schema + base64 images.
4. **Read-through disk cache (`LLM_CACHE=on`)** for development — all UI iteration replays recorded responses at zero API cost; prompt edits change the cache key and go live transparently.
5. **Golden-fixture demo fallback (`DEMO_FALLBACK=true`)** — best real Day-3 responses served if every live path fails; the demo cannot die to a provider outage. Verifiable locally with an invalid API key.
6. **One model for all modules** — no per-task model split; report stays LLM-free (ReportLab). Fully-paid worst case ≈ 1–2¢ per inspection; expected total spend for the build: $0–10.
