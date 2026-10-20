-- Intern+ profile v2: richer student questions, aligned employer roles, PDF CV storage
-- Run once in Supabase > SQL Editor, after setup.sql and 02_hardening.sql.

-- ---------- Students: new questions ----------
alter table public.students
  add column if not exists university_other text not null default '',
  add column if not exists major_other text not null default '',
  add column if not exists status_now text check (status_now in ('student','fresh_grad','working')),
  add column if not exists role_interests text[] not null default '{}',
  add column if not exists position_types text[] not null default '{}',
  add column if not exists availability text,
  add column if not exists duration text check (duration in ('year_round','breaks','either')),
  add column if not exists goals text not null default '',
  add column if not exists linkedin text not null default '',
  add column if not exists unique_skill text not null default '',
  add column if not exists cv_path text;

-- ---------- Roles: same questions from the employer side ----------
alter table public.roles
  add column if not exists category text not null default '',
  add column if not exists position_type text not null default '',
  add column if not exists duration text not null default '' check (duration in ('','year_round','summer','winter')),
  add column if not exists start_when text not null default '',
  add column if not exists work_mode text not null default '',
  add column if not exists fields text[] not null default '{}',
  add column if not exists stages text[] not null default '{}';

-- ---------- Students guard: a CV path must be the student's own folder ----------
create or replace function public.students_guard() returns trigger
language plpgsql security definer set search_path = public as $$
declare sc jsonb;
begin
  if not public.is_trusted() then
    if tg_op = 'INSERT' then
      new.id := auth.uid(); new.override := null; new.sample := false;
      new.status := 'registered'; new.answers := '{}'; new.code := null;
    else
      new.id := old.id; new.override := old.override; new.sample := old.sample;
      if old.status = 'completed' then new.status := 'completed'; new.answers := old.answers; end if;
    end if;
    if new.cv_path is not null and new.cv_path <> auth.uid()::text || '/cv.pdf' then
      raise exception 'CV must be uploaded to your own folder.';
    end if;
  end if;
  new.cohort := case split_part(upper(coalesce(new.code,'')), '-', 1)
    when 'PAID' then 'A' when 'SPON' then 'B' when 'TEAM' then 'Team' else null end;
  if new.code is not null and new.cohort is null then
    raise exception 'That access code is not recognised.';
  end if;
  if new.status in ('started','completed') and new.cohort is null then
    raise exception 'Enter a valid access code before starting the assessment.';
  end if;
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

-- ---------- Anonymous talent pool and open roles, with the new fields ----------
drop function if exists public.get_talent();
create function public.get_talent()
returns table (id uuid, university text, major text, grad_year text, location text, skills text[], total int, scores jsonb, sample boolean,
               status_now text, role_interests text[], position_types text[], duration text, availability text)
language sql stable security definer set search_path = public as $$
  select s.id,
         case when s.university in ('Other university in Egypt','University abroad') and s.university_other <> '' then s.university_other else s.university end,
         case when s.major = 'Other' and s.major_other <> '' then s.major_other else s.major end,
         s.grad_year, s.location, s.skills, coalesce(s.override, s.total), s.scores, s.sample,
         s.status_now, s.role_interests, s.position_types, s.duration, s.availability
  from public.students s
  where auth.uid() is not null and s.status = 'completed' and s.consent and s.visible;
$$;

drop function if exists public.get_openings();
create function public.get_openings()
returns table (id uuid, title text, company text, location text, min_score int, must text[], nice text[], majors text[], years text[], published_at timestamptz,
               category text, position_type text, duration text, start_when text, work_mode text, fields text[], stages text[])
language sql stable security definer set search_path = public as $$
  select r.id, r.title, r.company, r.location, r.min_score, r.must, r.nice, r.majors, r.years, r.published_at,
         r.category, r.position_type, r.duration, r.start_when, r.work_mode, r.fields, r.stages
  from public.roles r
  where auth.uid() is not null and r.status = 'live';
$$;
revoke execute on function public.get_talent(), public.get_openings() from public, anon;
grant execute on function public.get_talent(), public.get_openings() to authenticated;

-- ---------- Private CV storage (PDF only, 5 MB) ----------
insert into storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
values ('cvs', 'cvs', false, 5242880, array['application/pdf'])
on conflict (id) do update set public = false, file_size_limit = 5242880, allowed_mime_types = array['application/pdf'];

