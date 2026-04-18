# TestGen AI — Paranoid Full Audit + UX/UI Optimization + Deployment Handoff

You are inheriting a near-finished master's thesis project. The user (Ali) is exhausted, running low on token quota, and needs **one end-to-end pass** from you that leaves the product demo-ready and deployed. Treat this as a forensic audit — assume the previous AI missed something. Be paranoid. Miss nothing.

**Respond to the user in Azerbaijani.** Reason internally in English if it helps. Stop and ask when you hit a missing credential or ambiguous decision — do not guess.

---

## 0. The original product vision (Ali's own words, April 2026)

> "Mən magistr dissertasiya işi yazmalıyam. Dissertasiya işimin adı belədir — *An Intelligent AI-Based System for Automatic Generation of Test Cases from Methodological Resources*. Azərbaycanda hər il DİM abituryentlər üçün yeni test topluları çıxarır, lakin ciddi dəyişiklik olmur — sualların yeri dəyişir, az sayda yeni sual əlavə olunur, üz qabığı dəyişir. Valideynlər az sayda yeni sual üçün 15-20 manat ödəməli olur.
>
> Həll: 11-ci sinif abituryentlər 3 fənndən (az dili, riyaziyyat, ingilis) imtahan verir. İmtahanda düşən sual məktəbdə keçilən dərslikdən olmalıdır. Əlimizdə dərsliklər və DİM-in keçmiş test toplularıdır. Gemini 3 Flash (sürət/qiymət/1M kontekst/multilingual), Gemini multimodal embedding (OCR azadlığı), Qdrant vektor DB (lokal, effektiv).
>
> Sistem axını: user mövzu + çətinlik + sual tipi seçir → LLM dərslikdən həmin mövzunu tapır (abituryentin nə keçdiyini bilir) → DİM test toplularından nümunəyə baxır → tamamilə yeni unikal sual generasiya edir (müəllif hüquqları korlanmır). Yeni sual bankları, süni intellekt əsaslı təhsil platformasına inteqrasiya.
>
> Ənənəvi müəllim sual yazması çox vaxt aparır, qiymət iki tərəfi qane etmir. Bu sistem təhsil qurumları + müəllimlər + abituryentlər üçün qazanclı olacaq. Müəllimləri əvəzləmirik — AI-nın xəta payı olduğu üçün suallar monitorinq edilməli, səhvlər düzəldilməlidir. Bu yalnız dissertasiya deyil, həm də Ultra şirkətinə məhsul kimi təqdim ediləcək."

This is the product's soul. Every decision you make must stay faithful to it.

---

## 1. Before you do anything — read these

**Documentation (read ALL, in order):**
1. `docs/specs/*.md` — original specifications
2. `docs/plans/*.md` — implementation plans
3. `HANDOFF_AUDIT_PROMPT.md` — the previous audit brief (sibling file in repo root)
4. Any `CLAUDE.md`, `AGENTS.md`, or `GEMINI.md` in the tree

**Claude Code memory directory (cross-session persistent notes written by the previous AI — treat as ground-truth-ish, verify before acting):**
- `C:\Users\User\.claude\projects\c--Users-User-Desktop-UltraEdu\memory\MEMORY.md` — index
- In particular: `project_testgen.md`, `reference_dim_structure.md`, `reference_test_accounts.md`, `reference_credentials.md`, `feedback_*.md`

**Codebase:**
- `Dərslik/testgen/backend/` — FastAPI + async SQLAlchemy + Alembic
- `Dərslik/testgen/frontend/` — Next.js 16 + React 19 + KaTeX + Tailwind 4
- `Dərslik/testgen/docker-compose.yml` — local stack (postgres + qdrant + backend + frontend)
- `Dərslik/testgen/docker-compose.prod.yml` — production stack + nginx

Do **not** start coding until you have read the above. If any doc contradicts the code, the code wins — flag the contradiction for Ali.

---

## 2. What is claimed to be working (audit these — do not trust)

Git is at commit `5082b4e` on `main` of `github.com/Ali190903/UltraEdu`. The last AI session claimed to have shipped:

