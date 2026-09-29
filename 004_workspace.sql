create table if not exists workspace_records (
  id uuid primary key default gen_random_uuid(),
  project_id uuid not null references projects(id) on delete cascade,
  record_type text not null,
  payload jsonb not null,
  created_at timestamptz not null default now()
);
create index if not exists idx_workspace_records_project on workspace_records(project_id, created_at desc);
