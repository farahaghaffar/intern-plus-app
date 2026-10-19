-- ============================================================
-- Intern+ pilot: database setup for Supabase
-- Paste into Supabase > SQL Editor > New query, then click Run.
-- Safe to run once on a new project.
-- ============================================================

-- ---------- Accounts and roles ----------
create table public.profiles (
  id uuid primary key references auth.users on delete cascade,
  role text not null default 'student' check (role in ('student','employer','admin')),
  created_at timestamptz not null default now()
);

create or replace function public.is_admin() returns boolean
language sql stable security definer set search_path = public as $$
  select exists (select 1 from public.profiles where id = auth.uid() and role = 'admin');
$$;

-- "trusted" = running from the SQL editor / server (no signed-in user) or an admin
create or replace function public.is_trusted() returns boolean
language sql stable security definer set search_path = public as $$
  select auth.uid() is null or public.is_admin();
$$;

-- New sign-ups get a profile. Users can pick student or employer, never admin.
create or replace function public.handle_new_user() returns trigger
language plpgsql security definer set search_path = public as $$
begin
  insert into public.profiles (id, role)
  values (new.id, case when new.raw_user_meta_data->>'role' = 'employer' then 'employer' else 'student' end)
  on conflict (id) do nothing;
  return new;
end $$;

drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created after insert on auth.users
  for each row execute function public.handle_new_user();

-- ---------- Students ----------
create table public.students (
  id uuid primary key default auth.uid(),
  name text not null,
  email text not null,
  phone text not null default '',
  location text, university text, major text, grad_year text,
  cv text not null default '',
  internships int not null default 0 check (internships between 0 and 10),
  projects int not null default 0 check (projects between 0 and 20),
  activities int not null default 0 check (activities between 0 and 20),
  skills text[] not null default '{}',
  consent boolean not null default false,
  visible boolean not null default true,
  code text, cohort text,
  status text not null default 'registered' check (status in ('registered','started','completed')),
  answers jsonb not null default '{}',
  scores jsonb, total int,
  override int check (override between 0 and 100),
  survey text check (survey in ('useful','somewhat','not')),
  sample boolean not null default false,
  created_at timestamptz not null default now(),
  completed_at timestamptz,
  updated_at timestamptz not null default now()
);

-- Server-side scoring, so a student cannot set their own score.
-- Draft question bank v1: points per answer option (2 best, 1 partial, 0 weak).
create or replace function public.score_student(p_answers jsonb, p_int int, p_proj int, p_act int)
returns jsonb language plpgsql immutable as $$
declare
  pts jsonb := '{"c1": [0, 2, 0, 1], "c2": [1, 0, 2, 0], "c3": [0, 2, 0, 1], "p1": [0, 2, 0, 1], "p2": [2, 0, 0, 0], "p3": [0, 2, 1, 0], "r1": [0, 2, 0, 1], "r2": [0, 2, 0, 0], "r3": [2, 1, 0, 0], "d1": [2, 0, 0, 0], "d2": [0, 2, 0, 0], "d3": [0, 0, 2, 0]}';
  cats jsonb := '{"comm":["c1","c2","c3"],"prob":["p1","p2","p3"],"prof":["r1","r2","r3"],"digi":["d1","d2","d3"]}';
  k text; q text; a int; p int; res jsonb := '{}';
begin
  for k in select jsonb_object_keys(cats) loop
    p := 0;
    for q in select jsonb_array_elements_text(cats->k) loop
      a := (p_answers->>q)::int;
      if a between 0 and 3 then p := p + (pts->q->>a)::int; end if;
    end loop;
    res := res || jsonb_build_object(k, round(p::numeric / 6 * 100));
  end loop;
  res := res || jsonb_build_object('exp', least(100, least(3, coalesce(p_int,0)) * 35 + coalesce(p_proj,0) * 15 + coalesce(p_act,0) * 10));
  return res;
end $$;

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

create trigger students_guard before insert or update on public.students
  for each row execute function public.students_guard();

-- Anonymous talent pool: no name, email, phone or CV. Only consenting, visible, assessed students.
create view public.talent as
  select id, university, major, grad_year, location, skills,
         coalesce(override, total) as total, scores, internships, projects, activities, sample
  from public.students
  where status = 'completed' and consent and visible;

-- ---------- Employer roles ----------
create table public.roles (
  id uuid primary key default gen_random_uuid(),
  employer_id uuid not null default auth.uid(),
  title text not null,
  company text not null,
  location text not null default 'Any',
  min_score int not null default 60 check (min_score between 0 and 100),
  must text[] not null default '{}',
  nice text[] not null default '{}',
  majors text[] not null default '{}',
  years text[] not null default '{}',
  ats text not null default '',
  status text not null default 'review' check (status in ('review','live','closed')),
  created_at timestamptz not null default now(),
  published_at timestamptz
);

