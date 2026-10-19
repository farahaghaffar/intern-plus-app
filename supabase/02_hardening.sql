-- Intern+ security hardening (run once, after setup.sql)

-- 1. Fixed search path on the scoring function
alter function public.score_student(jsonb, int, int, int) set search_path = public;

-- 2. Trigger functions are never called directly
revoke execute on function public.handle_new_user() from public, anon, authenticated;
revoke execute on function public.students_guard() from public, anon, authenticated;
revoke execute on function public.roles_guard() from public, anon, authenticated;

-- 3. Helper functions used by the privacy rules: signed-in users only
revoke execute on function public.is_admin() from public, anon;
revoke execute on function public.is_trusted() from public, anon;
revoke execute on function public.role_is_live(uuid) from public, anon;
grant execute on function public.is_admin(), public.is_trusted(), public.role_is_live(uuid) to authenticated;

-- 4. Replace the two definer views with functions that return only anonymous fields
drop view if exists public.talent;
drop view if exists public.openings;

create or replace function public.get_talent()
returns table (id uuid, university text, major text, grad_year text, location text, skills text[], total int, scores jsonb, sample boolean)
language sql stable security definer set search_path = public as $$
  select s.id, s.university, s.major, s.grad_year, s.location, s.skills, coalesce(s.override, s.total), s.scores, s.sample
  from public.students s
  where auth.uid() is not null and s.status = 'completed' and s.consent and s.visible;
$$;

create or replace function public.get_openings()
returns table (id uuid, title text, company text, location text, min_score int, must text[], nice text[], majors text[], years text[], published_at timestamptz)
language sql stable security definer set search_path = public as $$
  select r.id, r.title, r.company, r.location, r.min_score, r.must, r.nice, r.majors, r.years, r.published_at
  from public.roles r
  where auth.uid() is not null and r.status = 'live';
$$;

revoke execute on function public.get_talent(), public.get_openings() from public, anon;
grant execute on function public.get_talent(), public.get_openings() to authenticated;