**A. LaTeX root-cause fix (three-layer defense):**
- Post-parse sanitizer in `backend/data_pipeline/json_utils.py` → `sanitize_question()` — collapses `\\\\frac`→`\frac`, fixes swapped MCQ keys (`{"0,125":"D"}` → `{"D":"0,125"}`), wraps bare LaTeX in `$...$`, normalises `correct_answer` to uppercase A-E.
- Strict prompt contract in `backend/generation/prompts.py` — forbids calculus for grade-11 buraxılış, requires A-E keys, requires `$...$` around any math-containing MCQ option, explicit JSON backslash-doubling rules.
- Structural validator in `backend/generation/pipeline.py` → `_structural_check()` — fast programmatic gate before the LLM validator; rejects malformed output and retries without burning Gemini calls. Uses `_CALCULUS_RE` for out-of-scope detection on grade-11 math.

**B. Teacher UI scaffolding:**
- `frontend/src/app/teacher/layout.tsx`, `TeacherSidebar.tsx`, `TeacherMobileBar.tsx`, `AuthShell.tsx`, `HomeCTA.tsx` (new)
- `frontend/.dockerignore`, `frontend/Dockerfile.dev` (new)
- Modified dashboard/bank/export/login/register/Navbar/VariantBuilder/QuestionCard/layout/globals.css/api.ts/tsconfig.json
- Deleted `backend/variants/latex_render.py` (server LaTeX render → client KaTeX)

**C. Test scripts (supposedly all passing):**
- `backend/scripts/test_sanitizer.py`
- `backend/scripts/test_live_generation.py`
- `backend/scripts/qdrant_health.py`

**Your audit must independently verify every claim.** Run the scripts. Diff the files. Look for: dead code, unused imports, commented-out blocks, silent exception swallowing, race conditions in `variants/service.py` refill loop, N+1 queries, missing indexes, unhandled 500 paths in FastAPI, CSRF holes, XSS in `dangerouslySetInnerHTML`, JWT stored in localStorage (known issue, Priority 5), secrets in `.env` that shouldn't be committed, Docker healthchecks that don't actually fail when the service is broken.

---

## 3. What is explicitly NOT done (DO NOT start these unless Ali confirms priority shift)

Priority order Ali set (lower number = earlier):
1. **DİM 6-block topic distribution** in `backend/variants/service.py::_auto_topic_dist`. Currently picks by raw Qdrant frequency → clustering (7× konus-silindr, 5× neft sızması). Blueprint lives in `memory/reference_dim_structure.md`. Needs block→sub-topic mapping (ask Ali to confirm the mapping before shipping — he said "don't distribute blindly").
2. **Three question types** (13 MCQ + 5 numeric-open + 7 written-solution rubric-graded). Touches schema, prompts, validator, pipeline, frontend, export. Large — brainstorm before coding.
3. **Matching question UI** multi-select interaction bug.
4. **Multi-grade selection** (9+10, 9+10+11) — currently single int.
5. **Auth security**: JWT in `localStorage` → httpOnly cookie.
6. **Design polish**: Sual Bankı, Export, typography, transitions.

**Ali has said in this current session: if no serious defects are found in the audit, priority for YOU is #6 (UX/UI optimization end-to-end), then push + deploy.** If your audit uncovers a blocker (security, data corruption, crash path), escalate to Ali before touching UX.

---

## 4. Execution plan — do these phases in order

### Phase 0 — Environment sanity (≤10 min)
```bash
cd "c:/Users/User/Desktop/UltraEdu/Dərslik/testgen"
docker compose ps              # all four services up?
docker compose logs backend --tail 100   # any recurring errors?
docker compose logs frontend --tail 50
docker exec -w /app testgen-backend-1 python -m scripts.qdrant_health
docker exec -w /app testgen-backend-1 python -m scripts.test_sanitizer
docker exec -w /app testgen-backend-1 python -m scripts.test_live_generation
```
If any of these fail, stop and report — don't proceed.

### Phase 1 — Paranoid code audit (read-only, produce a findings report)

Walk the tree systematically. For each finding, record `file:line → severity (blocker/high/medium/low) → evidence → suggested fix`.

