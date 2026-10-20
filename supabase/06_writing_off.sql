-- Pilot: writing task switched off. Only the 24 questions are required to finish.
-- Sample students are scored on the questions only.

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
    if (select count(*) from jsonb_object_keys(new.answers)) < 24 then
      raise exception 'Answer all 24 questions before finishing.';
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

update public.students set writing_score = null, writing_scored_by = '', task_writing = '' where sample;
