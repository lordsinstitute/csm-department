# EngineerAI — Design Tokens & UI Brief

This file is the single source of visual truth. `colors.dart`, `typography.dart`, and `spacing.dart` are generated 1:1 from sections 1–3; no color, size, or radius may be hardcoded anywhere else in the app. This is a **manual-edit file** — tweak values here by hand, never regenerate.

**Context**: used by industrial technicians on a factory floor — possibly gloved hands, poor lighting, standing up. Every choice favors: high contrast, large touch targets, minimal ornamentation.

**Hard scope rules**: ONE light theme only (no dark mode). System default font (Roboto on Android) — no font packages. Material icons only. No animations beyond the loading screens and default page transitions.

---

## 1. Colors (`colors.dart`)

### Core
| Token | Hex | Use |
|---|---|---|
| `primary` | `#16548C` | Buttons, links, active states, progress fill, app bar text/icons |
| `primaryDark` | `#0F3D61` | Pressed state of primary elements |
| `primaryTint` | `#E9F1F8` | Selected-card tint, icon-circle backgrounds, chips of primary |
| `background` | `#F4F6F8` | Screen background |
| `surface` | `#FFFFFF` | Cards, sheets, inputs |
| `border` | `#D8DEE4` | Card borders, dividers, progress track |
| `textPrimary` | `#1A202C` | Headings, body |
| `textSecondary` | `#5A6572` | Captions, hints, secondary info |
| `onPrimary` | `#FFFFFF` | Text/icons on primary |
| `disabledBg` | `#C7D4E0` | Disabled button fill (text: onPrimary at 80%) |

### Semantic (also reused for confidence + status — do NOT invent new colors)
| Token | Hex | Tint bg | Dark text on tint |
|---|---|---|---|
| `success` | `#1E7B44` | `#E6F4EC` | `#14532D` |
| `warning` | `#B45309` | `#FEF3C7` | `#7C3A03` |
| `error` | `#B3261E` | `#FDECEA` | `#7F1D1D` |

### Mappings (no new tokens)
- **Confidence badge**: High → success set, Medium → warning set, Low → error set.
- **Status chips**: draft → textSecondary on border-gray tint; analyzing/diagnosed/repairing → primary on primaryTint; complete → success set.
- **Safety warnings**: always the warning set — never primary, never error (error is reserved for failures).

---

## 2. Typography (`typography.dart`)

Font: system default (Roboto). Line height 1.4 unless noted.

| Token | Size / Weight | Use |
|---|---|---|
| `display` | 28 / w700 | Screen titles ("Root Cause Analysis") |
| `headline` | 22 / w600 | Section headers, diagnosis root-cause name |
| `title` | 18 / w600 | Card titles, question text, step titles |
| `body` | 16 / w400, lh 1.5 | Main content, explanations, repair steps |
| `bodyBold` | 16 / w600 | Emphasis inside body, button labels |
| `label` | 14 / w500 | Chips, badges, input labels, stepper caption |
| `caption` | 12 / w400 | Timestamps, source citations, footnotes |

Minimum text size anywhere: 12. Body text on `background` or `surface` must always be `textPrimary`/`textSecondary` — never tinted colors.

---

## 3. Spacing, radius, sizing (`spacing.dart`)

| Token | Value |
|---|---|
| `xs / sm / md / lg / xl / xxl` | 4 / 8 / 16 / 24 / 32 / 48 |
| Screen padding | 16 horizontal, 24 top |
| Gap between cards in a list/grid | 12 |
| `radiusCard` | 16 |
| `radiusButton` | 14 |
| `radiusInput` | 12 |
| `radiusChip` | 999 (pill) |
| Min touch target | 48 × 48 |
| Primary button height | 56 |
| Checklist row min height | 64 |
| Selection card min height | 88 |

Elevation: cards are `surface` + 1px `border` + faint shadow (black 6%, blur 8, y-offset 2). Nothing else casts shadows.

---

## 4. Component specs

- **Primary button**: filled `primary`, `onPrimary` `bodyBold` label, height 56, `radiusButton`, full-width for main CTAs. Pressed → `primaryDark`. Disabled → `disabledBg`.
- **Secondary button**: 1.5px `primary` outline, `primary` label, same dimensions.
- **Text button**: `primary` label only — for "Retake", "Skip".
- **Selection card** (dept/machine/problem grids): `surface`, `radiusCard`, `border`; leading icon (40, inside a `primaryTint` circle) or machine image (radius 12); `title` text + chevron. Pressed/selected → `primaryTint` fill.
- **Progress stepper**: 4px bar, `primary` fill on `border` track, `label` caption "Step 2 of 4" underneath, right-aligned.
- **Confidence badge**: pill (`radiusChip`), semantic tint bg + dark-on-tint text, `label` weight.
- **Safety warning banner**: `warning` tint bg, 4px left border in `warning`, warning icon, dark-on-tint text, `radiusInput`. Sits ABOVE the step it applies to.
- **Checklist tile**: `surface` card, min height 64, 28px checkbox; checked → `success` tint bg + `textSecondary` strikethrough text.
- **Status chip**: pill, `label` text, per the status mapping above.
- **Loading screens**: centered pulsing icon in `primaryTint` circle, one cycling status line in `body`/`textSecondary` below. Calm, no spinners-on-spinners.
- **Empty states**: Material icon (48, `textSecondary`), one `body` line, one primary button.
- **Error banner**: `error` tint bg, dark-on-tint text, trailing "Retry" text button.

---

## 5. Tone & microcopy

- Voice: calm, direct, plain English. Short sentences. No exclamation marks, no jargon without context, never blame the user.
- Repair steps: imperative — "Disconnect the power supply." One action per step.
- Loading lines: factual engineer style — "Analyzing image…", "Checking motor housing…", "Consulting knowledge base…", "Evaluating hypotheses…", "Ranking likely causes…". Never jokey.
- Errors: state + action — "Connection lost — tap to retry."
- Confidence shown as words + percent: "High confidence (87%)".
- Safety copy is always explicit and first: "⚠ Lock out and tag the power supply before continuing."