drop policy if exists "students manage own CV" on storage.objects;
create policy "students manage own CV" on storage.objects for all to authenticated
  using (bucket_id = 'cvs' and (storage.foldername(name))[1] = auth.uid()::text)
  with check (bucket_id = 'cvs' and (storage.foldername(name))[1] = auth.uid()::text);

drop policy if exists "admins read CVs" on storage.objects;
create policy "admins read CVs" on storage.objects for select to authenticated
  using (bucket_id = 'cvs' and public.is_admin());

drop policy if exists "employers read shortlisted CVs" on storage.objects;
create policy "employers read shortlisted CVs" on storage.objects for select to authenticated
  using (bucket_id = 'cvs' and exists (
    select 1 from public.shortlist s
    where s.employer_id = auth.uid() and s.student_id::text = (storage.foldername(name))[1]));

-- ---------- Sample students: new lists and answers (fictional) ----------
update public.students s set
  university = v.university, major = v.major, location = v.location, status_now = v.status_now,
  role_interests = v.ri, position_types = v.pt, duration = v.duration, availability = v.availability,
  skills = v.skills, linkedin = 'https://linkedin.com/in/intern-plus-sample', goals = v.goals
from (values
  ('nour.sample@example.com','American University in Cairo (AUC)','Marketing','New Cairo','student',array['Marketing','Content & Social Media'],array['Internship (Paid)','Entry-level part-time job'],'either','Within 1 month',
     array['Social Media Management','Content Creation','Canva','Copywriting','Arabic & English (fluent)','AI Tools (ChatGPT, Claude, Gemini)'],'I want to grow brands on social media and learn performance marketing.'),
  ('youssef.sample@example.com','German University in Cairo (GUC)','Business Administration','Nasr City','student',array['Data & Analytics','Business Development'],array['Internship (Paid)','Entry-level full-time job'],'year_round','Immediately',
     array['Excel / Spreadsheets','Power BI','SQL','Data Analysis','Market Research','Prompt Engineering'],'I want to turn messy business data into decisions.'),
  ('laila.sample@example.com','Cairo University','Mass Communication','Dokki','fresh_grad',array['Content & Social Media','Marketing'],array['Entry-level full-time job','Freelance'],'year_round','Immediately',
     array['Content Creation','Public Speaking','Social Media Management','Market Research','Video Editing'],'Storytelling for brands, especially video.'),
  ('omar.sample@example.com','Ain Shams University','Commerce','Heliopolis','student',array['Finance & Accounting','Operations'],array['Internship (Paid)','Internship (for experience / credit)'],'breaks','Within 3 months',
     array['Excel / Spreadsheets','Accounting / Finance','Data Analysis'],'Finance and operations at a fast-growing company.'),
  ('mariam.sample@example.com','American University in Cairo (AUC)','Economics','Maadi','student',array['Data & Analytics','Finance & Accounting'],array['Internship (Paid)'],'breaks','Within 3 months',
     array['Excel / Spreadsheets','Python','Data Analysis','Market Research','SQL','AI Automation (Zapier, Make, n8n)'],'Economic research and data work.'),
  ('karim.sample@example.com','Alexandria University','Mechatronics Engineering','Alexandria','student',array['Engineering','Tech'],array['Internship (Paid)','Project Based'],'either','Within 1 month',
     array['Project Management','Excel / Spreadsheets','Python','Vibe Coding'],'Building hardware and automation products.'),
  ('salma.sample@example.com','British University in Egypt (BUE)','Business Administration','Shorouk City','working',array['Sales','Business Development'],array['Entry-level full-time job'],'year_round','Within 1 month',
     array['Sales','Customer Service','Public Speaking','Arabic & English (fluent)','CRM Tools (HubSpot, Salesforce)'],'B2B sales at a tech company.'),
  ('hana.sample@example.com','Helwan University','Graphic Design','6th of October','student',array['Design','Content & Social Media'],array['Internship (for experience / credit)','Freelance'],'breaks','Within 3 months',
     array['Canva','Social Media Management','Adobe Photoshop / Illustrator','Graphic Design'],'Visual design for brands.')
) as v(email, university, major, location, status_now, ri, pt, duration, availability, skills, goals)
where s.email = v.email and s.sample;
