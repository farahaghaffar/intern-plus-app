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

Match % = 40% skills overlap + 30% Intern+ score + 15% major fit + 10% graduation-year fit + 5% location fit. Must-have skills and the minimum score act as filters.

## Folders

| Folder | What it is |
| --- | --- |
| `web/` | **The real app.** Runs on Supabase with email sign-up. This is what Netlify publishes. |
| `supabase/setup.sql`, `supabase/02_hardening.sql` | Database setup (run in order): tables, privacy rules (row-level security), server-side scoring, sample students. Run once in Supabase's SQL Editor. |
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

## Next step

Host `web/` on Netlify (connected to this repository; `netlify.toml` already points at `web/`), then set the Netlify address as the Site URL in Supabase > Authentication > URL Configuration so confirmation and password-reset emails link back to the app.

## Status

Draft question bank v1 is a placeholder pending the validated bank. No real payments: access codes (`PAID-`, `SPON-`, `TEAM-`) stand in for payment.
