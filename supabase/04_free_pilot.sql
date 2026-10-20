-- Intern+ free pilot: students no longer need an access code to take the assessment.
-- Applied 2026-10-20 through the Supabase connector. Kept here for the record.
create or replace function public.students_guard() returns trigger
language plpgsql security definer set search_path = public as $$
declare sc jsonb;
begin
  if not public.is_trusted() then
    if tg_op = 'INSERT' then
      new.id := auth.uid(); new.override := null; new.sample := false;
      new.status := 'registered'; new.answers := '{}'; new.code := null;
    else
      new.id := old.id; new.override := old.override; new.sample := old.sample; new.code := old.code;
      if old.status = 'completed' then new.status := 'completed'; new.answers := old.answers; end if;
    end if;
    if new.cv_path is not null and new.cv_path <> auth.uid()::text || '/cv.pdf' then
      raise exception 'CV must be uploaded to your own folder.';
    end if;
  end if;
  new.cohort := case split_part(upper(coalesce(new.code,'')), '-', 1)
    when 'PAID' then 'A' when 'SPON' then 'B' when 'TEAM' then 'Team' else 'Pilot' end;
  if new.status = 'completed' then
    if (select count(*) from jsonb_object_keys(new.answers)) < 12 then
      raise exception 'Answer all 12 questions before finishing.';
    end if;
    sc := public.score_student(new.answers, new.internships, new.projects, new.activities);
    new.scores := sc;
    new.total := round(0.20*(sc->>'comm')::numeric + 0.20*(sc->>'prob')::numeric + 0.20*(sc->>'prof')::numeric
                     + 0.15*(sc->>'digi')::numeric + 0.25*(sc->>'exp')::numeric);
    if tg_op = 'INSERT' or old.completed_at is null then new.completed_at := coalesce(new.completed_at, now()); end if;
  end if;
  new.updated_at := now();
  return new;
end $$;
revoke execute on function public.students_guard() from public, anon, authenticated;