-- Employers cannot publish their own roles; Intern+ approves them. Employers may close a role.
create or replace function public.roles_guard() returns trigger
language plpgsql security definer set search_path = public as $$
begin
  if not public.is_trusted() then
    if tg_op = 'INSERT' then
      new.employer_id := auth.uid(); new.status := 'review'; new.published_at := null;
    else
      new.employer_id := old.employer_id; new.published_at := old.published_at;
      if new.status <> 'closed' then new.status := old.status; end if;
    end if;
  elsif tg_op = 'UPDATE' and new.status = 'live' and old.status <> 'live' then
    new.published_at := now();
  end if;
  return new;
end $$;

create trigger roles_guard before insert or update on public.roles
  for each row execute function public.roles_guard();

-- Public list of approved roles, without employer details beyond company name.
create view public.openings as
  select id, title, company, location, min_score, must, nice, majors, years, published_at
  from public.roles where status = 'live';

create or replace function public.role_is_live(p_role uuid) returns boolean
language sql stable security definer set search_path = public as $$
  select exists (select 1 from public.roles where id = p_role and status = 'live');
$$;

-- ---------- Applications, intro requests, shortlists ----------
create table public.applications (
  role_id uuid not null references public.roles on delete cascade,
  student_id uuid not null default auth.uid() references public.students on delete cascade,
  created_at timestamptz not null default now(),
  primary key (role_id, student_id)
);

create table public.intro_requests (
  role_id uuid not null references public.roles on delete cascade,
  student_id uuid not null references public.students on delete cascade,
  employer_id uuid not null default auth.uid(),
  created_at timestamptz not null default now(),
  primary key (role_id, student_id)
);

create table public.shortlist (
  role_id uuid not null references public.roles on delete cascade,
  student_id uuid not null references public.students on delete cascade,
  employer_id uuid not null,
  card jsonb not null,
  match int not null default 0,
  status text not null default 'Shortlisted' check (status in ('Shortlisted','Interviewing','Hired','Not a fit')),
  source text not null default 'intern' check (source in ('intern','apply','request')),
  sent_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  primary key (role_id, student_id)
);

-- ---------- Row-level security ----------
alter table public.profiles enable row level security;
alter table public.students enable row level security;
alter table public.roles enable row level security;
alter table public.applications enable row level security;
alter table public.intro_requests enable row level security;
alter table public.shortlist enable row level security;

create policy "read own profile" on public.profiles for select using (id = auth.uid() or public.is_admin());

create policy "student reads own" on public.students for select using (id = auth.uid() or public.is_admin());
create policy "student creates own" on public.students for insert with check (id = auth.uid() or public.is_admin());
create policy "student updates own" on public.students for update using (id = auth.uid() or public.is_admin()) with check (id = auth.uid() or public.is_admin());
create policy "admin deletes students" on public.students for delete using (public.is_admin());

create policy "employer reads own roles" on public.roles for select using (employer_id = auth.uid() or public.is_admin());
create policy "employer creates roles" on public.roles for insert with check (employer_id = auth.uid() or public.is_admin());
create policy "employer updates own roles" on public.roles for update using (employer_id = auth.uid() or public.is_admin());
create policy "admin deletes roles" on public.roles for delete using (public.is_admin());

create policy "student reads own applications" on public.applications for select using (student_id = auth.uid() or public.is_admin());
create policy "student applies to live roles" on public.applications for insert with check (student_id = auth.uid() and public.role_is_live(role_id));
create policy "student withdraws" on public.applications for delete using (student_id = auth.uid() or public.is_admin());

create policy "employer reads own requests" on public.intro_requests for select using (employer_id = auth.uid() or public.is_admin());
create policy "employer requests intros for own roles" on public.intro_requests for insert
  with check (employer_id = auth.uid() and exists (select 1 from public.roles r where r.id = role_id and r.employer_id = auth.uid()));
create policy "admin clears requests" on public.intro_requests for delete using (public.is_admin() or employer_id = auth.uid());

create policy "employer reads own shortlist" on public.shortlist for select using (employer_id = auth.uid() or public.is_admin());
create policy "admin sends shortlist" on public.shortlist for insert with check (public.is_admin());
create policy "employer updates status" on public.shortlist for update using (employer_id = auth.uid() or public.is_admin());
create policy "admin removes from shortlist" on public.shortlist for delete using (public.is_admin());

