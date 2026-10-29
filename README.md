# Intern+ Pilot App

The Intern+ founding-pilot MVP: an employability platform connecting students, employers and the Intern+ team in Egypt.

## What it does

- **Students** build a profile, enter a pilot access code, take a 12-question employability assessment, and get a score out of 100 with a readiness band and three next steps. They browse open roles ranked by fit and apply. They control whether their anonymous profile is visible to employers.
- **Employers** browse an anonymous talent pool (no names or contact details) ranked against their roles, request intros, post roles, track candidate status, and export shortlists as CSV.
- **Intern+ team (Admin)** approves roles before they go live, reviews applicants, intro requests and the best matches, sends shortlists with contact details, overrides scores, and tracks the pilot funnel and exit criteria. Admin opens via the `#admin` link and only for editors.

## Scoring

| Component | Source | Weight |
| --- | --- | --- |
| Communication | Assessment | 20% |
| Problem solving | Assessment | 20% |
| Professional readiness | Assessment | 20% |
| Digital skills | Assessment | 15% |
| Experience & activities | Profile | 25% |

Match % = 35% skills overlap + 25% Intern+ score + 10% field of study + 10% role area + 5% position type + 5% timing (year-round vs breaks) + 2.5% candidate stage + 2.5% graduation year + 5% location (remote roles always fit). Must-have skills and the minimum score act as filters. Student and employer forms use the same lists (role areas, position types, timing, stages, fields of study, skills) so the comparison is like for like.

CVs are PDFs (max 5 MB) in a private Supabase Storage bucket `cvs`: students manage their own file, admins read all, employers read only CVs of students in their shortlist.

## Folders

| Folder | What it is |
| --- | --- |
| `web/` | **The real app.** Runs on Supabase with email sign-up. Published to GitHub Pages. |
| `supabase/setup.sql`, `02_hardening.sql`, `03_profile_v2.sql` | Database setup (run in order): tables, privacy rules (row-level security), server-side scoring, sample students. Run once in Supabase's SQL Editor. |
| `claude-pilot/` | The earlier prototype that runs inside claude.ai (uses its built-in database). Kept for reference. |
| `seed/` | The 8 fictional sample students as JSON. |

## Supabase version: who can see what

| Table / view | Who can read | Who can write |
| --- | --- | --- |
| `students` | that student, admins | that student (score, override and sample flag are protected), admins |
| `get_talent()` (anonymous: no name or contact) | signed-in users | computed from `students` |
| `roles` | the employer who posted it, admins | that employer (cannot publish), admins approve |
| `get_openings()` (approved roles) | signed-in users | computed from `roles` |
| `applications` | that student, admins | students, to approved roles only |
| `intro_requests` | that employer, admins | employers, for their own roles only |
| `shortlist` | that employer, admins | admins send; employers can only change the status |

Scores are calculated in the database, so students cannot change their own score. Admins are set by hand (see the end of `setup.sql`). Admin opens at `#admin`.

## Earlier claude.ai prototype

`claude-pilot/index.html` runs as a claude.ai artifact and uses its built-in database (`window.claude.use('db')`). Its collections and privacy rules:

| Collection | Who can read | Who can write |
| --- | --- | --- |
| `students/{id}` | that student, editors | that student, editors |
| `applications/{id}` | that student, editors | that student, editors |
| `employers/{id}` | that employer, editors | that employer, editors |
| `talent/{id}` (anonymous) | signed-in users | that student, editors |
| `openings` | everyone with access | editors |

`seed/` holds the 8 fictional sample students (marked `sample: true`) and their anonymous talent records.

## Live app

Published by GitHub Actions (`.github/workflows/pages.yml`) to **https://farahaghaffar.github.io/intern-plus-app/** on every push to `main`. Admin: add `#admin` to the address.

`*.netlify.app` addresses are unreachable from Egyptian networks (connection-not-private error), so Netlify is not used for now. Before launch, point a custom domain at the app. The Supabase Site URL and Redirect URLs (Authentication > URL Configuration) must match the live address.

## Status

Draft question bank v1 is a placeholder pending the validated bank. The pilot is free: no access codes or payments. Students go straight from profile to assessment.

## Assessment v2

- 24 timed questions (6 per area, options graded 0 to 3, three calculation questions) plus a short writing task. Question order and answer order are shuffled per student. No going back.
- The database scores everything (`score_student_v2` in `supabase/05_assessment_v2.sql`); students cannot set their own score.
- The writing task is scored by Claude against a fixed rubric through the `score-writing` edge function (`supabase/functions/score-writing`). It needs an `ANTHROPIC_API_KEY` secret in Supabase. Admins can always type a score by hand.
- Experience is capped at 50 until an admin ticks "Exp. verified" after checking the CV.
- Percentile ranking appears once 50 real students have completed.
- Students scoring under 80 in an area can join a free waitlist for future coaching (`waitlist_areas`). No payment is taken.
- The question bank lives in `assessment/bank_v2.json`; `assessment/build_sql.py` regenerates the SQL.

## Assessment v3 (levels and field examples)

- Two levels: **Undergraduate** (still at university, graduating after the coming summer) and **Graduate** (final year, fresh graduates, working). The level is fixed by the database (`level_for`) when the intern answers the first question.
- Some questions use examples from the intern's field (business, tech, media, health, social). The options and the correct answer never change, so scores stay comparable.
- Percentiles compare interns only with others at the same level who have completed their profile.
- Sign-up is a 5-field quick start; the full profile (CV, skills, experience, consent) comes after the report. Interns only enter the talent pool after completing it.
- The report explains the score band, each area, specific tips, and every answer with the reasoning.
- Bank source: `assessment/make_bank_v3.py` builds `bank_v3.json`; `assessment/build_sql_v3.py` builds `supabase/07_levels.sql`.
