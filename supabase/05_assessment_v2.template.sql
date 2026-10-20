-- Intern+ assessment v2: harder 24-question bank, writing task, experience cap, percentiles.
-- Run once in Supabase > SQL Editor (after 01 to 04).

alter table public.students
  add column if not exists assessment_version int not null default 2,
  add column if not exists task_writing text not null default '',
  add column if not exists writing_score int check (writing_score between 0 and 100),
  add column if not exists writing_feedback text not null default '',
  add column if not exists writing_scored_by text not null default '',
  add column if not exists exp_verified boolean not null default false,
  add column if not exists waitlist_areas text[] not null default '{}',
  add column if not exists waitlist_at timestamptz;

-- Scoring v2. MCQ options score 0-3; numeric answers score 3 if within tolerance.
-- Communication = average of the 6 questions and the writing task once it is scored.
-- Experience is capped at 50 until an admin verifies it against the CV.
create or replace function public.score_student_v2(p_answers jsonb, p_int int, p_proj int, p_act int, p_writing int, p_verified boolean)
returns jsonb language plpgsql immutable set search_path = public as $$
declare
  pts jsonb := '__PTS__';
  nums jsonb := '__NUMS__';
  cats jsonb := '__CATS__';
  k text; q text; v text; p int; n int; res jsonb := '{}'; e int;
begin
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
declare sc jsonb;
begin
  if not public.is_trusted() then
    if tg_op = 'INSERT' then
      new.id := auth.uid(); new.override := null; new.sample := false;
      new.status := 'registered'; new.answers := '{}'; new.code := null; new.task_writing := '';
      new.writing_score := null; new.writing_feedback := ''; new.writing_scored_by := ''; new.exp_verified := false; new.assessment_version := 2;
    else
      new.id := old.id; new.override := old.override; new.sample := old.sample; new.code := old.code;
      new.writing_score := old.writing_score; new.writing_feedback := old.writing_feedback; new.writing_scored_by := old.writing_scored_by;
      new.exp_verified := old.exp_verified; new.assessment_version := old.assessment_version;
      if old.status = 'completed' then new.status := 'completed'; new.answers := old.answers; new.task_writing := old.task_writing; end if;
      -- changing experience after verification needs re-verification
      if old.exp_verified and (new.internships, new.projects, new.activities) is distinct from (old.internships, old.projects, old.activities) then
        new.exp_verified := false;
      end if;
    end if;
    if new.cv_path is not null and new.cv_path <> auth.uid()::text || '/cv.pdf' then
      raise exception 'CV must be uploaded to your own folder.';
    end if;
  end if;
  new.cohort := case split_part(upper(coalesce(new.code,'')), '-', 1)
    when 'PAID' then 'A' when 'SPON' then 'B' when 'TEAM' then 'Team' else 'Pilot' end;
  if new.status = 'completed' then
    if (select count(*) from jsonb_object_keys(new.answers)) < 24 or coalesce(new.task_writing,'') = '' then
      raise exception 'Answer all 24 questions and the writing task before finishing.';
    end if;
    sc := public.score_student_v2(new.answers, new.internships, new.projects, new.activities, new.writing_score, new.exp_verified);
    new.scores := sc;
    new.total := round(0.20*(sc->>'comm')::numeric + 0.20*(sc->>'prob')::numeric + 0.20*(sc->>'prof')::numeric
                     + 0.15*(sc->>'digi')::numeric + 0.25*(sc->>'exp')::numeric);
    if tg_op = 'INSERT' or old.completed_at is null then new.completed_at := coalesce(new.completed_at, now()); end if;
  end if;
  new.updated_at := now();
  return new;
end $$;
revoke execute on function public.students_guard() from public, anon, authenticated;

-- Percentile among real (non-sample) completed students; shown only once 50 have completed.
create or replace function public.get_my_percentile()
returns table (pct int, n int) language sql stable security definer set search_path = public as $$
  with pool as (select id, coalesce(override, total) as t from public.students where status = 'completed' and not sample),
       me as (select coalesce(override, total) as t from public.students where id = auth.uid() and status = 'completed')
  select case when (select count(*) from pool) >= 50 and exists (select 1 from me)
              then (select floor(100.0 * count(*) filter (where p.t < (select t from me)) / greatest(count(*) - 1, 1))::int from pool p) end,
         (select count(*)::int from pool);
$$;
revoke execute on function public.get_my_percentile() from public, anon;
grant execute on function public.get_my_percentile() to authenticated;

create or replace function public.get_talent_v2()
returns table (id uuid, university text, major text, grad_year text, location text, skills text[], total int, scores jsonb, sample boolean,
               status_now text, role_interests text[], position_types text[], duration text, availability text, pct int, exp_verified boolean)
language sql stable security definer set search_path = public as $$
  with pool as (select coalesce(override, total) as t from public.students where status = 'completed' and not sample),
       cnt as (select count(*) as c from pool)
  select s.id,
         case when s.university in ('Other university in Egypt','University abroad') and s.university_other <> '' then s.university_other else s.university end,
         case when s.major = 'Other' and s.major_other <> '' then s.major_other else s.major end,
         s.grad_year, s.location, s.skills, coalesce(s.override, s.total), s.scores, s.sample,
         s.status_now, s.role_interests, s.position_types, s.duration, s.availability,
         case when (select c from cnt) >= 50 and not s.sample
              then (select floor(100.0 * count(*) filter (where p.t < coalesce(s.override, s.total)) / greatest(count(*) - 1, 1))::int from pool p) end,
         s.exp_verified
  from public.students s
  where auth.uid() is not null and s.status = 'completed' and s.consent and s.visible;
$$;
revoke execute on function public.get_talent_v2() from public, anon;
grant execute on function public.get_talent_v2() to authenticated;

-- Earlier test attempts used the old 12 easy questions: send real (non-sample) students back to retake.
update public.students set status = 'registered', answers = '{}', task_writing = '', scores = null, total = null,
  completed_at = null, writing_score = null, writing_feedback = '', writing_scored_by = '', assessment_version = 2
where not sample and (status <> 'registered' or answers <> '{}');

-- Sample students: v2 answers, scored writing, verified experience (fictional).
update public.students s set answers = v.answers, writing_score = v.ws, writing_scored_by = 'sample', exp_verified = true,
  task_writing = 'Sample answer: Dear customer, I am truly sorry for the delay and for having to chase us three times. Our courier lost your parcel, which is our responsibility. We can send a replacement that reaches you within 2 days, or refund you in full within 5 to 7 working days. Just reply with your choice and I will arrange it today.',
  assessment_version = 2, status = 'completed'
from (values
  __SAMPLES__
) as v(email, answers, ws)
where s.email = v.email and s.sample;