-- ---------- Access for the app ----------
grant usage on schema public to anon, authenticated;
revoke all on all tables in schema public from anon;
grant select, insert, update, delete on public.profiles, public.students, public.roles,
  public.applications, public.intro_requests, public.shortlist to authenticated;
revoke insert, update, delete on public.profiles from authenticated;
-- employers may only change a shortlisted candidate's status
revoke update on public.shortlist from authenticated;
grant update (status, updated_at) on public.shortlist to authenticated;
-- the two views: signed-in users only
revoke all on public.talent, public.openings from anon;
grant select on public.talent, public.openings to authenticated;

-- ---------- Sample students (fictional, marked sample) ----------
insert into public.students (id, name, email, location, university, major, grad_year, internships, projects, activities, skills, answers, consent, visible, code, status, sample)
select gen_random_uuid(), v.name, v.email, v.location, v.university, v.major, v.grad_year, v.i, v.p, v.a, v.skills, v.answers, true, true, 'TEAM-SAMPLE', 'completed', true
from (values
  ('Nour Khaled','nour.sample@example.com','Cairo','AUC','Marketing','2026',1,3,2,array['Social media','Content writing','Canva','Copywriting','Arabic/English bilingual']::text[],'{"c1": 1, "c2": 2, "c3": 1, "p1": 1, "p2": 0, "p3": 1, "r1": 1, "r2": 1, "r3": 0, "d1": 1, "d2": 1, "d3": 2}'::jsonb),
  ('Youssef Adel','youssef.sample@example.com','Cairo','GUC','Business Administration','2026',2,2,1,array['Excel','Power BI','SQL','Data analysis','Research']::text[],'{"c1": 1, "c2": 0, "c3": 1, "p1": 1, "p2": 0, "p3": 1, "r1": 1, "r2": 1, "r3": 0, "d1": 0, "d2": 1, "d3": 2}'::jsonb),
  ('Laila Mostafa','laila.sample@example.com','Giza','Cairo University','Mass Communication','2025',0,2,3,array['Content writing','Public speaking','Social media','Research']::text[],'{"c1": 1, "c2": 2, "c3": 1, "p1": 1, "p2": 1, "p3": 1, "r1": 1, "r2": 1, "r3": 0, "d1": 1, "d2": 1, "d3": 2}'::jsonb),
  ('Omar Fathy','omar.sample@example.com','Cairo','Ain Shams University','Commerce','2026',1,1,1,array['Excel','Accounting','Data analysis']::text[],'{"c1": 3, "c2": 2, "c3": 1, "p1": 1, "p2": 0, "p3": 1, "r1": 1, "r2": 1, "r3": 1, "d1": 0, "d2": 1, "d3": 2}'::jsonb),
  ('Mariam Hassan','mariam.sample@example.com','Cairo','AUC','Economics','2027',0,3,2,array['Excel','Python','Data analysis','Research','SQL']::text[],'{"c1": 1, "c2": 2, "c3": 1, "p1": 1, "p2": 0, "p3": 1, "r1": 3, "r2": 1, "r3": 0, "d1": 0, "d2": 1, "d3": 2}'::jsonb),
  ('Karim Samir','karim.sample@example.com','Alexandria','Alexandria University','Engineering','2026',1,2,0,array['Project management','Excel','Python']::text[],'{"c1": 1, "c2": 2, "c3": 3, "p1": 3, "p2": 0, "p3": 1, "r1": 1, "r2": 1, "r3": 0, "d1": 0, "d2": 1, "d3": 2}'::jsonb),
  ('Salma Tarek','salma.sample@example.com','Cairo','BUE','Business Administration','2025',2,0,2,array['Sales','Customer service','Public speaking','Arabic/English bilingual']::text[],'{"c1": 1, "c2": 2, "c3": 1, "p1": 1, "p2": 0, "p3": 2, "r1": 1, "r2": 1, "r3": 0, "d1": 0, "d2": 0, "d3": 2}'::jsonb),
  ('Hana Ibrahim','hana.sample@example.com','Giza','Helwan University','Marketing','2027',0,1,1,array['Canva','Social media','Adobe Creative Suite']::text[],'{"c1": 3, "c2": 2, "c3": 1, "p1": 3, "p2": 0, "p3": 1, "r1": 1, "r2": 0, "r3": 0, "d1": 0, "d2": 1, "d3": 0}'::jsonb)
) as v(name, email, location, university, major, grad_year, i, p, a, skills, answers);

-- ---------- Make Farah and Sara admins (run AFTER they sign up) ----------
-- update public.profiles set role = 'admin'
--   where id in (select id from auth.users where email in ('farahaghaffar@be-empire.com', 'SARA_EMAIL_HERE'));