**Backend audit checklist:**
- [ ] `main.py` — CORS config, middleware order, startup/shutdown hooks, exception handlers.
- [ ] `auth/` — password hashing (bcrypt/argon2?), JWT signing, token expiry, refresh logic. Is `JWT_SECRET` actually random? Grep for fallback defaults.
- [ ] `models/` — required/optional fields, `nullable=False` where it should be, foreign-key `ondelete` behaviour, timestamps.
- [ ] Alembic migrations — is the chain consistent? Any orphaned revision? Any `downgrade` missing?
- [ ] `generation/pipeline.py` — retry semantics, what happens when ALL attempts fail (currently returns last failed question — is that what callers expect?).
- [ ] `generation/generator.py` — `parsed[0]` assumption safe after the recent fix? What if `parsed` is a dict with wrong keys?
- [ ] `data_pipeline/json_utils.py::sanitize_question` — are there LaTeX edge cases that still slip through? Test with `\\text{ m}^2` inside an already-wrapped `$...$` string. Test a string that starts with `$` but has a trailing unclosed `$`.
- [ ] `variants/service.py` — concurrent `Semaphore(5)` to Gemini: any rate-limit handling? Refill loop correctness (successful count reaches target exactly, never exceeds). DB flush-per-question in a loop — slow on 25-question variants.
- [ ] `variants/export.py` — PDF/Word rendering. Known bug history: `\frac`→`rac` Unicode corruption. Verify KaTeX→HTML→PDF path handles Azerbaijani chars + math end-to-end.
- [ ] `core/gemini_client.py` — structured output mode? Temperature? Timeout? 503 retry?
- [ ] `core/qdrant_client.py` — connection pooling, error on collection miss.

**Frontend audit checklist:**
- [ ] `src/lib/api.ts` — token source, auth header, error interceptor, 401 redirect.
- [ ] `src/app/teacher/layout.tsx` + `RequireRole.tsx` — is role gating actually enforced? Client-side only = not enforced.
- [ ] `VariantBuilder.tsx` — form validation, loading state, error surface, what happens if Gemini returns 0/25 passing questions.
- [ ] `QuestionCard.tsx` — KaTeX render path, XSS surface (is option text passed through `dangerouslySetInnerHTML`?), image/matching render.
- [ ] Responsive breakpoints — every page at 360×640, 768×1024, 1440×900.
- [ ] Route-level code splitting, suspense boundaries, error boundaries.
- [ ] Accessibility — alt text, aria labels, focus order, contrast ratio.
- [ ] `globals.css` — custom font loading, FOUC.

Deliver the findings report to Ali in Azerbaijani before Phase 2 — **if any BLOCKER is found, stop and wait for his decision.**

### Phase 2 — Browser-based end-to-end test (subagent with Playwright)

