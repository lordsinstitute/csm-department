-- EngineerAI initial schema, RLS, storage buckets, and seed data.
-- Runnable top-to-bottom in the Supabase SQL editor on a fresh project.
-- Per specs/contracts.md (frozen). No triggers, no functions, no extra
-- indexes beyond PK/FK -- the backend sets updated_at itself.

-- ============================================================
-- 1. Tables
-- ============================================================

create table departments (
  id uuid primary key default gen_random_uuid(),
  name text not null
);

create table machines (
  id uuid primary key default gen_random_uuid(),
  department_id uuid not null references departments(id),
  name text not null,
  image_url text
);

create table problems (
  id uuid primary key default gen_random_uuid(),
  machine_id uuid not null references machines(id),
  name text not null,
  description text
);

create table inspections (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id),
  machine_id_fk uuid not null references machines(id),
  problem_id_fk uuid not null references problems(id),
  photo_url text,
  answers jsonb,
  vision_result jsonb,
  diagnosis jsonb,
  repair_plan jsonb,
  checklist_state jsonb,
  pdf_url text,
  status text not null default 'draft'
    check (status in ('draft', 'analyzing', 'diagnosed', 'repairing', 'complete')),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

-- ============================================================
-- 2. Row Level Security
-- ============================================================

alter table departments enable row level security;
alter table machines enable row level security;
alter table problems enable row level security;
alter table inspections enable row level security;

-- Reference tables: select for any authenticated user (includes anonymous).
create policy "departments_select_authenticated" on departments
  for select to authenticated using (true);

create policy "machines_select_authenticated" on machines
  for select to authenticated using (true);

create policy "problems_select_authenticated" on problems
  for select to authenticated using (true);

-- inspections: authenticated users (including anonymous) can select/insert/update
-- only rows where auth.uid() = user_id.
create policy "inspections_select_own" on inspections
  for select to authenticated using (auth.uid() = user_id);

create policy "inspections_insert_own" on inspections
  for insert to authenticated with check (auth.uid() = user_id);

create policy "inspections_update_own" on inspections
  for update to authenticated
  using (auth.uid() = user_id)
  with check (auth.uid() = user_id);

-- ============================================================
-- 3. Storage
-- ============================================================

insert into storage.buckets (id, name, public)
values ('inspection-photos', 'inspection-photos', false);

insert into storage.buckets (id, name, public)
values ('inspection-reports', 'inspection-reports', false);

-- inspection-photos: authenticated users read/write only their own auth.uid()/ folder.
create policy "inspection_photos_select_own" on storage.objects
  for select to authenticated
  using (bucket_id = 'inspection-photos' and (storage.foldername(name))[1] = auth.uid()::text);

create policy "inspection_photos_insert_own" on storage.objects
  for insert to authenticated
  with check (bucket_id = 'inspection-photos' and (storage.foldername(name))[1] = auth.uid()::text);

create policy "inspection_photos_update_own" on storage.objects
  for update to authenticated
  using (bucket_id = 'inspection-photos' and (storage.foldername(name))[1] = auth.uid()::text);

-- inspection-reports: authenticated users read-only their own auth.uid()/ folder.
-- (Backend writes reports using the service key, which bypasses RLS.)
create policy "inspection_reports_select_own" on storage.objects
  for select to authenticated
  using (bucket_id = 'inspection-reports' and (storage.foldername(name))[1] = auth.uid()::text);

-- ============================================================
-- 4. Seed data
-- ============================================================

with dept as (
  insert into departments (name) values ('Industrial Equipment')
  returning id
),
machine as (
  insert into machines (department_id, name)
  select id, 'Electric Motor' from dept
  returning id
)
insert into problems (machine_id, name, description)
select machine.id, p.name, p.description
from machine, (
  values
    ('Vibration', 'Motor shakes or vibrates abnormally during operation.'),
    ('Overheating', 'Motor housing runs hotter than normal under load.'),
    ('Noise', 'Motor produces abnormal grinding, humming, or rattling sounds.'),
    ('Won''t Start', 'Motor fails to start or run when powered on.')
) as p(name, description);
