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

## Where it runs today

`app/index.html` is published as a claude.ai artifact and uses its built-in database (`window.claude.use('db')`). It does not save data when opened outside claude.ai. Data collections and their privacy rules:

| Collection | Who can read | Who can write |
| --- | --- | --- |
| `students/{id}` | that student, editors | that student, editors |
| `applications/{id}` | that student, editors | that student, editors |
| `employers/{id}` | that employer, editors | that employer, editors |
| `talent/{id}` (anonymous) | signed-in users | that student, editors |
| `openings` | everyone with access | editors |

`seed/` holds the 8 fictional sample students (marked `sample: true`) and their anonymous talent records.

## Next step

Move the data layer to Supabase (tables + row-level security mirroring the rules above) and host the app on Netlify or Vercel so students and employers can sign up without Claude accounts.

## Status

Draft question bank v1 is a placeholder pending the validated bank. No real payments: access codes (`PAID-`, `SPON-`, `TEAM-`) stand in for payment.