**Accounts (check `memory/reference_test_accounts.md` first; if they don't exist, ask Ali):**
- `test1` — student (abituryent) role
- `test2` — teacher (müəllim) role

If the accounts do not exist, **ask Ali for the credentials or permission to create them via `/register` and record them.** Do not invent passwords.

Use the `playwright` skill (or `superpowers:dispatching-parallel-agents` with two browser subagents in parallel — one per account). For each account:

**Student (test1) flow to exercise:**
- `/register` (if not already) → `/login` → land on student dashboard
- Browse available variants
- Start a variant → answer all 25 questions → submit
- Check result/score page — KaTeX renders, no `rac` or raw `\frac`, no broken options
- Open profile, logout

**Teacher (test2) flow to exercise:**
- `/login` → `/teacher/dashboard`
- Create new variant: set subject=riyaziyyat, grade=11, difficulty split, total=25 → submit → watch generation progress → variant completes
- Open variant → QuestionCard renders every question cleanly (LaTeX, matching pairs, A-E options)
- Export PDF — download, open, verify math + Azerbaijani chars
- Export Word — same
- Sual Bankı → filter by topic/difficulty/grade → bulk select → approve/reject
- Report a bad question → verify report appears somewhere
- Logout

**For every page:** take a screenshot at desktop + mobile. Click every button. Fill every form. Submit intentionally invalid data and see if errors are handled gracefully.

**Record every defect** with screenshot path + repro steps + severity. Keep them grouped by page.

### Phase 3 — UX/UI optimization pass

Only after Phases 1-2 are complete and Ali has seen the findings. Scope:
- Unified design tokens (spacing, radius, shadow, font scale) — check if they're already in `globals.css` or Tailwind config; consolidate if scattered.
- Typography hierarchy — heading scale, line-height, measure.
- Empty states and loading skeletons everywhere data is fetched.
- Micro-interactions: button hover/active, card hover, form focus rings, transitions (`transition-colors`, `transition-transform`, 150-200ms).
- Error states: toast vs inline, consistent copy.
- Mobile nav polish (TeacherMobileBar + student equivalent if exists).
- Dark mode? — only if already scaffolded; do not introduce.
- Ensure every interactive element has `:focus-visible` styling.
- Consistent icon set (lucide-react probably — verify).
- Run Lighthouse on `/`, `/login`, `/teacher/dashboard`, `/teacher/bank`, `/teacher/export` and aim ≥90 on Performance, Accessibility, Best Practices.

Use the `frontend-design` or `ui-ux-pro-max:ui-ux-pro-max` skill if available. Respect the existing visual language — do **not** redesign the product unless Ali asks. Polish, don't reinvent.

**After every frontend edit:** `docker restart testgen-frontend-1` and re-screenshot.

### Phase 4 — Commit and push
- Logical commits, conventional commit messages.
- Do NOT force-push. Do NOT touch `main` history.
- `git push origin main` — remote already has Ali's token embedded.

### Phase 5 — Deploy to Digital Ocean via MCP

Ali has GitHub Student Pack $200 credit on DO. `docker-compose.prod.yml` + nginx reverse proxy are already authored — **verify they work** before deploying.

- Use the Digital Ocean MCP (check `zen-discovery` skill to confirm it's connected; if not, ask Ali to connect it).
- Provision a droplet (sane default: Basic, 2 vCPU / 4GB RAM, Ubuntu 24.04, same region as user — Frankfurt or Amsterdam).
- Transfer secrets via `scp` or droplet environment: `GEMINI_API_KEY`, `JWT_SECRET`, `POSTGRES_PASSWORD`, `QDRANT_API_KEY` (if used). **Never bake secrets into the image.** Ask Ali for any secret you don't have.
- Point a subdomain if Ali provides one; otherwise use the droplet IP + self-signed cert and note this for post-deploy follow-up.
- Open ports 80/443; firewall everything else.
- Run `docker compose -f docker-compose.prod.yml up -d --build`, then Alembic migrations, then smoke-test via `curl` on the public URL.
- Seed Qdrant: you'll need to transfer or reindex the textbook + DIM collections. Check if there's a seed script in `backend/scripts/` or `backend/data_pipeline/` — if not, tell Ali this is a gap.
- **Before declaring deployment done**, run the student + teacher flows from Phase 2 against the live URL.

---

## 5. Critical rules

1. **Stop and ask** when you hit: missing credential, ambiguous product decision, destructive git op, anything that touches real user data, anything the docs don't cover.
2. **Respond in Azerbaijani** to Ali. Keep responses terse — he is token-limited.
3. **No mocks in E2E tests.** Real Qdrant, real Gemini, real DB, real browser.
4. **`docker restart testgen-frontend-1` after every frontend edit** — hot reload is unreliable on his Windows setup.
5. **Do not amend or force-push.** New commits only.
6. **Do not delete files that look like in-progress work** without asking.
7. **Do not add features beyond what's listed.** No premature abstractions, no comments explaining obvious code, no backwards-compat shims.
8. **Trust but verify memory.** Memory files are point-in-time notes; the code is ground truth.
9. **Every claim you make back to Ali must have evidence** — a file:line, a screenshot path, a test-run output. No vague "looks good."

---

## 6. Final deliverable back to Ali (Azerbaijani, structured)

1. **Audit nəticələri** — tapılan hər defekt üçün `fayl:sətr → ciddilik → dəlil → həlli`.
2. **Brauzer testi** — hər səhifə üçün skrinşot yolları + tapılan problemlər.
3. **UX/UI dəyişiklikləri** — commit hashes + əvvəl/sonra skrinşotlar.
4. **Deployment statusu** — prod URL, droplet IP, resurs istifadəsi, smoke-test nəticələri.
5. **Qalan işlər** — nə edilmədi və nə üçün (bloker, vaxt, Ali-nin təsdiqi lazımdır).
6. **Növbəti sessiya üçün tövsiyə** — bir-iki cümlə.

Start with Phase 0. Good hunting.
