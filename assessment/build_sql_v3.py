"""Generates supabase/07_levels.sql from bank_v3.json."""
import json
b = json.load(open('/home/claude/intern-plus-app/assessment/bank_v3.json'))
pts = {i['id']: [o[1] for o in i['o']] for i in b['items'] if not i.get('num')}
nums = {i['id']: [i['answer'], i['tol']] for i in b['items'] if i.get('num')}
cats = {str(l): {k: [i['id'] for i in b['items'] if i['level'] == l and i['cat'] == k] for k in ('comm', 'prob', 'prof', 'digi')} for l in (1, 2)}
J = lambda x: json.dumps(x).replace("'", "''")
sql = f"""-- Intern+ assessment levels (bank v3).
-- Level 1: undergraduates before their final year. Level 2: final year, graduates, working.
-- The level is fixed when the intern answers the first question, so changing the profile later cannot switch it.
-- Percentiles compare interns only with others at the same level who have completed their profile.

alter table public.students add column if not exists assessment_level int check (assessment_level in (1,2));

create or replace function public.level_for(p_status text, p_grad text) returns int
language sql stable set search_path = public as $$
  select case when coalesce(p_status,'student') = 'student' and p_grad ~ '^[0-9]{{4}}$'
                   and p_grad::int > extract(year from now())::int + case when extract(month from now()) >= 9 then 1 else 0 end
              then 1 else 2 end;
$$;

create or replace function public.score_student_v3(p_answers jsonb, p_level int, p_int int, p_proj int, p_act int, p_writing int, p_verified boolean)
returns jsonb language plpgsql immutable set search_path = public as $$
declare
  pts jsonb := '{J(pts)}';
  nums jsonb := '{J(nums)}';
  allcats jsonb := '{J(cats)}';
  cats jsonb;
  k text; q text; v text; p int; n int; res jsonb := '{{}}'; e int;
begin
  cats := allcats->coalesce(p_level,2)::text;
  for k in select jsonb_object_keys(cats) loop
    p := 0; n := 0;
    for q in select jsonb_array_elements_text(cats->k) loop
      n := n + 1;
      v := p_answers->>q;
      if v is null then continue; end if;
      if nums ? q then
        begin
          if abs(v::numeric - (nums->q->>0)::numeric) <= (nums->q->>1)::numeric then p := p + 3; end if;
        exception when others then null;
        end;
      elsif v ~ '^[0-3]$' then
        p := p + (pts->q->>(v::int))::int;
      end if;
    end loop;
    res := res || jsonb_build_object(k, round(p::numeric / (3 * n) * 100));
  end loop;
  if p_writing is not null then
    res := res || jsonb_build_object('comm', round(((res->>'comm')::numeric + p_writing) / 2));
  end if;
  e := least(100, least(3, coalesce(p_int,0)) * 35 + coalesce(p_proj,0) * 15 + coalesce(p_act,0) * 10);
  if not p_verified then e := least(e, 50); end if;
  res := res || jsonb_build_object('exp', e);
  return res;
end $$;

create or replace function public.students_guard() returns trigger
language plpgsql security definer set search_path = public as $$
declare sc jsonb; need jsonb; have int;
begin
  if not public.is_trusted() then
    if tg_op = 'INSERT' then
      new.id := auth.uid(); new.override := null; new.sample := false;
      new.status := 'registered'; new.answers := '{{}}'; new.code := null; new.task_writing := '';
      new.writing_score := null; new.writing_feedback := ''; new.writing_scored_by := ''; new.exp_verified := false;
      new.assessment_version := 3; new.assessment_level := null;
    else
      new.id := old.id; new.override := old.override; new.sample := old.sample; new.code := old.code;
      new.writing_score := old.writing_score; new.writing_feedback := old.writing_feedback; new.writing_scored_by := old.writing_scored_by;
      new.exp_verified := old.exp_verified; new.assessment_version := old.assessment_version; new.assessment_level := old.assessment_level;
      if old.status = 'completed' then new.status := 'completed'; new.answers := old.answers; new.task_writing := old.task_writing; end if;
      if old.exp_verified and (new.internships, new.projects, new.activities) is distinct from (old.internships, old.projects, old.activities) then
        new.exp_verified := false;
      end if;
    end if;
    if new.cv_path is not null and new.cv_path <> auth.uid()::text || '/cv.pdf' then
      raise exception 'CV must be uploaded to your own folder.';
    end if;
  end if;
  -- lock the level at the first answer
  if new.assessment_level is null and new.answers <> '{{}}'::jsonb then
    new.assessment_level := public.level_for(new.status_now, new.grad_year);
  end if;
  new.cohort := case split_part(upper(coalesce(new.code,'')), '-', 1)
    when 'PAID' then 'A' when 'SPON' then 'B' when 'TEAM' then 'Team' else 'Pilot' end;
  if new.status = 'completed' then
    need := '{J(cats)}'::jsonb -> coalesce(new.assessment_level,2)::text;
    select count(*) into have from jsonb_object_keys(new.answers) a
      where exists (select 1 from jsonb_each(need) c, jsonb_array_elements_text(c.value) x where x = a);
    if have < 24 then
      raise exception 'Answer all 24 questions before finishing.';
    end if;
    sc := public.score_student_v3(new.answers, new.assessment_level, new.internships, new.projects, new.activities, new.writing_score, new.exp_verified);
    new.scores := sc;
    new.total := round(0.20*(sc->>'comm')::numeric + 0.20*(sc->>'prob')::numeric + 0.20*(sc->>'prof')::numeric
                     + 0.15*(sc->>'digi')::numeric + 0.25*(sc->>'exp')::numeric);
    if tg_op = 'INSERT' or old.completed_at is null then new.completed_at := coalesce(new.completed_at, now()); end if;
  end if;
  new.updated_at := now();
  return new;
end $$;
revoke execute on function public.students_guard() from public, anon, authenticated;

create or replace function public.get_my_percentile()
returns table (pct int, n int) language sql stable security definer set search_path = public as $$
  with me as (select coalesce(override, total) as t, coalesce(assessment_level,2) as l from public.students
              where id = auth.uid() and status = 'completed' and consent),
       pool as (select coalesce(override, total) as t from public.students
                where status = 'completed' and not sample and consent and coalesce(assessment_level,2) = (select l from me))
  select case when (select count(*) from pool) >= 50 and exists (select 1 from me)
              then (select floor(100.0 * count(*) filter (where p.t < (select t from me)) / greatest(count(*) - 1, 1))::int from pool p) end,
         (select count(*)::int from pool);
$$;
revoke execute on function public.get_my_percentile() from public, anon;
grant execute on function public.get_my_percentile() to authenticated;

create or replace function public.get_talent_v3()
returns table (id uuid, university text, major text, grad_year text, location text, skills text[], total int, scores jsonb, sample boolean,
               status_now text, role_interests text[], position_types text[], duration text, availability text, pct int, exp_verified boolean, level int)
language sql stable security definer set search_path = public as $$
  with pool as (select coalesce(override, total) as t, coalesce(assessment_level,2) as l from public.students
                where status = 'completed' and not sample and consent)
  select s.id,
         case when s.university in ('Other university in Egypt','University abroad') and s.university_other <> '' then s.university_other else s.university end,
         case when s.major = 'Other' and s.major_other <> '' then s.major_other else s.major end,
         s.grad_year, s.location, s.skills, coalesce(s.override, s.total), s.scores, s.sample,
         s.status_now, s.role_interests, s.position_types, s.duration, s.availability,
         case when not s.sample and (select count(*) from pool p where p.l = coalesce(s.assessment_level,2)) >= 50
              then (select floor(100.0 * count(*) filter (where p.t < coalesce(s.override, s.total)) / greatest(count(*) - 1, 1))::int
                    from pool p where p.l = coalesce(s.assessment_level,2)) end,
         s.exp_verified, coalesce(s.assessment_level,2)
  from public.students s
  where auth.uid() is not null and s.status = 'completed' and s.consent and s.visible;
$$;
revoke execute on function public.get_talent_v3() from public, anon;
grant execute on function public.get_talent_v3() to authenticated;

update public.students set assessment_level = 2 where sample;
"""
open('/home/claude/intern-plus-app/supabase/07_levels.sql', 'w').write(sql)
print('ok', len(sql))
